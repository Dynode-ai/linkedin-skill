# Workflow: ideas (content ideas and posting plan)

Goal: a backlog of post ideas the user is excited to write, built from **their** raw material and their audience's real interests, each with a drafted hook. Optionally, a posting calendar matched to their capacity.

Read first: `SKILL_DIR/references/content-playbook.md` (§1-4 and §7).

## Step 1: Load context
Read `linkedin/brief.md` (goal, audience, pillars, capacity, formats, off-limits), `stories.md`, `learnings.md` (what works for them), `ideas.md` (avoid duplicates), recent files in `posts/`, and the latest `reports/niche-*.md` if any.

No pillars yet? Derive 3-4 quickly from the brief and profile (see `content-playbook.md` §1), and mention `/linkedin:niche` for a researched version.

Parse the request: number of ideas (default 15), a specific pillar or format, or "calendar N weeks".

## Step 2: Gather raw material (only if thin)
If `stories.md` has fewer than ~5 unused entries, ask 3-5 quick story-mining questions in one message before generating. The answers make ideas 10x more specific. For example:
- "What's a result from the last year you're proud of? Any numbers?"
- "What's a mistake you made (or see others make) in your field that cost real time or money?"
- "What do clients/colleagues ask you about most often?"
- "What's something most people in your field believe that you think is wrong?"
- "What are you working on right now that others would find interesting?"

If the user prefers to skip, continue and mark ideas that need their input. Save any answers to `stories.md`.

## Step 3: Check what's timely (optional, fast)
Run 2-4 WebSearches for recent news, debates or changes in their niche (last ~30 days). Keep only items where the user has a real take to add, and record the source link and date in the idea.

## Step 4: Generate, then filter hard
Generate ~2x the requested number using the idea engine (`content-playbook.md` §2: sources × angles). Then keep only ideas that pass the quality bar (§3): only-you, audience, goal, payoff and truth tests. Balance across:
- pillars (follow the brief's shares);
- purposes (teach / show / think / be human / offer);
- formats the user is willing to make;
- effort (mix quick wins with a few bigger pieces).

If `learnings.md` shows what works for them (topics, hook types, formats), weight toward it, and say so ("leans on story hooks, which get you 2x your median").

## Step 5: Present
For each idea:

```
#12 · Pillar: Startup finance mistakes · Teach · Text · Effort: S
Hook: "Your burn multiple is lying to you."
Core idea: Why burn multiple misleads at <$1M ARR and what to track instead.
Raw material: Story #4 (the Series A diligence call) + your Q3 client benchmark
Needs from you: nothing  /  [the actual burn numbers you can share]
```

Then:
- **Start with these 3**, and why (quick, strongest material, best fit with what's working).
- Any **series** opportunity (a recurring format they could own).

## Step 6: Calendar (if requested, or if capacity is known and the user wants a plan)
Build an N-week table matching their capacity (`content-playbook.md` §7): date, day, idea #, format, pillar. Rules:
- At least 24 hours between posts.
- Alternate pillars and purposes; put an offer post at most every 1-2 weeks.
- Timing: suggest weekday slots when their audience is likely online (their time zone), and treat timing as a tiebreaker (see `algorithm.md` §7). Their own analytics override general studies.
- Include the daily engagement routine as a line item.

Save as `linkedin/calendar-YYYY-MM-DD.md`.

## Step 7: Save
Append the ideas to `linkedin/ideas.md` with stable IDs, status `idea`, date added, pillar, format, hook, raw material, and needs. Don't renumber old ideas. Update `stories.md` statuses if ideas were built from stories.

Next: `/linkedin:write 12` (write idea #12).
