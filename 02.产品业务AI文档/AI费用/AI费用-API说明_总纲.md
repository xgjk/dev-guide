# AI费用查询服务 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-04-01 | 初版创建 | 刘艳华 |
| 1.1 | 2026-04-02 | 新增用户/模型/产品使用明细接口 | 刘艳华 |
| 1.2 | 2026-04-03 | 补充 inCacheToken（缓存输入Token）字段说明；修复 personId 类型 Long→String | 刘艳华 |
| 1.3 | 2026-04-20 | 新增企业级过滤支持（enterprise 参数）；新增获取企业列表接口；完善所有接口示例 | 刘艳华 |
| 1.4 | 2026-04-20 | 完善周期对比基准；统一钻取维度枚举值 | 刘艳华 |
| 1.5 | 2026-04-20 | 完善 4xxxx/61xxxx 错误码；修正周期对比逻辑；审计全量接口字段名 | 刘艳华 |

---

## 一、概述

本文档描述了 **AI费用查询服务** 对外开放的全部 API 接口。通过这些接口，可以实现以下业务能力：

1. **费用概览查询** — 获取今日、昨日、本周、本月等多时间维度的费用汇总、Token用量及环比增长率
2. **费用趋势分析** — 查询每日费用变化趋势，支持自定义时间范围
3. **周期对比分析** — 按模型/产品/人员等维度进行周环比、月环比费用对比
4. **自定义时间段查询** — 查询任意时间段的费用分布、趋势、Token用量，支持多维度筛选与钻取
5. **联动排行榜** — 查询Model/Product/Person三维度排行榜，支持二级交叉过滤
6. **产品用户分析** — 查询指定产品的用户费用统计，含人均费用、中位数、分位数等指标
7. **实体列表查询** — 获取所有AI模型、产品、人员、企业的基础信息列表
8. **使用明细查询** — 查询指定用户/模型/产品的详细使用数据，包含费用、Token、调用次数及其关联维度分布
9. **企业数据隔离** — 支持按企业维度过滤分析数据，满足多租户场景下的费用管理需求

---


---

> **二、通用说明**（访问地址、环境、请求头、响应结构、认证、数据设计）和**三、关键业务流程说明**（6个典型场景）已拆分至 [API接口明细/_通用约定.md](API接口明细/_通用约定.md)。

---

## 四、接口索引

| 编号 | 接口名称 | 接口地址 | 子文档 |
|------|----------|----------|--------|
| 4.1 | 费用总览卡片 | GET /llm-cost/overview | [费用概览与趋势](API接口明细/01-费用概览与趋势.md) |
| 4.2 | 每日费用趋势 | GET /llm-cost/trend | [费用概览与趋势](API接口明细/01-费用概览与趋势.md) |
| 4.3 | 周期对比数据 | GET /llm-cost/compare | [对比与钻取分析](API接口明细/02-对比与钻取分析.md) |
| 4.4 | 自定义时间段费用分布 | GET /llm-cost/custom-range | [对比与钻取分析](API接口明细/02-对比与钻取分析.md) |
| 4.5 | 自定义时间段费用趋势 | GET /llm-cost/custom-range/trend | [对比与钻取分析](API接口明细/02-对比与钻取分析.md) |
| 4.6 | 自定义时间段Token趋势 | GET /llm-cost/custom-range/token-trend | [对比与钻取分析](API接口明细/02-对比与钻取分析.md) |
| 4.7 | 自定义时间段钻取 | GET /llm-cost/custom-range/drilldown | [对比与钻取分析](API接口明细/02-对比与钻取分析.md) |
| 4.8 | 联动排行榜 | GET /llm-cost/custom-range/linked-rankings | [排行榜与用户统计](API接口明细/03-排行榜与用户统计.md) |
| 4.9 | 二级钻取目标趋势 | GET /llm-cost/custom-range/target-trend | [排行榜与用户统计](API接口明细/03-排行榜与用户统计.md) |
| 4.10 | 产品用户费用统计 | GET /llm-cost/product-user-stats | [排行榜与用户统计](API接口明细/03-排行榜与用户统计.md) |
| 4.11 | 获取所有AI模型列表 | GET /llm-cost/models | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |
| 4.12 | 获取所有产品列表 | GET /llm-cost/products | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |
| 4.13 | 获取所有人员列表 | GET /llm-cost/persons | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |
| 4.14 | 用户使用明细 | GET /llm-cost/user-usage | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |
| 4.15 | 模型使用明细 | GET /llm-cost/model-usage | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |
| 4.16 | 产品使用明细 | GET /llm-cost/product-usage | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |
| 4.17 | 获取企业列表 | GET /llm-cost/enterprises | [实体列表与使用明细](API接口明细/04-实体列表与使用明细.md) |

> 通用约定（访问地址、环境、请求头、响应结构、认证、数据设计）请参阅 [API接口明细/_通用约定.md](API接口明细/_通用约定.md)。


---

## 五、公共数据结构

### 5.1 TrendItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `date` | String | 日期，格式 `YYYY-MM-DD` |
| `cost` | Number | 费用（$） |

### 5.2 RangeItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 维度实体 ID |
| `name` | String | 维度实体名称 |
| `cost` | Number | 费用（$） |
| `vendor` | String | 厂商名称（仅 model 维度） |
| `enterprise_code` | String | 企业标识（仅 person 维度） |
| `total_in_token` | Long | 输入 Token 总量 |
| `total_out_token` | Long | 输出 Token 总量 |
| `total_inCacheToken` | Long | 缓存输入 Token 总量 |
| `request_count` | Long | 请求次数 |

### 5.3 CompareItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 维度实体 ID |
| `name` | String | 维度实体名称 |
| `primary_cost` | Number | 主周期费用（$） |
| `compare_cost` | Number | 对比周期费用（$） |
| `growth_rate` | Number | 增长率（%） |
| `cost_delta` | Number | 费用差额（$） |
| `vendor` | String | 厂商名称（仅 model 维度） |
| `alert_level` | String | 告警级别 |

### 5.4 TokenTrendItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `date` | String | 日期，格式 `YYYY-MM-DD` |
| `in_token` | Long | 当日输入 Token 总量 |
| `out_token` | Long | 当日输出 Token 总量 |
| `inCacheToken` | Long | 当日缓存输入 Token 总量 |

### 5.5 CompanyTrend

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `company` | String | 厂商名称 |
| `items` | Array\<TrendItem\> | 该厂商每日费用趋势，TrendItem 见 5.1 |

### 5.6 CompanyTokenTrend

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `company` | String | 厂商名称 |
| `total_in_token` | Long | 该厂商输入 Token 总量 |
| `total_out_token` | Long | 该厂商输出 Token 总量 |
| `total_inCacheToken` | Long | 该厂商缓存输入 Token 总量 |
| `items` | Array\<TokenTrendItem\> | 该厂商每日 Token 用量趋势，TokenTrendItem 见 5.4 |

### 5.7 DailyStat

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `date` | String | 日期，格式 `YYYY-MM-DD` |
| `user_count` | Integer | 当日活跃用户数 |
| `total_cost` | Number | 当日总费用（$） |
| `avg_cost_per_user` | Number | 当日人均费用（$） |
| `median_cost` | Number | 当日费用中位数 P50（$） |
| `p10_cost` | Number | 当日费用 P10 分位数（$） |
| `max_user_cost` | Number | 当日单用户最大费用（$） |
| `total_in_token` | Long | 当日总输入 Token |
| `total_out_token` | Long | 当日总输出 Token |
| `total_in_cache_token` | Long | 当日总缓存输入 Token |

### 5.8 ModelItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 模型 ID，如 `gpt-4o` |
| `name` | String | 模型名称，如 `GPT-4o` |
| `vendor` | String | 厂商名称，如 `OpenAI` |

### 5.9 ProductItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 产品 bizCode，如 `llm-inference` |
| `name` | String | 产品名称，如 `LLM推理服务` |

### 5.10 PersonItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 人员 ID，如 `zhang.san` |
| `name` | String | 人员姓名，如 `张三` |

### 5.11 ProductUsageItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `productId` | String | 产品 bizCode |
| `productName` | String | 产品名称 |
| `inputTokens` | Long | 输入 Token 总量 |
| `outputTokens` | Long | 输出 Token 总量 |
| `inCacheToken` | Long | 缓存输入 Token 总量 |
| `callCount` | Long | 调用次数 |
| `cost` | Number | 费用（$） |
| `currency` | String | 货币单位，如 `USD` |
| `models` | Array\<ModelUsageItem\> | 该产品下各模型明细，ModelUsageItem 见 5.13 |

### 5.12 ProductFlatItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `productId` | String | 产品 bizCode |
| `productName` | String | 产品名称 |
| `inputTokens` | Long | 输入 Token 总量 |
| `outputTokens` | Long | 输出 Token 总量 |
| `inCacheToken` | Long | 缓存输入 Token 总量 |
| `callCount` | Long | 调用次数 |
| `cost` | Number | 费用（$） |
| `currency` | String | 货币单位 |

### 5.13 ModelUsageItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `modelCode` | String | 模型代码（aiType），如 `gpt-4o` |
| `modelName` | String | 模型名称，如 `GPT-4o` |
| `inputTokens` | Long | 输入 Token 总量 |
| `outputTokens` | Long | 输出 Token 总量 |
| `inCacheToken` | Long | 缓存输入 Token 总量 |
| `callCount` | Long | 调用次数 |
| `cost` | Number | 费用（$） |
| `currency` | String | 货币单位 |

### 5.14 UserUsageItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `personId` | String | 用户 ID |
| `personName` | String | 用户姓名 |
| `inputTokens` | Long | 输入 Token 总量 |
| `outputTokens` | Long | 输出 Token 总量 |
| `inCacheToken` | Long | 缓存输入 Token 总量 |
| `callCount` | Long | 调用次数 |
| `cost` | Number | 费用（$） |
| `currency` | String | 货币单位 |

### 5.15 EnterpriseItem

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `code` | String | 企业标识（如 `xg`） |
| `name` | String | 企业名称 |

---

## 六、错误码说明

开放平台接口统一使用 `resultCode` 表示业务处理结果。除通用的成功（1）和失败（0）外，系统还定义了以下标准错误码，便于调用方进行精确的分支处理与异常提示：

| resultCode | 说明 | 参考信息 / 异常原因 |
| ---------- | ---------------------- | ------------------------------------------ |
| **1** | 请求成功 | success |
| **0** | 通用失败 | failure |
| **500** | 系统异常/内部错误 | 系统崩溃、微服务超时或内部异常 |
| **40001** | 参数校验失败 | 缺少必填参数或参数格式错误 |
| **40002** | 枚举值非法 | 传入了不在定义范围内的枚举值 |
| **40003** | 查询范围越界 | 时间段跨度过大（如超过 1 年） |
| **40100** | 认证失败 | `appKey` 无效或权限不足 |
| **42900** | 请求太频繁（限流） | 超过 QPS 限制，请稍后重试 |
| **610002** | `appKey` 无效 | 应用密钥不匹配或未分配 |
| **610003** | `appSecret` 无效 | 密钥校验失败 |
| **610005** | 签名 `sign` 无效 | 签名计算错误 |
| **610006** | `access_key` 无效/非最新 | 授权令牌过期或已被顶替 |
| **610007** | 授权度达到上限 | 授权额度已耗尽 |
| **610008** | 请求 URL 不在白名单 | 跨域或未白名单授权的 API 访问 |
| **610009** | 不支持的请求方法 | 例如 GET 接口使用了 POST 请求 |
| **610010** | `nonce` 防重放值无效 | `nonce` 重复使用 |
| **610011** | 时间戳 `timestamp` 无效 | 调用方系统时间相差过大（通常需在 5 分钟内） |
| **610012** | 请求太频繁（限流） | 超过 QPS 限制，请休眠后重试 |
| **610013** | 请求 API 未找到 | 404，路由错误 |
| **610014** | 应用被禁用 | 开发者应用已被管理员冻结 |
| **610015** | 无访问权限 | 未给该 `appKey` 授权对应接口调用权限 |
| **610016** | `openUserId` 无效 | 外部用户 ID 映射错误 |
| **610018** | 非当前企业用户 | 跨企业越权访问禁止 |
| **610019** | 用户已被禁用 | 对应的协同系统用户已离职或冻结 |
| **610030** | 重复的请求 | 防重放/幂等拦截 |

---

## 七、注意事项

1. **日期格式统一**：所有日期参数统一使用 `YYYY-MM-DD` 格式，如 `2026-03-31`。
2. **费用单位**：所有费用字段单位均为美元（$），保留小数点后 1～2 位。
3. **Token 统计口径**：Token 数量为原始计费 Token 数，不做二次换算。
4. **维度枚举值**：`dimension` 参数的可选值为 `company` / `model` / `product` / `person`，不同接口支持的子集可能有差异，请参照各接口说明。
5. **钻取关系**：维度间钻取关系为 model ↔ product ↔ person，不支持 company 维度的下钻。
6. **数据延迟**：费用数据可能有数分钟至数小时的延迟，不建议用于实时计费场景。
7. **AI 消费建议**：本组接口主要供 AI Agent / Skill 直接消费使用，数据直接以 JSON 返回，不需要作为其他接口的前置接口。若返回数据量较大，建议通过 `limit`、`days`、`start_date`/`end_date` 参数控制查询范围。
8. **使用明细三接口关系**：`user-usage`（4.14）、`model-usage`（4.15）、`product-usage`（4.16）分别从用户/模型/产品三个视角查询使用明细，各自返回其他两个维度的平铺分布，可互相跳转。

---

## 八、变更管理

| 项 | 说明 |
| --- | --- |
| 向后兼容要求 | 新增字段须可选，不得破坏已有字段类型；返回体新增字段不得影响旧调用方解析 |
| 废弃通知周期 | 提前 2 周通知，旧版并行期不少于 2 周 |
| 字段新增规则 | 新增字段默认值为 `null`，文档与 OpenAPI 同步更新 |
| 字段删除规则 | 先标注废弃，保留 2 周并行期后再下线 |
| 空值兼容规则 | `null` 与字段缺失等价；空数组表示无数据 |
| 顺序与分页稳定性 | 列表接口排序可能因数据更新而变化，不依赖固定顺序 |
| 变更通知人 | 产品、对接方、运维 |
