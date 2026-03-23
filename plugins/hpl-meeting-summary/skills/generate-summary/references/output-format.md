# Meeting Summary Output Format

Use this as the template for all generated Slack posts. Adapt sections based on meeting type (sales call, internal sync, one-on-one). See guidelines below.

---

## Full Format — Sales / Client Call

```
📋 *Call Breakdown — [Client Name or Meeting Title]*

[One paragraph: who the client/contact is, what they're building or what their business does, what they need from the team, and any important constraints or context. Be specific. Avoid vague language like "we discussed X" — instead say what was decided, confirmed, or needed.]

*Core Direction:*
• [Key topic or product direction 1]
• [Key topic or product direction 2]
• [Key topic or product direction 3]

*What Was Discussed:*
• [Chapter/section title]: [1-sentence description]
• [Chapter/section title]: [1-sentence description]
• [Chapter/section title]: [1-sentence description]

🔴 *Action Items*
• [Assignee first name]: [what they need to do]
• [Assignee first name]: [what they need to do]
• [Assignee first name]: [what they need to do]

🔴 *Next Steps / Timeline*
• [Date or deadline and what happens then]
• [Any follow-up meeting, deliverable, or milestone]

🔗 Full report: [report_url]
```

---

## Compact Format — Internal Sync

```
🗒 *Sync Recap — [Meeting Title]*

[One sentence: what the meeting was about and what was resolved.]

*Decisions:*
• [Decision 1]
• [Decision 2]

*Action Items:*
• [Assignee]: [task]
• [Assignee]: [task]

*Blockers / Pending:*
• [Anything still unresolved or waiting on someone]

🔗 Full report: [report_url]
```

---

## Minimal Format — One-on-One

```
📝 *[Meeting Title]*

*Decisions:*
• [Decision 1]

*Action Items:*
• [Assignee]: [task]
• [Assignee]: [task]

🔗 Full report: [report_url]
```

---

## Formatting Rules

- Use Slack markdown: `*bold*`, `_italic_`, bullet points with `•`
- Keep bullet points to one sentence each — no nested bullets
- If a section has no content (e.g., no key questions), omit it entirely
- Always include the `report_url` at the end
- Never use filler phrases like "the team discussed", "it was mentioned that", or "moving forward"
- Write action items with the assignee's first name first: "Tyler: share the recording with William"
- Timeline entries should be specific: "Wednesday 12 PM PST — MAP due" not "follow up later"

---

## Meeting Type Detection

Determine the format to use based on:

| Signal | Format |
|--------|--------|
| External participant (different email domain) | Full (Sales/Client Call) |
| All participants from same company, >3 people | Compact (Internal Sync) |
| Only 2 participants, same company | Minimal (One-on-One) |
| Folder labeled "Sales Strategy" or "Client" | Full (Sales/Client Call) |
| No folder, internal only | Compact (Internal Sync) |

When in doubt, use the Full format.
