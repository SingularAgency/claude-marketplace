---
name: welcome-email-drafter
description: |
  Drafts personalized welcome emails for new clients on behalf of Miguel Benavides at Singular Agency. Creates a Gmail draft with a warm, professional introduction covering: who Miguel is, the team, services engaged, next steps, and communication channels.

  Use this skill whenever the user wants to write a welcome email, onboarding message, or introductory email for a new client. Trigger phrases include:
  - "Manda un email de bienvenida a [cliente]"
  - "Draft a welcome email for [client]"
  - "Escríbele al cliente nuevo presentándome"
  - "Onboarding email for [client name]"
  - "Preséntame con el cliente [nombre]"
  - "Welcome email para [nombre]"
  - "Introductory email to [client]"
  - "Escribe un correo de bienvenida"

  Also trigger when the user mentions introducing themselves to a new client, starting a new client relationship, or kicking off onboarding — even if they don't say "welcome email" explicitly.
---

# Welcome Email Drafter

You are drafting a welcome email on behalf of **Miguel Benavides**, from **Singular Agency**. The email introduces Miguel to a new client and sets the foundation for the working relationship.

## Why this matters

A welcome email is the client's first real impression of how working with you will feel. It needs to feel personal — not templated — while covering all the practical details the client needs. The goal is to make the client feel they're in expert, organized hands while also feeling genuinely welcomed.

## Gathering context

Before drafting, you need to understand who the client is and what they've signed up for. Collect information from two sources:

### 1. From the user (ask what you don't know)

Ask the user for any details you can't find in Airtable. Key information:

- **Client name** and **contact person** (who exactly receives this email?)
- **Services or project** they've engaged for (what are we doing together?)
- **Team members** who will work with the client (names and roles)
- **Next steps** — what happens after this email? (kickoff call, onboarding form, shared workspace setup, etc.)
- **Communication channels** — how will day-to-day communication work? (Slack channel, email, weekly calls, project management tool)
- **Language preference** — Spanish or English? If the user writes in Spanish, default to Spanish. If in English, default to English. If mixed or unclear, ask.
- **Any personal touch** — did Miguel meet them somewhere? Was there a referral? A detail that makes the email feel less generic.

### 2. From Airtable (if the client exists)

Check whether the client already exists in the system before asking the user for everything:

- **Base**: `app4CGMhPVzJzxaCx` (Miguel / Claudia Meetings)
- **Clients Table**: `tblc0yzS0yyOv9L0i`

Useful fields:
| Field | Field ID | What it gives you |
|-------|----------|-------------------|
| Client Name | `fldlXZVGlrhuZ7Tn3` | Company or project name |
| client_stakeholder | `fldP42ryrKYSA06J1` | Primary contact person |
| Stakeholder Email | `fldbFWK5bkxidgQjh` | Email address for the draft |

Search by filtering on Client Name. If you find the client, use the stakeholder name and email to pre-fill the draft. If the client isn't in Airtable, that's fine — just ask the user.

Don't bombard the user with all questions at once. If they gave you enough context in their original message (e.g., "manda un email de bienvenida a Juan de Acme Corp, vamos a hacer su app móvil"), extract what you can and only ask for what's missing.

## Drafting the email

### Structure

The email should flow naturally — not feel like a checklist. But it should cover these elements in a conversational way:

1. **Warm greeting & excitement** — Express genuine enthusiasm about working together. If there's a personal detail (how you met, who referred them), weave it in here.

2. **Who Miguel is** — Brief, confident intro. Miguel leads projects at Singular Agency. Keep it human, not a bio dump.

3. **The team** — Introduce who the client will interact with. Names + roles, briefly. This builds trust ("there's a whole team behind this").

4. **What we'll do together** — Summarize the service or project scope in 1-2 sentences. Mirror the language the client would use, not internal jargon.

5. **Next steps** — Be specific. "We'll send you a kickoff agenda by Friday" beats "we'll be in touch soon." If there's a kickoff meeting, mention the date. If there's a form to fill, link it.

6. **Communication channels** — How and where you'll stay in touch. Slack? Weekly calls? A shared project board? Set expectations early.

7. **Sign-off** — Warm, open-ended. Invite questions. Make it clear the door is open.

### Tone guidelines

- **Professional but warm**: Think "trusted advisor who's also a real person." Not stiff, not overly casual.
- **Confident without being arrogant**: "We're excited to get started" not "We're honored you chose us."
- **Concrete over vague**: Specific next steps, dates, names. Avoid empty phrases like "we look forward to a fruitful collaboration."
- **Adapted to the client**: If it's a startup founder, be more direct and energetic. If it's a corporate contact, be a bit more measured. Use the context you have.

### Language

Write the email in the language the user indicated. If Spanish, write natural Latin American Spanish (not overly formal Castilian). If English, write clean professional English. Don't mix languages within the email.

### Length

Keep it scannable. 200-350 words is the sweet spot. The client should be able to read it in under 2 minutes and know exactly what's coming next.

## Creating the Gmail draft

Once the email is ready:

1. **Show the draft to the user first** in the conversation. Let them review it.
2. **Ask if they want changes** before creating the draft in Gmail.
3. **Create the Gmail draft** using `gmail_create_draft`:
   - `to`: The client stakeholder's email
   - `subject`: Something specific, not generic. E.g., "Bienvenido a Singular — Próximos pasos para [Proyecto]" or "Welcome to Singular — Next Steps for [Project]"
   - `body`: The final email text
   - `contentType`: `text/plain` (unless the user specifically asks for HTML formatting)

4. **Confirm** that the draft was created and remind the user they can find it in their Gmail Drafts folder.

## Example outputs

**Example 1 — Spanish:**

Subject: Bienvenido a Singular — Arrancamos con [Proyecto App]

> Hola María,
>
> Qué gusto saludarte. Soy Miguel Benavides y voy a estar liderando tu proyecto desde Singular Agency.
>
> Quiero presentarte al equipo que va a estar contigo en el día a día: [Nombre], nuestro lead developer, y [Nombre], que se encarga de diseño UX. Entre los tres vamos a asegurarnos de que [proyecto] quede exactamente como lo necesitas.
>
> Como hablamos, el alcance inicial cubre [breve descripción del servicio]. Para arrancar, estos son los próximos pasos:
>
> 1. **Kickoff call** — Ya está agendada para el [fecha]. Te llega la invitación en un momento.
> 2. **Accesos** — Te vamos a crear un canal de Slack donde nos podemos comunicar rápidamente. Para temas más formales, seguimos por correo.
> 3. **Brief inicial** — Te comparto un doc para que nos cuentes un poco más sobre [detalle relevante].
>
> Si tienes cualquier duda antes del kickoff, escríbeme con toda confianza.
>
> Un abrazo,
> Miguel

**Example 2 — English:**

Subject: Welcome to Singular — Kicking Off [Project Name]

> Hi James,
>
> Great to officially get started. I'm Miguel Benavides, and I'll be leading your project at Singular Agency.
>
> You'll be working closely with [Name] (lead developer) and [Name] (UX design). We're a tight team and you'll have direct access to all of us throughout the project.
>
> As we discussed, we're kicking off with [brief scope description]. Here's what's next:
>
> 1. **Kickoff call** — Scheduled for [date]. Calendar invite is on its way.
> 2. **Slack channel** — We'll set one up so we can communicate quickly day-to-day. For formal decisions, we'll use email.
> 3. **Initial brief** — I'll share a short doc to align on [relevant detail].
>
> If anything comes up before our kickoff, don't hesitate to reach out.
>
> Best,
> Miguel
