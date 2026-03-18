---
description: Summarizes the user's Gmail inbox from the past 7 days, filtering out automated, promotional, and notification emails to surface only real human conversations. Triggered by phrases like "recap my emails", "summarize my inbox", "what emails did I get this week", "email digest", "catch me up on my emails", "what did I miss in my inbox".
---

Generate a weekly email digest for the user by fetching and filtering their Gmail inbox from the last 7 days.

## Step 1 — Fetch emails

Use the Gmail MCP to search for emails received in the past 7 days. Use the search query:

```
after:<date_7_days_ago> -category:promotions -category:social -category:updates -category:forums
```

Where `<date_7_days_ago>` is today's date minus 7 days in `YYYY/MM/DD` format.

Fetch up to 50 messages. For each message, retrieve: subject, sender name and address, date, and a brief snippet or body preview.

## Step 2 — Filter out noise

Discard any email where ANY of the following signals are true:

- Sender domain is a known service/platform (e.g. noreply@*, no-reply@*, notifications@*, alerts@*, support@*, hello@*, team@* from SaaS tools)
- Subject contains words like: "notification", "alert", "invoice", "receipt", "order", "confirm", "verify", "unsubscribe", "newsletter", "digest", "weekly update", "your account", "password", "sign in", "OTP", "code", "2FA", "reminder", "you have a new", "new message from"
- The email was sent by an automated system (check for List-Unsubscribe headers, bulk send indicators, or generic sender names like "The [App] Team", "[App] Notifications", "[App] Support")
- The sender's email address contains: noreply, no-reply, donotreply, do-not-reply, automated, newsletter, notifications, alerts, mailer, postmaster

Keep only emails that appear to be sent by a real human directly to the user — genuine conversations, replies, direct messages, or personal outreach.

## Step 3 — Group and summarize

Organize the filtered emails into logical groups. Use these categories as a guide (adapt as needed based on what's actually present):

- **Action Required** — emails where someone is waiting for a reply, a decision, or a task from the user
- **Conversations** — ongoing exchanges or replies that don't require immediate action
- **FYI / Shared with you** — informational emails from real people (e.g. someone forwarding something, sharing a doc, looping you in)

For each email in the digest, include:
- Sender name
- Subject line
- One-sentence summary of what the email is about
- If action is needed, note it with ⚡

## Step 4 — Deliver the digest

Present the digest inline in this format:

---

## 📬 Email Recap — Last 7 Days
*<N> emails from real people • <M> require your attention*

### ⚡ Action Required
[list emails needing response or decision]

### 💬 Conversations
[list ongoing threads]

### 👀 FYI / Shared with you
[list informational emails from real people]

---

If no real human emails were found, say so clearly and reassure the user their inbox is quiet.

Keep summaries tight — one sentence per email. Do not include full email body text. If the user wants to read a specific email, they can ask and you can fetch it.
