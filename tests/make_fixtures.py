#!/usr/bin/env python3
"""Generate synthetic LinkedIn exports for testing (fictional persona: Priya Raman).

Writes tests/fixtures/priya/:
  Basic_LinkedInDataExport_10-14-2026.zip   (Profile, Positions, Skills, Education, Shares,
                                              Comments, Connections, Recommendations_Received)
  AggregateAnalytics_Priya_Raman_2025-10-15_2026-10-14.xlsx  (5 sheets, LinkedIn-like layout)

Formats mirror what's documented in skills/linkedin/references/data-sources.md.
Everything is made up. Run: python tests/make_fixtures.py
"""
import csv
import datetime as dt
import io
import os
import random
import zipfile
from xml.sax.saxutils import escape

random.seed(7)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixtures", "priya")
os.makedirs(OUT, exist_ok=True)

# (days before 2026-10-14, hour UTC, impressions, engagements, media?, text)
POSTS = [
    (3, 15, 8420, 291, False, """I've sat in 31 due diligence calls this year.

The question that sinks founders isn't about revenue. It's "walk me through your deferred revenue."

Most seed-stage founders book annual contracts as revenue the day the cash lands. Investors catch it in about four minutes.

Here's the fix, and it takes one afternoon:

1. List every annual or multi-year contract.
2. Recognize 1/12 of each per month.
3. Put the rest on the balance sheet as deferred revenue.
4. Reconcile it to cash every month.

You don't need an ERP for this. A clean spreadsheet works until about $3M ARR.

Fix it before the data room opens, not during."""),
    (8, 14, 2310, 61, False, """Remote work made me a better CFO.

Not because of the commute. Because I had to write everything down.

Every board memo, every forecast assumption, every "why did cash drop in March" lives in a doc now. My clients can read my reasoning without a call.

The side effect: my forecasts got more accurate. Writing assumptions down makes the bad ones obvious."""),
    (12, 16, 12650, 512, True, """5 SaaS metrics investors check before your pitch even starts.

I made a one-page cheat sheet from 30+ diligence calls. Swipe through.

The one most founders get wrong is net revenue retention. If you're below 100%, lead with the story of why, not the number.

Which of these do you track monthly today?"""),
    (17, 13, 1980, 40, False, """Quick reminder that my newsletter goes out Thursday. This week: a teardown of a real seed-stage budget (anonymized).

Subscribe here: https://priyaraman.substack.com"""),
    (22, 15, 9870, 344, False, """My dad ran a hardware store in Leicester for 34 years.

He never once looked at a P&L. He knew his margin on every bolt by heart and he knew which customers paid late.

When I became a CFO I thought he'd been lucky.

Twenty years later I think he understood something most startups miss: cash is a habit, not a report.

Three of his habits I still use with every client:

- Know the 10 numbers that matter by heart.
- Chase late payers on day one, not day thirty.
- Never let a supplier's terms surprise you.

He'd hate the word "runway". He'd love the idea."""),
    (27, 14, 3100, 77, False, """Hot take: most seed startups don't need a CFO.

They need a clean bookkeeper, a 13-week cash forecast, and someone to look at both once a month.

I tell about half the founders who call me exactly that. It's the best marketing I've ever done. They come back at Series A."""),
    (33, 15, 6240, 205, False, """Your burn multiple is lying to you.

Below $1M ARR it swings wildly with a single customer. One annual prepay can make you look like the most efficient company in your batch.

What I track instead for early-stage clients:

- Months of runway at current net burn
- Net new ARR per $ of sales and marketing spend, on a trailing 3-month basis
- Gross margin after hosting and support

Boring numbers. They don't lie as much."""),
    (38, 16, 1720, 33, False, """Spent the weekend at a wedding in Lisbon. Beautiful city, terrible Wi-Fi, excellent pastries. Back to spreadsheets tomorrow."""),
    (44, 14, 11200, 430, True, """The 13-week cash forecast template I give every client.

Free, no email required. It's the single most useful finance tool for a startup under $5M ARR.

Slide 6 is the part everyone skips: the assumptions log."""),
    (51, 15, 4870, 150, False, """A founder asked me last week: "When should I hire my first finance person?"

My rule of thumb after 40+ clients:

When the CEO spends more than 4 hours a week on finance admin, or when you're 6 months from a raise. Whichever comes first.

Before that, a good bookkeeper and a fractional CFO a few hours a month is cheaper and usually better."""),
    (58, 13, 2650, 58, False, """Leadership lesson from my first boss at Stripe: "Bring me the number and what you'd do about it."

I still write every client email that way. Number first, recommendation second, context last."""),
    (64, 15, 7310, 260, False, """We almost ran out of cash at 41% gross margin and $2.4M ARR.

Nobody noticed because revenue was growing 9% a month.

The problem was hosting. Every new enterprise customer needed a dedicated instance, and nobody had priced that in.

What we did in 6 weeks:

1. Re-priced enterprise with a hosting line item.
2. Moved 60% of customers to shared infrastructure.
3. Pushed gross margin to 68%.

Growth hides margin problems. Look at gross margin per customer cohort, not just in total."""),
    (71, 14, 1540, 29, False, """Excited to share that I'll be speaking at SaaStr Europa in June! Come say hi if you're there."""),
    (78, 15, 5420, 171, False, """3 things I check in the first hour with any new client:

1. Is cash in the bank reconciled to the books? (It's not, about half the time.)
2. Who can approve payments, and is it written down anywhere?
3. When was the last time anyone updated the forecast?

None of this is advanced finance. All of it matters more than your model's formatting."""),
    (86, 16, 3890, 98, False, """What I've learned in 2 years of running a fractional CFO practice:

- Specialize early. "CFO for SaaS from seed to Series A" brought me 3x more referrals than "fractional CFO".
- Cap your clients. I work with 6 at a time, max.
- Write things down. My best leads come from people who read my posts for months before reaching out."""),
    (93, 15, 2080, 47, False, """Unpopular opinion: investor updates should be boring.

Same format every month. Same metrics. Same order. Highlights, lowlights, asks.

When your update is predictable, the one surprising line gets read."""),
    (101, 14, 6890, 232, False, """A Series A founder showed me a model with 147 tabs.

The board looked at one: the cash runway chart.

We rebuilt it with 9 tabs in two days. The board meeting took 40 minutes instead of 2 hours.

Your model is a communication tool first. If nobody can follow it, it doesn't matter how clever it is."""),
    (109, 15, 2440, 52, False, """Monday reading list for startup finance people:

- The latest Bessemer State of the Cloud
- A great thread on usage-based pricing
- My own post from last week on deferred revenue

Links in the comments."""),
]

PROFILE = {
    "First Name": "Priya", "Last Name": "Raman", "Maiden Name": "", "Address": "", "Birth Date": "",
    "Headline": "Fractional CFO | Finance | Startups | Ex-Stripe",
    "Summary": "I'm a finance professional with 15+ years of experience across fintech and SaaS. Passionate about helping startups grow. Previously at Stripe and Deloitte. Let's connect!",
    "Industry": "Financial Services", "Zip Code": "", "Geo Location": "London, England, United Kingdom",
    "Twitter Handles": "", "Websites": "[COMPANY:https://priyaraman.co]", "Instant Messengers": "",
}
POSITIONS = [
    {"Company Name": "Raman Finance", "Title": "Founder & Fractional CFO", "Description": "Fractional CFO services for startups.", "Location": "London", "Started On": "Sep 2024", "Finished On": ""},
    {"Company Name": "Stripe", "Title": "Finance Lead, EMEA", "Description": "Led FP&A for EMEA business.", "Location": "Dublin", "Started On": "Mar 2018", "Finished On": "Aug 2024"},
    {"Company Name": "Deloitte", "Title": "Senior Manager, Audit", "Description": "", "Location": "London", "Started On": "Sep 2010", "Finished On": "Feb 2018"},
]
SKILLS = ["Financial Modeling", "FP&A", "Microsoft Excel", "Audit", "Fundraising", "SaaS Metrics", "Budgeting", "Microsoft Word", "Team Leadership", "IFRS"]
END = dt.datetime(2026, 10, 14, 23, 0)


def rand22():
    return random.getrandbits(22)


def post_rows():
    rows = []
    for days, hour, imp, eng, media, text in POSTS:
        t = (END - dt.timedelta(days=days)).replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        ms = int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        activity_id = (ms << 22) | rand22()
        share_id = ((ms - random.randint(50, 900)) << 22) | rand22()
        rows.append({"t": t, "activity": activity_id, "share": share_id, "imp": imp, "eng": eng, "media": media, "text": text})
    return rows


def csv_bytes(header, rows, preamble=""):
    buf = io.StringIO()
    if preamble:
        buf.write(preamble)
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow([r.get(h, "") for h in header])
    return ("﻿" + buf.getvalue()).encode("utf-8")


def build_zip(rows):
    path = os.path.join(OUT, "Basic_LinkedInDataExport_10-14-2026.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Profile.csv", csv_bytes(list(PROFILE), [PROFILE]))
        z.writestr("Positions.csv", csv_bytes(["Company Name", "Title", "Description", "Location", "Started On", "Finished On"], POSITIONS))
        z.writestr("Skills.csv", csv_bytes(["Name"], [{"Name": s} for s in SKILLS]))
        z.writestr("Education.csv", csv_bytes(["School Name", "Start Date", "End Date", "Notes", "Degree Name", "Activities"],
                                              [{"School Name": "London School of Economics", "Start Date": "2006", "End Date": "2009", "Degree Name": "BSc Accounting and Finance"}]))
        shares = []
        for i, r in enumerate(rows):
            urn = "ugcPost" if i % 5 == 4 else "share"
            shares.append({"Date": r["t"].strftime("%Y-%m-%d %H:%M:%S"),
                           "ShareLink": f"https://www.linkedin.com/feed/update/urn%3Ali%3A{urn}%3A{r['share']}",
                           "ShareCommentary": r["text"],
                           "SharedUrl": "", "MediaUrl": "https://media.licdn.com/dms/document/abc" if r["media"] else "",
                           "Visibility": "MEMBER_NETWORK"})
        z.writestr("Shares.csv", csv_bytes(["Date", "ShareLink", "ShareCommentary", "SharedUrl", "MediaUrl", "Visibility"], shares))
        z.writestr("Comments.csv", csv_bytes(["Date", "Link", "Message"], [
            {"Date": "2026-10-10 09:12:00", "Link": "https://www.linkedin.com/feed/update/urn:li:activity:7383000000000000000",
             "Message": "We saw the same thing with annual prepays. The fix that worked for us was showing the board a cash-adjusted burn next to the GAAP one."},
            {"Date": "2026-10-02 18:40:00", "Link": "https://www.linkedin.com/feed/update/urn:li:activity:7380000000000000000",
             "Message": "Strongly agree on the 13-week forecast. Most founders I work with have never seen one before their first board meeting."}]))
        notes = ('Notes:\n"When exporting your connection data, you may notice that some of the email addresses are missing. '
                 'You will only see email addresses for connections who have allowed their connections to see or download their email address."\n\n')
        titles = ["Founder & CEO", "CFO", "VP Finance", "Talent Acquisition Partner", "Software Engineer", "Head of Finance",
                  "Investor", "Partner", "Controller", "Product Manager", "Recruiter", "Co-founder"]
        cons = [{"First Name": f"Person{i}", "Last Name": "Example", "URL": f"https://www.linkedin.com/in/person{i}-example",
                 "Email Address": "", "Company": random.choice(["Stripe", "Monzo", "Seedcamp", "Deloitte", "Acme SaaS", "Index Ventures", "Revolut"]),
                 "Position": random.choice(titles), "Connected On": (END - dt.timedelta(days=random.randint(10, 3000))).strftime("%d %b %Y")}
                for i in range(240)]
        z.writestr("Connections.csv", csv_bytes(["First Name", "Last Name", "URL", "Email Address", "Company", "Position", "Connected On"], cons, notes))
        z.writestr("Recommendations_Received.csv", csv_bytes(
            ["First Name", "Last Name", "Company", "Job Title", "Text", "Creation Date", "Status"],
            [{"First Name": "Tom", "Last Name": "Example", "Company": "Acme SaaS", "Job Title": "CEO",
              "Text": "Priya rebuilt our finance function in 8 weeks before our Series A. Diligence took 3 weeks instead of 8.",
              "Creation Date": "03/14/2025, 10:22 AM", "Status": "VISIBLE"}]))
    return path


# --- tiny xlsx writer with shared strings (LinkedIn's exports use them) ------------------------
def col(n):
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def write_xlsx(path, sheets):
    strings, index = [], {}

    def sidx(s):
        if s not in index:
            index[s] = len(strings)
            strings.append(s)
        return index[s]

    sheet_xml = []
    for name, rows in sheets:
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
        for ri, row in enumerate(rows, 1):
            cells = []
            for ci, v in enumerate(row):
                if v is None or v == "":
                    continue
                ref = f"{col(ci)}{ri}"
                if isinstance(v, (int, float)):
                    cells.append(f'<c r="{ref}"><v>{v}</v></c>')
                else:
                    cells.append(f'<c r="{ref}" t="s"><v>{sidx(str(v))}</v></c>')
            out.append(f'<row r="{ri}">{"".join(cells)}</row>')
        out.append("</sheetData></worksheet>")
        sheet_xml.append("".join(out))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, len(sheets) + 1))
                   + '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _) in enumerate(sheets, 1)) + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1))
                   + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>')
        for i, x in enumerate(sheet_xml, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", x)
        z.writestr("xl/sharedStrings.xml", '<?xml version="1.0" encoding="UTF-8"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   f'count="{len(strings)}" uniqueCount="{len(strings)}">' + "".join(f"<si><t xml:space=\"preserve\">{escape(s)}</t></si>" for s in strings) + "</sst>")


def build_xlsx(rows):
    us = lambda d: f"{d.month}/{d.day}/{d.year}"
    start = END.date() - dt.timedelta(days=364)
    daily = []
    by_day = {r["t"].date(): r for r in rows}
    for i in range(365):
        d = start + dt.timedelta(days=i)
        base = random.randint(250, 700)
        r = by_day.get(d)
        imp = base + (int(r["imp"] * 0.55) if r else 0)
        daily.append([us(d), imp, int(imp * random.uniform(0.012, 0.03))])
    total_imp = sum(x[1] for x in daily)
    top_eng = sorted(rows, key=lambda r: -r["eng"])
    top_imp = sorted(rows, key=lambda r: -r["imp"])
    # one post that exists only in analytics (e.g. a repost with no commentary)
    extra_t = END - dt.timedelta(days=120)
    extra_id = (int(extra_t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000) << 22) | rand22()
    tp = [["Maximum of 50 posts available to include in this list"], [],
          ["Post URL", "Post publish date", "Engagements", None, "Post URL", "Post publish date", "Impressions"]]
    url = lambda a: f"https://www.linkedin.com/feed/update/urn:li:activity:{a}/"
    n = max(len(top_eng), len(top_imp)) + 1
    for i in range(n):
        left = [url(top_eng[i]["activity"]), us(top_eng[i]["t"]), top_eng[i]["eng"]] if i < len(top_eng) else [url(extra_id), us(extra_t), 18]
        right = [url(top_imp[i]["activity"]), us(top_imp[i]["t"]), top_imp[i]["imp"]] if i < len(top_imp) else [url(extra_id), us(extra_t), 1210]
        tp.append(left + [None] + right)
    followers = [["Total followers on 10/14/2026:", 4120], [], ["Date", "New followers"]]
    for i in range(365):
        d = start + dt.timedelta(days=i)
        followers.append([us(d), random.randint(0, 14) + (40 if d in by_day and by_day[d]["imp"] > 8000 else 0)])
    demo = [["Top Demographics", "Value", "Percentage"],
            ["Job titles", "Founder", "14%"], ["Job titles", "Chief Executive Officer", "8%"], ["Job titles", "Software Engineer", "7%"],
            ["Job titles", "Recruiter", "6%"], ["Job titles", "Chief Financial Officer", "4%"], ["Job titles", "Accountant", "4%"],
            ["Locations", "London Area, United Kingdom", "31%"], ["Locations", "Dublin", "7%"], ["Locations", "San Francisco Bay Area", "5%"],
            ["Industries", "Software Development", "29%"], ["Industries", "Financial Services", "18%"], ["Industries", "Venture Capital and Private Equity", "9%"],
            ["Seniority", "Senior", "27%"], ["Seniority", "Owner", "16%"], ["Seniority", "Entry", "11%"], ["Seniority", "CXO", "9%"],
            ["Company size", "11-50 employees", "23%"], ["Company size", "2-10 employees", "18%"], ["Company size", "10,001+ employees", "12%"],
            ["Companies", "Stripe", "2%"], ["Companies", "Deloitte", "< 1%"]]
    sheets = [("DISCOVERY", [["Overall Performance", "10/15/2025 - 10/14/2026"], ["Impressions", total_imp], ["Members reached", int(total_imp * 0.38)]]),
              ("ENGAGEMENT", [["Date", "Impressions", "Engagements"]] + daily),
              ("TOP POSTS", tp),
              ("FOLLOWERS", followers),
              ("DEMOGRAPHICS", demo)]
    path = os.path.join(OUT, "AggregateAnalytics_Priya_Raman_2025-10-15_2026-10-14.xlsx")
    write_xlsx(path, sheets)
    return path


if __name__ == "__main__":
    rows = post_rows()
    print(build_zip(rows))
    print(build_xlsx(rows))
