# 本地演示指南

这份指南使用仓库内的合成职位数据，演示从导入、质量检查、分析报告到离线仪表盘的完整流程。样例数据不代表真实劳动力市场，也不应被当作招聘或薪资建议。

## 运行演示

在仓库根目录执行：

```bash
python -m venv .venv
python -m pip install -e .
mkdir -p reports
jobpulse analyze data/sample_jobs.csv \
  -o reports/sample-report.md \
  --json-output reports/sample-report.json \
  --csv-output reports/sample-report.csv
jobpulse dashboard data/sample_jobs.csv \
  -o reports/jobpulse-dashboard.html
```

Windows PowerShell 中，`mkdir -p reports` 可以替换为：

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
```

打开 `reports/jobpulse-dashboard.html` 即可查看仪表盘；它是单文件页面，不需要启动服务器、登录账号或加载第三方 CDN。

## 演示检查点

样例数据包含 10 条职位记录、4 个城市，日期集中在 2026 年 8 月。运行后可以检查：

- Markdown 报告包含薪资统计、城市、技能、经验、学历、岗位类别和月份趋势；
- JSON 报告包含 `schema_version`、`analysis_version`、来源元数据和质量摘要；
- CSV 报告按指标展开，便于在表格工具中继续检查；
- 仪表盘的城市筛选会同步更新职位数、薪资和分布图；
- 质量摘要显示本次样例没有被拒绝的记录，且薪资字段完整率为 100%。

如果不希望安装命令行入口，也可以直接运行：

```powershell
$env:PYTHONPATH = "src"
python -m china_job_market_pulse.cli analyze data/sample_jobs.csv -o reports/sample-report.md
python -m china_job_market_pulse.cli dashboard data/sample_jobs.csv -o reports/jobpulse-dashboard.html
```

## 使用真实数据前

只导入你有权处理的数据，例如自己的导出文件、获得许可的公开数据集或授权 API 导出。运行时建议记录来源信息：

```bash
jobpulse analyze export.csv \
  -o reports/export-report.md \
  --source-name "你的数据来源" \
  --source-license "填写适用许可" \
  --access-mode user_export \
  --allow-errors
```

不要把 API key、Cookie、手机号、私人原始数据或未获授权的抓取结果提交到仓库。

## 反馈清单

试用者反馈时请尽量附上：

1. 操作系统、Python 版本和安装方式；
2. 使用的是样例、自己的导出文件还是公开数据集；
3. 可复现的命令和最小化后的字段示例；
4. 期望结果、实际结果和完整错误信息；
5. 若涉及数据问题，说明来源许可和是否可以公开样本。

涉及安全、凭证或隐私问题时，请按 [SECURITY.md](../SECURITY.md) 的方式报告，不要在公开 Issue 中粘贴敏感数据。

