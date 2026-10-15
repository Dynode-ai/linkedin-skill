# Workflow: analyze (personal benchmarks from the user's own data)

Goal: tell the user what actually works **for them**, from their own exports, and feed it back into their strategy. Generic benchmarks ("carousels get 1.4x") are a fallback; their own numbers ("your story posts get 2.1x your median") are the point.

Read first: `SKILL_DIR/references/data-sources.md` (what each export contains and how to get it).

## Step 1: Get the data
Accept whatever the user has, in any combination:
- **Analytics export** (.xlsx, `AggregateAnalytics_*.xlsx` or per-post exports): impressions, engagement, top posts, followers, demographics.
- **Data archive** (.zip or folder): `Shares.csv` (all post text), profile, connections, comments.
- **Screenshots or pasted numbers** if they can't export. Work with these manually.

If they have nothing yet, give the export steps from `data-sources.md` (both exports take ~2 minutes to request; the full archive can take up to 48 hours). Suggest requesting the archive now and running the analytics export in the meantime.

Save inputs under `linkedin/data/` (copy them there, or reference the user's path).

## Step 2: Parse
```
python3 "SKILL_DIR/scripts/linkedin_data.py" build <archive.zip> <analytics.xlsx> --out linkedin/data
```
It reads zips directly, matches loosely named columns, joins post text to metrics (by post ID, then by the publish time encoded in IDs, then by date), and writes `posts.json`, `analytics.json`, `profile_archive.md`, `network.md` and `voice.json`. Read its summary output. If something wasn't recognized, run `inspect <path>` to see what's inside, and handle that file manually.

**Know the data's limits and tell the user:**
- The aggregate analytics export lists only the **top 50 posts** by impressions and by engagements. If they have more posts in the period, comparisons are among their better posts.
- `Shares.csv` has text but no metrics. Posts without metrics can still be used for voice and topic analysis.
- Under ~10 posts with metrics, treat every pattern as a hypothesis, not a finding.

## Step 3: Tag the posts
List the posts compactly:
```
python3 "SKILL_DIR/scripts/linkedin_data.py" list linkedin/data --sort impressions --chars 200
```
Read each post (open `posts.json` for full text when the excerpt isn't enough) and assign tags in `linkedin/data/tags.json`, keyed by the post number `n`:
```json
{ "1": { "topic": "Fundraising & diligence", "hook": "observation", "format": "text", "purpose": "teach" } }
```
- **topic**: map to the user's pillars from `brief.md` when they exist, plus "off-topic" for posts outside them. Use 4-8 topics total.
- **hook**: story · result · contrarian · observation · number · question · statement · announcement.
- **format**: text · image · carousel · video · poll · article · reshare. Media posts can be identified from the `MediaUrl` column but not their type, so infer from the text ("swipe through" → carousel).
- **purpose**: teach · show · think · human · offer.

## Step 4: Compute benchmarks
```
python3 "SKILL_DIR/scripts/linkedin_data.py" stats linkedin/data --tags linkedin/data/tags.json
```
This prints medians and lift (relative to the user's own median) by length, first-line length, media, links, list use, weekday, and every tag, with sample sizes. Use medians, because LinkedIn impressions are heavily skewed by outliers.

## Step 5: Interpret like an analyst
Look for patterns that are **large** (lift ≥ ~1.3x or ≤ ~0.75x), **supported** (n ≥ 3, ideally 5+), and **plausible** (there's a reason it would work). Also check:
- **Trend:** monthly medians and posting frequency. Is reach improving? Did a gap in posting coincide with a drop?
- **Top 5 vs bottom 5:** what the best posts share (topic, hook, specificity, format) and what the weakest share.
- **Audience fit:** compare `analytics.json` demographics (job titles, seniority, industries) with the target audience in `brief.md`. "Only 4% of your audience are CFOs, your stated buyers; 14% are founders, who are a reasonable secondary buyer" is one of the most valuable insights you can give.
- **Network fit:** `network.md` shows who they're connected to. A network full of recruiters won't help a consultant sell to CTOs.
- **Profile alignment:** do their best-performing topics match the headline and About? If their best topic isn't in their headline, say so.
- **Credibility consistency:** do the numbers and facts in their posts agree with each other and with the profile (years of experience, client counts, dates, titles)? Prospects and recruiters read both, so flag contradictions.
- **Their own advice:** posts sometimes contain lessons the user hasn't applied to their profile ("specializing brought 3x more referrals" next to a generic headline). Point these out; they're persuasive because they're the user's own words.
- **Confounders:** follower growth over time, one viral outlier, seasonality, a carousel that was also the newest post. Name them.

Be honest about uncertainty. "Posts with a list did better (1.6x, n=7)" is a finding. "Tuesday posts do better (n=2)" is noise, so say it's noise.

## Step 6: Recommend
Write 4-6 insights, each tied to a number:
- **Do more** (2): the strongest positive patterns.
- **Stop** (1-2): what underperforms and doesn't serve the goal.
- **Test next** (1-2): an experiment for the next 30 days with a clear success measure ("4 carousels from your best text posts; success = beat your median 3 of 4 times").

Save them as `linkedin/data/insights.json`:
```json
[ { "kind": "do", "title": "Lead with a specific number or moment", "detail": "Posts opening with a number or scene got 2.1x your median (n=7)." } ]
```
`kind` is one of `do`, `stop`, `test`, `keep`.

## Step 7: Dashboard
```
python3 "SKILL_DIR/scripts/linkedin_data.py" dashboard linkedin/data --out linkedin/reports/analytics-YYYY-MM-DD --name "First Last" --insights linkedin/data/insights.json
```
This writes `index.html` + `data.js` with:
- headline numbers;
- the insights;
- weekly impressions and follower charts;
- "what works for you" lift charts;
- a sortable post table;
- audience demographics;
- their measured writing style.

Give the user the path to open.

## Step 8: Feed it back
- `linkedin/learnings.md`: add a dated section with the insights and their numbers. Every future `ideas` and `write` run reads this.
- `linkedin/voice.md`: fill or refresh the "Measured style" section from `voice.json`. If there's no voice profile yet, build one now from their posts and comments (`writing-rules.md` §2).
- `linkedin/brief.md`: if audience fit is off, add it to Open questions and suggest a fix (profile repositioning or content shift).
- `linkedin/posts/`: mark posts as published with their metrics where they match.

## Step 9: Reply in chat
- The 3 most important findings, each with its number and sample size.
- Audience fit in one line.
- The one experiment to run next.
- Dashboard path.
- Next: `/linkedin:ideas` (it will now use these learnings), and run `/linkedin:analyze` again in 30 days to see whether the experiment worked.
