import unittest
from pathlib import Path

from china_job_market_pulse.analysis import analyze_jobs
from china_job_market_pulse.io import load_jobs, split_skills
from china_job_market_pulse.models import JobPosting


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = [
            JobPosting("分析师", "A", "深圳", 10_000, 20_000, 1, "本科", ("Python", "SQL")),
            JobPosting("数据分析师", "B", "深圳", 12_000, 24_000, 2, "本科", ("Python", "SQL")),
            JobPosting("财务分析", "C", "广州", 8_000, 16_000, 1, "本科", ("Excel",)),
        ]

    def test_split_skills_supports_chinese_separators(self) -> None:
        self.assertEqual(split_skills("Python， SQL/Excel; Python"), ("Python", "SQL", "Excel"))

    def test_report_counts_and_medians(self) -> None:
        report = analyze_jobs(self.jobs)
        self.assertEqual(report["overall"]["total_jobs"], 3)
        self.assertEqual(report["overall"]["city_count"], 2)
        self.assertEqual(report["overall"]["salary_max_median"], 20_000)
        self.assertEqual(report["insights"]["most_demanded_skill"], "Python")
        self.assertEqual(report["insights"]["largest_job_market"], "深圳")

    def test_empty_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            analyze_jobs([])

    def test_sample_csv_is_loadable(self) -> None:
        sample_path = Path(__file__).parents[1] / "data" / "sample_jobs.csv"
        jobs = load_jobs(sample_path)
        self.assertEqual(len(jobs), 10)
        self.assertEqual(jobs[0].city, "深圳")
        self.assertIn("Python", jobs[0].skills)


if __name__ == "__main__":
    unittest.main()
