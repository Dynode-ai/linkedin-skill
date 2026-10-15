# Workflow: start (setup and dashboard)

Goal: in about five minutes, learn enough about the user to make every other command personal, save it to `linkedin/`, and show them a plan. This is the user's first impression of the skill. Make it fast, warm and visibly useful. Don't make it an interrogation.

## If `linkedin/brief.md` already exists: show the dashboard

Read the workspace and reply with a compact status:

```
Your LinkedIn workspace
- Goal: {goal} · Audience: {audience}
- Profile: audited {date}, score {N}/100   (or "not audited yet")
- Ideas in backlog: {N} unused · Drafts: {N} · Published: {N}
- People to engage: {N} (verified {date})
- Last analytics: {date or "none yet"}
```

Then suggest the single most valuable next command, based on what's missing or stale (audit older than 90 days, no ideas left, no analytics yet...). Ask whether anything has changed (new job, new goal, new offer) and update the brief if so. Stop here.

## Otherwise: run setup

### Step 1: Welcome (keep it to 3-4 lines)
Say what you'll do: learn their goal, audience and voice, save a private brief in `./linkedin/` on their computer, and give them a plan. Then ask for their profile in the same message.

Ask for the profile in whichever form is easiest for them (exact steps in `SKILL_DIR/references/data-sources.md`):
- **Best:** profile PDF (on their profile: "Resources" or "More" → "Save to PDF"), plus a screenshot of the top of the profile so you can see the photo and banner.
- **Also fine:** paste the headline, About and current role.
- **Optional, unlocks the most:** their LinkedIn data archive or analytics export (see `analyze` workflow). Don't block setup on this, since the archive can take a while to arrive.

If they've already given a profile in the request, skip asking for it.

### Step 2: Read the profile and infer
From the profile, infer a first guess at: role, seniority, industry, likely goal, likely audience, topics they could be known for, and proof points (numbers, logos, titles). You'll use these guesses to offer smart options instead of open-ended questions.

### Step 3: Ask the essential questions in one round
Use AskUserQuestion if available (up to 4 questions, clickable options plus "Other"). Otherwise ask the same as a short numbered list in one message.

1. **Main goal for LinkedIn in the next 90 days?** Options: Get hired · Win clients · Grow my startup / pipeline · Build an audience. (Other covers career growth, hiring, etc.)
2. **Who most needs to notice you?** Offer 2-3 audience options inferred from the profile (e.g. "Hiring managers at AI startups", "Heads of Data at mid-size companies") plus Other.
3. **How much time can you give LinkedIn per week?** Options: ~30 min (profile + commenting) · 1-2 hrs (1-2 posts) · 3-5 hrs (3+ posts) · More.
4. **Which formats are you up for?** (multi-select) Text posts · Images/carousels · Short video · Newsletter.

Then, in one free-text follow-up message, ask for what options can't capture. Make all of it optional:
- 1-3 results they're proud of, with numbers if possible;
- anything off-limits (employer confidentiality, personal topics);
- 3+ samples of their writing (past posts, emails, or just "tell me about a recent work win as if talking to a friend"). This seeds the voice profile.

If they skip things, continue. You can always ask later. Record skipped items under "Open questions" in the brief.

### Step 4: Write the workspace
Create `linkedin/` and write:
- `brief.md` from `SKILL_DIR/assets/templates/brief.md`. Fill what you know, and mark inferences as "(inferred, confirm)". Draft the positioning one-liner and 3-4 content pillars from what you've learned.
- `profile.md`: the profile text as received, with the date and source ("PDF export 2026-10-15").
- `voice.md` from the template, if you have samples. Follow the voice-building steps in `SKILL_DIR/references/writing-rules.md`.
- `stories.md` from the template, seeded with any results and stories they shared.

### Step 5: Show their game plan
Reply with a short, personal plan. This is the "wow" moment, so make it specific to them:

1. **Your positioning (draft):** the one-liner, and the 2-4 topics they should be known for.
2. **3 quick wins from a first look at your profile:** the three highest-impact fixes you noticed (e.g. "Your headline is your job title; recruiters searching 'ML Engineer' won't find you"). Not a full audit, just the obvious ones.
3. **Your content pillars (draft):** 3-4 pillars, one line each.
4. **Your first 30 days:**
   - Week 1: `/linkedin:audit` and fix the profile (it's the landing page for everything else).
   - Week 1: `/linkedin:follow` to build the list of people to engage with; start 15 minutes of daily commenting.
   - Weeks 2-4: `/linkedin:ideas`, then `/linkedin:write`, at the cadence their time allows.
   - Day 30: `/linkedin:analyze` with their analytics export to see what's working.

End with: "Saved to `linkedin/`. Next: `/linkedin:audit`."
