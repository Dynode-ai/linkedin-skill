#!/usr/bin/env python3
"""LinkedIn copy checker: posts and profile fields. Standard library only.

Usage:
  python check.py post   <file|->              [--json]
  python check.py field  <field> <file|->     [--json]
  python check.py field  <field> --text "..." [--json]

Fields: headline, about, title, experience, post, comment, article-title,
        newsletter-name, newsletter-description, skill, custom-url

Exit code is always 0 so the caller can read the report; parse --json for scores.
"""
import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# Platform numbers. Keep in sync with references/profile-playbook.md.
# Folds are approximations: LinkedIn truncates by rendered lines, not a fixed
# character count, so we simulate lines at a typical width.
# ---------------------------------------------------------------------------
LIMITS = {
    "headline": 220,
    "about": 2600,
    "title": 100,
    "experience": 2000,
    "post": 3000,
    "comment": 1250,
    "article-title": 150,
    "newsletter-name": 30,
    "newsletter-description": 120,
    "skill": 80,
    "custom-url": 100,
}
FOLDS = {  # name: (chars per rendered line, lines shown before "...see more")
    "mobile": (46, 3),
    "desktop": (70, 3),
}
ABOUT_FOLD_CHARS = 265  # About section preview before "see more" (approx.)

# ---------------------------------------------------------------------------
# Pattern library. (regex, message, severity). Severity: error | warn | info
# ---------------------------------------------------------------------------
AI_TELLS = [
    (r"\bdelve[sd]?\b|\bdelving\b", "\"delve\" is the #1 AI tell", "warn"),
    (r"\btapestry\b", "\"tapestry\" reads as AI-written", "warn"),
    (r"\btestament to\b", "\"a testament to\" is an AI cliché", "warn"),
    (r"\b(ever[- ]evolving|fast[- ]paced) (world|landscape|industry)\b", "generic scene-setting; start with something specific", "warn"),
    (r"\bin today'?s\b[^.\n]{0,40}\b(world|landscape|age|era|market)\b", "\"In today's ... world\" opener is filler", "warn"),
    (r"\b(navigate|navigating) the (complexities|landscape|world)\b", "\"navigate the complexities\" is filler", "warn"),
    (r"\bgame[- ]?changer\b|\bgame[- ]?changing\b", "\"game-changer\": say what actually changed", "warn"),
    (r"\b(unlock|unleash|elevate|supercharge|turbocharge)\b", "hype verb; use a plain, concrete verb", "warn"),
    (r"\bleverag(e|es|ed|ing)\b", "\"leverage\": try \"use\"", "info"),
    (r"\b(seamless(ly)?|robust|cutting[- ]edge|state[- ]of[- ]the[- ]art|revolutioni[sz]e|paradigm shift|synerg(y|ies))\b", "corporate buzzword", "warn"),
    (r"\b(holistic|pivotal|transformative|invaluable|myriad|plethora|meticulous(ly)?|bustling|realm)\b", "AI-flavored vocabulary", "info"),
    (r"\b(let that sink in|read that again|here'?s the kicker|here'?s the thing|plot twist|buckle up)\b", "overused LinkedIn-ism", "warn"),
    (r"\b(deep dive|dive (in|into))\b", "\"dive in\" is filler", "info"),
    (r"\b(i'?m|we'?re) (so )?(thrilled|excited|humbled|honou?red|delighted) to\b", "announcement cliché; lead with the news itself", "warn"),
    (r"\bit'?s important to (note|remember)\b|\bin conclusion\b|\bultimately,", "essay filler", "info"),
    (r"\b(imagine this|picture this|in a world where)\b", "movie-trailer opener", "warn"),
    (r"\bstop scrolling\b", "\"stop scrolling\" is a worn-out hook", "warn"),
    (r"\b(the (secret|result|best part|answer|truth|catch|twist))\?", "colon/question reveal (\"The result?\") is a formula tell", "warn"),
    (r"\bno (fluff|filler|bs)\b", "\"no fluff\" is itself fluff", "info"),
    (r"\bjourney\b", "\"journey\" as metaphor is overused", "info"),
    (r"\b(resonate[sd]?|foster(s|ed|ing)?|empower(s|ed|ing)?|harness(es|ed|ing)?|embark(s|ed|ing)?)\b", "AI-flavored verb", "info"),
]

BAIT = [
    (r"\b(comment|type|drop|reply)\b[^.\n]{0,25}\b(yes|below|\"[^\"]+\"|'[^']+'|[A-Z]{3,})\b[^.\n]{0,40}\b(and|to|i'?ll|get|receive|send)\b", "\"comment X to get Y\" is engagement bait LinkedIn demotes", "warn"),
    (r"\blike (this|if)\b|\bsmash (that|the) like\b", "asking for likes is engagement bait", "warn"),
    (r"\btag (someone|a friend|3|three|a colleague)\b", "\"tag someone\" is engagement bait", "warn"),
    (r"\brepost (if|to help)\b|\bshare (if|this with)\b", "\"repost if...\" formula; earn shares with substance", "info"),
    (r"(^|\n)\s*(agree|thoughts|right|yes or no)\s*\?+\s*$", "one-word question CTA invites one-word comments; ask something specific", "warn"),
]

STRUCTURE = [
    (r"\b(it'?s|this is|that'?s) not (just )?(about )?[^.\n]{1,40}[.,;—-]+\s*(it'?s|this is|that'?s)\b", "\"It's not X, it's Y\" antithesis (AI formula)", "warn"),
    (r"\bisn'?t (just )?(about )?[^.\n]{1,40}\.\s*it'?s\b", "\"isn't X. It's Y.\" antithesis (AI formula)", "warn"),
    (r"(^|\n|\. )no [a-z]+\.\s+no [a-z]+\.\s+(just|only) ", "staccato triplet (\"No X. No Y. Just Z.\")", "warn"),
    (r"(^|\n)\s*(have you ever|ever wonder(ed)?|did you know|what if i told you)\b", "rhetorical-question hook; open with a claim or a moment instead", "warn"),
]

URL_RE = re.compile(r"(https?://|www\.)\S+|\b[a-z0-9-]+\.(com|io|ai|co|org|net|dev|app)(/\S*)?\b", re.I)
HASHTAG_RE = re.compile(r"(?<![\w&])#[A-Za-z][\w]*")
MENTION_RE = re.compile(r"(?<!\w)@[A-Za-z][\w.-]+")
# Any [bracketed gap] (but not a Markdown [link](url)), TK, {{var}} or XX% the user still has to fill.
PLACEHOLDER_RE = re.compile(r"\[[^\[\]\n]{2,160}\](?!\()|\bTK\b|\{\{.*?\}\}|\bX{2,}%?(?![A-Za-z])")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐⬆↔-⇿✅❌✔]")
MATH_ALNUM_RE = re.compile("[\U0001D400-\U0001D7FF]")  # unicode "bold/italic" fonts
EMDASH_RE = re.compile("—")


def read_input(path, text):
    if text is not None:
        return text
    if path in (None, "-"):
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def strip_frontmatter(s):
    """Allow drafts saved as Markdown with a YAML header or '# Title' line."""
    s = s.replace("\r\n", "\n")
    if s.startswith("---\n"):
        end = s.find("\n---", 4)
        if end != -1:
            s = s[end + 4:].lstrip("\n")
    return s.strip("\n")


def nchars(s):
    return len(s)  # code points; LinkedIn's counter is close to this for most text


def fold(text, width, lines):
    """Return the text visible before '...see more' by simulating wrapped lines."""
    out, used = [], 0
    for para in text.split("\n"):
        if used >= lines:
            break
        if para.strip() == "":
            out.append("")
            used += 1
            continue
        words, cur, wrapped = para.split(" "), "", []
        for w in words:
            cand = (cur + " " + w).strip() if cur else w
            if len(cand) <= width:
                cur = cand
            else:
                if cur:
                    wrapped.append(cur)
                while len(w) > width:
                    wrapped.append(w[:width])
                    w = w[width:]
                cur = w
        if cur:
            wrapped.append(cur)
        for wl in wrapped:
            if used >= lines:
                break
            out.append(wl)
            used += 1
    while out and out[-1] == "":
        out.pop()
    return out


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if re.search(r"[A-Za-z]", p or "")]


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def fk_grade(text):
    sents = sentences(text)
    words = re.findall(r"[A-Za-z']+", text)
    if not sents or not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return round(0.39 * len(words) / len(sents) + 11.8 * syl / len(words) - 15.59, 1)


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def scan(patterns, text, issues, label):
    for rx, msg, sev in patterns:
        for m in re.finditer(rx, text, re.I | re.M):
            frag = m.group(0).strip()
            lead = len(m.group(0)) - len(m.group(0).lstrip(" \t\n.")) if frag else 0
            issues.append({"severity": sev, "rule": label, "line": line_of(text, m.start() + lead),
                           "match": frag[:60], "message": msg})


def check_post(raw):
    text = strip_frontmatter(raw)
    issues = []
    n = nchars(text)
    words = re.findall(r"\S+", text)
    paras = [p for p in re.split(r"\n\s*\n|\n", text) if p.strip()]
    first_line = next((l for l in text.split("\n") if l.strip()), "")

    # Length
    if n > LIMITS["post"]:
        issues.append({"severity": "error", "rule": "length", "line": None, "match": "",
                       "message": f"{n} chars exceeds LinkedIn's {LIMITS['post']} limit"})
    elif n < 400:
        issues.append({"severity": "info", "rule": "length", "line": None, "match": "",
                       "message": "under 400 chars tends to underperform for text posts; fine for a sharp one-liner or an image/carousel caption"})
    elif n > 2600:
        issues.append({"severity": "info", "rule": "length", "line": None, "match": "",
                       "message": "very long post; data favors ~1,200-1,500 chars for text. Every paragraph must earn its place (dwell time)"})

    # Hook
    if len(first_line) > 110:
        issues.append({"severity": "warn", "rule": "hook", "line": 1, "match": first_line[:60],
                       "message": f"first line is {len(first_line)} chars; short first lines (<40 chars) get the most engagement, and under ~80 lets line 2 show above the mobile fold"})
    elif len(first_line) > 80:
        issues.append({"severity": "info", "rule": "hook", "line": 1, "match": first_line[:60],
                       "message": f"first line is {len(first_line)} chars; consider tightening (short first lines win)"})
    if re.match(r"\s*(hi|hello|hey)\b", first_line, re.I):
        issues.append({"severity": "warn", "rule": "hook", "line": 1, "match": first_line[:40],
                       "message": "greeting as first line wastes the hook"})

    scan(AI_TELLS, text, issues, "ai-tell")
    scan(BAIT, text, issues, "engagement-bait")
    scan(STRUCTURE, text, issues, "formula")

    # Em dashes
    ed = len(EMDASH_RE.findall(text))
    if ed >= 3:
        issues.append({"severity": "warn", "rule": "em-dash", "line": None, "match": f"{ed}x —",
                       "message": f"{ed} em dashes; heavy em-dash use is now read as an AI tell. Use periods, commas or parentheses"})
    elif ed == 2:
        issues.append({"severity": "info", "rule": "em-dash", "line": None, "match": "2x —",
                       "message": "2 em dashes; consider swapping one for a period"})

    # Links
    links = list(URL_RE.finditer(text))
    if links:
        issues.append({"severity": "warn", "rule": "link", "line": line_of(text, links[0].start()), "match": links[0].group(0)[:50],
                       "message": "body link likely costs modest reach (studies: -19% to -36%). Keep it only if clicks are the goal; otherwise point to Featured"})

    # Hashtags
    tags = HASHTAG_RE.findall(text)
    if len(tags) > 3:
        issues.append({"severity": "warn", "rule": "hashtags", "line": None, "match": " ".join(tags[:6]),
                       "message": f"{len(tags)} hashtags; they barely affect reach now. Use 0-3, at the end"})
    body_wo_last = "\n".join(text.split("\n")[:-1])
    if tags and HASHTAG_RE.search(body_wo_last) and len(tags) >= 2:
        issues.append({"severity": "info", "rule": "hashtags", "line": None, "match": "",
                       "message": "hashtags inside sentences hurt readability; move them to the end or drop them"})

    # Mentions
    ments = MENTION_RE.findall(text)
    if len(ments) > 5:
        issues.append({"severity": "warn", "rule": "mentions", "line": None, "match": " ".join(ments[:6]),
                       "message": f"{len(ments)} tags; tagging people who won't engage looks spammy and can hurt reach. Tag only those who'll genuinely reply"})

    # Emoji
    emo = EMOJI_RE.findall(text)
    if len(emo) > 6:
        issues.append({"severity": "warn", "rule": "emoji", "line": None, "match": "".join(emo[:8]),
                       "message": f"{len(emo)} emoji; heavy emoji reads as template content"})
    bullet_emoji_lines = sum(1 for l in text.split("\n") if EMOJI_RE.match(l.strip() or " "))
    if bullet_emoji_lines >= 4:
        issues.append({"severity": "info", "rule": "emoji", "line": None, "match": "",
                       "message": f"{bullet_emoji_lines} lines start with an emoji; emoji bullets (✅ 🚀 👉) are a template tell. Plain dashes or numbers read as more human"})

    # Fake bold/italic unicode
    if MATH_ALNUM_RE.search(text):
        issues.append({"severity": "warn", "rule": "unicode-font", "line": None, "match": "",
                       "message": "unicode 'bold/italic' letters are unreadable to screen readers and invisible to search; use plain text"})

    # Placeholders the user still has to fill
    for m in PLACEHOLDER_RE.finditer(text):
        issues.append({"severity": "error", "rule": "placeholder", "line": line_of(text, m.start()), "match": m.group(0),
                       "message": "unfilled placeholder; replace with a real detail before posting"})

    # Walls of text
    for p in paras:
        if len(p) > 320:
            issues.append({"severity": "warn", "rule": "wall-of-text", "line": line_of(text, text.find(p[:30])), "match": p[:50],
                           "message": f"{len(p)}-char paragraph; break it up (2-3 short lines per paragraph read best on mobile)"})

    # Sentence length / readability
    sents = sentences(text)
    if sents:
        avg = sum(len(s.split()) for s in sents) / len(sents)
        long_ones = [s for s in sents if len(s.split()) > 32]
        if avg > 22:
            issues.append({"severity": "warn", "rule": "readability", "line": None, "match": "",
                           "message": f"average sentence is {avg:.0f} words; aim for under ~18"})
        for s in long_ones[:2]:
            issues.append({"severity": "info", "rule": "readability", "line": line_of(text, text.find(s[:25])), "match": s[:50],
                           "message": f"{len(s.split())}-word sentence; split it"})
    grade = fk_grade(text)
    if grade > 11:
        issues.append({"severity": "info", "rule": "readability", "line": None, "match": "",
                       "message": f"reading grade ~{grade}; simpler words travel further (aim for 6-9)"})

    # Specificity: numbers and named things are what make a post credible and "only you"
    numbers = re.findall(r"(?<![\w#])[$€£]?\d[\d,.]*\s?(%|k|m|x|hrs?|days?|weeks?|months?|years?)?", text, re.I)
    caps = 0
    for s in sentences(text):
        toks = re.findall(r"[A-Za-z][\w'’-]*", s)
        caps += sum(1 for t in toks[1:] if t[0].isupper() and t.lower() not in ("i", "i'm", "i've", "i'd", "i'll"))
    specifics = len(numbers) + caps
    if n >= 400 and specifics == 0:
        issues.append({"severity": "warn", "rule": "specificity", "line": None, "match": "",
                       "message": "no numbers or named things (tools, companies, places, people); add one real detail so it couldn't be anyone's post"})
    elif n >= 600 and not numbers:
        issues.append({"severity": "info", "rule": "specificity", "line": None, "match": "",
                       "message": "no numbers; a concrete figure (time, money, count, before/after) usually makes the point land"})

    # Broetry
    one_liners = sum(1 for p in paras if len(sentences(p)) <= 1)
    if len(paras) >= 14 and one_liners / max(1, len(paras)) > 0.85:
        issues.append({"severity": "info", "rule": "formatting", "line": None, "match": "",
                       "message": "almost every line is a standalone sentence ('broetry'); group related lines so it reads like a person talking"})

    # Score
    penalty = {"error": 15, "warn": 5, "info": 1}
    seen = {}
    score = 100
    for i in issues:
        key = (i["rule"], i["message"])
        seen[key] = seen.get(key, 0) + 1
        if seen[key] <= 2:  # don't let one repeated pattern sink the score
            score -= penalty[i["severity"]]
    score = max(0, score)
    if any(i["rule"] == "specificity" and i["severity"] == "warn" for i in issues):
        score = min(score, 70)  # clean but generic copy is not ready: it's the "could be anyone's post" failure
    verdict ="Ready to post" if score >= 85 and not any(i["severity"] == "error" for i in issues) else \
              "Almost there" if score >= 70 else "Needs another pass"

    return {
        "kind": "post",
        "chars": n,
        "limit": LIMITS["post"],
        "words": len(words),
        "paragraphs": len(paras),
        "reading_grade": grade,
        "hashtags": len(tags),
        "links": len(links),
        "specifics": specifics,
        "score": score,
        "verdict": verdict,
        "above_fold": {k: fold(text, w, l) for k, (w, l) in FOLDS.items()},
        "issues": sorted(issues, key=lambda i: ({"error": 0, "warn": 1, "info": 2}[i["severity"]], i["line"] or 0)),
    }


def check_field(field, raw):
    field = field.lower()
    if field not in LIMITS:
        raise SystemExit(f"unknown field '{field}'. Options: {', '.join(LIMITS)}")
    text = raw.replace("\r\n", "\n").strip("\n")
    if field in ("headline", "title", "skill", "custom-url", "newsletter-name", "article-title"):
        text = text.strip()
    n = nchars(text)
    lim = LIMITS[field]
    issues = []
    if n > lim:
        issues.append({"severity": "error", "rule": "length", "message": f"{n}/{lim}: cut {n - lim} characters"})
    if field == "headline":
        if "\n" in text:
            issues.append({"severity": "error", "rule": "format", "message": "headlines can't contain line breaks"})
        if n < 60:
            issues.append({"severity": "warn", "rule": "length", "message": "short headline; you're leaving searchable space unused"})
        if re.fullmatch(r"[^|]{0,60}\bat\b[^|]{0,60}", text, re.I) and n < 70:
            issues.append({"severity": "warn", "rule": "content", "message": "looks like 'Title at Company' (LinkedIn's default); add who you help / what you're known for"})
        if MATH_ALNUM_RE.search(text) or len(EMOJI_RE.findall(text)) > 2:
            issues.append({"severity": "warn", "rule": "format", "message": "fancy fonts/emoji in a headline hurt search matching"})
    if field == "custom-url":
        if not re.fullmatch(r"[a-z0-9-]{3,100}", text.lower()):
            issues.append({"severity": "error", "rule": "format", "message": "custom URL: 3-100 letters, numbers or hyphens; no spaces or symbols"})
    if field == "about":
        scan(AI_TELLS, text, issues, "ai-tell")
        for i in issues:
            i.pop("match", None)
            i.pop("line", None)
    out = {"kind": "field", "field": field, "chars": n, "limit": lim, "remaining": lim - n, "issues": issues}
    if field == "about":
        out["above_fold"] = text[:ABOUT_FOLD_CHARS]
    return out


def render(res):
    lines = []
    if res["kind"] == "post":
        lines.append(f"LinkedIn post check: {res['chars']}/{res['limit']} chars · {res['words']} words · "
                     f"{res['paragraphs']} paragraphs · grade {res['reading_grade']}")
        lines.append(f"Score {res['score']}/100 · {res['verdict']}")
        lines.append("")
        for k, v in res["above_fold"].items():
            lines.append(f"Before \"...see more\" on {k} (approx.):")
            for l in v:
                lines.append(f"  | {l}")
            lines.append("")
    else:
        lines.append(f"{res['field']}: {res['chars']}/{res['limit']} chars ({res['remaining']} left)")
        if res.get("above_fold"):
            lines.append("Visible before \"see more\" (approx.):")
            lines.append("  | " + res["above_fold"].replace("\n", "\n  | "))
        lines.append("")
    if not res["issues"]:
        lines.append("No issues found.")
    icon = {"error": "ERROR", "warn": "WARN ", "info": "info "}
    for i in res["issues"]:
        loc = f"L{i['line']}: " if i.get("line") else ""
        m = f" [{i['match']}]" if i.get("match") else ""
        lines.append(f"  {icon[i['severity']]} {loc}{i['message']}{m}")
    return "\n".join(lines)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Check LinkedIn posts and profile fields.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("post")
    p.add_argument("path", nargs="?", default="-")
    p.add_argument("--text")
    p.add_argument("--json", action="store_true")
    f = sub.add_parser("field")
    f.add_argument("field")
    f.add_argument("path", nargs="?", default="-")
    f.add_argument("--text")
    f.add_argument("--json", action="store_true")
    a = ap.parse_args()
    raw = read_input(a.path, a.text)
    res = check_post(raw) if a.cmd == "post" else check_field(a.field, raw)
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else render(res))


if __name__ == "__main__":
    main()
