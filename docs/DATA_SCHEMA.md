# 数据 Schema 与数据契约

## 1. 设计原则

项目区分三类数据：

1. **原始输入（raw）**：用户导入的原始字段，尽可能保留原值。
2. **规范化记录（normalized）**：经过类型转换、单位统一和文本标准化后的内部记录。
3. **分析输出（derived）**：由规范化记录计算出的汇总指标，不回写原始数据。

原始输入和规范化记录必须能通过记录 ID 与来源元数据关联。任何会改变统计含义的转换都应写入处理版本或质量报告。

## 2. 当前 MVP 输入字段

字段名使用 snake_case。CSV 中的必填字段为 `title`、`city`、`skills`；其余字段可以为空。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `title` | string | 是 | 职位名称，不能为空 |
| `city` | string | 是 | 工作城市或城市文本，不能为空 |
| `skills` | string | 是 | 技能文本，可用逗号、中文逗号、顿号、分号或换行分隔 |
| `company` | string | 否 | 公司名称；缺失时留空 |
| `salary_min` | number | 否 | 月薪下限，人民币元/月 |
| `salary_max` | number | 否 | 月薪上限，人民币元/月 |
| `experience_years_min` | number | 否 | 最低经验年数，可以是小数 |
| `education` | string | 否 | 学历要求原文 |
| `posted_date` | date | 否 | 职位发布时间，推荐 ISO 8601 日期 |
| `source_url` | string | 否 | 来源页面 URL，仅接受 `http`/`https` |
| `employment_type` | string | 否 | 全职、兼职、实习等原文或标准值 |

### 2.1 单位约定

- `salary_min` 和 `salary_max` 统一解释为人民币元/月。
- 若来源为年薪、日薪或其他周期，必须先转换并记录转换规则；不能直接写入月薪字段。
- 货币不是人民币时，必须先完成经明确汇率和日期标注的转换，或将该记录排除在薪资统计之外。
- 不确定的数值应为空并在质量报告中计入缺失，而不是猜测。

## 3. 当前规范化字段

以下字段已经由 `load_job_dataset` 生成。原始值保存在 `*_raw` 字段，分析默认使用规范化字段。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `title` | string | 清理空白后的职位名称 |
| `title_raw` | string | 职位名称原文 |
| `company` | string | 清理空白后的公司名称 |
| `company_raw` | string/null | 公司名称原文 |
| `city` | string | 城市标准化名称 |
| `city_raw` | string | 城市原文 |
| `salary_min` | number/null | 人民币元/月下限 |
| `salary_max` | number/null | 人民币元/月上限 |
| `salary_period` | enum/null | `monthly`、`annual`、`daily`、`unknown` |
| `experience_years_min` | number/null | 最低经验年数 |
| `education` | string | 学历要求原文 |
| `education_normalized` | enum/null | 标准学历等级 |
| `skills` | array[string] | 去空白、去重后的技能列表 |
| `skills_raw` | string | 技能原文 |
| `posted_date` | date/null | 发布时间 |
| `source_url` | string/null | 来源 URL |
| `source_name` | string/null | 数据源名称 |
| `collected_at` | datetime/null | 数据采集或导出时间 |
| `employment_type` | string/null | 用工类型 |
| `record_id` | string/null | 规范化记录的 SHA-256 稳定标识 |

导入结果还包含 `JobDataset` 元数据：`schema_version`、`source_path` 和
`DataQualityReport`。质量报告记录总行数、接收行数、拒绝行数、重复行数、错误数、警告数以及逐行问题。

当前支持 CSV 和 JSON 输入。JSON 可以是职位对象数组，也可以是包含 `jobs` 数组的对象。

## 4. 校验规则

### 4.1 错误（阻止记录进入分析）

- `title`、`city` 或 `skills` 缺失或清理后为空。
- 薪资为负数。
- `salary_min > salary_max`。
- 经验年数为负数。
- 日期无法解析为 ISO 8601 日期。
- `source_url` 存在但不是 `http` 或 `https` URL。
- 字段类型无法转换，且没有可安全保留的空值语义。

### 4.2 警告（允许进入分析，但必须计数）

- 薪资字段部分缺失。
- 学历或经验要求为“面议”“不限”等无法映射到数值的文本。
- 技能列表为空或只包含无法识别的占位文本。
- 城市名称无法映射到标准城市词典。
- 发布时间缺失或超出分析时间范围。

质量报告必须区分错误和警告，并提供记录数、字段数以及可定位的行号。

## 5. 清洗与去重

- 文本清洗只移除多余空白、统一明显的全角/半角分隔符，不删除原始字段。
- 技能拆分后去除空项，保留原出现顺序，并使用标准化值进行统计。
- 去重键由规范化的职位名称、公司、城市、薪资区间、发布时间、来源 URL 和来源名称组成，使用 SHA-256 生成稳定 `record_id`。
- 去重必须是确定性的；输出应说明输入记录数、重复记录数和保留记录数。
- 不把相似职位自动合并为同一职位，除非规则可以解释并且用户明确启用。

## 6. 示例

```csv
title,city,skills,company,salary_min,salary_max,experience_years_min,education,posted_date,source_url,employment_type
Python后端工程师,北京,"Python, FastAPI, PostgreSQL",示例科技,18000,30000,3,本科,2026-01-15,https://example.com/jobs/1,全职
```

## 7. 数据来源、隐私与安全

- 支持用户自己的导出文件、获得授权的数据接口和合法公开数据集。
- 仓库中的样例数据必须是合成数据、已公开且允许再分发的数据，或经过脱敏的数据。
- 不允许提交密码、Cookie、令牌、API key、个人联系方式或其他凭证。
- 原始文件的来源、许可、采集时间和处理版本应写入报告或伴随元数据。
- 对外发布前应检查仓库历史、日志和示例文件中是否包含敏感信息。
