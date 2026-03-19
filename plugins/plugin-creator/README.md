# Plugin Creator

Guides Singular Agency team members through building a new Claude plugin and submitting it to the team marketplace. Works on macOS, Linux and Windows — no Docker or special tools required.

## Install

```shell
/plugin install plugin-creator@singular-agency-marketplace
```

## How it works

Just say **"create a plugin"** or **"I want to add a plugin to the marketplace"** and Claude will:

1. Ask what the plugin should do
2. Generate all the required files (manifest, skill, README)
3. Ask for your GitHub token at the end
4. Create a branch, push the files, update `marketplace.json`, and open a PR automatically using Python3

A reviewer approves the PR, and once merged the plugin is live for the whole team.

## Requirements

- A GitHub Personal Access Token with `repo` scope (only needed at submission time)
- Python3 (pre-installed on macOS, Linux and Windows)

## Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| /create-plugin | "create a plugin", "new plugin", "add a plugin to the marketplace", "contribute a plugin" | Full guided plugin creation + PR submission |
