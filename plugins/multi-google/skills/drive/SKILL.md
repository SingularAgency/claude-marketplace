---
name: drive
description: >
  Use this skill for any Google Drive action: searching files, reading document content,
  viewing recent activity, sharing files, uploading, moving, creating folders, or listing
  folder contents. Triggered by phrases like: "find the [doc] in my drive",
  "buscar el archivo [nombre] en drive", "what changed in my drive",
  "read the content of [doc]", "share [file] with [person]", "upload [file] to drive",
  "create a folder called [name]", "show me what's in [folder]",
  "who has access to [file]", "move [file] to [folder]",
  "what files did [person] change this week", "find docs about [topic]",
  or any request to interact with Google Drive files.
metadata:
  version: "1.0.0"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 0 — Auto-bootstrap (run FIRST, every time)

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
PLUGIN_SCRIPTS=$(find /sessions/*/mnt/.remote-plugins/*/scripts -name "setup_oauth.py" 2>/dev/null | head -1 | xargs -I{} dirname {})

if [ ! -f "$MNT/.multi-google/scripts/auth.py" ]; then
  mkdir -p "$MNT/.multi-google/scripts" "$MNT/.multi-google/accounts"
  cp "$PLUGIN_SCRIPTS"/*.py "$MNT/.multi-google/scripts/"
fi

# Pre-install Google packages silently (handles pypi.org-blocked networks gracefully)
pip install -q google-auth google-api-python-client --break-system-packages 2>/dev/null || true

if [ ! -f "$MNT/.multi-google/oauth.json" ]; then
  python3 "$MNT/.multi-google/scripts/setup_oauth.py"
fi
```

If no accounts exist after bootstrap → tell user: "Primero agrega una cuenta. Di 'agregar cuenta de Google'."

## Step 1 — Verify accounts

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

If no account specified and multiple exist, ask which one to use. With a single account, use it automatically.

## Commands

### Recent files
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> recent [days] [max]
```

### Search files
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> search "<query>" [max]
```

### Get file metadata
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> get <file_id>
```

### Read file content (Docs/Sheets/Slides)
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> read <file_id>
```

### Share file
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> share <file_id> <email> [role]
```
Role: `reader` (default), `writer`, `commenter`

### Unshare
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> unshare <file_id> <email>
```

### Move file
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> move <file_id> <folder_id>
```

### Create folder
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> create_folder "<name>" [parent_folder_id]
```

### Upload file
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> upload <local_path> [parent_folder_id]
```

### List folder
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> list_folder [folder_id]
```

## Guidelines
- Search before acting on files (need file IDs)
- Confirm before share/unshare/delete operations
