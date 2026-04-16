#!/usr/bin/env python3
# Auto-add user local site-packages so Google packages are found in any env
import sys as _sys, os as _os, glob as _glob
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

"""
Unified Google Drive API script.

Usage:
  python3 drive.py <alias> recent [days=7] [max=20]
  python3 drive.py <alias> search <query> [max=20]
  python3 drive.py <alias> read <file_id>
  python3 drive.py <alias> get <file_id>
  python3 drive.py <alias> share <file_id> <email> [role=reader]
  python3 drive.py <alias> unshare <file_id> <email>
  python3 drive.py <alias> move <file_id> <folder_id>
  python3 drive.py <alias> create_folder <name> [parent_folder_id]
  python3 drive.py <alias> upload <local_path> [parent_folder_id]
  python3 drive.py <alias> list_folder [folder_id=root]

All commands output JSON. 'read' outputs plain text for Docs/Sheets/text files.

Roles for share: reader, commenter, writer
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

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

MIME_LABELS = {
    'application/vnd.google-apps.document': 'Google Doc',
    'application/vnd.google-apps.spreadsheet': 'Google Sheet',
    'application/vnd.google-apps.presentation': 'Google Slides',
    'application/vnd.google-apps.folder': 'Folder',
    'application/vnd.google-apps.form': 'Google Form',
    'application/pdf': 'PDF',
    'text/plain': 'Text',
    'text/csv': 'CSV',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Doc',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
}

# Export MIME types for Google Workspace files
EXPORT_MIME = {
    'application/vnd.google-apps.document': 'text/plain',
    'application/vnd.google-apps.spreadsheet': 'text/csv',
    'application/vnd.google-apps.presentation': 'text/plain',
}


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
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def check_service(alias):
    try:
        accounts = json.load(open(os.path.join(CONFIG_DIR, 'accounts.json')))
        if 'drive' not in accounts.get(alias, {}).get('services', []):
            error(f'Drive not enabled for account "{alias}".')
    except Exception:
        pass


def format_file(f):
    mime = f.get('mimeType', '')
    modifier = f.get('lastModifyingUser', {})
    return {
        'id': f.get('id'),
        'name': f.get('name', '(untitled)'),
        'type': MIME_LABELS.get(mime, mime.split('.')[-1] if '.' in mime else mime),
        'mime_type': mime,
        'modified': f.get('modifiedTime', ''),
        'modified_by': modifier.get('displayName', modifier.get('emailAddress', 'Unknown')),
        'modified_by_me': modifier.get('me', False),
        'owners': [o.get('emailAddress') for o in f.get('owners', [])],
        'shared': f.get('shared', False),
        'link': f.get('webViewLink', ''),
        'parent': (f.get('parents') or [''])[0],
        'size': f.get('size', None),
    }


def cmd_recent(svc, days=7, max_results=20):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=int(days))).isoformat()
    try:
        result = svc.files().list(
            q=f"modifiedTime > '{cutoff}' and trashed = false",
            pageSize=int(max_results), orderBy='modifiedTime desc',
            fields='files(id,name,mimeType,modifiedTime,lastModifyingUser,webViewLink,owners,shared,size,parents)'
        ).execute()
        print(json.dumps([format_file(f) for f in result.get('files', [])], ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Recent files failed: {e}')


def cmd_search(svc, query, max_results=20):
    # If query looks like a raw Drive API expression (contains operators), use it directly.
    # Otherwise wrap in a name/fullText search.
    drive_operators = ('=', '!=', ' in ', 'contains', 'sharedWithMe', 'trashed',
                       'mimeType', 'modifiedTime', 'createdTime', 'starred', 'parents')
    is_raw_query = any(op in query for op in drive_operators)
    if is_raw_query:
        drive_query = query if 'trashed' in query else f"({query}) and trashed = false"
    else:
        safe = query.replace("'", "\\'")
        drive_query = f"(name contains '{safe}' or fullText contains '{safe}') and trashed = false"
    try:
        result = svc.files().list(
            q=drive_query, pageSize=int(max_results), orderBy='modifiedTime desc',
            fields='files(id,name,mimeType,modifiedTime,lastModifyingUser,webViewLink,owners,shared,size,parents)'
        ).execute()
        print(json.dumps([format_file(f) for f in result.get('files', [])], ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Search failed: {e}')


def cmd_get(svc, file_id):
    try:
        f = svc.files().get(
            fileId=file_id,
            fields='id,name,mimeType,modifiedTime,lastModifyingUser,webViewLink,owners,shared,size,parents,description'
        ).execute()
        result = format_file(f)
        result['description'] = f.get('description', '')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'Get failed: {e}')


def cmd_read(svc, file_id):
    """Export and return text content of a Drive file."""
    try:
        meta = svc.files().get(fileId=file_id, fields='name,mimeType').execute()
        mime = meta.get('mimeType', '')
        name = meta.get('name', '')

        if mime in EXPORT_MIME:
            content = svc.files().export(fileId=file_id, mimeType=EXPORT_MIME[mime]).execute()
            text = content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
            print(json.dumps({'id': file_id, 'name': name, 'type': MIME_LABELS.get(mime, mime), 'content': text[:10000]}, ensure_ascii=False, indent=2))
        elif mime.startswith('text/'):
            content = svc.files().get_media(fileId=file_id).execute()
            text = content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
            print(json.dumps({'id': file_id, 'name': name, 'type': 'Text', 'content': text[:10000]}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({'id': file_id, 'name': name, 'type': MIME_LABELS.get(mime, mime),
                              'error': 'Binary file — cannot read as text. Open via link instead.',
                              'link': f'https://drive.google.com/file/d/{file_id}/view'}))
    except Exception as e:
        error(f'Read failed: {e}')


def cmd_share(svc, file_id, email, role='reader'):
    valid_roles = ['reader', 'commenter', 'writer']
    if role not in valid_roles:
        error(f'Role must be one of: {", ".join(valid_roles)}')
    try:
        perm = svc.permissions().create(
            fileId=file_id,
            body={'type': 'user', 'role': role, 'emailAddress': email},
            sendNotificationEmail=True
        ).execute()
        print(json.dumps({'success': True, 'shared_with': email, 'role': role, 'permission_id': perm['id']}))
    except Exception as e:
        error(f'Share failed: {e}')


def cmd_unshare(svc, file_id, email):
    try:
        perms = svc.permissions().list(fileId=file_id, fields='permissions(id,emailAddress)').execute()
        perm_id = next((p['id'] for p in perms.get('permissions', []) if p.get('emailAddress') == email), None)
        if not perm_id:
            error(f'No permission found for {email} on this file.')
        svc.permissions().delete(fileId=file_id, permissionId=perm_id).execute()
        print(json.dumps({'success': True, 'unshared_from': email}))
    except Exception as e:
        error(f'Unshare failed: {e}')


def cmd_move(svc, file_id, folder_id):
    try:
        # Get current parents
        f = svc.files().get(fileId=file_id, fields='parents').execute()
        prev_parents = ','.join(f.get('parents', []))
        svc.files().update(
            fileId=file_id,
            addParents=folder_id,
            removeParents=prev_parents,
            fields='id,parents'
        ).execute()
        print(json.dumps({'success': True, 'moved_to': folder_id}))
    except Exception as e:
        error(f'Move failed: {e}')


def cmd_create_folder(svc, name, parent_id=''):
    body = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        body['parents'] = [parent_id]
    try:
        folder = svc.files().create(body=body, fields='id,name,webViewLink').execute()
        print(json.dumps({'success': True, 'id': folder['id'], 'name': folder['name'], 'link': folder.get('webViewLink', '')}))
    except Exception as e:
        error(f'Create folder failed: {e}')


def cmd_upload(svc, local_path, parent_id=''):
    if not os.path.exists(local_path):
        error(f'File not found: {local_path}')
    try:
        from googleapiclient.http import MediaFileUpload
        import mimetypes
        mime, _ = mimetypes.guess_type(local_path)
        mime = mime or 'application/octet-stream'

        body = {'name': os.path.basename(local_path)}
        if parent_id:
            body['parents'] = [parent_id]

        media = MediaFileUpload(local_path, mimetype=mime, resumable=True)
        f = svc.files().create(body=body, media_body=media, fields='id,name,webViewLink').execute()
        print(json.dumps({'success': True, 'id': f['id'], 'name': f['name'], 'link': f.get('webViewLink', '')}))
    except Exception as e:
        error(f'Upload failed: {e}')


def cmd_list_folder(svc, folder_id='root'):
    try:
        result = svc.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=50, orderBy='name',
            fields='files(id,name,mimeType,modifiedTime,size,webViewLink)'
        ).execute()
        files = []
        for f in result.get('files', []):
            files.append({
                'id': f['id'], 'name': f['name'],
                'type': MIME_LABELS.get(f.get('mimeType', ''), f.get('mimeType', '')),
                'modified': f.get('modifiedTime', ''),
                'link': f.get('webViewLink', ''),
            })
        print(json.dumps(files, ensure_ascii=False, indent=2))
    except Exception as e:
        error(f'List folder failed: {e}')


COMMANDS = {
    'recent': (cmd_recent, 0, 2),
    'search': (cmd_search, 1, 2),
    'get': (cmd_get, 1, 1),
    'read': (cmd_read, 1, 1),
    'share': (cmd_share, 2, 3),
    'unshare': (cmd_unshare, 2, 2),
    'move': (cmd_move, 2, 2),
    'create_folder': (cmd_create_folder, 1, 2),
    'upload': (cmd_upload, 1, 2),
    'list_folder': (cmd_list_folder, 0, 1),
}


def main():
    if len(sys.argv) < 3:
        print('Usage: drive.py <alias> <command> [args...]')
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
