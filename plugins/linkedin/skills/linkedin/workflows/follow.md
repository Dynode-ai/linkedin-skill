# Workflow: follow (who to follow and engage with)

Goal: a short list of **real, active** LinkedIn accounts, each with a specific reason and a way to engage, plus a daily routine that turns the list into growth. Every account is verified, and the ones that couldn't be verified are shown separately. Most "who to follow" lists online are stale or invented; this one isn't.

Read first: `SKILL_DIR/references/research.md` (follow the verification rules exactly) and `SKILL_DIR/references/content-playbook.md` §8.

## Step 1: Load context
Read `linkedin/brief.md` (niche, audience, goal, region), `people.md` (don't repeat; re-verify entries older than ~90 days), and the latest `reports/niche-*.md`. If the niche or audience is unknown, ask one question first.

## Step 2: Define the tiers
Explain the tiers briefly to the user. They're what makes this list useful rather than a celebrity list:

| Tier | Who | Why | How many |
|---|---|---|---|
| **1. Learn from** | The biggest, best creators in the niche | Study their hooks, formats and topics. Don't expect replies. | 3-5 |
| **2. Peers** | People at a similar stage serving the same audience | Engage, reply, collaborate (co-posts, guest spots). Relationships here compound. | 5-8 |
| **3. Audience hubs** | Creators whose comment sections are full of the user's target audience (e.g. CFO creators for someone selling to CFOs) | Thoughtful comments there put the user in front of buyers, hiring managers or followers. | 5-8 |
| **4. Rising voices** | Smaller, fast-growing, very active creators | Early comments get noticed; easier to build real relationships. | 3-5 |
| **Also** | Company pages, newsletters, communities | Target employers (job seekers), industry news sources, idea sources. | 3-6 |

Adapt to the goal: for job seekers, tier 3 is people whose audience includes hiring managers in their field, and "Also" includes target companies' pages. For founders, tier 3 is where their buyers hang out.

## Step 3: Research (fast and parallel)
The user is waiting and paying for every search, so aim to finish research and verification within about 30 searches total. Do the research yourself in this conversation; don't delegate it to subagents, which multiply cost and time many times over. Showing 15 well-verified accounts beats showing 40.
- **Send searches in parallel batches** (4-8 WebSearch calls in one message), never one at a time.
- **Batch 1, discovery:** Top Voices lists for the niche, `site:linkedin.com/posts "<niche term>"` for 2-3 niche terms, newsletters, podcasts and speaker lists, and industry associations (see `research.md`).
- **Shortlist:** about 1.5x the accounts you'll show.

## Step 4: Verify every candidate
Verify efficiently. One query per person, `"Full Name" site:linkedin.com/posts`, usually returns both their profile slug and dated recent posts. Batch these queries. Date all the post URLs at once with `python3 "SKILL_DIR/scripts/linkedin_data.py" postdate <url1> <url2> ...`.

For each candidate, record:
- the LinkedIn URL exactly as seen in a source;
- identity confirmation (a second source, often the same result's snippet plus a company or podcast page);
- evidence of activity in the last ~90 days;
- relevance (what they post about).

Label each ✅ verified, ⚠️ partly verified, or ❌ not recommended (with the reason). Stop verifying once each tier has enough ✅ accounts.

## Step 5: Present
For each tier, a table:

| Name | Posts about | Why for you | How to engage | Link | Evidence |
|---|---|---|---|---|---|
| ✅ Name | One line | Specific to the user's goal | A concrete first action ("Comment on her weekly teardown with your own SaaS example") | URL | "Post on 2026-10-02" (link) |

Then:
- **❌ Couldn't verify** (one line each, with the reason). It shows the list is honest.
- **Your daily 15-minute routine**, built from `content-playbook.md` §8 and named after people on this list.
- **Setup tips:** follow tier 1-3; ring the notification bell for 3-5 key people so their new posts reach the user early (fresh posts are where comments get seen); don't mass-connect; send personalized requests to peers.
- **A reminder:** "Click each link once before following. I can't see behind LinkedIn's login, so a profile may have changed since I checked."

## Step 6: Save
Write or update `linkedin/people.md`:

```markdown
| Tier | Name | URL | Posts about | Engage by | Status | Verified on |
|---|---|---|---|---|---|---|
```

Keep a "Not recommended" section with reasons, so future runs don't re-check them unnecessarily.

Next: `/linkedin:ideas` (and start the routine today).
