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
  version: "0.6.0"
---

## IMPORTANT: Use Desktop Commander for ALL commands

ALL commands MUST run via Desktop Commander (`mcp__Desktop_Commander__start_process` with `shell: "bash"`). Do NOT use the VM Bash tool. The config and scripts live in the WSL2 environment.

## Step 1 — Verify config (via Desktop Commander)

```bash
python3 -c "import json,os; print(json.load(open(os.path.expanduser('~/.multi-google/config.json')))['scripts_dir'])"
```

If this fails → tell user: "Di 'configurar multi-google' primero."

If no account specified, list accounts:
```bash
python3 ~/.multi-google/scripts/list_accounts.py
```

## Commands (all via Desktop Commander)

### Recent files
```bash
python3 ~/.multi-google/scripts/drive.py <alias> recent [days] [max]
```

### Search files
```bash
python3 ~/.multi-google/scripts/drive.py <alias> search "<query>" [max]
```

### Get file metadata
```bash
python3 ~/.multi-google/scripts/drive.py <alias> get <file_id>
```

### Read file content (Docs/Sheets/Slides)
```bash
python3 ~/.multi-google/scripts/drive.py <alias> read <file_id>
```

### Share file
```bash
python3 ~/.multi-google/scripts/drive.py <alias> share <file_id> <email> [role]
```
Role: `reader` (default), `writer`, `commenter`

### Unshare
```bash
python3 ~/.multi-google/scripts/drive.py <alias> unshare <file_id> <email>
```

### Move file
```bash
python3 ~/.multi-google/scripts/drive.py <alias> move <file_id> <folder_id>
```

### Create folder
```bash
python3 ~/.multi-google/scripts/drive.py <alias> create_folder "<name>" [parent_folder_id]
```

### Upload file
```bash
python3 ~/.multi-google/scripts/drive.py <alias> upload <local_path> [parent_folder_id]
```

### List folder
```bash
python3 ~/.multi-google/scripts/drive.py <alias> list_folder [folder_id]
```

## Guidelines
- Search before acting on files (need file IDs)
- Confirm before share/unshare/delete operations
