import json
import tempfile
import unittest
from pathlib import Path

from china_job_market_pulse.dedupe import fingerprint_job
from china_job_market_pulse.io import load_job_dataset, load_jobs
from china_job_market_pulse.models import JobPosting
from china_job_market_pulse.normalize import normalize_city, normalize_education, split_skills


class DataQualityTests(unittest.TestCase):
    def write_csv(self, content: str) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", delete=False)
        with handle:
            handle.write(content)
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return Path(handle.name)

    def test_normalization_handles_common_chinese_values(self) -> None:
        self.assertEqual(normalize_city(" 深圳市 "), "深圳")
        self.assertEqual(normalize_education("硕士及以上"), "硕士")
        self.assertEqual(split_skills("Python， SQL\nPython"), ("Python", "SQL"))

    def test_invalid_rows_are_rejected_and_reported(self) -> None:
        path = self.write_csv(
            "title,city,skills,salary_min,salary_max,posted_date,source_url\n"
            "有效职位,深圳,Python,10000,20000,2026-08-01,https://example.com/jobs/1\n"
            "错误职位,广州,SQL,30000,10000,not-a-date,ftp://example.com/jobs/2\n"
        )
        dataset = load_job_dataset(path)
        self.assertEqual(len(dataset.jobs), 1)
        self.assertEqual(dataset.quality.total_rows, 2)
        self.assertEqual(dataset.quality.accepted_rows, 1)
        self.assertEqual(dataset.quality.rejected_rows, 1)
        self.assertGreaterEqual(dataset.quality.error_count, 3)
        self.assertEqual(dataset.jobs[0].city, "深圳")
        with self.assertRaises(ValueError):
            load_jobs(path)

    def test_duplicate_rows_are_deterministically_removed(self) -> None:
        content = (
            "title,company,city,skills,salary_min,salary_max,posted_date,source_url\n"
            "数据分析师,示例公司,深圳,Python,10000,20000,2026-08-01,https://example.com/jobs/1\n"
            "数据分析师,示例公司,深圳,Python,10000,20000,2026-08-01,https://example.com/jobs/1\n"
        )
        first = load_job_dataset(self.write_csv(content))
        second = load_job_dataset(self.write_csv(content))
        self.assertEqual(len(first.jobs), 1)
        self.assertEqual(first.quality.duplicate_rows, 1)
        self.assertEqual(first.jobs[0].record_id, second.jobs[0].record_id)
        self.assertEqual(first.jobs[0].record_id, fingerprint_job(first.jobs[0]))

    def test_json_input_accepts_jobs_array(self) -> None:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
        payload = [
            {
                "title": "后端工程师",
                "city": "北京市",
                "skills": "Python, FastAPI",
                "salary_min": 18000,
                "salary_max": 30000,
            }
        ]
        with handle:
            json.dump(payload, handle, ensure_ascii=False)
        path = Path(handle.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        dataset = load_job_dataset(path)
        self.assertEqual(dataset.jobs[0].city, "北京")
        self.assertEqual(dataset.jobs[0].salary_period, "monthly")


class ModelCompatibilityTests(unittest.TestCase):
    def test_existing_positional_job_constructor_remains_usable(self) -> None:
        job = JobPosting("分析师", "公司", "上海", 10000, 20000, 2, "本科", ("SQL",))
        self.assertEqual(job.title, "分析师")
        self.assertIsNone(job.record_id)


if __name__ == "__main__":
    unittest.main()
