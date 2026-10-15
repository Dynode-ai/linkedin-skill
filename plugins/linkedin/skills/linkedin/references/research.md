# Web research methods

Used by the `niche` and `follow` workflows. Everything here uses WebSearch and WebFetch on public pages. The two failure modes to avoid: **generic research** (things anyone could guess) and **invented facts** (accounts, URLs, numbers or quotes that don't exist). A wrong account recommendation destroys trust in everything else the skill says.

## The verification rules

1. **Never construct a LinkedIn URL.** Only output `linkedin.com/in/...`, `/company/...` or `/newsletters/...` URLs that you saw verbatim in a search result or on a fetched page during this session. Guessing a slug from a name ("satya-nadella") can point to the wrong person or nowhere.
2. **Confirm identity with two sources.** The name plus role/company from the LinkedIn result should match another source: a company site, speaker bio, podcast page, newsletter, or article.
3. **Confirm recent activity.** Require evidence of LinkedIn activity in the last ~90 days:
   - a `linkedin.com/posts/...` search result with a visible recent date, or
   - a recent newsletter edition or article, or
   - a dated third-party mention of a recent post.
   
   **Dating a post from its URL:** LinkedIn post URLs contain a 19-digit activity ID (`...activity-7380000000000000000-...` or `urn:li:activity:738...`). Shifting it right by 22 bits gives the Unix time in milliseconds when it was posted. This is community-derived but reliable. Run `python3 "SKILL_DIR/scripts/linkedin_data.py" postdate "<post-url>"` to get the date.
4. **Label everything.** ✅ Verified (URL + identity + recent activity), ⚠️ Partly verified (URL and identity, activity unknown), ❌ Not recommended (couldn't verify, or inactive). Show the ❌ list briefly too, with reasons. That transparency is a feature.
5. **Blocked isn't the same as fake.** A logged-out fetch of LinkedIn often returns an authwall or HTTP 999. Treat that as "couldn't check", not "doesn't exist". Don't retry aggressively, and never try to get around it.
6. **Time-sensitive claims need a source that says it.** News, awards, job changes, funding and events go in the output only with a link to a page that actually states it. If you inferred it or the page doesn't say it outright, phrase it as unconfirmed ("LCI presented its Pioneer Award on Oct 15; check who won") or leave it out. These "this week" hooks are exactly what users repeat publicly.
7. **Date your claims.** Record when you verified something (`people.md` keeps a "verified on" date). Re-verify entries older than ~90 days before recommending them again.
8. **Public figures only.** Recommend creators, executives with a public presence, companies, newsletters and communities. Don't compile lists of private individuals. For a job seeker who wants hiring managers at target companies, explain how to find them in LinkedIn search rather than listing private people.

## Where to find real niche voices

Best first:
1. **LinkedIn News "Top Voices" lists** (`site:linkedin.com/pulse "Top Voices" <topic>`): editorially curated. Check the year; many lists are from 2021-2024, and some people on them are no longer active.
2. **Recent LinkedIn posts on the topic**: `site:linkedin.com/posts "<niche term>"`. Authors who show up repeatedly are active. The slug before the first `_` in a post URL is the author's profile slug, but still verify the profile URL in a result.
3. **LinkedIn newsletters**: `site:linkedin.com/newsletters "<topic>"`.
4. **Profile search**: `site:linkedin.com/in "<niche term>" "<role>"`. Good for peers and rising voices; check activity.
5. **Creator rankings** (Favikon and similar): a starting point only. Some rankings sell placement, and methodology is opaque.
6. **Podcasts, conference speaker pages, industry newsletters, LinkedIn Learning instructors**: excellent for confirming someone is real and credible, and for finding people who are respected offline but smaller on LinkedIn (great peers).
7. **"Best LinkedIn creators for <niche>" listicles**: low trust, often outdated or paid. Use only as leads.

Normalize country subdomains (`uk.linkedin.com/in/...` → `www.linkedin.com/in/...`).

## Researching an audience (voice of customer)

Goal: learn what the target audience worries about, wants, and how they phrase it. Their exact words become hooks and keywords.
- **Job postings** for the audience's roles: what they're responsible for, tools, KPIs.
- **Reddit, forums, communities**: `site:reddit.com <role> <problem>` and similar. Capture verbatim phrases, with links.
- **Review sites** (G2, Capterra, Trustpilot) for the products they use: complaints and desired outcomes.
- **Industry reports and surveys**: priorities, budgets, trends. Cite the date.
- **Questions people ask**: "how do I...", "why does...", "best way to..." queries in the niche.

Quote short phrases (under ~15 words) with the source link. Summarize the rest.

## Researching a niche's conversation

- What do the active creators in the niche post about? Which topics and formats show up most? → saturated angles.
- What does the audience ask about that creators rarely cover? What does nobody show with real numbers? → white space.
- What changed recently (regulation, tools, market shifts, layoffs, funding)? → timely angles.

## Research hygiene

- **Budget:** about 30 searches for `follow` and 8-15 for `niche`. Stop when you have enough evidence, not when you run out of ideas.
- **No subagents for research:** search directly in the main conversation. Delegating to subagents multiplies cost and time (a test run that delegated made 200+ searches).
- Run searches in parallel batches (4-8 per message) when they're independent.
- Prefer sources from the last 12 months; note the date of anything older.
- Keep a source list with URLs in every research output.
- If research turns up little (a very small niche), say so. Thin evidence is a finding too, and it suggests adjacent topics.
