#!/usr/bin/env python3
"""Parse LinkedIn's own exports into personal benchmarks. Standard library only.

Inputs: the "Download your data" archive (.zip or unzipped folder or single CSVs)
and analytics exports (.xlsx aggregate "AggregateAnalytics_*.xlsx" or per-post).

Subcommands
  build <inputs...> --out DIR        Parse everything; write posts.json, analytics.json,
                                     profile_archive.md, network.md, voice.json into DIR.
  list DIR [--sort impressions|date|engagements] [--limit N] [--chars N]
                                     Compact post listing (for tagging topics/hooks).
  stats DIR [--tags tags.json]       Personal benchmarks: medians and lift by group.
  voice DIR|Shares.csv [--draft F]   Voice fingerprint; with --draft, compare a draft to it.
  dashboard DIR --out REPORT_DIR     Write the analytics dashboard (index.html + data.js).
  postdate <post-url-or-id>          When was a LinkedIn post published (decoded from its ID).
  inspect <path>                     Show what files/sheets/headers were found (debugging).

LinkedIn changes export formats without notice. Everything here matches columns
loosely and reports what it couldn't read instead of failing.
"""
import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import shutil
import statistics
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def norm(s):
    """Normalize a header or file name: lowercase alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def file_key(name):
    base = os.path.splitext(os.path.basename(name))[0]
    return re.sub(r"\d+$", "", norm(base))


def to_num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip().replace(" ", "").replace(" ", "")
    if not s:
        return None
    s = s.replace("%", "")
    if re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", s):
        s = s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", s):
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d+,\d+", s):
        s = s.replace(",", ".")
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def out(s=""):
    print(s)


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def excel_serial(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if 20000 < f < 80000:
        return dt.datetime(1899, 12, 30) + dt.timedelta(days=f)
    return None


def infer_dayfirst(values):
    """Look at a column of x/y/z dates and decide if the first number is the day."""
    dayfirst = monthfirst = False
    for v in values:
        m = re.match(r"\s*(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", str(v or ""))
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > 12:
                dayfirst = True
            if b > 12:
                monthfirst = True
    if dayfirst and not monthfirst:
        return True
    return False  # default US order; ambiguous columns are reported by the caller


def parse_date(v, dayfirst=False):
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v
    if isinstance(v, (int, float)):
        return excel_serial(v)
    s = str(v).strip()
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?)?", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        h, mi, se = int(m.group(4) or 0), int(m.group(5) or 0), int(m.group(6) or 0)
        try:
            return dt.datetime(y, mo, d, h, mi, se)
        except ValueError:
            return None
    m = re.match(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})(?:,?\s+(\d{1,2}):(\d{2}))?", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        d, mo = (a, b) if dayfirst else (b, a)
        if mo > 12:
            d, mo = mo, d
        try:
            return dt.datetime(y, mo, d, int(m.group(4) or 0), int(m.group(5) or 0))
        except ValueError:
            return None
    m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?,?\s+(\d{4})", s)  # 23 Apr 2026
    if m and m.group(2).lower() in MONTHS:
        return dt.datetime(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    m = re.match(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})", s)  # Apr 23, 2026
    if m and m.group(1).lower() in MONTHS:
        return dt.datetime(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    return excel_serial(s)


# ---------------------------------------------------------------------------
# LinkedIn post IDs: the top bits of activity IDs encode the post time (ms)
# ---------------------------------------------------------------------------
ID_RE = re.compile(r"(?:activity|share|ugcPost)(?::|%3A|-)(\d{15,20})", re.I)


def extract_id(url):
    if not url:
        return None, None
    s = str(url)
    m = ID_RE.search(s)
    if m:
        kind = re.search(r"(activity|share|ugcPost)", m.group(0), re.I).group(1).lower()
        return m.group(1), kind
    m = re.search(r"\b(\d{18,20})\b", s)
    return (m.group(1), None) if m else (None, None)


def id_time(pid):
    try:
        ms = int(pid) >> 22
    except (TypeError, ValueError):
        return None
    if not (1262304000000 < ms < 4102444800000):  # 2010..2100
        return None
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Reading files from zips, folders and plain paths
# ---------------------------------------------------------------------------
class Source:
    def __init__(self, name, loader):
        self.name = name
        self.key = file_key(name)
        self._loader = loader

    def read(self):
        return self._loader()


def collect_sources(paths):
    sources = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    full = os.path.join(root, f)
                    if full.lower().endswith((".csv", ".xlsx")):
                        sources.append(Source(full, (lambda fp=full: open(fp, "rb").read())))
        elif p.lower().endswith(".zip"):
            z = zipfile.ZipFile(p)
            for n in z.namelist():
                if n.lower().endswith((".csv", ".xlsx")) and not n.startswith("__MACOSX"):
                    sources.append(Source(n, (lambda zz=z, nn=n: zz.read(nn))))
        elif os.path.isfile(p):
            sources.append(Source(p, (lambda fp=p: open(fp, "rb").read())))
        else:
            print(f"warning: not found: {p}", file=sys.stderr)
    return sources


def decode(b):
    for enc in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", "replace")


def read_csv(b, expect=()):
    """Return (header, rows as dicts keyed by normalized header). Skips note lines above the header."""
    text = decode(b)
    rows = list(csv.reader(io.StringIO(text)))
    expect = [norm(e) for e in expect]
    hdr_i = None
    for i, r in enumerate(rows[:15]):
        cells = [norm(c) for c in r]
        if expect and any(e in cells for e in expect):
            hdr_i = i
            break
    if hdr_i is None:
        hdr_i = next((i for i, r in enumerate(rows[:15]) if len([c for c in r if c.strip()]) >= 2), 0)
    if not rows:
        return [], []
    header = rows[hdr_i]
    keys = [norm(h) for h in header]
    data = []
    for r in rows[hdr_i + 1:]:
        if not any((c or "").strip() for c in r):
            continue
        d = {}
        for k, v in zip(keys, r):
            if k and k not in d:
                d[k] = v
        data.append(d)
    return header, data


def pick(row, *names):
    for n in names:
        v = row.get(norm(n))
        if v not in (None, ""):
            return v
    return ""


# ---------------------------------------------------------------------------
# Minimal XLSX reader (zip of XML)
# ---------------------------------------------------------------------------
def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _col_index(ref):
    letters = re.match(r"([A-Z]+)", ref or "")
    if not letters:
        return None
    n = 0
    for ch in letters.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx(b):
    z = zipfile.ZipFile(io.BytesIO(b))
    names = set(z.namelist())
    shared = []
    if "xl/sharedStrings.xml" in names:
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            if _local(si.tag) == "si":
                shared.append("".join(t.text or "" for t in si.iter() if _local(t.tag) == "t"))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    relmap = {}
    if "xl/_rels/workbook.xml.rels" in names:
        for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")):
            relmap[r.get("Id")] = r.get("Target")
    sheets = []
    for el in wb.iter():
        if _local(el.tag) != "sheet":
            continue
        rid = next((v for k, v in el.attrib.items() if _local(k) == "id"), None)
        target = relmap.get(rid, "")
        path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        path = os.path.normpath(path).replace("\\", "/")
        if path not in names:
            continue
        sheets.append({"name": el.get("name"), "rows": _read_sheet(z.read(path), shared)})
    return sheets


def _read_sheet(xml, shared):
    rows = []
    root = ET.fromstring(xml)
    for row in root.iter():
        if _local(row.tag) != "row":
            continue
        vals = {}
        nxt = 0
        for c in row:
            if _local(c.tag) != "c":
                continue
            ci = _col_index(c.get("r"))
            ci = nxt if ci is None else ci
            nxt = ci + 1
            t = c.get("t")
            v = None
            vnode = next((x for x in c if _local(x.tag) == "v"), None)
            if t == "s" and vnode is not None:
                try:
                    v = shared[int(vnode.text)]
                except (ValueError, IndexError):
                    v = vnode.text
            elif t == "inlineStr":
                v = "".join(x.text or "" for x in c.iter() if _local(x.tag) == "t")
            elif t == "b" and vnode is not None:
                v = vnode.text == "1"
            elif vnode is not None:
                v = vnode.text
                if t not in ("str", "e"):
                    n = to_num(v)
                    v = n if n is not None else v
            vals[ci] = v
        if vals:
            width = max(vals) + 1
            rows.append([vals.get(i) for i in range(width)])
        else:
            rows.append([])
    return rows


# ---------------------------------------------------------------------------
# Analytics workbook interpretation
# ---------------------------------------------------------------------------
METRIC_ALIASES = {
    "impressions": ["impressions"],
    "members_reached": ["membersreached", "uniqueimpressions", "reach"],
    "engagements": ["engagements", "engagement"],
    "reactions": ["reactions", "likes"],
    "comments": ["comments"],
    "reposts": ["reposts", "shares", "reshares"],
    "saves": ["saves"],
    "sends": ["sends", "sendsonlinkedin"],
    "profile_views": ["profileviewersfromthispost", "profileviews", "profileviewers"],
    "followers_gained": ["followersgainedfromthispost", "followersgained", "newfollowers"],
    "clicks": ["linkclicks", "clicks"],
}


def metric_name(label):
    n = norm(label)
    for k, al in METRIC_ALIASES.items():
        if n in al:
            return k
    for k, al in METRIC_ALIASES.items():
        if any(n.startswith(a) for a in al):
            return k
    return None


def classify_sheet(rows):
    flat = " ".join(norm(c) for r in rows[:12] for c in r if isinstance(c, str))
    has_urls = any(isinstance(c, str) and "linkedin.com" in c for r in rows[:80] for c in r)
    if has_urls and ("url" in flat or "post" in flat):
        return "top_posts"
    if "totalfollowers" in flat or ("followers" in flat and "new" in flat):
        return "followers"
    pct_like = sum(1 for r in rows[:40] if len(r) >= 3 and (isinstance(r[2], (int, float)) or (isinstance(r[2], str) and "%" in r[2])))
    if pct_like >= 5 and not any(parse_date(r[0]) for r in rows[1:10] if r):
        return "demographics"
    if "membersreached" in flat or ("impressions" in flat and len(rows) <= 6):
        return "discovery"
    dated = sum(1 for r in rows[:30] if r and parse_date(r[0]) and len(r) >= 2)
    if dated >= 3:
        return "engagement"
    if any(metric_name(r[0]) for r in rows[:40] if r and isinstance(r[0], str)):
        return "post_metrics"
    return "unknown"


def parse_analytics_workbook(sheets, src):
    res = {"source": src, "discovery": {}, "daily": [], "top_posts": {}, "followers": {}, "demographics": defaultdict(list),
           "post_metrics": {}, "notes": [], "sheets": []}
    for sh in sheets:
        rows = sh["rows"]
        kind = classify_sheet(rows)
        res["sheets"].append(f"{sh['name']}: {kind}")
        if kind == "discovery":
            for r in rows:
                if len(r) >= 2 and isinstance(r[0], str):
                    m = metric_name(r[0])
                    if m and to_num(r[1]) is not None:
                        res["discovery"][m] = to_num(r[1])
                    elif not res["discovery"].get("period") and r[1] and isinstance(r[1], str) and re.search(r"\d", r[1]):
                        res["discovery"]["period"] = r[1]
            if rows and rows[0] and isinstance(rows[0][0], str) and not res["discovery"].get("period"):
                res["discovery"]["period"] = " ".join(str(c) for c in rows[0] if c)
        elif kind == "engagement":
            hdr = next((r for r in rows if r and any(isinstance(c, str) and metric_name(c) for c in r)), None)
            names = [metric_name(c) if isinstance(c, str) else None for c in (hdr or [])]
            dayfirst = infer_dayfirst([r[0] for r in rows if r])
            for r in rows:
                d = parse_date(r[0], dayfirst) if r else None
                if not d:
                    continue
                item = {"date": d.date().isoformat()}
                for i, v in enumerate(r[1:], 1):
                    k = names[i] if i < len(names) and names[i] else ("impressions" if i == 1 else "engagements" if i == 2 else f"col{i}")
                    item[k] = to_num(v)
                res["daily"].append(item)
        elif kind == "top_posts":
            hdr_i = next((i for i, r in enumerate(rows) if any(isinstance(c, str) and norm(c) in ("posturl", "url") for c in r)), None)
            if hdr_i is None:
                res["notes"].append(f"{sh['name']}: no 'Post URL' header found")
                continue
            hdr = rows[hdr_i]
            url_cols = [i for i, c in enumerate(hdr) if isinstance(c, str) and "url" in norm(c)]
            dayfirst = infer_dayfirst([r[i + 1] for r in rows[hdr_i + 1:] for i in url_cols if len(r) > i + 1])
            for ucol in url_cols:
                mcol = ucol + 2
                mname = metric_name(hdr[mcol]) if len(hdr) > mcol and isinstance(hdr[mcol], str) else None
                mname = mname or ("engagements" if ucol == url_cols[0] and len(url_cols) > 1 else "impressions")
                for r in rows[hdr_i + 1:]:
                    if len(r) <= ucol or not isinstance(r[ucol], str) or "linkedin" not in r[ucol]:
                        continue
                    url = r[ucol].strip()
                    p = res["top_posts"].setdefault(url, {"url": url})
                    d = parse_date(r[ucol + 1], dayfirst) if len(r) > ucol + 1 else None
                    if d:
                        p["date"] = d.date().isoformat()
                    if len(r) > mcol:
                        p[mname] = to_num(r[mcol])
        elif kind == "followers":
            dayfirst = infer_dayfirst([r[0] for r in rows if r])
            for r in rows:
                if not r:
                    continue
                if isinstance(r[0], str) and "total" in norm(r[0]) and "follower" in norm(r[0]):
                    tot = to_num(r[1]) if len(r) > 1 else None
                    if tot is None:
                        mm = re.search(r"([\d,.]+)\s*$", r[0])
                        tot = to_num(mm.group(1)) if mm else None
                    res["followers"]["total"] = tot
                    md = re.search(r"on\s+(.+?):?$", r[0])
                    if md:
                        res["followers"]["as_of"] = md.group(1)
                    continue
                d = parse_date(r[0], dayfirst)
                if d and len(r) > 1 and to_num(r[1]) is not None:
                    res["followers"].setdefault("daily", []).append({"date": d.date().isoformat(), "new": to_num(r[1])})
        elif kind == "demographics":
            for r in rows:
                if len(r) < 3 or not r[0] or not r[1]:
                    continue
                if norm(r[0]) in ("topdemographics", "category"):
                    continue
                pct = r[2]
                if isinstance(pct, str):
                    lt = "<" in pct
                    pct = to_num(pct.replace("<", ""))
                    pct = (pct / 100.0 if pct is not None and pct > 1 else pct) if not lt else 0.005
                elif isinstance(pct, (int, float)) and pct > 1:
                    pct = pct / 100.0
                res["demographics"][str(r[0]).strip()].append({"value": str(r[1]).strip(), "pct": pct})
        elif kind == "post_metrics":
            for r in rows:
                if len(r) >= 2 and isinstance(r[0], str):
                    m = metric_name(r[0])
                    if m and to_num(r[1]) is not None:
                        res["post_metrics"][m] = to_num(r[1])
                    elif "url" in norm(r[0]) and isinstance(r[1], str):
                        res["post_metrics"]["url"] = r[1]
                    elif "date" in norm(r[0]):
                        d = parse_date(r[1])
                        if d:
                            res["post_metrics"]["date"] = d.date().isoformat()
    res["demographics"] = dict(res["demographics"])
    return res


# ---------------------------------------------------------------------------
# Text features (shared by posts, voice and drafts)
# ---------------------------------------------------------------------------
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐✅❌✔]")
URL_RE = re.compile(r"(https?://|www\.)\S+", re.I)
HASHTAG_RE = re.compile(r"(?<![\w&])#[A-Za-z]\w*")
STOP = set("""a an the and or but if of to in on for with at by from as is are was were be been being it its this that these those
i me my we our you your he she they them their his her not no so do does did have has had will would can could should just
than then there here what which who whom when where why how all any each more most some such only own same too very s t
about into over after before again also up out off down because while until one two get got like""".split())


def text_features(text):
    t = (text or "").replace("\r\n", "\n").strip()
    lines = [l for l in t.split("\n")]
    first = next((l.strip() for l in lines if l.strip()), "")
    paras = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if re.search(r"[A-Za-z]", s)]
    words = re.findall(r"[A-Za-z'’]+", t)
    return {
        "chars": len(t),
        "words": len(words),
        "first_line": first[:200],
        "first_line_chars": len(first),
        "paragraphs": len(paras),
        "avg_sentence_words": round(len(words) / len(sents), 1) if sents else 0,
        "emoji": len(EMOJI_RE.findall(t)),
        "hashtags": len(HASHTAG_RE.findall(t)),
        "em_dashes": t.count("—"),
        "questions": t.count("?"),
        "exclamations": t.count("!"),
        "has_link": bool(URL_RE.search(t)),
        "has_list": bool(re.search(r"(?m)^\s*(\d+[.)]|[-•*→✅👉])\s+\S", t)),
        "starts_with_number": bool(re.match(r"\W*\d", first)),
        "ends_with_question": t.rstrip().endswith("?"),
        "i_rate": round(100 * sum(1 for w in words if w.lower() in ("i", "i'm", "i've", "i'd", "i'll", "me", "my")) / max(1, len(words)), 1),
        "you_rate": round(100 * sum(1 for w in words if w.lower() in ("you", "your", "you're", "you've", "yours")) / max(1, len(words)), 1),
        "we_rate": round(100 * sum(1 for w in words if w.lower() in ("we", "our", "us", "we're", "we've")) / max(1, len(words)), 1),
        "contractions": sum(1 for w in words if "'" in w or "’" in w),
    }


def length_band(n):
    return "<400" if n < 400 else "400-899" if n < 900 else "900-1499" if n < 1500 else "1500-2199" if n < 2200 else "2200+"


def hook_band(n):
    return "<=40" if n <= 40 else "41-80" if n <= 80 else "81+"


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def parse_shares(src):
    _, rows = read_csv(src.read(), expect=("ShareCommentary", "ShareLink", "Date"))
    posts = []
    for r in rows:
        text = pick(r, "ShareCommentary", "Commentary", "Text")
        if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
            text = text[1:-1].replace('""', '"')
        link = pick(r, "ShareLink", "Link", "URL")
        d = parse_date(pick(r, "Date", "Created", "CreatedAt"))
        pid, kind = extract_id(link)
        posts.append({
            "id": pid, "urn_type": kind, "url": link, "date": d.isoformat() if d else None,
            "text": text, "shared_url": pick(r, "SharedUrl", "SharedURL"), "media_url": pick(r, "MediaUrl", "MediaURL"),
            "visibility": pick(r, "Visibility"), "source": "shares",
        })
    return posts


def join_metrics(posts, analytics_list):
    """Attach metrics from analytics exports to posts parsed from Shares.csv."""
    metric_rows = []
    for a in analytics_list:
        for url, m in a["top_posts"].items():
            metric_rows.append(dict(m, metrics_source="aggregate top-50"))
        if a["post_metrics"]:
            metric_rows.append(dict(a["post_metrics"], metrics_source="per-post export"))
    stats = {"metric_rows": len(metric_rows), "matched_by_id": 0, "matched_by_time": 0, "matched_by_date": 0, "unmatched": 0}

    by_id = {p["id"]: p for p in posts if p.get("id")}
    # Decoded post times, validated against the CSV date so we only trust IDs that really encode time
    timed = []
    for p in posts:
        t = id_time(p.get("id"))
        if t and p.get("date"):
            if abs((t - dt.datetime.fromisoformat(p["date"])).total_seconds()) < 36 * 3600:
                timed.append((t, p))
        elif t:
            timed.append((t, p))
    by_day = defaultdict(list)
    for p in posts:
        if p.get("date"):
            by_day[p["date"][:10]].append(p)

    extra = []
    for m in metric_rows:
        mid, _ = extract_id(m.get("url"))
        target = by_id.get(mid) if mid else None
        how = "matched_by_id" if target else None
        if not target and mid:
            mt = id_time(mid)
            if mt and timed:
                best = min(timed, key=lambda x: abs((x[0] - mt).total_seconds()))
                if abs((best[0] - mt).total_seconds()) <= 300:
                    target, how = best[1], "matched_by_time"
        if not target and m.get("date"):
            cands = by_day.get(m["date"], [])
            if len(cands) == 1:
                target, how = cands[0], "matched_by_date"
        if target:
            stats[how] += 1
            for k, v in m.items():
                if k not in ("url", "date") and v is not None:
                    target[k] = v
            target.setdefault("analytics_url", m.get("url"))
        else:
            stats["unmatched"] += 1
            t = id_time(mid) if mid else None
            extra.append({"id": mid, "url": m.get("url"), "date": (t.isoformat() if t else m.get("date")),
                          "text": "", "source": "analytics-only", **{k: v for k, v in m.items() if k not in ("url", "date")}})
    return posts + extra, stats


def finalize_posts(posts):
    for i, p in enumerate(sorted(posts, key=lambda x: x.get("date") or "", reverse=True), 1):
        p["n"] = i
        p.update(text_features(p.get("text", "")))
        d = dt.datetime.fromisoformat(p["date"]) if p.get("date") else None
        p["weekday"] = d.strftime("%a") if d else None
        p["hour"] = d.hour if (d and (d.hour or d.minute)) else None
        p["has_media"] = bool(p.get("media_url"))
        imp, eng = p.get("impressions"), p.get("engagements")
        if eng is None and any(p.get(k) is not None for k in ("reactions", "comments", "reposts")):
            eng = sum(p.get(k) or 0 for k in ("reactions", "comments", "reposts", "saves", "sends", "clicks"))
            p["engagements"] = eng
        p["engagement_rate"] = round(eng / imp, 4) if (imp and eng is not None) else None
    return sorted(posts, key=lambda x: x["n"])


def profile_markdown(srcs):
    md = []
    prof = srcs.get("profile")
    if prof:
        _, rows = read_csv(prof.read(), expect=("First Name", "Headline"))
        if rows:
            r = rows[0]
            name = f"{pick(r, 'First Name')} {pick(r, 'Last Name')}".strip()
            md += [f"# Profile (from LinkedIn data archive)", "", f"**Name:** {name}",
                   f"**Headline:** {pick(r, 'Headline')}", f"**Industry:** {pick(r, 'Industry')}",
                   f"**Location:** {pick(r, 'Geo Location', 'Location')}", f"**Websites:** {pick(r, 'Websites')}", "",
                   "## About", "", pick(r, "Summary") or "_(empty)_", ""]
    pos = srcs.get("positions")
    if pos:
        _, rows = read_csv(pos.read(), expect=("Company Name", "Title"))
        md += ["## Experience", ""]
        for r in rows:
            md += [f"### {pick(r, 'Title')} · {pick(r, 'Company Name', 'Company')}",
                   f"_{pick(r, 'Started On')} – {pick(r, 'Finished On') or 'Present'} · {pick(r, 'Location')}_", "",
                   pick(r, "Description") or "_(no description)_", ""]
    edu = srcs.get("education")
    if edu:
        _, rows = read_csv(edu.read(), expect=("School Name",))
        md += ["## Education", ""]
        for r in rows:
            md.append(f"- {pick(r, 'School Name')}: {pick(r, 'Degree Name')} ({pick(r, 'Start Date')}–{pick(r, 'End Date')})")
        md.append("")
    sk = srcs.get("skills")
    if sk:
        _, rows = read_csv(sk.read(), expect=("Name",))
        names = [pick(r, "Name") for r in rows if pick(r, "Name")]
        md += [f"## Skills ({len(names)})", "", ", ".join(names), ""]
    for key, title, cols in (("certifications", "Certifications", ("Name", "Authority", "Started On")),
                             ("projects", "Projects", ("Title", "Description", "Started On")),
                             ("languages", "Languages", ("Name", "Proficiency"))):
        s = srcs.get(key)
        if s:
            _, rows = read_csv(s.read(), expect=cols[:1])
            md += [f"## {title}", ""] + [f"- " + " · ".join(pick(r, c) for c in cols if pick(r, c)) for r in rows] + [""]
    rec = srcs.get("recommendationsreceived")
    if rec:
        _, rows = read_csv(rec.read(), expect=("First Name", "Text"))
        vis = [r for r in rows if norm(pick(r, "Status")) in ("", "visible")]
        md += [f"## Recommendations received ({len(vis)} visible)", ""]
        for r in vis[:10]:
            md.append(f"- {pick(r, 'Creation Date')} · {pick(r, 'Job Title')} at {pick(r, 'Company')}: \"{pick(r, 'Text')[:220]}...\"")
        md.append("")
    return "\n".join(md) if md else None


def network_markdown(src):
    """Aggregate only. Never write individual connections' names or emails."""
    _, rows = read_csv(src.read(), expect=("First Name", "Connected On"))
    if not rows:
        return None
    pos = Counter()
    comp = Counter(pick(r, "Company") for r in rows if pick(r, "Company"))
    years = Counter()
    for r in rows:
        title = pick(r, "Position").lower()
        for kw, label in (("recruit", "Recruiters / talent"), ("talent", "Recruiters / talent"), ("founder", "Founders"),
                          ("ceo", "CEOs"), ("chief", "C-level"), ("vp", "VPs"), ("vice president", "VPs"), ("head of", "Heads of"),
                          ("director", "Directors"), ("manager", "Managers"), ("engineer", "Engineers"), ("developer", "Engineers"),
                          ("sales", "Sales"), ("account exec", "Sales"), ("marketing", "Marketing"), ("product", "Product"),
                          ("design", "Design"), ("data", "Data"), ("analyst", "Analysts"), ("consult", "Consultants"),
                          ("student", "Students"), ("finance", "Finance"), ("cfo", "Finance"), ("controller", "Finance"),
                          ("investor", "Investors / VC"), ("partner", "Investors / VC"), ("venture", "Investors / VC"),
                          ("hr ", "HR / People"), ("people", "HR / People")):
            if kw in title:
                pos[label] += 1
                break
        else:
            pos["Other / unknown"] += 1
        d = parse_date(pick(r, "Connected On"))
        if d:
            years[d.year] += 1
    n = len(rows)
    md = [f"# Network composition ({n} connections)", "", "_Aggregated from Connections.csv. Titles are matched by keyword; many connections hide their title._", "",
          "| Role group | Share |", "|---|---|"]
    for k, v in pos.most_common(12):
        md.append(f"| {k} | {100 * v / n:.0f}% ({v}) |")
    md += ["", "**Top companies in network:** " + ", ".join(f"{c} ({k})" for c, k in comp.most_common(10)), "",
           "**Connections added per year:** " + ", ".join(f"{y}: {k}" for y, k in sorted(years.items())), ""]
    return "\n".join(md)


def voice_profile(posts):
    texts = [p["text"] for p in posts if p.get("text") and len(p["text"]) >= 120]
    if len(texts) < 3:
        return None
    texts = texts[:60]
    feats = [text_features(t) for t in texts]
    avg = lambda k: round(statistics.mean(f[k] for f in feats), 2)
    med = lambda k: statistics.median(f[k] for f in feats)
    openers = Counter(" ".join(re.findall(r"[A-Za-z'’]+", f["first_line"])[:2]).lower() for f in feats)
    grams = Counter()
    for t in texts:
        w = [x.lower() for x in re.findall(r"[A-Za-z'’]{2,}", t)]
        for n in (2, 3):
            for i in range(len(w) - n + 1):
                g = w[i:i + n]
                if g[0] in STOP or g[-1] in STOP:
                    continue
                grams[" ".join(g)] += 1
    single_line_paras = []
    for t in texts:
        paras = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
        if paras:
            single_line_paras.append(sum(1 for p in paras if "\n" not in p.strip()) / len(paras))
    return {
        "posts_analyzed": len(texts),
        "median_chars": med("chars"),
        "avg_sentence_words": avg("avg_sentence_words"),
        "median_paragraphs": med("paragraphs"),
        "single_line_paragraph_share": round(statistics.mean(single_line_paras), 2) if single_line_paras else None,
        "emoji_per_post": avg("emoji"),
        "hashtags_per_post": avg("hashtags"),
        "em_dashes_per_post": avg("em_dashes"),
        "questions_per_post": avg("questions"),
        "exclamations_per_post": avg("exclamations"),
        "share_ending_with_question": round(sum(f["ends_with_question"] for f in feats) / len(feats), 2),
        "share_with_lists": round(sum(f["has_list"] for f in feats) / len(feats), 2),
        "i_per_100_words": avg("i_rate"),
        "you_per_100_words": avg("you_rate"),
        "we_per_100_words": avg("we_rate"),
        "contractions_per_post": avg("contractions"),
        "common_openers": [o for o, c in openers.most_common(8) if o and c >= 2],
        "signature_phrases": [g for g, c in grams.most_common(40) if c >= 3][:15],
        "sample_first_lines": [f["first_line"] for f in feats[:8]],
    }


def cmd_build(a):
    os.makedirs(a.out, exist_ok=True)
    sources = collect_sources(a.inputs)
    by_key = {}
    analytics = []
    seen = []
    for s in sources:
        if s.name.lower().endswith(".xlsx"):
            try:
                sheets = read_xlsx(s.read())
            except Exception as e:  # noqa: BLE001 - report and keep going
                out(f"! could not read {s.name}: {e}")
                continue
            res = parse_analytics_workbook(sheets, os.path.basename(s.name))
            analytics.append(res)
            seen.append(f"{os.path.basename(s.name)} (analytics: {', '.join(res['sheets'])})")
        else:
            k = s.key
            if k in ("shares", "profile", "positions", "education", "skills", "connections", "comments", "certifications",
                     "projects", "languages", "recommendationsreceived", "reactions"):
                by_key.setdefault(k, s)
                seen.append(os.path.basename(s.name))
            elif k.startswith("shares"):
                by_key.setdefault("shares", s)
                seen.append(os.path.basename(s.name))

    out(f"Found: {', '.join(seen) if seen else 'nothing usable'}")
    written = []

    pm = profile_markdown(by_key)
    if pm:
        with open(os.path.join(a.out, "profile_archive.md"), "w", encoding="utf-8") as f:
            f.write(pm)
        written.append("profile_archive.md")

    if "connections" in by_key:
        nm = network_markdown(by_key["connections"])
        if nm:
            with open(os.path.join(a.out, "network.md"), "w", encoding="utf-8") as f:
                f.write(nm)
            written.append("network.md")

    posts = parse_shares(by_key["shares"]) if "shares" in by_key else []
    join = None
    if analytics:
        posts, join = join_metrics(posts, analytics)
    posts = finalize_posts(posts)
    if posts:
        with open(os.path.join(a.out, "posts.json"), "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=1)
        written.append("posts.json")

    if analytics:
        merged = {"sources": [x["source"] for x in analytics], "discovery": {}, "daily": [], "followers": {}, "demographics": {}, "notes": []}
        for x in analytics:
            merged["discovery"].update(x["discovery"])
            merged["daily"] += x["daily"]
            if x["followers"]:
                merged["followers"].update(x["followers"])
            merged["demographics"].update(x["demographics"])
            merged["notes"] += x["notes"]
        merged["daily"] = sorted({d["date"]: d for d in merged["daily"]}.values(), key=lambda d: d["date"])
        with open(os.path.join(a.out, "analytics.json"), "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=1)
        written.append("analytics.json")

    vp = voice_profile(posts)
    if vp:
        with open(os.path.join(a.out, "voice.json"), "w", encoding="utf-8") as f:
            json.dump(vp, f, ensure_ascii=False, indent=1)
        written.append("voice.json")

    # Summary
    out(f"Wrote to {a.out}: {', '.join(written) or 'nothing'}")
    if posts:
        with_text = sum(1 for p in posts if p.get("text"))
        with_m = [p for p in posts if p.get("impressions") is not None or p.get("engagements") is not None]
        dates = sorted(p["date"][:10] for p in posts if p.get("date"))
        out(f"Posts: {len(posts)} ({with_text} with text, {len(with_m)} with metrics)" + (f", {dates[0]} → {dates[-1]}" if dates else ""))
        if join:
            out(f"Join: {join['matched_by_id']} by ID, {join['matched_by_time']} by ID timestamp, {join['matched_by_date']} by date, "
                f"{join['unmatched']} metrics rows without post text")
            if any(len(x["top_posts"]) >= 50 for x in analytics):
                out("Note: the aggregate analytics export lists only the top 50 posts by impressions and by engagements. "
                    "Posts outside both lists have no metrics, so comparisons are among the better-performing posts.")
    if analytics:
        d = analytics[0]
        disc = {}
        for x in analytics:
            disc.update(x["discovery"])
        if disc:
            out("Discovery: " + ", ".join(f"{k}={v}" for k, v in disc.items()))
        fol = next((x["followers"] for x in analytics if x["followers"]), {})
        if fol:
            new = sum(i["new"] for i in fol.get("daily", []) if isinstance(i.get("new"), (int, float)))
            out(f"Followers: total {fol.get('total')}, +{new} in export period")
        for x in analytics:
            for n in x["notes"]:
                out(f"! {n}")
    if not posts and not analytics and not pm:
        out("Nothing parsed. Run `inspect` on the input to see what's inside.")


# ---------------------------------------------------------------------------
# list / stats / voice / dashboard / postdate / inspect
# ---------------------------------------------------------------------------
def load_posts(d):
    p = os.path.join(d, "posts.json") if os.path.isdir(d) else d
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cmd_list(a):
    posts = load_posts(a.dir)
    key = {"impressions": lambda p: -(p.get("impressions") or -1), "engagements": lambda p: -(p.get("engagements") or -1),
           "date": lambda p: p["n"]}[a.sort]
    posts = sorted(posts, key=key)[: a.limit]
    out("n | date | impressions | engagements | ER | chars | text")
    for p in posts:
        txt = (p.get("text") or "(no text: analytics only)").replace("\n", " / ")
        er = f"{100 * p['engagement_rate']:.1f}%" if p.get("engagement_rate") is not None else "-"
        out(f"{p['n']} | {(p.get('date') or '')[:10]} | {p.get('impressions', '-')} | {p.get('engagements', '-')} | {er} | {p['chars']} | {txt[: a.chars]}")


def group_posts(posts, keyfn, metric):
    """Group posts by keyfn(post); list-valued keys put a post in several groups."""
    groups = defaultdict(list)
    for p in posts:
        k = keyfn(p)
        if k is None or k == "" or p.get(metric) is None:
            continue
        for kk in (k if isinstance(k, list) else [k]):
            groups[str(kk)].append(p)
    return groups


def cmd_stats(a):
    posts = load_posts(a.dir)
    tags = {}
    if a.tags:
        with open(a.tags, encoding="utf-8") as f:
            raw = json.load(f)
        tags = {str(k): v for k, v in raw.items()}
    for p in posts:
        for k, v in tags.get(str(p["n"]), {}).items():
            p["tag_" + k] = v
    metric = "impressions" if any(p.get("impressions") is not None for p in posts) else "engagements"
    scored = [p for p in posts if p.get(metric) is not None]
    # Benchmark the user's own written posts. Analytics-only rows (reposts, articles, posts missing from
    # Shares.csv) have no text features, so they're excluded when text is available and reported separately.
    excluded = [p for p in scored if not p.get("text")]
    if len(excluded) < len(scored):
        scored = [p for p in scored if p.get("text")]
    else:
        excluded = []
    if not scored:
        out("No posts with metrics. Provide an analytics export to `build`.")
        return
    overall = median(p[metric] for p in scored)
    er_overall = median(p.get("engagement_rate") for p in scored)
    res = {"metric": metric, "n": len(scored), "excluded_without_text": len(excluded), "overall_median": overall, "overall_median_er": er_overall, "groups": {}}

    dims = {
        "length": lambda p: length_band(p["chars"]) if p.get("text") else None,
        "first line length": lambda p: hook_band(p["first_line_chars"]) if p.get("text") else None,
        "media attached": lambda p: ("yes" if p.get("has_media") else "no") if p.get("source") == "shares" else None,
        "link in post": lambda p: ("yes" if p.get("has_link") or p.get("shared_url") else "no") if p.get("text") else None,
        "starts with a number": lambda p: ("yes" if p.get("starts_with_number") else "no") if p.get("text") else None,
        "ends with a question": lambda p: ("yes" if p.get("ends_with_question") else "no") if p.get("text") else None,
        "has a list": lambda p: ("yes" if p.get("has_list") else "no") if p.get("text") else None,
        "weekday": lambda p: p.get("weekday"),
    }
    tag_keys = sorted({k for p in posts for k in p if k.startswith("tag_")})
    for tk in tag_keys:
        dims[tk[4:]] = (lambda key: (lambda p: p.get(key)))(tk)

    lines = [f"# Personal benchmarks ({metric}, n={len(scored)} posts)", "",
             f"Overall median {metric}: **{overall:,.0f}**" + (f" · median engagement rate: **{100 * er_overall:.2f}%**" if er_overall else ""), ""]
    if excluded:
        lines += [f"_{len(excluded)} post(s) with metrics but no text in the archive (e.g. reposts) are left out of these benchmarks._", ""]
    if sum(1 for p in scored if p.get("metrics_source") == "aggregate top-50") >= 50:
        lines += ["> Metrics come from the aggregate export's top-50 lists, so posts outside them are missing. "
                  "Read comparisons as 'among your better posts'.", ""]
    for name, fn in dims.items():
        g = group_posts(scored, fn, metric)
        if len(g) < 2:
            continue
        rows = []
        for k, ps in sorted(g.items(), key=lambda kv: -median(p[metric] for p in kv[1])):
            m = median(p[metric] for p in ps)
            rows.append({"group": k, "n": len(ps), "median": m, "lift": round(m / overall, 2) if overall else None,
                         "median_er": median(p.get("engagement_rate") for p in ps)})
        res["groups"][name] = rows
        lines += [f"## By {name}", "", "| Group | n | Median | vs. your median | Median ER |", "|---|---|---|---|---|"]
        for r in rows:
            flag = " (small sample)" if r["n"] < 3 else ""
            er = f"{100 * r['median_er']:.2f}%" if r["median_er"] is not None else "-"
            lines.append(f"| {r['group']}{flag} | {r['n']} | {r['median']:,.0f} | {r['lift']}x | {er} |")
        lines.append("")

    # Monthly trend and cadence
    months = defaultdict(list)
    for p in posts:
        if p.get("date"):
            months[p["date"][:7]].append(p)
    trend = []
    for mth in sorted(months):
        ps = months[mth]
        trend.append({"month": mth, "posts": len(ps), "median": median(p.get(metric) for p in ps)})
    res["monthly"] = trend
    lines += ["## By month", "", "| Month | Posts | Median " + metric + " |", "|---|---|---|"]
    for t in trend:
        med = "-" if t["median"] is None else f"{t['median']:,.0f}"
        lines.append(f"| {t['month']} | {t['posts']} | {med} |")
    lines.append("")

    top = sorted(scored, key=lambda p: -p[metric])[:5]
    res["top"] = [{"n": p["n"], "date": p.get("date"), metric: p[metric], "first_line": p.get("first_line")} for p in top]
    lines += ["## Top 5", ""] + [f"- #{p['n']} {(p.get('date') or '')[:10]} · {p[metric]:,} · {p.get('first_line') or '(no text)'}" for p in top] + [""]

    with open(os.path.join(a.dir, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    out("\n".join(lines))


def cmd_voice(a):
    if os.path.isdir(a.src) and os.path.exists(os.path.join(a.src, "posts.json")):
        posts = load_posts(a.src)
    else:
        srcs = collect_sources([a.src])
        sh = next((s for s in srcs if s.key.startswith("shares")), None)
        if not sh:
            out("No posts.json or Shares.csv found.")
            return
        posts = finalize_posts(parse_shares(sh))
    vp = voice_profile(posts)
    if not vp:
        out("Need at least 3 posts with 120+ characters of text to build a voice profile.")
        return
    out(f"Voice fingerprint from {vp['posts_analyzed']} posts")
    for k, v in vp.items():
        if k != "posts_analyzed":
            out(f"- {k.replace('_', ' ')}: {v}")
    if a.draft:
        with open(a.draft, encoding="utf-8-sig") as f:
            txt = f.read()
        if txt.startswith("---\n"):
            end = txt.find("\n---", 4)
            txt = txt[end + 4:] if end != -1 else txt
        d = text_features(txt)
        out("")
        out("Draft vs. your usual style:")
        checks = [("chars", "median_chars", "length (chars)"), ("avg_sentence_words", "avg_sentence_words", "words per sentence"),
                  ("emoji", "emoji_per_post", "emoji"), ("hashtags", "hashtags_per_post", "hashtags"),
                  ("em_dashes", "em_dashes_per_post", "em dashes"), ("questions", "questions_per_post", "questions"),
                  ("exclamations", "exclamations_per_post", "exclamation marks")]
        off = 0
        for dk, vk, label in checks:
            base, val = vp[vk], d[dk]
            far = (base == 0 and val >= 2) or (base > 0 and (val > base * 2 + 1 or val < base / 2 - 1))
            off += far
            out(f"  {'!' if far else ' '} {label}: draft {val} · usual {base}")
        out(f"Voice match: {'close' if off == 0 else 'mostly close' if off <= 2 else 'off; revise toward the usual style'}")


def cmd_dashboard(a):
    os.makedirs(a.out, exist_ok=True)
    posts = load_posts(a.dir) if os.path.exists(os.path.join(a.dir, "posts.json")) else []
    def opt(name):
        p = os.path.join(a.dir, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        return None
    data = {
        "generated": dt.date.today().isoformat(),
        "name": a.name or "",
        "posts": [{k: p.get(k) for k in ("n", "date", "first_line", "chars", "impressions", "engagements", "engagement_rate",
                                          "reactions", "comments", "reposts", "saves", "url", "has_media")} for p in posts],
        "analytics": opt("analytics.json"),
        "stats": opt("stats.json"),
        "voice": opt("voice.json"),
        "insights": [],
    }
    if a.insights and os.path.exists(a.insights):
        with open(a.insights, encoding="utf-8") as f:
            data["insights"] = json.load(f)
    shutil.copyfile(os.path.join(SKILL_DIR, "assets", "dashboard", "index.html"), os.path.join(a.out, "index.html"))
    with open(os.path.join(a.out, "data.js"), "w", encoding="utf-8") as f:
        f.write("window.DASH = " + json.dumps(data, ensure_ascii=False) + ";\n")
    out(f"Dashboard written to {os.path.join(a.out, 'index.html')}")


def cmd_postdate(a):
    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    for ref in a.refs:
        pid, _ = extract_id(ref)
        if not pid and re.fullmatch(r"\d{15,20}", ref.strip()):
            pid = ref.strip()
        t = id_time(pid)
        label = ref if len(ref) <= 90 else ref[:87] + "..."
        if not t:
            out(f"?           {label}  (no dated post ID found)")
            continue
        out(f"{t.strftime('%Y-%m-%d')}  {(now - t).days:>4} days ago  {label}")


def cmd_inspect(a):
    for s in collect_sources([a.path]):
        if s.name.lower().endswith(".xlsx"):
            try:
                sheets = read_xlsx(s.read())
            except Exception as e:  # noqa: BLE001
                out(f"{s.name}: unreadable xlsx ({e})")
                continue
            out(f"{s.name}: {len(sheets)} sheets")
            for sh in sheets:
                out(f"  [{sh['name']}] classified as {classify_sheet(sh['rows'])}, {len(sh['rows'])} rows")
                for r in sh["rows"][:4]:
                    out("    " + " | ".join("" if c is None else str(c)[:40] for c in r[:8]))
        else:
            header, rows = read_csv(s.read())
            out(f"{s.name} (key: {s.key}): {len(rows)} rows; header: {', '.join(h[:25] for h in header[:10])}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="parse exports")
    b.add_argument("inputs", nargs="+")
    b.add_argument("--out", required=True)
    l = sub.add_parser("list", help="compact post listing")
    l.add_argument("dir")
    l.add_argument("--sort", choices=["impressions", "engagements", "date"], default="date")
    l.add_argument("--limit", type=int, default=100)
    l.add_argument("--chars", type=int, default=140)
    s = sub.add_parser("stats", help="personal benchmarks")
    s.add_argument("dir")
    s.add_argument("--tags", help='JSON: {"<post n>": {"topic": "...", "hook": "...", "format": "..."}}')
    v = sub.add_parser("voice", help="voice fingerprint")
    v.add_argument("src")
    v.add_argument("--draft")
    d = sub.add_parser("dashboard", help="write dashboard html + data.js")
    d.add_argument("dir")
    d.add_argument("--out", required=True)
    d.add_argument("--name")
    d.add_argument("--insights", help='JSON list: [{"title": "...", "detail": "...", "kind": "do|stop|test"}]')
    pdp = sub.add_parser("postdate", help="decode posts' publish dates from their URLs or IDs")
    pdp.add_argument("refs", nargs="+")
    i = sub.add_parser("inspect", help="show what's inside an export")
    i.add_argument("path")
    a = ap.parse_args()
    {"build": cmd_build, "list": cmd_list, "stats": cmd_stats, "voice": cmd_voice, "dashboard": cmd_dashboard,
     "postdate": cmd_postdate, "inspect": cmd_inspect}[a.cmd](a)


if __name__ == "__main__":
    main()
