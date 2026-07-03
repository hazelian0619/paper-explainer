from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "skills" / "paper-explainer" / "scripts" / "check_sources.py"

spec = spec_from_file_location("check_sources", CHECKER_PATH)
assert spec is not None
assert spec.loader is not None
check_sources = module_from_spec(spec)
sys.modules[spec.name] = check_sources
spec.loader.exec_module(check_sources)


class L1CheckerTests(unittest.TestCase):
    def test_normalize_unifies_quotes_dashes_and_whitespace(self) -> None:
        text = "  Robots\u2019   claims \u2014 across\nlines  "
        self.assertEqual(check_sources.normalize(text), "robots' claims - across lines")

    def test_exact_quote_match_returns_one(self) -> None:
        source = check_sources.normalize("The method improves accuracy by 50 percent.")
        quote = check_sources.normalize("The method improves accuracy by 50 percent.")
        self.assertEqual(check_sources.best_window_ratio(quote, source), 1.0)

    def test_fuzzy_match_tolerates_small_formatting_drift(self) -> None:
        source = check_sources.normalize(
            "Combining RGB-D and LiDAR mitigates the instability of vision-only systems."
        )
        quote = check_sources.normalize(
            "Combining RGB-D and LiDAR mitigates instability of vision only systems."
        )
        self.assertGreaterEqual(
            check_sources.best_window_ratio(quote, source),
            check_sources.DEFAULT_THRESHOLD,
        )

    def test_run_l1_marks_ok_unsupported_and_skipped(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            },
            {
                "table": "Table 7",
                "cell": "Fake",
                "claim": "The method gets 99 percent on ImageNet.",
                "quote": "The method gets 99 percent on ImageNet.",
            },
            {
                "table": "Table 8",
                "cell": "Limit",
                "claim": "missing",
                "quote": "missing",
            },
        ]
        report = check_sources.run_l1(
            claims,
            "The method improves accuracy by 50 percent.",
            check_sources.DEFAULT_THRESHOLD,
        )
        self.assertEqual([result.status for result in report.results], ["ok", "unsupported", "skipped"])
        self.assertEqual(len(report.checked), 2)
        self.assertEqual(len(report.unsupported), 1)

    def test_main_json_output_and_review_exit_code(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            },
            {
                "table": "Table 7",
                "cell": "Fake",
                "claim": "The method gets 99 percent on ImageNet.",
                "quote": "The method gets 99 percent on ImageNet.",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tables = tmp_path / "claims.json"
            source = tmp_path / "source.txt"
            tables.write_text(json.dumps(claims), encoding="utf-8")
            source.write_text("The method improves accuracy by 50 percent.", encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_sources.main([
                    "--tables",
                    str(tables),
                    "--source",
                    str(source),
                    "--json",
                ])

        self.assertEqual(code, 1)
        data = json.loads(stdout.getvalue())
        self.assertEqual([result["status"] for result in data], ["ok", "unsupported"])

    def test_main_pass_exit_code(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tables = tmp_path / "claims.json"
            source = tmp_path / "source.txt"
            tables.write_text(json.dumps(claims), encoding="utf-8")
            source.write_text("The method improves accuracy by 50 percent.", encoding="utf-8")

            code = check_sources.main([
                "--tables",
                str(tables),
                "--source",
                str(source),
            ])

        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
