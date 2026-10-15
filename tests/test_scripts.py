#!/usr/bin/env python3
"""Regression tests for the skill's scripts. Standard library only.

Run from the repo root:
    python tests/make_fixtures.py      # (re)generate synthetic exports
    python -m unittest discover tests  # run the tests
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugins", "linkedin", "skills", "linkedin", "scripts")
FIX = os.path.join(ROOT, "tests", "fixtures")
ZIP = os.path.join(FIX, "priya", "Basic_LinkedInDataExport_10-14-2026.zip")
XLSX = os.path.join(FIX, "priya", "AggregateAnalytics_Priya_Raman_2025-10-15_2026-10-14.xlsx")


def run(script, *args):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise AssertionError(f"{script} {' '.join(args)} failed:\n{p.stderr}")
    return p.stdout


class CheckPost(unittest.TestCase):
    def check(self, path):
        return json.loads(run("check.py", "post", os.path.join(FIX, path), "--json"))

    def test_sloppy_post_fails(self):
        r = self.check("sloppy-post.md")
        rules = {i["rule"] for i in r["issues"]}
        self.assertLess(r["score"], 50)
        for rule in ("ai-tell", "engagement-bait", "formula", "placeholder", "hashtags", "link"):
            self.assertIn(rule, rules)

    def test_good_post_passes(self):
        r = self.check("good-post.md")
        self.assertGreaterEqual(r["score"], 85)
        self.assertEqual(r["verdict"], "Ready to post")

    def test_generic_post_is_capped(self):
        txt = ("Leadership is about people.\n\nGreat leaders listen more than they talk. They build trust over time and they make "
               "sure everyone on the team feels heard and valued, because when people feel heard they do their best work.\n\n"
               "The best managers always focus on growth, on coaching, and on giving feedback that is honest but kind. "
               "That is what makes a real difference in the long run.\n\nWhat do you think makes a great leader?")
        r = json.loads(run("check.py", "post", "--text", txt, "--json"))
        self.assertLessEqual(r["score"], 70)
        self.assertTrue(any(i["rule"] == "specificity" for i in r["issues"]))

    def test_placeholders_any_case(self):
        # Found in a live test: lowercase gaps used to slip through and score 100/100.
        def holes(txt):
            r = json.loads(run("check.py", "post", "--text", txt, "--json"))
            return [i["match"] for i in r["issues"] if i["rule"] == "placeholder"]
        self.assertEqual(holes("Covered by [who covers it, e.g. someone stays late] every week."), ["[who covers it, e.g. someone stays late]"])
        self.assertEqual(holes("Revenue grew XX% last year."), ["XX%"])
        self.assertEqual(holes("Our [NUMBER] signups."), ["[NUMBER]"])
        self.assertEqual(holes("See [our guide](https://x.com) for details."), [])

    def test_fold_simulation(self):
        r = self.check("good-post.md")
        self.assertEqual(r["above_fold"]["mobile"][0], "We cut customer onboarding from 14 days to 3.")

    def test_field_limits(self):
        r = json.loads(run("check.py", "field", "headline", "--text", "x" * 230, "--json"))
        self.assertEqual(r["remaining"], -10)
        self.assertTrue(any(i["severity"] == "error" for i in r["issues"]))
        r = json.loads(run("check.py", "field", "custom-url", "--text", "maya-chen-ml", "--json"))
        self.assertEqual(r["issues"], [])


@unittest.skipUnless(os.path.exists(ZIP) and os.path.exists(XLSX), "run tests/make_fixtures.py first")
class LinkedInData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp()
        cls.summary = run("linkedin_data.py", "build", ZIP, XLSX, "--out", cls.out)
        with open(os.path.join(cls.out, "posts.json"), encoding="utf-8") as f:
            cls.posts = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_outputs_written(self):
        for f in ("posts.json", "analytics.json", "profile_archive.md", "network.md", "voice.json"):
            self.assertTrue(os.path.exists(os.path.join(self.out, f)), f)

    def test_join_text_to_metrics(self):
        with_text_and_metrics = [p for p in self.posts if p.get("text") and p.get("impressions") is not None]
        self.assertEqual(len(with_text_and_metrics), 18)
        self.assertIn("18 by ID timestamp", self.summary)
        top = max(self.posts, key=lambda p: p.get("impressions") or 0)
        self.assertTrue(top["text"].startswith("5 SaaS metrics"))

    def test_analytics_sheets(self):
        with open(os.path.join(self.out, "analytics.json"), encoding="utf-8") as f:
            a = json.load(f)
        self.assertEqual(a["followers"]["total"], 4120)
        self.assertEqual(len(a["daily"]), 365)
        self.assertIn("Job titles", a["demographics"])
        self.assertAlmostEqual(a["demographics"]["Job titles"][0]["pct"], 0.14)

    def test_profile_and_network(self):
        with open(os.path.join(self.out, "profile_archive.md"), encoding="utf-8") as f:
            prof = f.read()
        self.assertIn("Fractional CFO | Finance | Startups | Ex-Stripe", prof)
        with open(os.path.join(self.out, "network.md"), encoding="utf-8") as f:
            net = f.read()
        self.assertIn("240 connections", net)
        self.assertNotIn("Person1 ", net)  # aggregate only, no names

    def test_stats_with_tags(self):
        tags = {str(p["n"]): {"topic": "on" if "CFO" in (p.get("text") or "") else "other"} for p in self.posts}
        tp = os.path.join(self.out, "tags.json")
        with open(tp, "w", encoding="utf-8") as f:
            json.dump(tags, f)
        out = run("linkedin_data.py", "stats", self.out, "--tags", tp)
        self.assertIn("## By topic", out)
        with open(os.path.join(self.out, "stats.json"), encoding="utf-8") as f:
            s = json.load(f)
        self.assertEqual(s["n"], 18)
        self.assertEqual(s["excluded_without_text"], 1)

    def test_voice_and_dashboard(self):
        out = run("linkedin_data.py", "voice", self.out, "--draft", os.path.join(FIX, "sloppy-post.md"))
        self.assertIn("Voice match: off", out)
        d = os.path.join(self.out, "dash")
        run("linkedin_data.py", "dashboard", self.out, "--out", d, "--name", "Test")
        with open(os.path.join(d, "data.js"), encoding="utf-8") as f:
            js = f.read()
        self.assertTrue(js.startswith("window.DASH = "))
        json.loads(js[len("window.DASH = "):].rstrip().rstrip(";"))

    def test_postdate(self):
        out = run("linkedin_data.py", "postdate", "https://www.linkedin.com/posts/x_y-activity-7380123456789012345-AbCd")
        self.assertIn("2025-10-04", out)
        out = run("linkedin_data.py", "postdate", "urn:li:activity:7290000000000000000", "https://www.linkedin.com/in/x")
        self.assertIn("2025-01-28", out)
        self.assertIn("no dated post ID", out)


if __name__ == "__main__":
    unittest.main()
