#!/usr/bin/env python3
# Auto-add user local site-packages so Google packages are found in any env
import sys as _sys, os as _os, glob as _glob
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

"""
Unified Google Calendar API script.

Usage:
  python3 calendar.py <alias> list [days_ahead=7] [days_behind=1]
  python3 calendar.py <alias> search <query>
  python3 calendar.py <alias> get <event_id>
  python3 calendar.py <alias> create <title> <start_iso> <end_iso> [attendees_csv] [description] [location]
  python3 calendar.py <alias> update <event_id> [title] [start_iso] [end_iso] [description] [location]
  python3 calendar.py <alias> delete <event_id>
  python3 calendar.py <alias> rsvp <event_id> <accept|decline|tentative>
  python3 calendar.py <alias> free_slots <date_iso> [duration_minutes=30]
  python3 calendar.py <alias> calendars

All commands output JSON.

Date/time format: ISO 8601, e.g. 2026-03-30T14:00:00 or 2026-03-30 (all-day)
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import glob as _g2

def _find_data_dir():
    if "MULTI_GOOGLE_HOME" in os.environ:
        d = os.environ["MULTI_GOOGLE_HOME"]; os.makedirs(d, exist_ok=True); return d
    ex = _g2.glob("/sessions/*/mnt/.multi-google")
    if ex: return ex[0]
    mnts = _g2.glob("/sessions/*/mnt")
    if mnts:
        d = os.path.join(mnts[0], ".multi-google"); os.makedirs(d, exist_ok=True); return d
    return os.path.expanduser("~/.multi-google")

CONFIG_DIR = _find_data_dir()


def error(msg):
    print(json.dumps({'error': msg}))
    sys.exit(1)


def get_service(alias):
    token_path = os.path.join(CONFIG_DIR, 'accounts', f'{alias}.json')
    if not os.path.exists(token_path):
        error(f'Account "{alias}" not found.')
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        error('Run: pip install google-api-python-client --break-system-packages')

    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            error(f'Token refresh failed: {e}')
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def check_service(alias):
    try:
        accounts = json.load(open(os.path.join(CONFIG_DIR, 'accounts.json')))
        if 'calendar' not in accounts.get(alias, {}).get('services', []):
            error(f'Calendar not enabled for account "{alias}".')
    except Exception:
        pass


def format_event(event):
    start = event.get('start', {})
    end = event.get('end', {})
    attendees = event.get('attendees', [])
    my_status = next((a.get('responseStatus') for a in attendees if a.get('self')), 'accepted')
    return {
        'id': event.get('id'),
        'title': event.get('summary', '(No title)'),
        'start': start.get('dateTime', start.get('date', '')),
        'end': end.get('dateTime', end.get('date', '')),
        'location': event.get('location', ''),
        'description': (event.get('description', '') or '')[:500],
        'attendees': [{'email': a.get('email'), 'name': a.get('displayName', ''), 'status': a.get('responseStatus')} for a in attendees],
        'organizer': event.get('organizer', {}).get('email', ''),
        'is_organizer': event.get('organizer', {}).get('self', False),
        'my_status': my_status,
        'meet_link': event.get('hangoutLink', ''),
        'is_all_day': 'date' in start and 'dateTime' not in start,
        'recurring': bool(event.get('recurringEventId')),
        'calendar_id': event.get('organizer', {}).get('email', 'primary'),
    }


def cmd_list(svc, days_ahead=7, days_behind=1):
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=int(days_behind))).isoformat()
    time_max = (now + timedelta(days=int(days_ahead))).isoformat()
    try:
        result = svc.events().list(
            calendarId='primary', timeMin=time_min, timeMax=time_max,
            maxResults=50, singleEvents=True, orderBy='startTime'
        ).execute()
        events = [format_event(e) for e in result.get('items', []) if e.get('status') != 'cancelled']
        # Remove declined
        events = [e for e in events if e['my_status'] != 'declined']
        print(json.dumps(events, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'List failed: {e}')


def cmd_search(svc, query):
    try:
        result = svc.events().list(
            calendarId='primary', q=query, maxResults=20,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = [format_event(e) for e in result.get('items', []) if e.get('status') != 'cancelled']
        print(json.dumps(events, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Search failed: {e}')


def cmd_get(svc, event_id):
    try:
        event = svc.events().get(calendarId='primary', eventId=event_id).execute()
        print(json.dumps(format_event(event), ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Get failed: {e}')


def cmd_create(svc, title, start_iso, end_iso, attendees_csv='', description='', location=''):
    def parse_dt(s):
        # All-day if date only
        if 'T' not in s and len(s) == 10:
            return {'date': s}
        return {'dateTime': s, 'timeZone': 'UTC'}

    body = {
        'summary': title,
        'start': parse_dt(start_iso),
        'end': parse_dt(end_iso),
    }
    if description:
        body['description'] = description
    if location:
        body['location'] = location
    if attendees_csv:
        body['attendees'] = [{'email': e.strip()} for e in attendees_csv.split(',') if e.strip()]

    try:
        event = svc.events().insert(
            calendarId='primary', body=body,
            sendUpdates='all' if attendees_csv else 'none'
        ).execute()
        print(json.dumps({'success': True, 'id': event['id'], 'link': event.get('htmlLink', ''), **format_event(event)}))
    except Exception as e:
        error(f'Create failed: {e}')


def cmd_update(svc, event_id, title='', start_iso='', end_iso='', description='', location=''):
    try:
        event = svc.events().get(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        error(f'Could not fetch event: {e}')

    def parse_dt(s):
        if 'T' not in s and len(s) == 10:
            return {'date': s}
        return {'dateTime': s, 'timeZone': 'UTC'}

    if title:
        event['summary'] = title
    if start_iso:
        event['start'] = parse_dt(start_iso)
    if end_iso:
        event['end'] = parse_dt(end_iso)
    if description:
        event['description'] = description
    if location:
        event['location'] = location

    try:
        updated = svc.events().update(
            calendarId='primary', eventId=event_id, body=event,
            sendUpdates='all'
        ).execute()
        print(json.dumps({'success': True, **format_event(updated)}))
    except Exception as e:
        error(f'Update failed: {e}')


def cmd_delete(svc, event_id):
    try:
        svc.events().delete(calendarId='primary', eventId=event_id, sendUpdates='all').execute()
        print(json.dumps({'success': True, 'action': 'deleted', 'id': event_id}))
    except Exception as e:
        error(f'Delete failed: {e}')


def cmd_rsvp(svc, event_id, response):
    valid = ['accept', 'decline', 'tentative']
    if response not in valid:
        error(f'Response must be one of: {", ".join(valid)}')

    status_map = {'accept': 'accepted', 'decline': 'declined', 'tentative': 'tentative'}

    try:
        event = svc.events().get(calendarId='primary', eventId=event_id).execute()
        for attendee in event.get('attendees', []):
            if attendee.get('self'):
                attendee['responseStatus'] = status_map[response]
                break

        updated = svc.events().patch(
            calendarId='primary', eventId=event_id,
            body={'attendees': event.get('attendees', [])},
            sendUpdates='all'
        ).execute()
        print(json.dumps({'success': True, 'rsvp': status_map[response], 'event': format_event(updated)}))
    except Exception as e:
        error(f'RSVP failed: {e}')


def cmd_free_slots(svc, date_iso, duration_minutes=30):
    """Find free time slots on a given date."""
    duration = int(duration_minutes)
    try:
        day_start = datetime.fromisoformat(f'{date_iso}T00:00:00').replace(tzinfo=timezone.utc)
        day_end = datetime.fromisoformat(f'{date_iso}T23:59:59').replace(tzinfo=timezone.utc)
    except Exception:
        error(f'Invalid date format: {date_iso}. Use YYYY-MM-DD.')

    try:
        result = svc.freebusy().query(body={
            'timeMin': day_start.isoformat(),
            'timeMax': day_end.isoformat(),
            'items': [{'id': 'primary'}]
        }).execute()
    except Exception as e:
        error(f'Freebusy query failed: {e}')

    busy = result.get('calendars', {}).get('primary', {}).get('busy', [])
    busy_ranges = [(datetime.fromisoformat(b['start'].replace('Z', '+00:00')),
                    datetime.fromisoformat(b['end'].replace('Z', '+00:00'))) for b in busy]

    # Work hours: 9am–6pm
    work_start = day_start.replace(hour=9)
    work_end = day_start.replace(hour=18)

    slots = []
    current = work_start
    slot_delta = timedelta(minutes=duration)

    while current + slot_delta <= work_end:
        slot_end = current + slot_delta
        overlaps = any(s < slot_end and e > current for s, e in busy_ranges)
        if not overlaps:
            slots.append({'start': current.isoformat(), 'end': slot_end.isoformat()})
        current += timedelta(minutes=30)  # step in 30min increments

    print(json.dumps({'date': date_iso, 'duration_minutes': duration, 'free_slots': slots[:10]}, ensure_ascii=False, indent=2))


def cmd_calendars(svc):
    try:
        result = svc.calendarList().list().execute()
        cals = [{'id': c['id'], 'name': c.get('summary', ''), 'primary': c.get('primary', False)} for c in result.get('items', [])]
        print(json.dumps(cals, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Calendars fetch failed: {e}')


COMMANDS = {
    'list': (cmd_list, 0, 2),
    'search': (cmd_search, 1, 1),
    'get': (cmd_get, 1, 1),
    'create': (cmd_create, 3, 6),
    'update': (cmd_update, 1, 5),
    'delete': (cmd_delete, 1, 1),
    'rsvp': (cmd_rsvp, 2, 2),
    'free_slots': (cmd_free_slots, 1, 2),
    'calendars': (cmd_calendars, 0, 0),
}


def main():
    if len(sys.argv) < 3:
        print('Usage: calendar.py <alias> <command> [args...]')
        print(f'Commands: {", ".join(COMMANDS.keys())}')
        sys.exit(1)

    alias, cmd = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]

    if cmd not in COMMANDS:
        error(f'Unknown command "{cmd}". Available: {", ".join(COMMANDS.keys())}')

    check_service(alias)
    svc = get_service(alias)
    fn, min_a, max_a = COMMANDS[cmd]

    if len(args) < min_a or len(args) > max_a:
        error(f'Command "{cmd}" needs {min_a}–{max_a} args, got {len(args)}')

    fn(svc, *args)


if __name__ == '__main__':
    main()
