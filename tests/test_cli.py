import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from china_job_market_pulse.cli import main


class CliTests(unittest.TestCase):
    def test_cli_writes_markdown_json_and_csv_reports(self) -> None:
        sample = Path(__file__).parents[1] / "data" / "sample_jobs.csv"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            markdown_path = root / "report.md"
            json_path = root / "report.json"
            csv_path = root / "report.csv"
            exit_code = main(
                [
                    "analyze",
                    str(sample),
                    "--output",
                    str(markdown_path),
                    "--json-output",
                    str(json_path),
                    "--csv-output",
                    str(csv_path),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertIn("## Monthly trend", markdown_path.read_text(encoding="utf-8"))
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], "0.2")
            self.assertEqual(report["quality"]["total_rows"], 10)
            self.assertEqual(report["analysis"]["overall"]["total_jobs"], 10)
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["section"], "overall")
            self.assertTrue(any(row["section"] == "trends" for row in rows))

    def test_dashboard_command_writes_self_contained_html(self) -> None:
        sample = Path(__file__).parents[1] / "data" / "sample_jobs.csv"
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "dashboard.html"
            exit_code = main(["dashboard", str(sample), "--output", str(output_path)])
            self.assertEqual(exit_code, 0)
            html = output_path.read_text(encoding="utf-8")
            self.assertIn("window.__JOBPULSE_REPORT__", html)
            self.assertIn("id=\"city-filter\"", html)
            self.assertIn("China Job Market Pulse", html)

    def test_cli_strict_mode_rejects_invalid_rows_and_allow_errors_keeps_valid_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "jobs.csv"
            input_path.write_text(
                "title,city,skills,salary_min,salary_max\n"
                "有效职位,深圳,Python,10000,20000\n"
                "错误职位,广州,SQL,30000,10000\n",
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                strict_code = main(["analyze", str(input_path)])
            self.assertEqual(strict_code, 2)
            self.assertIn("--allow-errors", stderr.getvalue())

            json_path = root / "allow-errors.json"
            allow_code = main(["analyze", str(input_path), "--allow-errors", "--json-output", str(json_path)])
            self.assertEqual(allow_code, 0)
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["quality"]["rejected_rows"], 1)
            self.assertEqual(report["analysis"]["overall"]["total_jobs"], 1)


if __name__ == "__main__":
    unittest.main()
