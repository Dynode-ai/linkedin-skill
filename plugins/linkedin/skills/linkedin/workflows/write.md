# Workflow: write (posts, carousels, comments)

Goal: publish-ready writing that sounds like the user on a good day, says something specific, and passes the checker. Not "AI content".

Read first: `SKILL_DIR/references/writing-rules.md` (every time), and `SKILL_DIR/references/content-playbook.md` §4-6 for hooks, structures and formats.

## Pick the mode from the request

| Request looks like | Mode |
|---|---|
| A topic, an idea number ("write 12"), or "write a post about..." | **Post** |
| A pasted draft + "fix / improve / review / feedback" | **Fix** |
| "carousel", "document post", "slides" | **Carousel** |
| Someone else's post + "comment / reply" | **Comment** |
| "interview me", "help me find something to post", or no topic at all | **Interview** |
| A long piece (article, transcript, talk, blog) + "turn into posts" | **Repurpose** |
| "hooks for..." | **Hooks only**: step 3 of Post mode, 8-10 options across hook types |

Always load `linkedin/brief.md`, `voice.md`, `stories.md`, `learnings.md` first, plus `ideas.md` if an idea number is given.

---

## Post mode

**1. Get real material.** A post is only as good as its raw material. Check whether you have the specifics: what happened, numbers, names (if shareable), the moment, the lesson. If the topic or idea lacks them and `stories.md` doesn't cover it, ask 2-4 targeted questions in one message ("What was the before/after number?", "What did you try first that didn't work?", "What exactly did the client say?"). This is the single biggest quality lever, so don't skip it to save a turn. If the user says "just write it", draft with `[PLACEHOLDERS]` instead of inventing.

**2. Choose the structure** (`content-playbook.md` §5) that fits the material, and the format (text by default; suggest a carousel or image if the content is a framework, checklist or data).

**3. Write 3-5 hooks** of different types (story, result, contrarian, observation, specific question). Prefer short first lines. Pick the strongest for the draft, and keep the rest as alternatives.

**4. Draft in their voice.** Follow `voice.md` over generic advice. One idea. Pay off the hook early. Specific details from their material. Cut 20% on the second pass.

If the draft deliberately departs from their measured habits, say so in one line and let them choose. For example: "Your posts are usually ~300-600 characters. This one is 1,300 because longer text posts tend to perform better (see `algorithm.md` §5). Want a short version?"

**5. Save** to `linkedin/posts/YYYY-MM-DD-slug.md`:
```markdown
---
status: draft
idea: 12
pillar: Startup finance mistakes
format: text
hook_type: contrarian
created: 2026-10-15
---
<the post text exactly as it should be pasted>
```

**6. Check and fix.** Run `python3 "SKILL_DIR/scripts/check.py" post "<file>"`. Fix every ERROR and WARN unless it's deliberate (say why), then re-run. Target 85+. Don't game the checker with odd wording; if a rule doesn't fit this post, explain instead. Also check the voice. If `linkedin/data/posts.json` exists, run `python3 "SKILL_DIR/scripts/linkedin_data.py" voice linkedin/data --draft "<file>"` to compare the draft with the user's measured style. Otherwise compare by eye against `voice.md`.

**7. Preview.** Create or update `linkedin/posts/preview/`: copy `SKILL_DIR/assets/preview/index.html` there (once), and write `data.js`:
```js
window.POSTS = {
  "author": { "name": "Priya Raman", "headline": "Fractional CFO for seed-to-Series A SaaS" },
  "drafts": [
    { "label": "Draft · contrarian hook", "text": "full post text" },
    { "label": "Alt hook · story", "text": "same post with the alternative first lines" }
  ]
};
```
The page shows each draft as it appears in the feed on mobile and desktop, cut at "...see more", with a live character count. The user can edit text there and copy it.

**8. Present** (compact):
- The post in a fenced code block (keeps line breaks when copied).
- 2-3 alternative hooks.
- Checker score and anything deliberately left as-is.
- Open `[PLACEHOLDERS]` as direct questions.
- If relevant: suggested visual (what image or screenshot would strengthen it), a note on links (`algorithm.md` §6), and one posting tip (e.g. be around to reply to comments in the first hour or two).
- Preview path: `linkedin/posts/preview/index.html`.

**9. Update the workspace:** idea status → `drafted` in `ideas.md`; story status in `stories.md`. When the user says they posted it, set `status: posted` with the date. Later analytics can be matched to it.

---

## Fix mode

The user wrote something and wants it better. Respect their voice; this is editing, not ghostwriting.
1. Run the checker on their draft and read it as their target reader would.
2. Give a short, prioritized critique: hook strength, specificity, structure and payoff, ending, AI tells. 3-6 points, most important first.
3. Provide a revised version that keeps their words wherever they work. Change what needs changing, not everything.
4. Summarize the changes in 2-4 bullets, re-run the checker, and show before → after scores.

## Carousel mode

1. Confirm the core takeaway and get real material (as in Post mode).
2. Outline 6-12 slides: slide 1 = hook (big promise, ≤ 8 words), one idea per slide (≤ 30 words), concrete examples, and a final slide with a summary or CTA (follow, comment with a specific question, newsletter).
3. Create `linkedin/posts/YYYY-MM-DD-slug-carousel/`, copy `SKILL_DIR/assets/carousel/index.html` into it, and write `data.js`:
```js
window.CAROUSEL = {
  "title": "5 SaaS metrics investors check first",
  "author": { "name": "Priya Raman", "headline": "Fractional CFO for SaaS" },
  "theme": { "bg": "#0f172a", "fg": "#f8fafc", "accent": "#38bdf8", "muted": "#94a3b8" },
  "slides": [
    { "type": "cover", "kicker": "Fundraising", "title": "5 metrics investors check before your pitch", "subtitle": "From 30+ diligence calls" },
    { "type": "point", "number": "01", "title": "Net revenue retention", "body": "..." },
    { "type": "list", "title": "Red flags", "items": ["...", "..."] },
    { "type": "stat", "value": "120%", "label": "NRR that gets a second meeting" },
    { "type": "quote", "quote": "...", "attribution": "..." },
    { "type": "cta", "title": "Save this for your next raise", "body": "I post about startup finance every week." }
  ]
};
```
Pick theme colors that fit the user's brand if known (high contrast, accessible). Slide types: `cover`, `point`, `list`, `stat`, `quote`, `cta`.
4. Write the caption post (800-1,000 characters, its own hook), save it alongside, and run the checker on it.
5. Tell the user: open `index.html` → click "Save as PDF" (or Ctrl/Cmd+P → Save as PDF, margins none, background graphics on) → upload the PDF as a **document** post on LinkedIn and give it a title.

## Comment mode

The user pastes someone else's post (and maybe their relationship or goal).
1. Read the post and identify what the user can genuinely add given their expertise (brief, stories).
2. Write 3 options of different kinds: (a) add a specific example or data point from their experience, (b) a respectful counterpoint or nuance, (c) a sharp follow-up question. 2-5 sentences each, in their voice. No pitching, no flattery openers, no "Great post!".
3. If the user wants to reply to comments on their own post, keep replies short, warm and specific, and continue the conversation with a question when natural.

## Interview mode

Turn a conversation into posts. This produces the most authentic content because the material comes straight from the user.
1. Ask questions one or two at a time, conversationally, following the energy. Start broad ("What's been the most interesting problem at work this month?"), then dig for specifics: the moment, what was at stake, what they tried, numbers, what they'd tell someone facing the same thing, what they disagree with.
2. Stop after ~5-8 exchanges or when you have 2+ strong stories.
3. Save each story to `stories.md` (only what they said).
4. Propose 3-5 post angles from the interview. Draft the one they pick (Post mode steps 2-9).
5. Their phrasing in the interview is a voice sample. Update `voice.md` if you learned something new about how they talk.

## Repurpose mode

1. Read the source (file, URL via WebFetch, or pasted).
2. Extract 5-10 post angles (`content-playbook.md` §9), each with a hook and the part of the source it uses.
3. Add them to `ideas.md`, and draft the strongest one (Post mode).
