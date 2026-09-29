import unittest

from edgesafe.doctor import CheckResult
from edgesafe.report import render_markdown_report


class MarkdownReportCountTests(unittest.TestCase):
    def test_counts_order_and_triage_hint(self):
        results = [
            CheckResult("python", "PASS", "synthetic pass"),
            CheckResult("camera", "WARN", "synthetic warning"),
            CheckResult("broker", "FAIL", "synthetic failure"),
            CheckResult("file", "FAIL", "synthetic missing"),
        ]
        report = render_markdown_report(results)
        self.assertIn("Summary: 1 PASS · 1 WARN · 2 FAIL", report)
        self.assertLess(report.index("- PASS python"), report.index("- WARN camera"))
        self.assertLess(report.index("- WARN camera"), report.index("- FAIL broker"))
        self.assertLess(report.index("- FAIL broker"), report.index("- FAIL file"))
        self.assertIn("broker", report)
        self.assertIn("triage hint", report)
        self.assertIn("does not prove root cause", report)


if __name__ == "__main__":
    unittest.main()
