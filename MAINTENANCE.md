# 维护记录与发布节奏

本文档把项目从“能运行”维护到“可持续复现”的最低流程固定下来。

## 日常维护

- 每个功能或修复都要有对应测试，数据字段变化要同步更新 `docs/DATA_SCHEMA.md`。
- 每次导入都保留来源名称、许可、访问方式和质量摘要；无法确认授权时不合并数据。
- Issue 先按 `bug`、`data-quality`、`feature`、`documentation` 或 `security` 分类，再确认是否能用样例或最小 fixture 复现。
- 不在仓库、Issue、日志或报告中提交 API key、Cookie、个人联系方式和私人原始数据。

## 发布前检查

在准备版本标签前，维护者执行：

```bash
python -m unittest discover -s tests -v
ruff check src tests
mypy src
python -m build
git diff --check
```

然后确认：

- `CHANGELOG.md` 已记录用户可见变化；
- `pyproject.toml`、包版本和发布标签一致；
- `README.md` 的命令在干净环境可运行；
- 样例数据仍为合成或已获再分发许可；
- CI 的 test、quality 和 build 三类任务均为绿色；
- 构建产物中没有凭证、私人数据或本地路径。

## 建议节奏

- 小修复：合并后随时发布 patch 版本或累积到下一次小版本。
- 新指标或兼容字段：先更新 Schema、测试和 CHANGELOG，再发布 minor 版本。
- 破坏性数据契约变化：提高主版本，提供迁移说明，并保留旧输入的清晰错误信息。
- 每月至少检查一次依赖、CI 运行环境和来源许可；如果项目没有新数据或新代码，也记录一次检查结果。

## 反馈闭环模板

每次发布后可在 Issue 或发布说明中记录：

```text
版本：
日期：
验证环境：
新增反馈：
已修复问题：
未解决问题：
下一步：
```

当前版本的公开事实以仓库中的测试、CI、CHANGELOG 和路线图为准；使用量、用户数量、截图和视频应在实际产生后再补录。

