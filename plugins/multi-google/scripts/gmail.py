#!/usr/bin/env python3
# Auto-add user local site-packages so Google packages are found in any env
import sys as _sys, os as _os, glob as _glob
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

"""
Unified Gmail API script. One script, all operations.

Usage:
  python3 gmail.py <alias> search <query> [max=20]
  python3 gmail.py <alias> read <message_id>
  python3 gmail.py <alias> send <to> <subject> <body>
  python3 gmail.py <alias> reply <message_id> <body>
  python3 gmail.py <alias> forward <message_id> <to> [note]
  python3 gmail.py <alias> archive <message_id>
  python3 gmail.py <alias> trash <message_id>
  python3 gmail.py <alias> label <message_id> <label_name>
  python3 gmail.py <alias> mark_read <message_id>
  python3 gmail.py <alias> labels
  python3 gmail.py <alias> profile

All commands output JSON.
"""
import base64
import email as email_lib
import json
import os
import sys
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import glob as _g2

def _find_data_dir():
    if "MULTI_GOOGLE_HOME" in os.environ:
        d = os.environ["MULTI_GOOGLE_HOME"]; os.makedirs(d, exist_ok=True); return d
    # CLAUDE_CONFIG_DIR is always set by Cowork on any OS (Mac, Windows, Linux)
    # It points to /sessions/SESSION/mnt/.claude — parent is the mnt folder
    claude_cfg = os.environ.get("CLAUDE_CONFIG_DIR", "")
    if claude_cfg:
        d = os.path.join(os.path.dirname(claude_cfg), ".multi-google")
        os.makedirs(d, exist_ok=True); return d
    # Fallback: match current session by HOME path
    import glob as _gf
    session = os.path.basename(os.environ.get("HOME", ""))
    for candidate in _gf.glob("/sessions/*/mnt"):
        if session and session in candidate:
            d = os.path.join(candidate, ".multi-google"); os.makedirs(d, exist_ok=True); return d
    for candidate in _gf.glob("/sessions/*/mnt"):
        d = os.path.join(candidate, ".multi-google"); os.makedirs(d, exist_ok=True); return d
    return os.path.expanduser("~/.multi-google")

CONFIG_DIR = _find_data_dir()


def get_service(alias):
    token_path = os.path.join(CONFIG_DIR, 'accounts', f'{alias}.json')
    if not os.path.exists(token_path):
        error(f'Account "{alias}" not found.')

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        error('Run: pip install google-auth google-auth-oauthlib google-api-python-client --break-system-packages')

    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            error(f'Token refresh failed: {e}')

    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def error(msg):
    print(json.dumps({'error': msg}))
    sys.exit(1)


def check_service(alias):
    try:
        accounts = json.load(open(os.path.join(CONFIG_DIR, 'accounts.json')))
        if 'gmail' not in accounts.get(alias, {}).get('services', []):
            error(f'Gmail not enabled for account "{alias}". Re-authenticate with gmail service.')
    except Exception:
        pass  # allow if accounts.json missing


def parse_headers(headers_list):
    return {h['name']: h['value'] for h in headers_list}


def extract_body(payload):
    """Recursively extract plain text body from Gmail message payload."""
    if payload.get('mimeType') == 'text/plain':
        data = payload.get('body', {}).get('data', '')
        return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace') if data else ''

    if payload.get('mimeType') == 'text/html':
        data = payload.get('body', {}).get('data', '')
        if data:
            html = base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
            # Strip basic HTML tags for readability
            import re
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        return ''

    for part in payload.get('parts', []):
        result = extract_body(part)
        if result:
            return result

    return ''


def cmd_search(svc, query, max_results=20):
    try:
        results = svc.users().messages().list(
            userId='me', q=query, maxResults=int(max_results)
        ).execute()
    except Exception as e:
        error(f'Search failed: {e}')

    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        try:
            detail = svc.users().messages().get(
                userId='me', id=msg['id'], format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            h = parse_headers(detail['payload']['headers'])
            emails.append({
                'id': msg['id'],
                'thread_id': detail.get('threadId'),
                'from': h.get('From', ''),
                'to': h.get('To', ''),
                'subject': h.get('Subject', '(no subject)'),
                'date': h.get('Date', ''),
                'snippet': detail.get('snippet', ''),
                'labels': detail.get('labelIds', []),
            })
        except Exception:
            continue
    print(json.dumps(emails, ensure_ascii=False, indent=2))


def cmd_read(svc, message_id):
    try:
        detail = svc.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
    except Exception as e:
        error(f'Could not read message: {e}')

    h = parse_headers(detail['payload']['headers'])
    body = extract_body(detail['payload'])

    print(json.dumps({
        'id': message_id,
        'thread_id': detail.get('threadId'),
        'from': h.get('From', ''),
        'to': h.get('To', ''),
        'cc': h.get('Cc', ''),
        'subject': h.get('Subject', '(no subject)'),
        'date': h.get('Date', ''),
        'labels': detail.get('labelIds', []),
        'body': body[:8000],  # cap for context size
        'snippet': detail.get('snippet', ''),
    }, ensure_ascii=False, indent=2))


def cmd_send(svc, to, subject, body, thread_id=None):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['To'] = to
    msg['Subject'] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    payload = {'raw': raw}
    if thread_id:
        payload['threadId'] = thread_id

    try:
        result = svc.users().messages().send(userId='me', body=payload).execute()
        print(json.dumps({'success': True, 'id': result['id'], 'thread_id': result.get('threadId')}))
    except Exception as e:
        error(f'Send failed: {e}')


def cmd_reply(svc, message_id, body):
    try:
        original = svc.users().messages().get(
            userId='me', id=message_id, format='metadata',
            metadataHeaders=['From', 'To', 'Subject', 'Message-ID', 'References']
        ).execute()
    except Exception as e:
        error(f'Could not fetch original message: {e}')

    h = parse_headers(original['payload']['headers'])
    thread_id = original.get('threadId')

    reply_to = h.get('Reply-To', h.get('From', ''))
    subject = h.get('Subject', '')
    if not subject.lower().startswith('re:'):
        subject = f'Re: {subject}'

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['To'] = reply_to
    msg['Subject'] = subject
    if h.get('Message-ID'):
        msg['In-Reply-To'] = h['Message-ID']
        msg['References'] = f"{h.get('References', '')} {h['Message-ID']}".strip()

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    try:
        result = svc.users().messages().send(
            userId='me', body={'raw': raw, 'threadId': thread_id}
        ).execute()
        print(json.dumps({'success': True, 'id': result['id'], 'thread_id': thread_id}))
    except Exception as e:
        error(f'Reply failed: {e}')


def cmd_forward(svc, message_id, to, note=''):
    try:
        original = svc.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
    except Exception as e:
        error(f'Could not fetch original message: {e}')

    h = parse_headers(original['payload']['headers'])
    original_body = extract_body(original['payload'])
    subject = h.get('Subject', '')
    if not subject.lower().startswith('fwd:'):
        subject = f'Fwd: {subject}'

    fwd_body = f"{note}\n\n---------- Forwarded message ----------\nFrom: {h.get('From','')}\nDate: {h.get('Date','')}\nSubject: {h.get('Subject','')}\n\n{original_body}"
    cmd_send(svc, to, subject, fwd_body)


def cmd_archive(svc, message_id):
    try:
        svc.users().messages().modify(
            userId='me', id=message_id,
            body={'removeLabelIds': ['INBOX']}
        ).execute()
        print(json.dumps({'success': True, 'action': 'archived', 'id': message_id}))
    except Exception as e:
        error(f'Archive failed: {e}')


def cmd_trash(svc, message_id):
    try:
        svc.users().messages().trash(userId='me', id=message_id).execute()
        print(json.dumps({'success': True, 'action': 'trashed', 'id': message_id}))
    except Exception as e:
        error(f'Trash failed: {e}')


def cmd_label(svc, message_id, label_name):
    # Get or create label
    try:
        labels_resp = svc.users().labels().list(userId='me').execute()
        labels = labels_resp.get('labels', [])
        label_id = next((l['id'] for l in labels if l['name'].lower() == label_name.lower()), None)

        if not label_id:
            new_label = svc.users().labels().create(
                userId='me', body={'name': label_name}
            ).execute()
            label_id = new_label['id']

        svc.users().messages().modify(
            userId='me', id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()
        print(json.dumps({'success': True, 'action': 'labeled', 'label': label_name, 'id': message_id}))
    except Exception as e:
        error(f'Label failed: {e}')


def cmd_mark_read(svc, message_id):
    try:
        svc.users().messages().modify(
            userId='me', id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(json.dumps({'success': True, 'action': 'marked_read', 'id': message_id}))
    except Exception as e:
        error(f'Mark read failed: {e}')


def cmd_labels(svc):
    try:
        result = svc.users().labels().list(userId='me').execute()
        labels = [{'id': l['id'], 'name': l['name']} for l in result.get('labels', [])]
        print(json.dumps(labels, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Labels fetch failed: {e}')


def cmd_profile(svc):
    try:
        profile = svc.users().getProfile(userId='me').execute()
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Profile fetch failed: {e}')


COMMANDS = {
    'search': (cmd_search, 2, 3),      # query, [max]
    'read': (cmd_read, 1, 1),           # message_id
    'send': (cmd_send, 3, 4),           # to, subject, body, [thread_id]
    'reply': (cmd_reply, 2, 2),         # message_id, body
    'forward': (cmd_forward, 2, 3),     # message_id, to, [note]
    'archive': (cmd_archive, 1, 1),     # message_id
    'trash': (cmd_trash, 1, 1),         # message_id
    'label': (cmd_label, 2, 2),         # message_id, label_name
    'mark_read': (cmd_mark_read, 1, 1), # message_id
    'labels': (cmd_labels, 0, 0),
    'profile': (cmd_profile, 0, 0),
}


def main():
    if len(sys.argv) < 3:
        print('Usage: gmail.py <alias> <command> [args...]')
        print(f'Commands: {", ".join(COMMANDS.keys())}')
        sys.exit(1)

    alias = sys.argv[1]
    cmd = sys.argv[2]
    args = sys.argv[3:]

    if cmd not in COMMANDS:
        error(f'Unknown command "{cmd}". Available: {", ".join(COMMANDS.keys())}')

    check_service(alias)
    svc = get_service(alias)
    fn, min_args, max_args = COMMANDS[cmd]

    if len(args) < min_args or len(args) > max_args:
        error(f'Command "{cmd}" requires {min_args}–{max_args} arguments, got {len(args)}')

    fn(svc, *args)


if __name__ == '__main__':
    main()
