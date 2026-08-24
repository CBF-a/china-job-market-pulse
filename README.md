# China Job Market Pulse

一个面向中国就业市场的开源分析工具：把职位 CSV 转换成薪资区间、技能需求、城市热度和可复现的 Markdown/JSON 报告。

> This project is intentionally data-source agnostic. Use public, permissioned, or user-exported data and follow the terms of each source.

## 当前能力

- 统一职位数据 CSV 格式；
- 薪资中位数和平均值；
- 薪资缺失率与完整区间计数；
- 技能需求排行；
- 城市职位量和薪资对比；
- 经验、学历、岗位类别和按月趋势分布；
- CSV / JSON 数据导入；
- Markdown / JSON 报告导出；
- 无第三方运行时依赖，便于本地和离线运行。

项目的产品边界、数据契约和后续路线见：

- [产品需求文档](docs/PRD.md)
- [数据 Schema](docs/DATA_SCHEMA.md)
- [技术架构](docs/ARCHITECTURE.md)
- [开发路线图](docs/ROADMAP.md)

## 快速开始

需要 Python 3.10+。

```bash
python -m venv .venv
python -m pip install -e .
jobpulse analyze data/sample_jobs.csv -o reports/sample-report.md --json-output reports/sample-report.json
```

需要表格化输出时增加 `--csv-output reports/sample-report.csv`。输入存在坏行时，默认严格退出；使用 `--allow-errors` 可以分析有效行并把错误保留在 JSON 质量报告中。

生成本地交互式仪表盘：

```bash
jobpulse dashboard data/sample_jobs.csv -o reports/jobpulse-dashboard.html
```

仪表盘是单文件输出，不依赖外部 CDN、在线账号或额外运行服务。

激活虚拟环境：

```text
Windows PowerShell: .venv\Scripts\Activate.ps1
Windows cmd:        .venv\Scripts\activate.bat
macOS/Linux:        source .venv/bin/activate
```

不安装命令行入口时，也可以直接运行模块：

```bash
# macOS/Linux
PYTHONPATH=src python -m china_job_market_pulse.cli analyze data/sample_jobs.csv

# Windows PowerShell
$env:PYTHONPATH = "src"
python -m china_job_market_pulse.cli analyze data/sample_jobs.csv
```

## CSV 字段

必填字段：`title`, `city`, `skills`。

可选字段：`company`, `salary_min`, `salary_max`, `experience_years_min`, `education`, `posted_date`, `source_url`, `employment_type`。

薪资按“月薪人民币”解释，技能支持英文逗号、中文逗号、斜杠、分号、顿号和竖线分隔。完整规则见 [数据 Schema](docs/DATA_SCHEMA.md)。

仓库中的样例数据用于演示和测试。实际分析请使用你拥有权限的导出文件、授权接口或允许再分发的公开数据集。

## 开发与质量检查

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
git diff --check
```

Pull request 会由 GitHub Actions 在 Python 3.10、3.11 和 3.12 上运行测试与编译检查。

## 项目结构

```text
data/       合成样例数据
docs/       产品、数据、架构和路线文档
src/        Python 包与命令行入口
tests/      标准库 unittest 测试
.github/    CI、Issue 模板和 PR 模板
```

## 参与贡献

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。提交数据适配器、分析指标或文档时，请同时补充测试和来源说明。不要提交 API key、Cookie、个人联系方式、私人原始数据或其他凭证。

行为准则见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)，安全问题见 [SECURITY.md](SECURITY.md)，版本变化见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

本项目使用 [MIT License](LICENSE)。
