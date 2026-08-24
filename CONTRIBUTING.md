# 贡献指南

感谢参与 China Job Market Pulse。项目希望把职位数据分析做成可复现、可解释、尊重数据来源和隐私的开源工具。

## 开始之前

1. 阅读 [产品需求文档](docs/PRD.md)、[数据 Schema](docs/DATA_SCHEMA.md) 和 [技术架构](docs/ARCHITECTURE.md)。
2. 搜索现有 Issue，避免重复提交。
3. 对较大的功能先开 Issue，说明使用场景、输入输出和验收标准。
4. 不要在 Issue、日志、测试 fixture 或提交历史中放入凭证和私人数据。

## 本地开发

```bash
python -m venv .venv
python -m pip install -e .
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

项目当前使用 Python 标准库 `unittest`，核心运行路径不要求第三方运行时依赖。

## 分支与提交

- 从 `main` 创建短生命周期分支，例如 `feat/data-quality` 或 `fix/csv-error`。
- 一个提交尽量只表达一个可回滚的逻辑变化。
- 提交信息使用简短的 Conventional Commits 风格前缀：`feat:`、`fix:`、`docs:`、`test:`、`refactor:`、`chore:`。
- 不要提交生成的 `reports/`、`build/`、`dist/`、`*.egg-info/` 和本地虚拟环境。

## 代码约定

- 目标 Python 版本为 3.10+。
- 公共函数需要清晰的参数、返回值和错误语义；复杂规则应有注释或文档。
- 处理输入数据时优先保留原始值，并让清洗结果可解释。
- 排序、去重和聚合必须是确定性的。
- 错误信息应尽可能包含文件、行号、字段名和修复方向。
- 新增指标时同时增加正常、缺失和边界案例测试。

## 数据与适配器要求

- 只使用公开、获得授权或用户主动导出的数据。
- 数据源适配器必须说明来源、许可、字段映射、采集时间和失败策略。
- 不实现绕过登录、验证码、访问控制或频率限制的逻辑。
- 不采集或提交姓名、电话、邮箱、账号信息等非必要个人数据。
- 样例数据必须是合成、已公开且允许再分发，或经过脱敏的数据。

## Pull request 检查清单

- [ ] 已说明变更目的、范围和不包含的内容。
- [ ] 已补充或更新测试。
- [ ] 已运行 `python -m unittest discover -s tests -v`。
- [ ] 已运行 `python -m compileall -q src tests`。
- [ ] 已运行 `git diff --check`。
- [ ] 已更新相关文档、Schema 或 CHANGELOG。
- [ ] 已确认没有凭证、个人信息和不应提交的原始数据。
- [ ] 如果改变输出格式，已说明兼容性影响。

维护者会根据产品范围、数据许可、可复现性和测试质量进行审阅。
