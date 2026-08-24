# OpenAI OSS 申请材料草稿

> 这是提交前工作稿，不是官方申请，也不代表已经获得资格、额度或 Pro 权益。提交时请以 [OpenAI Developers community](https://developers.openai.com/community) 和 OpenAI 官方文档中的当期说明为准。

## 项目事实

| 项目 | 当前内容 |
| --- | --- |
| 名称 | China Job Market Pulse |
| 仓库 | <https://github.com/CBF-a/china-job-market-pulse> |
| 许可证 | MIT，见 `LICENSE` |
| 当前版本 | 0.2.0 |
| 技术栈 | Python 3.10+、标准库运行时、可选 Ruff/Mypy/build 开发工具 |
| 演示入口 | `docs/DEMO.md`，使用 `data/sample_jobs.csv` |
| 质量证据 | 17 个测试、Ruff、Mypy、GitHub Actions、可构建 sdist/wheel |

## 项目简介

China Job Market Pulse 是一个面向中国就业市场的离线开源分析工具。它把用户有权处理的职位 CSV/JSON 转换为可复现的薪资、技能、城市、经验、学历、岗位类别和按月趋势报告，并同时输出质量摘要、来源元数据和单文件 HTML 仪表盘。

项目的重点不是收集更多个人数据，而是提供一个可审计的数据处理边界：输入字段有明确契约，坏行可以定位，重复记录有确定性指纹，来源许可和访问方式会进入报告，分析结果不依赖在线服务。

## 解决的问题

求职者、研究者和开源贡献者经常需要把零散的职位导出文件整理成可比较的指标，但常见脚本缺少字段契约、质量报告和来源记录。这个项目提供一条小而完整的本地工作流：

1. 导入 CSV/JSON 并规范化字段；
2. 报告缺失、非法和重复记录；
3. 用固定排序生成确定性分析；
4. 同时导出 Markdown、JSON、CSV 和离线仪表盘；
5. 在数据许可允许的前提下，让别人用同一命令复现结果。

## 公开证据索引

- [README.md](../README.md)：安装、CLI、数据边界和项目结构。
- [docs/DEMO.md](DEMO.md)：从样例数据生成报告和仪表盘的完整命令。
- [docs/DATA_SCHEMA.md](DATA_SCHEMA.md)：字段、单位、错误和隐私边界。
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)：模块边界和数据流。
- [docs/ROADMAP.md](ROADMAP.md)：已完成里程碑和后续工作。
- [MAINTENANCE.md](../MAINTENANCE.md)：测试、发布和反馈维护规则。
- [CHANGELOG.md](../CHANGELOG.md)：版本变化记录。
- `.github/workflows/ci.yml`：测试、静态检查和构建门禁。

## 提交前需要补齐的真实信息

请由维护者在提交前填写，不能用估计值替代：

- 维护者姓名或组织、联系邮箱和时区；
- 实际使用者数量、Issue/PR 数量和近期活跃提交；
- 可公开访问的演示链接、截图或演示视频；
- 所有输入数据的来源、许可证和再分发依据；
- 计划如何使用 OpenAI 产品或 API，以及相关成本预算；
- 需要申请的支持类型和预期使用周期；
- 是否存在商业关联、赞助、冲突或其他需要披露的事项。

## 英文申请简介草稿

```text
China Job Market Pulse is an MIT-licensed, offline-first Python toolkit for reproducible analysis of China job-market data. It accepts permissioned CSV or JSON exports and produces deterministic salary, skill, city, experience, education, role-category, and monthly-trend reports, together with data-quality summaries, source metadata, and a self-contained HTML dashboard.

The project addresses a practical reproducibility gap: job-market analyses often start from heterogeneous exports but do not document schemas, rejected rows, duplicate handling, or source permissions. China Job Market Pulse makes those boundaries explicit and keeps the core workflow local, dependency-light, and easy to audit.

The public repository includes an MIT license, documentation, synthetic sample data, 17 automated tests, Ruff and Mypy checks, GitHub Actions, release notes, and a reproducible demo. We are seeking support to improve the project’s documentation and maintainability, validate the workflow with real users, and help open-source contributors build trustworthy analyses without exposing private or unauthorized data.
```

## 提交前核对

- [ ] 官方项目页面和当期申请入口仍然有效；
- [ ] 申请要求、资格、期限和任何额度/订阅权益已按官方页面重新核对；
- [ ] 所有项目事实都能在仓库或公开演示页面验证；
- [ ] 没有把合成样例、仓库提交数或本地测试结果写成真实用户规模；
- [ ] 未在申请表或 Issue 中粘贴 API key、Cookie、个人联系方式或私人原始数据。

