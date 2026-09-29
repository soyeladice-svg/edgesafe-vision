import unittest

from edgesafe.report import render_evidence_markdown


class EvidenceReportTests(unittest.TestCase):
    def test_saved_evidence_renders_without_probes(self):
        evidence = {
            "schema": "edgesafe-evidence-v1",
            "checks": [
                {"name": "python", "status": "PASS", "detail": "synthetic"},
                {"name": "demo", "status": "FAIL", "detail": "synthetic"},
            ],
        }
        report = render_evidence_markdown(evidence)
        self.assertIn("Summary: 1 PASS · 0 WARN · 1 FAIL", report)
        self.assertIn("- FAIL demo — synthetic", report)


if __name__ == "__main__":
    unittest.main()
