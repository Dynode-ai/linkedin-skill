# Getting the user's LinkedIn data (no scraping)

Everything here uses LinkedIn's own export features or the user's copy-paste. Nothing logs into LinkedIn, scrapes, or automates. LinkedIn's User Agreement prohibits scraping and bots, and accounts get restricted for it. Verified October 2026. Menu names move around, so if the user can't find something, tell them to look for the nearest equivalent.

## Quick comparison

| Source | Time to get | What you get | Best for |
|---|---|---|---|
| Profile PDF | 30 seconds | Headline, About, experience, education, top skills, certifications | Audit |
| Screenshots | 1 minute | Photo, banner, top card, Featured, Activity | Audit (visuals) |
| Paste | 1-2 minutes | Whatever they copy | Anything quick |
| Data archive, specific categories | ~10 minutes (email) | Profile, positions, skills, education, recommendations, certifications... | Audit with exact text |
| Data archive, full | up to 24-48 hours | All of the above + every post (Shares), comments, connections, reactions | Voice, post history, analysis |
| Analytics export (.xlsx) | 1 minute | Impressions and engagement over time, top 50 posts, followers, audience demographics | Analyze |

## 1. Profile PDF

**Tell the user:** "On desktop, open your LinkedIn profile, click **Resources** (or **More**) under your name, then **Save to PDF**. Drop the file here or give me its path."
- Desktop only. Works best for English profiles.
- Contains: name, headline, location, About (Summary), experience (titles, companies, dates, descriptions), education, a few top skills, languages, certifications, honors, publications, contact URL.
- **Missing:** photo and banner (ask for a screenshot), Featured, posts and activity, recommendations text, full skills list, follower count.
- The PDF has two columns. Text extraction can interleave the sidebar (skills, languages) with the main column, so read it carefully and reassemble sections.

## 2. Screenshots

**Tell the user:** "Take screenshots of (1) the top of your profile (photo, banner, headline), (2) your About and Featured sections, and optionally (3) your Activity tab. Paste or drag them in."
Screenshots are the only way to assess the photo and banner. On mobile, the top card shows how the banner gets cropped.

## 3. Paste

The user can copy their headline, About and experience straight from the profile's edit forms. Quickest when they just want one section fixed.

## 4. Data archive ("Download your data")

**Tell the user:** "On desktop: **Me** (your photo, top right) → **Settings & Privacy** → **Data privacy** → **Download your data**. Choose either the full archive (includes all your posts; can take up to 24-48 hours) or pick specific categories (arrives in about 10 minutes). Click **Request archive**. LinkedIn emails a download link valid for 72 hours. Download the .zip and give me the path. No need to unzip it."

**The fast categories** (~10 minutes): Profile, Positions, Education, Skills, Certifications, Languages, Projects, Honors, Publications, Recommendations, Endorsements, Invitations, Rich Media, Articles, Company Follows, and more.
**The slow part** (up to 48 hours): Shares (posts), Comments, Reactions, Connections, Messages, Member Follows, Saved Items, and more. Older exports put Connections in the fast archive, so handle both.

**Useful files** (column headers vary slightly between exports; match case-insensitively):

| File | Key columns | Use |
|---|---|---|
| `Profile.csv` | First Name, Last Name, Headline, Summary, Industry, Geo Location, Websites | Exact headline and About text |
| `Positions.csv` | Company Name, Title, Description, Location, Started On, Finished On | Experience |
| `Skills.csv` | Name | Full skills list |
| `Education.csv` | School Name, Start Date, End Date, Degree Name, Notes, Activities | Education |
| `Shares.csv` | Date, ShareLink, ShareCommentary, SharedUrl, MediaUrl, Visibility | **Every post they wrote**, with date and text, but no metrics |
| `Comments.csv` | Date, Link, Message | Their comments: a great voice sample |
| `Recommendations_Received.csv` | First Name, Last Name, Company, Job Title, Text, Creation Date, Status | Social proof |
| `Connections.csv` | First Name, Last Name, URL, Email Address, Company, Position, Connected On | Network composition (the file starts with ~3 note lines before the header) |
| `Certifications.csv`, `Projects.csv`, `Languages.csv` | name, dates, details | Supporting sections |

`SKILL_DIR/scripts/linkedin_data.py build <zip>` reads the zip directly (no unzipping) and handles these quirks.

**Privacy:** the archive includes messages, connections' names and emails, and search history. Only read the files the task needs. Never quote private messages or other people's personal data back into deliverables. Keep everything in `linkedin/data/` on their machine.

## 5. Analytics export (.xlsx)

**Tell the user:** "On desktop: go to your profile → **Analytics** section → **Show all analytics** → open **Post impressions** (or Content) → set the date range to the longest available (365 days) → click **Export** (top right). You'll get an .xlsx file. Drop it here or give me the path. If you can, also export **Followers** the same way."
- Custom date ranges are only available in the mobile app. Desktop presets run 7-365 days.
- The aggregate file (named like `AggregateAnalytics_*.xlsx`) usually has five sheets in this order: **Discovery** (impressions and members reached), **Engagement** (daily impressions and engagements), **Top posts** (up to 50 posts by engagements and 50 by impressions, each with URL and date), **Followers** (total plus daily new followers), and **Demographics** (top job titles, locations, industries, seniority, company sizes of the audience). Sheet names change with the account language, so the parser reads them by position and content.
- **Important limit:** the aggregate export lists only the **top 50 posts**. For a full per-post picture, combine it with the data archive's `Shares.csv` (post text), or have the user export analytics for individual posts ("View analytics" on a post → Export).
- Per-post analytics include impressions, members reached, reactions, comments, reposts, saves, sends, profile views and followers gained from the post, link clicks, and viewer demographics.

`SKILL_DIR/scripts/linkedin_data.py build <xlsx> [<zip>]` parses these and joins post text to metrics.

## 6. Other public sources

The user's personal website, company page, podcast appearances, talks and articles can be read with WebFetch to enrich the story bank and proof points. LinkedIn profile URLs themselves usually return a login wall to non-logged-in fetches. Don't keep retrying, and never try to get around it.
