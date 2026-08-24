import unittest

from china_job_market_pulse.analysis import analyze_jobs, classify_role, experience_bucket
from china_job_market_pulse.models import JobPosting


class MetricTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = [
            JobPosting("数据分析师", "A", "深圳", 10000, 20000, 1, "本科", ("Python", "SQL"), "2026-01-02"),
            JobPosting("Python后端工程师", "B", "深圳", 12000, 24000, 3, "硕士", ("Python", "SQL"), "2026-01-20"),
            JobPosting("财务分析", "C", "广州", None, None, 5, "本科", ("Excel",), "2026-02-01"),
            JobPosting("招聘运营", "D", "广州", 8000, 14000, None, "不限", ("Excel",), None),
        ]

    def test_experience_buckets_and_role_classification(self) -> None:
        self.assertEqual([experience_bucket(value) for value in (None, 0.5, 1, 3, 5)], ["unknown", "<1", "1-2", "3-4", "5+"])
        self.assertEqual(classify_role("数据分析师"), "data_analytics")
        self.assertEqual(classify_role("招聘运营"), "hr_recruiting")

    def test_analysis_includes_distributions_and_trends(self) -> None:
        report = analyze_jobs(self.jobs)
        self.assertEqual(report["overall"]["total_jobs"], 4)
        self.assertEqual(report["overall"]["salary_job_count"], 3)
        self.assertEqual(report["overall"]["salary_missing_rate"], 0.25)
        self.assertEqual(report["skills"][0]["name"], "Excel")
        self.assertEqual(report["skills"][0]["job_share"], 0.5)
        self.assertEqual(report["experience"][0]["name"], "unknown")
        self.assertEqual(report["education"][0]["name"], "本科")
        self.assertEqual([item["period"] for item in report["trends"]], ["2026-01", "2026-02"])
        self.assertEqual(report["insights"]["largest_job_market"], "广州")

    def test_city_ties_are_alphabetically_stable(self) -> None:
        jobs = [
            JobPosting("职位", "A", "广州", 1, 2, None, "", ("SQL",)),
            JobPosting("职位", "B", "深圳", 1, 2, None, "", ("SQL",)),
        ]
        report = analyze_jobs(jobs)
        self.assertEqual(report["insights"]["largest_job_market"], "广州")


if __name__ == "__main__":
    unittest.main()
