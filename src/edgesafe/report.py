"""Dependency-free Markdown reporting for EdgeSafe Doctor evidence."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .doctor import CheckResult

_VALID_STATUSES = ("PASS", "WARN", "FAIL")


def _coerce_result(item: CheckResult | Mapping[str, Any]) -> CheckResult:
    if isinstance(item, CheckResult):
        result = item
    elif isinstance(item, Mapping):
        try:
            result = CheckResult(
                name=str(item["name"]),
                status=str(item["status"]),
                detail=str(item["detail"]),
            )
        except KeyError as exc:
            raise ValueError(f"check is missing {exc.args[0]}") from exc
    else:
        raise ValueError("checks must contain CheckResult objects or JSON objects")

    if result.status not in _VALID_STATUSES:
        raise ValueError(f"unsupported check status: {result.status}")
    return result


def render_markdown_report(
    checks: Iterable[CheckResult | Mapping[str, Any]],
) -> str:
    """Render deterministic Markdown from existing check results."""
    results = [_coerce_result(item) for item in checks]
    counts = {status: 0 for status in _VALID_STATUSES}
    for item in results:
        counts[item.status] += 1

    lines = [
        "# EdgeSafe Diagnostic Report",
        "",
        (
            f"Summary: {counts['PASS']} PASS · "
            f"{counts['WARN']} WARN · {counts['FAIL']} FAIL"
        ),
        "",
        "## Findings",
    ]
    if results:
        lines.extend(
            f"- {item.status} {item.name} — {item.detail}" for item in results
        )
    else:
        lines.append("- No checks supplied.")

    lines.extend(["", "## Next verification"])
    first_failure = next((item for item in results if item.status == "FAIL"), None)
    if first_failure is None:
        lines.append(
            "No failing check is present. Continue with the next planned verification."
        )
    else:
        lines.append(
            f"Start with `{first_failure.name}` as a triage hint. "
            "This identifies the first failing check in supplied order; "
            "it does not prove root cause."
        )

    return "\n".join(lines) + "\n"


def render_evidence_markdown(evidence: Mapping[str, Any]) -> str:
    """Render Markdown from an existing edgesafe-evidence-v1 object."""
    if evidence.get("schema") != "edgesafe-evidence-v1":
        raise ValueError("unsupported evidence schema")
    checks = evidence.get("checks")
    if not isinstance(checks, list):
        raise ValueError("evidence checks must be a JSON array")
    return render_markdown_report(checks)


def load_evidence(path: str) -> Mapping[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read evidence: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("evidence must contain valid JSON") from exc
    if not isinstance(value, Mapping):
        raise ValueError("evidence root must be a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m edgesafe.report",
        description="Render an existing EdgeSafe Doctor evidence bundle as Markdown.",
    )
    parser.add_argument("evidence", help="Path to an edgesafe-evidence-v1 JSON bundle.")
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="Write Markdown to PATH instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        rendered = render_evidence_markdown(load_evidence(args.evidence))
    except ValueError as exc:
        parser.error(str(exc))

    if args.output:
        target = Path(args.output)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            parser.error(f"cannot write report: {exc}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
