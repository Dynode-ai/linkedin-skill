# Workflow: audit (profile score and rewrites)

Goal: tell the user exactly how strong their profile is for **their goal and audience**, and hand them finished, copy-paste rewrites, as a chat summary plus a visual HTML report they'll want to share.

Read first: `SKILL_DIR/references/profile-playbook.md` (specs, section guidance, formulas) and the user's goal section in `SKILL_DIR/references/goals.md`.

## Step 1: Gather inputs
- **Workspace:** `linkedin/brief.md` (goal, audience, keywords, proof), `linkedin/profile.md`, `linkedin/voice.md`, `linkedin/learnings.md` if present.
- **Profile content:** use what the user provided now. Otherwise use `profile.md` if it's under ~30 days old and the user hasn't said it changed. Otherwise ask for a PDF, screenshots or pasted text (instructions in `references/data-sources.md`). A data archive's `Profile.csv`, `Positions.csv` and `Skills.csv` also work.
- **Screenshots** of the top card (photo, banner, headline) are needed to score Photo & banner. Without them, mark that category n/a.
- **Goal and audience:** from the brief. If there's no brief, infer from the profile and confirm in one short question (AskUserQuestion if available) before scoring, because the score depends on it.
- **Target job descriptions** (job seekers): if the user shares 1-5 JDs, use them for keywords. Encourage this for job seekers; it makes the audit far more precise.
- **Recent activity:** posts from the archive, analytics, `posts/`, or an activity screenshot, if available. This feeds the alignment check.

## Step 2: Build the keyword set
List 8-15 terms the target audience types into LinkedIn search, or expects to see.
- **Job seekers:** extract titles, hard skills, tools and domain terms from the JDs, and count how many JDs mention each. Without JDs, run 2-3 WebSearches for current postings for the target title and extract from those (cite them).
- **Everyone else:** the names of what they do or sell, the problems their audience has, the titles of their buyers, and industry terms (from the brief and `niche` report if present).

Then mark where each keyword appears today: Headline, About, Experience, Skills. This becomes the keyword heatmap.

## Step 3: Score with the rubric
Score each category strictly against the criteria below. Be consistent: two people with equally strong profiles should get the same score. When you can't see a category (no screenshot, no activity data), mark it `n/a`, exclude it, and rescale: `total = round(100 × points earned ÷ points possible among scored categories)`. Say what wasn't scored and how to include it.

This is the skill's own rubric, not a LinkedIn metric. Say so if the user asks.

| Category | Max | Criteria (points) |
|---|---|---|
| **Headline** | 15 | A stranger gets what they do and for whom in 3 seconds (4) · Contains the keywords the audience/recruiters search, in plain words (4) · Differentiator or proof: niche, result, credential (3) · Front-loaded: the key words appear in the first ~70 characters, which is what shows in comments and search snippets (2) · Uses the space well with no clutter (emoji soup, fancy fonts, buzzword strings) (2) |
| **About** | 15 | The first ~265 characters (before "see more") hook the target reader (4) · What they do and who they help is unmistakable (3) · Proof: numbers, results, names (3) · Personality or point of view (2) · Keywords appear naturally (1) · Clear call to action or contact path (1) · Readable: short paragraphs, sensible length (1) |
| **Experience** | 15 | Current role shows outcomes and scope, not just duties (5) · Quantified achievements across recent roles (4) · Standard, searchable titles (2) · Keywords and skills attached to roles (2) · Complete: no empty recent roles, unexplained gaps, or missing descriptions (2) |
| **Photo & banner** | 10 | Photo: face fills most of the frame, good light, current, approachable, appropriate for the field (5) · Banner: custom, reinforces positioning (what they do, proof or CTA), readable on mobile with nothing important hidden behind the photo (5) |
| **Featured** | 8 | Present with 2-4 items (2) · Items serve the goal: portfolio, case study, lead magnet, best post, booking link (4) · Clear titles and descriptions (2) |
| **Skills** | 7 | Top (pinned) skills match the target keywords (4) · 15+ relevant skills, no outdated or irrelevant clutter (3) |
| **Social proof** | 8 | 3+ relevant recommendations, ideally recent and specific (4) · Relevant certifications, education, publications, awards, or Services reviews (2) · Other trust signals: notable employers/clients, follower count, endorsements (2) |
| **Search readiness** | 8 | The top 5 keywords appear in the headline or current title (3) · Keywords appear naturally in About and Experience (3) · Location, industry and Open to Work / Services settings support being found (2) |
| **Content alignment** | 7 | Activity (posts or substantial comments) in the last 30 days (3) · Activity topics match the positioning (3) · Nothing off-brand in recent activity (1) |
| **Conversion path** | 7 | Custom profile URL (1) · Primary button (Follow vs Connect) fits the goal (1) · A clear next step for visitors: CTA in About or Featured, website, booking link, Services (3) · Open to Work or Services set appropriately for the goal (1) · Contact info or website present (1) |

Calibration anchors:
- Headline "Data Analyst at Acme Corp" for a job seeker targeting ML roles: ~4/15 (clear-ish, wrong keywords, no proof, wasted space).
- An empty About: 0/15. A 3-line generic About ("Passionate professional with 10 years of experience..."): ~4/15.
- Experience with duty bullets and no numbers: ~6/15.

**Bands:** 90-100 Magnetic · 75-89 Strong · 60-74 Solid · 40-59 Underperforming · 0-39 Invisible.

Also estimate a **potential score** for after the user applies your rewrites, counting only what they can actually do (a recommendation can be requested, but a photo you haven't seen can't be guaranteed).

## Step 4: Write the rewrites
Everything must be copy-paste ready, in the user's voice (`voice.md`), true to their real experience (`writing-rules.md` §1), and checked with the script for length.

1. **Headline: 3 options**, each with a different strategy, labeled:
   - *Search-optimized:* target title and keywords first.
   - *Value proposition:* who they help and the result.
   - *Authority:* niche plus proof or credential.

   Recommend one and say why, for their goal. Check each: `python3 "SKILL_DIR/scripts/check.py" field headline --text "..."`.
2. **About:** one full rewrite following the structure for their goal in `profile-playbook.md`. Make the first ~265 characters a hook for the target reader, include proof and a CTA, and aim for roughly 1,200-2,000 characters (2,600 max). Use `[PLACEHOLDERS]` for missing numbers, and list the questions. Check it with `check.py field about <file>`.
3. **Experience:** rewrite the current role and the most relevant previous role: a 1-2 line scope statement, then 3-5 outcome bullets ("Did X, which led to Y, measured by Z"). Suggest the market-standard title if theirs is internal jargon.
4. **Featured plan:** 2-4 specific items to feature, in order, each with a suggested title and one-line description.
5. **Skills:** the 5 to pin as top skills, skills to add, and skills to remove.
6. **Photo and banner:** feedback on what you can see. A banner concept: the text to put on it (≤ 8-10 words), what to show, and the layout (keep the left ~third clear on mobile where the photo overlaps; check specs in `profile-playbook.md`).
7. **Settings checklist:** custom URL suggestion, Follow vs Connect, Open to Work or Services configuration, contact info, location, name pronunciation, and any section to add (Projects, Services...).
8. **Recommendations:** who to ask (2-3 types of people), plus a short, specific request message they can send.
9. **Job seekers with target JDs: fit and gaps.** One line per JD: strong match / stretch, and why. Then up to 3 concrete actions that close gaps wording can't fix (e.g. "add MLflow + Docker to your GitHub forecasting project; both JDs require deployment experience"). Only list tools or skills as theirs if the profile or the user says so; everything else is "add if true" or a gap.

## Step 5: Alignment and consistency checks
**Topic alignment.** If you know what they post about, compare the topics of their recent activity with the topics their headline and About claim. LinkedIn's feed uses the author's profile as a ranking input, and a mismatch weakens both. Report it in one or two sentences, e.g.: "Your headline says 'B2B SaaS growth', but 7 of your last 10 posts are about remote work. Either reposition or shift your content."

**Fact consistency.** Recruiters and buyers cross-check. Look for contradictions between profile sections, and between the profile and their posts:
- years of experience versus the dates in Experience;
- client or project counts;
- titles;
- dates of events;
- "current" roles that ended.

Also check that the profile export isn't stale (e.g. "2 years 8 months" implies the export date). List any contradictions as fixes; never resolve them by guessing which version is true.

## Step 6: Build the report
1. Create `linkedin/reports/audit-YYYY-MM-DD/`, then copy `SKILL_DIR/assets/report/index.html` into it.
2. Write `data.js` in the same folder in exactly this shape. It's JavaScript, so the object must be valid JSON after `window.REPORT =`. Escape quotes and newlines properly; the safest way is to build the object and serialize it.

```js
window.REPORT = {
  "type": "audit",
  "generated": "2026-10-15",
  "tool_name": "LinkedIn skill for Claude Code",
  "repo_url": "https://github.com/Dynode-ai/linkedin-skill",
  "person": { "name": "Maya Chen", "location": "Austin, Texas" },
  "goal": "Get hired as an ML Engineer",
  "audience": "Hiring managers at AI startups",
  "summary": "One or two sentences: the overall verdict and the single biggest lever.",
  "score": { "total": 58, "band": "Underperforming", "potential": 86,
             "coverage": "Photo & banner not scored (no screenshot). Share one to include it." },
  "categories": [
    { "name": "Headline", "score": 4, "max": 15, "verdict": "Job title only; no ML keywords" }
    // ... one per category. For n/a use "score": null, "status": "na"
  ],
  "priorities": [
    { "title": "Replace your headline", "why": "Recruiters search 'Machine Learning Engineer'; you don't match.", "impact": "High", "effort": "2 min" }
    // 3-5 items, highest impact first
  ],
  "preview": { "before_headline": "Data Analyst at Acme Corp", "after_headline": "the recommended headline" },
  "rewrites": [
    { "section": "Headline", "limit": 220, "options": [
      { "label": "A · Search-optimized (recommended)", "text": "...", "note": "why this one" } ] },
    { "section": "About", "limit": 2600, "options": [ { "label": "Rewrite", "text": "...", "note": "" } ] },
    { "section": "Experience: Senior Data Analyst, Acme", "limit": 2000, "options": [ { "label": "Rewrite", "text": "..." } ] }
    // also: Featured plan, Skills, Banner text, Recommendation request: anything they'll copy
  ],
  "keywords": { "fields": ["Headline", "About", "Experience", "Skills"],
                "terms": ["Machine Learning", "Python", "PyTorch"],
                "matrix": [[false, true, true, true], [false, true, true, true], [false, false, false, false]],
                "caption": "from 4 target job descriptions", "note": "optional one-liner" },
  "findings": [ { "section": "About", "working": ["..."], "fix": ["..."] } ],
  "checklist": [ "Update headline", "Paste new About", "Set custom URL to linkedin.com/in/maya-chen-ml" ]
};
```
Keep `tool_name` and `repo_url` exactly as shown; they credit the open-source project in the report footer. The page computes character counts itself, so the counts it shows are always accurate.

3. Also save the full audit as `linkedin/reports/audit-YYYY-MM-DD.md` (scores, findings, all rewrites). It's easy to diff against future audits and readable without a browser.

## Step 7: Reply in chat
Keep it short; the report holds the detail:
- **Score {N}/100 ({band})**, potential ~{M} after fixes, and one line on why.
- **Top 3 moves**, one line each.
- **Recommended headline**, in a code block so it's easy to copy.
- The report path, e.g. "Open `linkedin/reports/audit-2026-10-15/index.html` in your browser". Show it with an artifact or preview tool if the session has one.
- Questions for any `[PLACEHOLDERS]`.

## Step 8: Update the workspace
- `profile.md`: add a dated line with the score.
- `brief.md`: keywords, proof points you learned, the "Profile last audited" line.
- `stories.md`: any achievements surfaced during the audit.

Next step: `/linkedin:niche` if positioning is fuzzy, otherwise `/linkedin:follow` or `/linkedin:ideas`.
