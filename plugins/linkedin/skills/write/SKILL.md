---
name: write
description: Write or fix a LinkedIn post, carousel or comment in your own voice. Includes hook options, an anti-AI-slop check and a feed preview.
argument-hint: "[topic, idea number, draft to fix, 'carousel', 'comment', or 'interview']"
disable-model-invocation: true
---

Run the LinkedIn **writing** workflow.

1. Read `${CLAUDE_SKILL_DIR}/../linkedin/SKILL.md` and follow its rules. In that file, SKILL_DIR means `${CLAUDE_SKILL_DIR}/../linkedin`, and "Request" means the user input below.
2. Then read `${CLAUDE_SKILL_DIR}/../linkedin/workflows/write.md` and follow it step by step.

User input: $ARGUMENTS
