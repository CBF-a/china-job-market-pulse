import tempfile
import unittest
from pathlib import Path

from china_job_market_pulse.quality import QualityThresholds, monitor_quality
from china_job_market_pulse.sources import LocalFileAdapter, SourceMetadata


class SourceAndQualityTests(unittest.TestCase):
    def test_local_adapter_records_provenance(self) -> None:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", delete=False)
        with handle:
            handle.write(
                "title,city,skills,salary_min,salary_max\n"
                "数据分析师,深圳,Python,10000,20000\n"
            )
        path = Path(handle.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        dataset = LocalFileAdapter(
            path,
            SourceMetadata("my-export", "user-provided", "user_export"),
        ).load()
        self.assertEqual(dataset.source_name, "my-export")
        self.assertEqual(dataset.source_license, "user-provided")
        self.assertEqual(dataset.access_mode, "user_export")
        self.assertEqual(dataset.jobs[0].source_name, "my-export")

    def test_quality_monitor_reports_threshold_breaches(self) -> None:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", delete=False)
        with handle:
            handle.write(
                "title,city,skills,salary_min,salary_max,posted_date\n"
                "有效职位,深圳,Python,10000,20000,2026-01-01\n"
                "有效职位,深圳,Python,10000,20000,2026-01-01\n"
                ",广州,SQL,10000,20000,2026-01-01\n"
            )
        path = Path(handle.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        dataset = LocalFileAdapter(
            path,
            SourceMetadata("fixture", "synthetic", "synthetic"),
        ).load()
        alerts = monitor_quality(dataset.quality, QualityThresholds(max_duplicate_rate=0.1))
        self.assertEqual([alert.metric for alert in alerts], ["rejected_rate", "duplicate_rate"])
        self.assertEqual(alerts[0].severity, "error")


if __name__ == "__main__":
    unittest.main()
