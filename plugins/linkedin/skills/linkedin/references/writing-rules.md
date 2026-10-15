# Writing rules

Read this before writing anything the user will publish: posts, comments, headlines, About sections, experience bullets, DMs.

The bar: a reader who knows the user should believe the user wrote it, and a stranger should learn something specific. Generic, polished, "AI-sounding" copy is the most common failure of LinkedIn tools, and readers now spot it instantly and scroll past. LinkedIn also reports that it demotes low-effort and AI-generated content in the feed.

## Contents
1. Never fabricate
2. Sound like the user
3. AI tells to avoid
4. Craft
5. Formatting for the feed
6. Comments and DMs
7. Editing checklist

---

## 1. Never fabricate

Do not invent experiences, numbers, clients, employers, quotes, results, credentials, or anecdotes. This is the rule that protects the user. Their colleagues, clients and ex-bosses read their posts, and one invented detail can cost real credibility.

- If a draft needs a detail you don't have, put a bracketed placeholder in caps, like `[HOW MANY CLIENTS?]` or `[NAME OF THE TOOL]`, and list the open questions after the draft. `scripts/check.py` flags placeholders as errors, so they can't slip through.
- Only attribute statistics, studies or quotes to a real source you verified in this session (with a link). Otherwise phrase it as the user's own observation ("In the 40 resumes I reviewed last month...") and only if the user supplied that observation.
- Rewrites of profile sections may restructure and sharpen what the user wrote. They may not add achievements the user didn't claim. If an obvious achievement is missing (a metric, a promotion), ask for it.

## 2. Sound like the user

If `linkedin/voice.md` exists, it overrides the generic style advice in this file. Re-read it before every draft.

### Building a voice profile
Collect 3-10 samples of the user's natural writing. Best to worst: transcripts or voice notes of them talking, their own past posts that performed well, emails or Slack messages, their About section. Spoken samples are the most valuable because they show how the user sounds before they start "writing for LinkedIn".

Extract and record in `voice.md`:
- **Rhythm**: typical sentence length, paragraph length, how often they use fragments.
- **Register**: casual or formal, contractions, jargon level, profanity (yes/no).
- **Person**: mostly "I", "we" or "you".
- **Stance**: blunt or hedged, how they disagree, how they show confidence.
- **Humor**: none, dry, self-deprecating, playful.
- **Signatures**: words and phrases they use repeatedly; how they open; how they close.
- **Never**: things they never do (emoji, exclamation marks, hashtags, rhetorical questions, certain words).
- **Exemplars**: 2-3 short excerpts that capture the voice best.

### Default voice (no samples yet)
"Smart friend explaining something over coffee": plain words, contractions, short sentences, concrete examples, opinions stated plainly with the reasoning shown, light personality, no hype. Ask for samples after the first draft so the next one can sound like them.

## 3. AI tells to avoid

`scripts/check.py post` catches most of these automatically. Know the patterns anyway, because the checker can't catch all of them.

**Vocabulary**: delve, tapestry, testament, realm, landscape (as in "the AI landscape"), navigate the complexities, game-changer, unlock, unleash, elevate, supercharge, leverage (verb), seamless, robust, cutting-edge, revolutionize, paradigm shift, synergy, holistic, pivotal, transformative, invaluable, myriad, plethora, meticulous, foster, empower, harness, embark, resonate, journey (as metaphor), "dive in", "deep dive".

**Openers**: "In today's fast-paced world", "Imagine this:", "Picture this:", "In a world where", "Have you ever wondered", "Did you know", "Stop scrolling", "I'm thrilled/humbled/excited to announce", "Let's talk about", "Unpopular opinion:" (fine once, but it's worn out as a default).

**Structures**:
- Antithesis on repeat: "It's not X. It's Y." / "This isn't about X, it's about Y."
- The reveal question: "The result? ..." "The secret? ..." "The best part? ..."
- Staccato triplets: "No fluff. No filler. Just results."
- Everything in threes: three adjectives, three bullets, three short sentences in a row.
- Moral-of-the-story endings: "Remember: ...", "And that's okay.", "Let that sink in."
- Empty hedges: "It's important to note that", "Ultimately,".

**Formatting**: em dashes everywhere (one per post at most), emoji bullets (✅ 🚀 👉 💡), unicode bold/italic letters, a single sentence per line for the whole post ("broetry"), a wall of five hashtags.

**Closers**: "Agree?", "Thoughts?", "What would you add?", "Comment YES and I'll send it", "♻️ Repost to help your network", "Follow me for more", "Let's connect!". One-word questions get one-word comments. "Comment X to get Y" is engagement bait that LinkedIn demotes.

### Before → after

> In today's fast-paced world, leveraging data is a game-changer for marketers. It's not about having more data — it's about using it wisely. The result? Unprecedented growth. 🚀

> Last quarter we deleted 31 of our 40 dashboards. Nobody noticed for six weeks. The 9 we kept are the only ones that ever changed a decision. Here's how we chose them.

The second version is specific (31 of 40, six weeks, 9), has tension (nobody noticed), and makes a promise the post has to keep.

> I'm thrilled to announce that I've joined Acme as Head of Growth! I'm humbled by this opportunity and excited for the journey ahead.

> New job: I'm running growth at Acme. They sell payroll software to restaurants, and their best channel today is a Facebook group with 9,000 restaurant owners. I'll share what I learn about growing a community-led B2B product in public.

## 4. Craft

- **One post, one idea.** If you can't say the point in one sentence, the post isn't ready.
- **Specific beats general.** Numbers, names, places, timestamps, dialogue, the actual email or screenshot. "We lost a client" < "We lost a $40k client because of one sentence in our proposal."
- **Earn every claim.** A claim is followed by proof: an example, a number, a story, or reasoning the reader can check.
- **Tension.** Something at stake, a mistake, a surprise, a gap between what people expect and what happened. Without tension there's no reason to read line 3.
- **Insight density.** Every sentence should teach, prove, or move the story forward. Cut the rest. Most first drafts lose 20-30% in editing.
- **Write to one reader.** Picture one specific person from the target audience (from the brief) and write to them.
- **Show earned opinions.** Take a position the user can defend from experience. Contrarian for its own sake reads as rage-bait.
- **Pay off the hook.** The body must deliver what the first line promised, early. Bait-and-switch hooks hurt dwell time and trust.

## 5. Formatting for the feed

- **Line 1** is the hook. Shorter is better (first lines under ~40 characters had the highest engagement in a 309k-post study), and under ~80 lets line 2 also show above "...see more" on mobile (~140 characters). Line 2 gives the reason to click.
- **Paragraphs** of 1-3 short lines with a blank line between. Group related sentences; don't make every sentence its own paragraph.
- **Lists**: numbers or plain dashes, 3-7 items, each item a complete thought.
- **Emoji**: 0-3 per post, only where they add meaning. Match the user's voice profile.
- **Hashtags**: 0-3 at the end. They do little for reach now.
- **Links**: a body link likely costs modest reach (see `algorithm.md` §6). If the post exists to get clicks, keep the link in the post and accept that. Otherwise leave it out and point to Featured or the newsletter. "Link in the first comment" is unproven and loses clicks, so don't present it as a trick.
- **Tags**: only people who are actually in the post and likely to engage.
- **Ending**: a specific question that invites stories or opinions ("What's one thing clients keep asking you in week one?"), a clear takeaway, or a natural stop. Ending questions barely move engagement, so not every post needs one. Occasional clear offers are fine; promotional posts perform well when they're useful.
- **Length**: let the idea set the length. For text posts, 900-1,800 characters is the default range (data favors ~1,200-1,500); captions for images and carousels can be shorter (800-1,000). Under ~400 characters tends to underperform unless it's a sharp one-liner.

## 6. Comments and DMs

**Comments on other people's posts** are one of the highest-leverage growth actions (see `content-playbook.md`). Good comments:
- add a specific example, data point, counterpoint, or follow-up question;
- are 2-5 sentences, written like a person talking;
- never pitch, never say "Great post!", never paste generic AI summaries of the post.

**DMs**: short, specific, about them first, with one clear ask. No pitch in the first message to a stranger.

## 7. Editing checklist

Before showing a draft to the user:
1. Does line 1 make the target reader want line 2?
2. Is every claim backed by something specific?
3. Cut 20%. Then replace remaining abstractions with specifics.
4. Read it aloud in the user's voice. Anything they'd never say out loud gets cut.
5. Run `python scripts/check.py post <file>` and fix every ERROR and WARN, or explain why one is intentional.
6. List any `[PLACEHOLDERS]` the user must fill.
