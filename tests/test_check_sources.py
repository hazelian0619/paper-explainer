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

spec = spec_from_file_location("_paper_explainer_check_sources_under_test", CHECKER_PATH)
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

    def test_run_l1_marks_too_short_quotes_invalid(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Overclaim",
                "claim": "The paper proves robots outperform humans by 99 percent.",
                "quote": "The",
            }
        ]
        report = check_sources.run_l1(
            claims,
            "The survey discusses multimodal robots in human robot interaction.",
            check_sources.DEFAULT_THRESHOLD,
        )

        self.assertEqual(report.results[0].status, "invalid_quote")
        self.assertEqual(len(report.invalid_quotes), 1)
        self.assertEqual(len(report.unsupported), 0)

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

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_sources.main([
                    "--tables",
                    str(tables),
                    "--source",
                    str(source),
                ])

        self.assertEqual(code, 0)

    def test_main_short_quote_exits_one_and_reports_invalid_quote(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Overclaim",
                "claim": "The paper proves robots outperform humans by 99 percent.",
                "quote": "The",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tables = tmp_path / "claims.json"
            source = tmp_path / "source.txt"
            tables.write_text(json.dumps(claims), encoding="utf-8")
            source.write_text(
                "The survey discusses multimodal robots in human robot interaction.",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_sources.main([
                    "--tables",
                    str(tables),
                    "--source",
                    str(source),
                ])

        self.assertEqual(code, 1)
        self.assertIn("L1 quote quality: 1 invalid", stdout.getvalue())
        self.assertIn("VERDICT: REVIEW NEEDED", stdout.getvalue())


class StrictModeTests(unittest.TestCase):
    def _install_fake_anthropic(self, responses: list[str]) -> None:
        response_iter = iter(responses)

        class FakeMessage:
            def __init__(self, text: str):
                self.content = [type("Content", (), {"text": text})()]

        class FakeMessages:
            def create(self, **_kwargs):
                return FakeMessage(next(response_iter))

        class FakeAnthropic:
            def __init__(self):
                self.messages = FakeMessages()

        original = sys.modules.get("anthropic")
        had_original = "anthropic" in sys.modules
        sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=FakeAnthropic)

        def restore() -> None:
            if had_original:
                sys.modules["anthropic"] = original
            else:
                sys.modules.pop("anthropic", None)

        self.addCleanup(restore)

    def _ok_report(self):
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            }
        ]
        return check_sources.run_l1(
            claims,
            "The method improves accuracy by 50 percent.",
            check_sources.DEFAULT_THRESHOLD,
        )

    def _run_l2_with_response(self, response: str):
        self._install_fake_anthropic([response])
        report = self._ok_report()
        check_sources.run_l2(report, "fake-model")
        return report

    def test_l2_judge_errors_make_strict_mode_review_needed(self) -> None:
        report = self._run_l2_with_response("not json")

        self.assertEqual(len(report.l2_errors), 1)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            check_sources.print_report(report, strict=True)

        self.assertIn("L2 supports    : 0 supported / 0 citation-swap / 1 judge-error", stdout.getvalue())
        self.assertIn("VERDICT: REVIEW NEEDED", stdout.getvalue())

    def test_l2_string_false_support_is_judge_error(self) -> None:
        report = self._run_l2_with_response(
            '{"supports": "false", "reason": "not supported"}'
        )

        self.assertIsNone(report.results[0].l2_supports)
        self.assertEqual(len(report.l2_errors), 1)
        self.assertIn("supports", report.results[0].l2_reason)

    def test_l2_missing_support_is_judge_error(self) -> None:
        report = self._run_l2_with_response('{"reason": "not supported"}')

        self.assertIsNone(report.results[0].l2_supports)
        self.assertEqual(len(report.l2_errors), 1)
        self.assertIn("supports", report.results[0].l2_reason)

    def test_l2_false_support_is_citation_swap(self) -> None:
        report = self._run_l2_with_response(
            '{"supports": false, "reason": "quote does not support claim"}'
        )

        self.assertFalse(report.results[0].l2_supports)
        self.assertEqual(len(report.citation_swaps), 1)
        self.assertEqual(len(report.l2_errors), 0)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            check_sources.print_report(report, strict=True)

        self.assertIn("citation-swap", stdout.getvalue())
        self.assertIn("VERDICT: REVIEW NEEDED", stdout.getvalue())

    def test_l2_success_clears_stale_error_state(self) -> None:
        report = self._run_l2_with_response("not json")
        self.assertEqual(len(report.l2_errors), 1)

        self._install_fake_anthropic(['{"supports": true, "reason": "direct support"}'])
        check_sources.run_l2(report, "fake-model")

        self.assertTrue(report.results[0].l2_supports)
        self.assertEqual(report.results[0].l2_reason, "direct support")
        self.assertFalse(report.results[0].l2_error)

    def test_main_strict_malformed_judge_response_exits_one(self) -> None:
        claims = [
            {
                "table": "Table 1",
                "cell": "Core",
                "claim": "The method improves accuracy.",
                "quote": "The method improves accuracy by 50 percent.",
            }
        ]
        self._install_fake_anthropic(['{"supports": "false", "reason": "not supported"}'])
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
                    "--strict",
                    "--model",
                    "fake-model",
                ])

        self.assertEqual(code, 1)
        self.assertIn("judge-error", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
