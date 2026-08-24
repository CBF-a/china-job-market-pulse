## 变更说明

<!-- 说明这个 PR 解决了什么问题，以及主要改动。 -->

## 验收方式

<!-- 写出运行过的命令或可复现步骤。 -->

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
git diff --check
```

## 检查清单

- [ ] 已补充或更新测试。
- [ ] 已更新相关文档或 CHANGELOG。
- [ ] 已确认没有凭证、个人信息或未授权原始数据。
- [ ] 已确认输出格式和 Schema 的兼容性影响。
- [ ] 这个 PR 的范围足够小，便于审阅和回滚。
