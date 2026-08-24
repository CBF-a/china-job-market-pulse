# 发布流程

## 发布前

1. 确认 `pyproject.toml`、`src/china_job_market_pulse/__init__.py` 和 CHANGELOG 的版本一致。
2. 运行完整质量门禁：

   ```bash
   python -m pip install -e ".[dev]"
   python -m unittest discover -s tests -v
   ruff check src tests
   mypy src
   python -m build
   ```

3. 用 `data/sample_jobs.csv` 生成 Markdown、JSON、CSV 和 HTML 仪表盘，确认输出可打开且没有本地绝对路径或凭证。
4. 检查 `git diff`、依赖变化、许可证和 CHANGELOG。

## 发布步骤

1. 提交版本变更并推送到 `main`。
2. 等待 GitHub Actions 的 test、quality 和 build 三个 job 全部通过。
3. 创建与版本一致的 Git tag，例如 `v0.2.0`。
4. 在 GitHub Release 中粘贴 CHANGELOG 对应版本内容，并附上构建产物。

## 回滚

如果发布后发现阻断性问题，先在 GitHub Release 中标记受影响版本，再修复、增加回归测试并发布补丁版本。不要重写已经公开的 tag。
