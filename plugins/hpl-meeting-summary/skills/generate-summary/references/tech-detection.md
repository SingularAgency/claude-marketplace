# Technology Type Detection

Use this logic to identify the project type from meeting content, then look up the accountable team member from `role_assignments` in the config.

---

## Detection Algorithm

Search the following meeting fields (in priority order) for technology keywords:

1. `title` — highest signal, usually names the tool or project
2. `topics[]` — explicit themes discussed
3. `summary` — full prose, use for context
4. `chapter_summaries[].title` and `chapter_summaries[].description`

Match against the `keywords` array for each role in `role_assignments` from the config. The match is case-insensitive.

**If multiple categories match**: pick the one with the most keyword hits. If tied, prefer the order: airtable → flutterflow → ai_custom → fullstack → custom categories.

**If no category matches**: do not tag any specific accountable. Fall back to `mention_users` from config (global tags), or tag no one.

---

## Default Keyword Reference

These are the baseline keywords per category. The config may extend them with custom categories.

### Airtable
`airtable`, `airtable base`, `airtable automation`, `airtable integration`, `no-code database`, `airtable view`, `airtable form`

### FlutterFlow
`flutterflow`, `flutter flow`, `flutter`, `mobile app`, `flutter app`, `flutterflow build`, `flutter screen`, `flutter widget`

### AI Custom Integration
`claude`, `openai`, `gpt`, `gpt-4`, `llm`, `ai agent`, `ai automation`, `custom ai`, `ai integration`, `langchain`, `cowork`, `anthropic`, `chatgpt`, `make.com ai`, `zapier ai`, `n8n`, `ai workflow`, `copilot`, `ai model`, `prompt`, `rag`, `vector`

### FullStack
`react`, `node`, `nodejs`, `next.js`, `nextjs`, `backend`, `frontend`, `web app`, `rest api`, `graphql`, `fullstack`, `full-stack`, `full stack`, `typescript`, `javascript`, `python`, `django`, `rails`, `laravel`, `database`, `postgres`, `mysql`, `supabase`, `firebase`

---

## Tagging Rules

Once the technology type is identified:

1. Look up `role_assignments[<tech_type>].user_ids` from config
2. Format each as `<@USER_ID>` for Slack mention
3. Place the mention(s) **in the thread reply** (summary body), not the headline

**Position in thread**: Add the tags at the very top of the thread message, before the summary body:

```
<@U123> <@U456>

📋 *Call Breakdown — ClientName*

[rest of summary...]
```

If no match found, omit the tag line entirely.

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Meeting mentions both Airtable and FlutterFlow | Tag both accountables |
| No tech keywords found | No accountable tag, only global `mention_users` if set |
| Category assigned to multiple people | Tag all of them |
| New category added via configure skill | Detect using its custom keywords |
| User explicitly says "tag William" in their message | Override detection and use that person |
