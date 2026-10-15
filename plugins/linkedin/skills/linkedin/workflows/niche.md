# Workflow: niche (positioning, audience, landscape)

Goal: give the user a sharp answer to "what should I be known for, for whom, and where's the opening?", backed by real research rather than guesses, and turn it into positioning, keywords and content pillars.

Read first: `SKILL_DIR/references/research.md` (methods and verification rules) and the user's goal in `SKILL_DIR/references/goals.md`.

## Step 1: Load what you know
Read `linkedin/brief.md`, `profile.md`, `stories.md`, `learnings.md`. Form a **niche hypothesis**: what they do + for whom + what makes them credible. If there's no brief and no profile, ask one question: "In a sentence: what do you do, and who do you most want to notice you on LinkedIn?"

If the user names a niche in the request, analyze that one (it may differ from their current profile, e.g. a career change).

## Step 2: Research (WebSearch, parallel where possible)
Spend real effort here; this is what makes the output specific. Target 8-15 searches, sent in parallel batches, done in this conversation rather than delegated to subagents. Keep a source list.

1. **Audience reality:** who exactly the audience is (titles, seniority, company types), their responsibilities and KPIs (job postings), top pains and goals (Reddit, forums, reviews, reports), and **the exact words they use** (collect 5-10 short verbatim phrases with links).
2. **Is the audience on LinkedIn?** Signals: active creators serving this audience, LinkedIn groups and newsletters, engagement on niche posts. Some audiences (e.g. hourly workers, some trades, some consumer niches) are thin on LinkedIn; say so if that's the case.
3. **The conversation landscape:** 5-10 active creators covering this space (verify per `research.md`; these feed `follow`), the topics and formats they lean on, and what's oversaturated.
4. **White space:** questions the audience asks that nobody answers well; angles nobody covers with real data; intersections (e.g. "finance for climate-tech startups").
5. **Timely shifts:** regulation, tools, market changes in the last 6-12 months that create new questions.

## Step 3: Analyze

**Niche scorecard** (score 1-5, one line of reasoning each, based on the research):

| Dimension | Question |
|---|---|
| Audience on LinkedIn | Is the target audience active here? |
| Pain / value | How badly do they want this solved (or how valuable is it to hire for)? |
| Right to win | Does the user have proof, experience or a unique angle others lack? |
| Competition | How crowded is the conversation? (5 = wide open) |
| Content runway | Could they post about it 100+ times without repeating? |
| Goal fit | Does winning here produce their goal (job, clients, pipeline, audience)? |

**Positioning options.** Offer 3 options, from broadest to sharpest. For each give the one-liner, who it attracts, the trade-off, and an example headline. Recommend one with reasons. Narrower usually wins early ("easy to remember, easy to refer"). The user can widen later.

Example:
- Broad: "Data analyst" → crowded, forgettable.
- Focused: "Analytics for e-commerce brands" → clear audience, still competitive.
- Sharp: "Turning Shopify data into decisions for DTC brands doing $5-50M" → memorable, referable, smaller pool.

**Positioning statement:** "I help {who} {achieve what} {through/with what}, unlike {common alternative}, because {proof/unique angle}." Plus a short one-liner version for the headline.

**Audience map** (1-2 personas): titles, seniority, company type, top 3 pains, top 3 goals, objections, verbatim phrases, what they read and who they follow.

**White space:** 3-5 specific openings, each with evidence (link) and an example post angle.

**Keyword map:** 10-15 terms for the profile (what they search) and 10-15 for content (what they talk about), in the audience's language.

**Content pillars:** 3-4 pillars (see `content-playbook.md` §1), each with purpose, example topics, and why it serves the goal.

## Step 4: Save
- Full report → `linkedin/reports/niche-YYYY-MM-DD.md` with the scorecard, options, audience map, white space, keyword map, pillars, the list of creators found (with verification status) and all source links.
- Update `brief.md`: positioning, audience, keywords, pillars. Mark changed fields with the date.
- Add verified creators to `people.md` (tier them later in `follow`).

## Step 5: Reply in chat
- The recommended positioning (one-liner + headline example) and why.
- Scorecard in one compact table.
- Top 3 white-space opportunities, one line each.
- The pillars.
- Path to the full report.
- Next: `/linkedin:follow` (people to engage with in this niche) or `/linkedin:audit` if the profile doesn't reflect the new positioning yet.
