# Markdown report

Use `python -m edgesafe.report` with a saved EdgeSafe evidence JSON file. The optional output flag writes the generated Markdown to a file. The Python function `render_evidence_markdown` renders the same saved evidence mapping. Rendering is deterministic, preserves supplied order and reports PASS, WARN and FAIL counts. Any first-failure guidance is a triage hint only and is not a root-cause claim.
