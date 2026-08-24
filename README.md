# China Job Market Pulse

一个面向中国就业市场的开源分析工具：把职位 CSV 转换成薪资区间、技能需求、城市热度和可复现的 Markdown 报告。

> This project is intentionally data-source agnostic. Use public, permissioned, or user-exported data and follow the terms of each source.

## 当前版本

第一版提供：

- 统一职位数据 CSV 格式；
- 薪资中位数和平均值；
- 技能需求排行；
- 城市职位量和薪资对比；
- Markdown / JSON 报告导出；
- 无第三方运行时依赖，便于快速部署。

## 快速开始

需要 Python 3.10+：

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
jobpulse analyze data/sample_jobs.csv -o reports/sample-report.md --json-output reports/sample-report.json
```

也可以不安装为命令行工具：

```bash
set PYTHONPATH=src
python -m china_job_market_pulse.cli analyze data/sample_jobs.csv
```

## CSV 字段

必填字段：`title`, `city`, `skills`。

可选字段：`company`, `salary_min`, `salary_max`, `experience_years_min`, `education`, `posted_date`, `source_url`, `employment_type`。

薪资按“月薪人民币”解释，技能支持英文逗号、中文逗号、斜杠、分号、顿号和竖线分隔。

## 开发

```bash
set PYTHONPATH=src
python -m unittest discover -s tests -v
```

后续路线：增加可插拔数据导入器、时间趋势分析、交互式可视化、匿名化数据质量检查和面向研究者的导出格式。

