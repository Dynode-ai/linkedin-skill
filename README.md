# LinkedIn Growth Skill for Claude Code

**Your LinkedIn strategist, editor and researcher, inside Claude Code.**
Audit your profile, find your niche, learn who to follow, and write posts that don't sound like AI. Built on your own LinkedIn data.
No scraping. No API keys. No subscriptions.

<!-- Replace with a GIF from your promo video: docs/demo.gif -->
<!-- ![Demo](docs/demo.gif) -->

```text
/linkedin:audit   →  Score 58/100 "Underperforming" → potential 87
                     3 headline options · About + experience rewrites · keyword heatmap · HTML report
```

---

## What it does

| Command | What you get |
|---|---|
| `/linkedin:start` | A 5-minute setup that learns your goal, audience and voice, saves a private brief, and gives you a 30-day plan. |
| `/linkedin:audit` | A **profile score out of 100** for *your* goal. Three headline options, About and experience rewrites, a Featured plan, a keyword heatmap against target job descriptions, and a shareable **HTML report**. |
| `/linkedin:niche` | Live web research: positioning options, a niche scorecard, your audience described in their own words, white-space opportunities, keywords and content pillars. |
| `/linkedin:follow` | **Real** accounts to follow in 4 tiers: learn from, peers, audience hubs and rising voices. Every link comes from an actual search result and is never guessed, identity is cross-checked, and each account is labeled with how far it was verified. Plus how to engage with each one and a 15-minute daily routine. |
| `/linkedin:ideas` | Post ideas built from *your* stories, your niche's open questions and what has worked for you, each with a drafted hook. Optional posting calendar. |
| `/linkedin:write` | Posts, carousels, hooks and comments in **your voice**. An anti-AI-slop checker runs on every draft, and a feed preview shows exactly where "…more" cuts your hook on mobile and desktop. |
| `/linkedin:analyze` | Your LinkedIn exports turned into **personal benchmarks**: which topics, hooks and formats work *for you*, whether your audience matches your buyers, plus a dashboard. |

You don't need to remember any of this. Just ask: *"audit my LinkedIn"*, *"who should I follow as a fintech founder?"*, *"turn this into a LinkedIn post"*. The skill picks the right workflow.

## Why it's different

Most LinkedIn tools give generic advice, write generic posts and invent things. This skill is built around six rules:

1. **Your real data, legally.** It works from your profile PDF, screenshots, LinkedIn's official "Download your data" archive and your analytics export. It joins your post text to your metrics, which LinkedIn's own exports don't do for you. No scraping, no logins, no browser automation, no risk to your account.
2. **It never makes things up.** It won't invent achievements, numbers or stories; missing facts become `[PLACEHOLDERS]` and questions. It only recommends accounts it actually found in this session. Every profile link is copied from a real search result, identity is cross-checked against a second source, and anything it couldn't confirm is labeled as such.
3. **It doesn't sound like AI.** LinkedIn now lets members report posts as "AI slop". Every draft goes through a deterministic checker covering 60+ AI tells, engagement bait, formatting problems and missing specifics. Your voice fingerprint, measured from your own past posts, keeps drafts sounding like you.
4. **It remembers you.** Your goal, audience, positioning, voice, story bank and learnings live as plain files in `./linkedin/`, so every session starts where the last one ended.
5. **Evidence over folklore.** Its knowledge of the algorithm comes from LinkedIn's engineering publications and studies of 300k to 4.8M posts. Each claim is tagged by confidence, and 13 common myths are debunked. ([see the research](plugins/linkedin/skills/linkedin/references/algorithm.md))
6. **Profile and content tell one story.** LinkedIn's feed uses your headline and profile to decide who sees your posts. The skill checks that your profile claims the topics you actually post about and that actually perform for you.

## Install

In Claude Code:

```bash
/plugin marketplace add Dynode-ai/linkedin-skill
```

```bash
/plugin install linkedin@linkedin-skill
```

That's it. Type `/linkedin` to see the commands.

<details>
<summary>Manual install (without the plugin system)</summary>

Copy the core skill folder into your personal skills directory:

```bash
git clone https://github.com/Dynode-ai/linkedin-skill
```

```bash
cp -r linkedin-skill/plugins/linkedin/skills/linkedin ~/.claude/skills/linkedin
```

Then use `/linkedin audit`, `/linkedin write ...` and so on, or just ask in plain English.
</details>

**Requirements:** Claude Code. Python 3.8+ is *optional*: it powers the post checker and the analytics engine, using only the standard library with no packages to install. Without Python, the skill does the same checks by hand. Works on macOS, Windows and Linux.

## Quick start (5 minutes)

1. Make a folder for your LinkedIn work and open Claude Code in it:
   ```bash
   mkdir my-linkedin && cd my-linkedin && claude
   ```
2. Save your profile as a PDF: open your LinkedIn profile on desktop → **Resources** (or **More**) → **Save to PDF**. Drop it into the folder.
3. Run:
   ```bash
   /linkedin:start
   ```

Then `/linkedin:audit` to fix your profile, `/linkedin:follow` to build your engagement list, and `/linkedin:ideas` → `/linkedin:write` to start posting. After a month, `/linkedin:analyze` with your analytics export.

**Get your data** (all official LinkedIn features):
- **Profile PDF:** Profile → Resources → Save to PDF.
- **Data archive:** Me → Settings & Privacy → Data privacy → Download your data. Includes every post you've written.
- **Analytics:** Profile → Analytics → Show all → Post impressions → Export (.xlsx).

## What's in the box

```
plugins/linkedin/skills/
  linkedin/                 the core skill: all the knowledge lives here
    SKILL.md                router, principles, workspace memory
    workflows/              start · audit · niche · ideas · write · follow · analyze
    references/             profile playbook · goal playbooks · algorithm evidence ·
                            content playbook · writing rules · research methods · data sources
    scripts/
      check.py              post and profile-field checker (AI tells, the "see more" fold, limits…)
      linkedin_data.py      parses LinkedIn exports → personal benchmarks, voice fingerprint, dashboard
    assets/
      report/               profile audit report (HTML)
      preview/              mobile + desktop feed preview with the real "…more" cut
      carousel/             1080×1350 carousel builder → PDF for document posts
      dashboard/            analytics dashboard
      templates/            brief · voice · story bank
  start/ audit/ niche/ ideas/ write/ follow/ analyze/   the slash commands
```

Every visual output is a single self-contained HTML file. It opens offline and sends nothing anywhere.

## Privacy

- Everything stays on your computer in `./linkedin/`. Nothing is uploaded except your conversation with Claude.
- The data archive contains messages and your connections' details. The skill reads only the files a task needs, and its network analysis is aggregate only (no names).
- If you run it inside a git repository, add `/linkedin/` to `.gitignore`.

## FAQ

**Does it post to LinkedIn for me?** No, by design. Automating LinkedIn violates its User Agreement and gets accounts restricted. You copy, paste and publish yourself.

**Is it against LinkedIn's terms?** No. It uses LinkedIn's own export features and your copy-paste. It never logs in, scrapes or automates.

**Will my posts sound like ChatGPT?** That's the main failure this skill is designed to prevent. Give it a few samples of your writing (or your data archive) and it writes to your measured style, then checks every draft for AI tells.

**How accurate is the profile score?** It's this skill's own transparent rubric (10 categories, 100 points, defined in [`workflows/audit.md`](plugins/linkedin/skills/linkedin/workflows/audit.md)), not a LinkedIn metric. It's designed to be consistent, so you can track progress.

**Can I use it with Claude.ai or other agents?** Claude Code is the primary target. The core `linkedin` folder follows the open Agent Skills format, so it can be uploaded to Claude.ai or used by other SKILL.md-compatible agents. That use is experimental, and the slash commands and file workspace work best in Claude Code.

## Contributing

Issues and pull requests are welcome, especially:
- LinkedIn export files that the parser doesn't understand (run `python3 linkedin_data.py inspect <file>` and share the output, never your data);
- new evidence on how the platform works, with sources;
- AI-tell patterns the checker misses.

Run the tests with `python tests/make_fixtures.py`, then the commands in [`tests/README.md`](tests/README.md).

## License

MIT © [Dynode.ai](https://github.com/Dynode-ai). Not affiliated with or endorsed by LinkedIn Corporation. LinkedIn is a trademark of LinkedIn Corporation.
