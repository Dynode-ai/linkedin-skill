# How LinkedIn distribution works (evidence base)

Compiled October 2026 from LinkedIn's own engineering posts, executive statements, and the largest available datasets. Use this file whenever you make a claim about reach, ranking, formats, timing, links or hashtags.

**Confidence tags** (say them in plain words to the user, e.g. "LinkedIn has confirmed..." or "one large study suggests..."):
- **[H]** LinkedIn primary source, or several large datasets agreeing.
- **[M]** one large dataset or consistent practitioner data.
- **[L]** secondhand, small sample, contested, or inference.

Vendor studies (AuthoredUp, Buffer, Ordinal, Metricool, Socialinsider) are correlational. Socialinsider and Metricool numbers are mostly company-page data, not personal profiles. Numbers drift every few months. If the user's own analytics disagree with this file, their data wins for their account.

## Contents
1. The ranking system today
2. Signals that matter
3. Reach trends
4. Formats
5. Post mechanics: length, hooks, formatting, CTAs
6. Links, hashtags, tagging, editing
7. Frequency and timing
8. Comments and engagement
9. Enforcement: pods, automation, AI slop
10. Myths
11. Sources

---

## 1. The ranking system today

- **[H]** In March 2026 LinkedIn described its new production feed. One **LLM-based retrieval model** (text embeddings of posts and members) replaced the older mix of network/trending/collaborative sources. A **transformer ranker** then reads a member's sequence of 1,000+ past interactions. It predicts passive actions (click, skip, long dwell) and active ones (like, comment, share). [1][2][3][4]
- **[H]** Inputs include the **post text, format, author name, headline, company and industry**, engagement counts, and on the member side the **profile (industry, skills, experience, location)** and engagement history. Demographic attributes are excluded. [1]
- **[H]** Matching is **semantic**, not keyword-based. LinkedIn's example: embeddings connect "electrical engineering" to "small modular reactors". The stated goal is to show expert posts "even if they are beyond your network". [1][8]
- **[H]** Quality is judged against natural-language policies (authenticity, timeliness, substantive professional discussion), checked by raters and LLM evaluations, and revised often. [8][24]
- **[L]** "360Brew" is a 150B-parameter **research** model from a 2025 paper. LinkedIn hasn't said it's the live feed ranker, and the March 2026 production post doesn't mention it. Don't tell users "360Brew decides your reach". [5][6][7]

**What this means for users**
- **[H mechanism / M effect]** Write **explicit, specific text**: name the roles, tools, industries and problems. The retrieval model places posts by what the text is about.
- **[H input / L effect size]** The author's **headline, company and industry are ranking inputs**, and readers match the headline to the post. A profile and a content stream about the same 1-3 topics is the sensible strategy. Van der Blom (2026) suggests one core topic plus a few subtopics, with ~80% of posts on-topic. [1][10][11]
- Out-of-network reach now comes mainly from **topical relevance**, not from who you're connected to.

## 2. Signals that matter

| Signal | What we know | Conf. |
|---|---|---|
| **Dwell time** | Modeled since 2020; "long dwell" is an explicit objective in 2026. A fast skip counts as a negative. Specific "good dwell" second-counts circulating online are invented. | [H] |
| **Comments** | An explicit objective. No published weighting; "a comment = 2x a like" is a vendor guess. | [H]/[L] |
| **Shares / reposts** | An explicit ranking objective. | [H] |
| **Saves and sends** | Shown in creator analytics since Sept 2025. AuthoredUp's correlational data: one save ≈ 5x the reach effect of a like. Not named in LinkedIn's production post. | [M]/[L] |
| **Early engagement** | Freshness and engagement counts update within minutes, so early engagement plausibly helps. A fixed "golden hour" is not documented by LinkedIn. | [L] |
| **Author replies** | Buffer, comparing each account with itself (72k posts): posts where the author replied to comments got ~30% more engagement. Causality unproven. | [M] |

## 3. Reach trends 2024-2026

- **[H direction]** Organic reach per post has fallen a lot. Van der Blom (1.3M posts, 2026): about −60% reach over two years for active creators, engagement −20-25%, so engagement *per view* rose. AuthoredUp: median impressions 1,211 (Jun 2024) → 636 (May 2025). Metricool 2026: visible likes, comments and shares down, but clicks and swipes up. [11][15][17]
- Tell users this so they judge their numbers fairly. A post with 800 impressions in 2026 isn't a failure. Track **trend vs. their own median**, and track conversions (profile views, followers, DMs) over raw impressions.

## 4. Formats

**Personal profiles** (AuthoredUp, Mar 2025-Feb 2026; reach relative to each profile's own median) [31]:

| Format | Reach | Notes |
|---|---|---|
| Poll | 1.78x | but engagement only 0.37x; downranked when used as bait; avoid for growth |
| Document / PDF carousel | 1.39x | top or near-top in every dataset [H] |
| Image | 1.20x | the safest default (57% of posts) |
| Text only | 1.07x | works best for strong writers |
| Video | 0.86x | the only major format below average; personal video reach −36% YoY |

**Company pages** (Socialinsider, 1.3M posts, 2025 data) [21]: Document 7.0% engagement rate · Multi-image 6.45% · Video 6.0% · Image 5.3% · Text 4.5% · Poll 4.2% · Link 3.25%.

- **Video** [M]: LinkedIn is pushing it (uploads +36%, vertical video feed), but per-creator performance is down. If users do video, longer is better (3+ min: 1.21x vs 30-60s: 0.95x), and fuller captions help (20+ sentences 1.13x vs under 5 sentences 0.73x). Captions must match the video. [32][33]
- **Multi-image** [M]: top on company pages in two 2026 datasets.
- **Newsletters** [M]: each edition notifies subscribers in-app and by email, which bypasses the feed. A strong conversion asset for consultants and creators.
- **Articles** [L-M]: roughly 0.4x a typical post in reach.
- **LinkedIn Live, reposts, emoji**: no reliable recent data. Say so.

## 5. Post mechanics

**Limits** [H]: post 3,000 characters; comment 1,250 (some sources say 1,750); poll question 140, options 30 each.

**"...see more" fold** [M]: about **140 characters on mobile, ~210 on desktop**, and line breaks use up the fold. ~72% of usage is mobile. Design the first line for mobile. `scripts/check.py` simulates both.

**Hooks** (AuthoredUp, 309,614 posts, Dec 2025-May 2026; median engagement rate by hook style) [37]: Story 2.60% · Contrarian 2.31% · Statement 2.27% · Results 2.19% · Question 2.16%. **Short first lines win**: 0-40 characters 2.61% vs 200+ characters 2.08%. LinkedIn's Laura Lorenzetti: "Hook the people, tell them the payoff, and then get them into it." [10]

**Length** [M]: substantive posts beat very short ones.
- Median engagement rate rises from 2.10% (<400 characters) to 2.61-2.67% (1,301-2,500 characters), per AuthoredUp (372k posts). [36]
- Creator-adjusted (709k posts): text posts peak around **1,200-1,500 characters**, and posts under 400 characters score −14%. [38]
- Best caption lengths: image 800-1,000, carousel 800-1,000, video 1,000-1,200.
- Recommendations elsewhere vary (900-3,000). Let the idea set the length, and default to 900-1,800 for text.

**Formatting** [M]: paragraphs of 4 lines or fewer; scannable lists. Unicode "bold" letters break screen readers and search, so avoid them. No credible data on emoji.

**CTAs** [M]: ending with a question gives a negligible lift (2.33% vs 2.26%). Explicit engagement bait ("comment YES", "like if you agree") is downranked [H]. Promotional posts got **+18%** median engagement in one study (376k posts), so occasional, clear offers are fine. [24][37][39]

## 6. Links, hashtags, tagging, editing

**External links in the post** (sources disagree):
- LinkedIn says the algorithm doesn't judge posts with outside URLs differently (Mar 2026). [18]
- Measured effects on personal posts range from about −19% (van der Blom) to −27% (Ordinal) to −36% (LinkPost, 358k posts). Metricool's company-page data showed a positive effect. [19][20]
- Link previews were shrunk in 2024. [22]
- Net **[M]**: a single body link likely costs modest reach. The famous "−60%" figure has no traceable source.
- **"Link in the first comment"** is unproven **[L]**, and links in comments get far fewer clicks. Advice: if the post's goal is clicks, put the link in the post and accept the cost. If the goal is reach or authority, skip the link and point to Featured or the newsletter.

**Hashtags** [H]: no longer boost reach. Hashtag following and profile hashtags were removed in 2024. LinkedIn calls them "a steering wheel, not a gas pedal". Use 0-3 relevant ones, or none. [18][23]

**Tagging** [L]: fine when respectful. Tag only people who are involved and likely to respond. An old 2020 study found that posts where under 25% of tagged people responded got 20-30% fewer views.

**Editing after posting** [L]: no documented penalty. Fixing a typo is fine.

**Scheduling tools** [H]: LinkedIn says the algorithm doesn't care which tool posts. [18]

## 7. Frequency and timing

**Frequency** [M]:
- LinkedIn says each post is judged independently and there's no frequency penalty, but audiences fatigue. [18]
- Buffer (2M+ posts, each account vs itself): more posts per week → more impressions per post, with no penalty at high frequency. [27]
- Van der Blom (2026): the sweet spot moved down to **2-4 posts/week**.
- Ordinal: posts under 12 hours apart get −17% engagement. [28]
- **Default advice:** 2-5 posts per week at least 24 hours apart, at a pace the user can sustain for 90 days. Consistency beats bursts.

**Time of day** [L]: studies conflict. Buffer (4.8M posts, Sep 2026) found weekday late afternoons (3-8 pm local) strongest, with Monday and Tuesday weakest. Sprout found Tuesday-Thursday mid-day; Hootsuite, early mornings; another study, Sundays. [29][30] Treat timing as a tiebreaker. Post when the target audience is on (their time zone) and the user can reply to comments in the first hour or two, then let their own analytics decide.

## 8. Comments and engagement

- **[M]** Comments on other people's posts are distribution. Comment authors now see impression counts on their comments, and comments are ranked by relevance to each viewer. [41]
- **[M]** Substance beats length. Comments of 250+ characters average more impressions, but median impressions are flat across lengths (LinkHub, 657k comments). [42] Write comments that add an example, data point, counterpoint or real question.
- **[M]** Reply to comments on your own posts (Buffer: ~30% more engagement).
- **[L-M]** Stay on-topic. Practitioners like van der Blom spend 25-30 minutes a day commenting on posts in their topic, and argue that off-topic or bot comments blur how LinkedIn classifies you.

## 9. Enforcement: pods, automation, AI slop

- **[H]** LinkedIn actively fights engagement pods, comment automation and unauthorized tools. Automated comments get removed from "Most relevant" and have limited reach, and repeat offenders risk their accounts. Downranked: "comment to agree" bait, poll-baiting, and videos that don't match their text. [2][8][24]
- **[H]** **July 30, 2026**: LinkedIn added a **"Seems like AI slop"** report option, retired its own "enhance your post" AI writer (in favor of a voice-preserving proofreader), and reported blocking hundreds of thousands of automated comment attempts per day. [25]
- **[M]** A 2026 Pangram study flagged ~41% of long LinkedIn posts as fully AI-generated. [26] Generic AI text is now a liability, which is why this skill's writing rules and checker exist.
- **[H]** LinkedIn's User Agreement prohibits scraping and bots (§8.2). This skill never automates LinkedIn.

## 10. Myths

| Myth | Reality |
|---|---|
| "Links cut reach by 60%" | No traceable source. Measured −19% to −36% on personal posts, some positive results on pages, and LinkedIn denies a penalty. |
| "360Brew is the algorithm" / "Depth Score" | 360Brew is a research model. "Depth Score" appears in no LinkedIn publication. |
| "Hashtags boost reach" | Hashtag following and profile hashtags were removed in 2024. Steering wheel, not gas pedal. |
| "You have one golden hour or the post dies" | Undocumented. Early replies help, but there's no fixed window. |
| "Editing a post kills it" | No documented penalty. |
| "Always end with a question" | ~+3%, negligible. Bait questions are downranked. |
| "Never self-promote" | Promotional posts got +18% engagement in one large study. |
| "Short posts win" | 1,200-2,500 characters performs best for text. |
| "Video is king on LinkedIn" | Platform video is growing, but personal-profile video reach is 0.86x and falling. |
| "Scheduling tools get penalized" | LinkedIn says it doesn't care which tool posts. |
| "Posting daily gets you penalized" | No penalty. Just space posts 24h+ apart and keep quality up. |
| "Pods and AI comments work" | Actively suppressed. Accounts at risk. |
| "Put links in the first comment" | Unproven, and it costs clicks. |

## 11. Sources
1. LinkedIn Engineering, "Engineering the next generation of LinkedIn's Feed", Mar 12 2026. https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed
2. LinkedIn Pressroom, Mar 12 2026. https://news.linkedin.com/2026/ImprovingTheFeed
3. arXiv 2510.14223 (Oct 2025). https://arxiv.org/abs/2510.14223
4. arXiv 2602.12354 (Feb 2026). https://arxiv.org/abs/2602.12354
5. arXiv 2501.16450 (360Brew). https://arxiv.org/abs/2501.16450
6. AI Engineer World's Fair talk on 360Brew, 2025. https://www.ai.engineer/talks/U0S6CfzAY5c-360brew-llm-based-personalized-ranking
7. Fast Growth evidence review, 2026. https://fast-growth.fr/en/white-paper/linkedin-algorithm-2026/
8. Tim Jurka (LinkedIn VP Engineering), Software Engineering Daily, 2026. https://softwareengineeringdaily.com/wp-content/uploads/2026/08/SED1949-LinkedIn.txt
9. Social Media Today, topic feeds test, Jun 2026. https://www.socialmediatoday.com/news/linkedin-tests-suggested-feeds/823722/
10. Buffer, quotes from LinkedIn's team, Dec 2025. https://buffer.com/resources/linkedin-algorithm/
11. Richard van der Blom on Creator Science, Jun 2026. https://creatorscience.com/podcast/richard-van-der-blom-2/
12. Kara Redman, summary of six algorithm reports, Mar 2026. https://newsletter.kararedman.com/p/i-binged-6-linkedin-algorithm-reports
13. LinkedIn Engineering, dwell time, 2020. https://engineering.linkedin.com/blog/2020/understanding-feed-dwell-time
14. Social Media Today, saves and sends analytics, Sept 2025. https://www.socialmediatoday.com/news/linkedin-adds-save-and-send-data-to-content-insights/759828/
15. AuthoredUp, algorithm analysis, Sep 2025. https://authoredup.com/blog/linkedin-algorithm
17. Metricool LinkedIn study 2026. https://metricool.com/press-release-linkedin-study-2026/
18. Future Social, Q&A with LinkedIn execs, Mar 2026. https://futuresocial.beehiiv.com/p/i-questioned-linkedin-execs-about-linkedin-s-algorithm
19. Ordinal, link penalty study. https://www.tryordinal.com/blog/linkedin-link-penalty-study
20. Search Engine Journal on Metricool 2025. https://www.searchenginejournal.com/linkedin-study-finds-adding-links-boosts-engagement-by-13/544524/
21. Socialinsider 2026 LinkedIn benchmarks. https://socialinsider.io/social-media-benchmarks/linkedin
22. Social Media Today, external links, Nov 2024. https://www.socialmediatoday.com/news/heres-where-each-of-the-big-social-platform-stands-on-external-links/733946/
23. Social Media Today, Creator mode and profile hashtags removed, Feb 2024. https://www.socialmediatoday.com/news/linkedins-removing-its-creator-mode-option/706585/
24. LinkedIn community, feed update on authenticity and relevance, Apr 2026. https://scommunity.linkedin.com/learn-explore-apply-68/linkedin-feed-update-the-focus-is-on-authenticity-relevance-8734
25. "Seems like AI slop" report button, Jul 30 2026. https://www.tweaktown.com/news/112933/linkedin-adds-a-seems-like-ai-slop-report-button-for-ai-generated-posts/index.html
26. Pangram study via The Decoder, Jul 2026. https://the-decoder.com/linkedin-is-the-undisputed-king-of-long-form-ai-slop-according-to-a-study-spanning-five-platforms/
27. Buffer, posting frequency. https://buffer.com/resources/how-often-to-post-on-linkedin/
28. Ordinal, posting frequency. https://www.tryordinal.com/blog/linkedin-posting-frequency
29. Buffer, best time to post, Sep 2026. https://buffer.com/resources/best-time-to-post-on-linkedin/
30. Sprout Social, best times, Mar 2026. https://sproutsocial.com/insights/best-times-to-post-on-LinkedIn/
31. AuthoredUp, polls and format multipliers, Apr 2026. https://authoredup.com/blog/linkedin-polls
32. TechCrunch, LinkedIn video, Feb 2025. https://techcrunch.com/2025/02/04/linkedin-amps-up-vertical-video-tools-as-uploads-jump-36
33. AuthoredUp, video posts. https://authoredup.com/blog/linkedin-video-posts
36. AuthoredUp, character limits and length, Apr 2026. https://authoredup.com/blog/linkedin-character-limit
37. AuthoredUp, hook study. https://authoredup.com/blog/linkedin-hook-examples
38. AuthoredUp, character counter dataset (709k posts). https://authoredup.com/tools/linkedin-character-counter
39. AuthoredUp, promotional posts. https://authoredup.com/blog/what-not-to-post-on-linkedin
41. Lindsey Gamble, comment impressions. https://lindseygamble.com/blog/linkedin-now-shows-analytics-for-comments-you-leave-on-posts
42. LinkHub, comment length study, Jun 2026. https://linkhub.gg/en/blog/longueur-commentaire-linkedin-impressions
