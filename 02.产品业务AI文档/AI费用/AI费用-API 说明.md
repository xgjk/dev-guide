# AI费用查询服务 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-04-01 | 初版创建 | 刘艳华 |
| 1.1 | 2026-04-02 | 新增用户/模型/产品使用明细接口 | 刘艳华 |
| 1.2 | 2026-04-03 | 补充 inCacheToken（缓存输入Token）字段说明；修复 personId 类型 Long→String | 刘艳华 |

---

## 一、概述

本文档描述了 **AI费用查询服务** 对外开放的全部 API 接口。通过这些接口，可以实现以下业务能力：

1. **费用概览查询** — 获取今日、昨日、本周、本月等多时间维度的费用汇总、Token用量及环比增长率
2. **费用趋势分析** — 查询每日费用变化趋势，支持自定义时间范围
3. **周期对比分析** — 按模型/产品/人员等维度进行周环比、月环比费用对比
4. **自定义时间段查询** — 查询任意时间段的费用分布、趋势、Token用量，支持多维度筛选与钻取
5. **联动排行榜** — 查询Model/Product/Person三维度排行榜，支持二级交叉过滤
6. **产品用户分析** — 查询指定产品的用户费用统计，含人均费用、中位数、分位数等指标
7. **实体列表查询** — 获取所有AI模型、产品、人员的基础信息列表
8. **使用明细查询** — 查询指定用户/模型/产品的详细使用数据，包含费用、Token、调用次数及其关联维度分布

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/open-api/llm-cost/{接口地址}
```

### 2.2 环境信息

| 环境 | 域名/Base URL | 备注 |
| --- | --- | --- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` | - |

### 2.3 公共请求头

| Header | 说明 | 是否必填 |
| --- | --- | --- |
| `appKey` | 应用密钥，用于接口鉴权 | 是 |
| `Content-Type` | `application/json` | 按接口要求 |

### 2.4 通用响应结构

所有接口返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，其他值表示失败 |
| `resultMsg` | String | 提示信息，成功时为 `null`，失败时为错误描述 |
| `data` | T | 业务数据，不同接口类型不同，失败时为 `null` |

### 2.5 认证与安全（文档级约定）

| 项 | 说明 |
| --- | --- |
| 认证方式 | 所有接口统一在请求头中携带 `appKey` |
| Header 约定 | Header 名称固定为 `appKey`，是否必填、示例值格式与特殊说明见 **2.3 公共请求头** |
| 获取方式 | `appKey` 的申请、开通、分发、轮换流程不在本规范范围内 |
| 鉴权机制 | 仅应用级鉴权 |
| 审计日志 | 记录调用者、时间、资源、动作 |
| 行级 / 字段级权限 | 无额外行级/字段级权限约束 |
| 敏感数据 | 费用金额不视为敏感数据，直接返回 |

### 2.6 面向 AI 消费的数据设计

| 项 | 说明 |
| --- | --- |
| 最小必要返回 | 仅返回费用、Token用量、模型信息等与费用分析直接相关的字段 |
| 去重原则 | 同一维度信息不在子结构中重复返回 |
| 层级控制 | 默认 1～2 层；排行榜等场景不超过 3 层 |
| 文本控制 | 不涉及长文本返回 |
| 富文本规则 | 不适用 |
| 列表控制 | 通过 `limit` 参数控制返回数量；默认 10～50 条，最大 100 条 |
| token 控制 | 通过 `limit`、`days` 等参数控制返回规模；建议单次响应不超过 50KB |

---

## 三、关键业务流程说明

### 场景一：查看整体费用概况

> 需求：快速了解当前AI费用的总体情况

1. 调用 **4.1 费用总览卡片**（`GET /llm-cost/overview`），无参数，获取今日/昨日/本周/本月费用、环比增长率及Token用量
2. 调用 **4.2 每日费用趋势**（`GET /llm-cost/trend`），传入 `days=7`，获取近7天每日费用变化

### 场景二：按维度对比分析费用变化

> 需求：对比本周与上周各模型的费用变化，找出增长最快的模型

1. 调用 **4.3 周期对比数据**（`GET /llm-cost/compare`），传入 `period=week&dimension=model`，获取各模型本周 vs 上周的费用对比及增长率
2. 根据返回的 `chart_items` 中的 `growth_rate` 排序，定位费用增长最大的模型

### 场景三：自定义时间段多维费用分析

> 需求：分析2026年3月各产品的费用分布，并下钻查看某产品下的模型明细

1. 调用 **4.4 自定义时间段费用分布**（`GET /llm-cost/custom-range`），传入 `start_date=2026-03-01&end_date=2026-03-31&dimension=product`，获取各产品费用排名
2. 调用 **4.7 自定义时间段钻取**（`GET /llm-cost/custom-range/drilldown`），传入 `start_date=2026-03-01&end_date=2026-03-31&parent_type=product&parent_id={4.4返回的id}&child_dimension=model`，获取该产品下的模型费用明细

### 场景四：查询某产品的用户使用情况

> 需求：了解某产品近7天的用户数、人均费用、费用中位数等

1. 调用 **4.10 产品用户费用统计**（`GET /llm-cost/product-user-stats`），传入 `product={产品bizCode}&days=7`，获取每日用户数、人均费用、P50/P10、最大费用

### 场景五：查询指定模型/产品/用户的使用明细

> 需求：了解某用户在某段时间内使用了哪些产品、哪些模型，各自的费用和Token用量

1. 调用 **4.14 用户使用明细**（`GET /llm-cost/user-usage`），传入 `personId=11628&startTime=2026-03-25&endTime=2026-03-31`，获取该用户的总费用、总Token、按产品（含嵌套模型）的明细数据
2. 若需从模型视角查看，调用 **4.15 模型使用明细**（`GET /llm-cost/model-usage`），传入 `aiType=gpt-4o&startTime=2026-03-25&endTime=2026-03-31`，获取该模型被哪些产品使用、被哪些用户使用
3. 若需从产品视角查看，调用 **4.16 产品使用明细**（`GET /llm-cost/product-usage`），传入 `bizCode=llm-inference&startTime=2026-03-25&endTime=2026-03-31`，获取该产品使用了哪些模型、被哪些用户使用

---

## 四、接口详细说明

---

### 4.1 费用总览卡片

返回今日、昨日、本周、本月费用及环比增长率、Token统计。通常作为费用分析的入口，快速了解整体费用概况。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/overview` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | AI费用概览、费用仪表盘 |

**请求参数**

无参数。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 幂等，重复调用返回相同结果 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪，返回固定字段集 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/overview' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `today` | Number | 今日费用（$） |
| `yesterday` | Number | 昨日费用（$） |
| `week` | Number | 本周费用（$） |
| `last_week` | Number | 上周费用（$） |
| `month` | Number | 本月费用（$） |
| `last_month` | Number | 上月费用（$） |
| `today_growth` | Number | 今日环比增长率（%），相比昨日 |
| `week_growth` | Number | 本周环比增长率（%），相比上周 |
| `month_growth` | Number | 本月环比增长率（%），相比上月 |
| `today_in_token` | Long | 今日输入Token总量 |
| `today_out_token` | Long | 今日输出Token总量 |
| `yesterday_in_token` | Long | 昨日输入Token总量 |
| `yesterday_out_token` | Long | 昨日输出Token总量 |
| `week_in_token` | Long | 本周输入Token总量 |
| `week_out_token` | Long | 本周输出Token总量 |
| `last_week_in_token` | Long | 上周输入Token总量 |
| `last_week_out_token` | Long | 上周输出Token总量 |
| `month_in_token` | Long | 本月输入Token总量 |
| `month_out_token` | Long | 本月输出Token总量 |
| `last_month_in_token` | Long | 上月输入Token总量 |
| `last_month_out_token` | Long | 上月输出Token总量 |
| `today_inCacheToken` | Long | 今日缓存输入Token总量 |
| `yesterday_inCacheToken` | Long | 昨日缓存输入Token总量 |
| `week_inCacheToken` | Long | 本周缓存输入Token总量 |
| `last_week_inCacheToken` | Long | 上周缓存输入Token总量 |
| `month_inCacheToken` | Long | 本月缓存输入Token总量 |
| `last_month_inCacheToken` | Long | 上月缓存输入Token总量 |
| `date_ranges` | Object | 各周期对应的日期范围，如 `{"week": "3/24-3/31", "last_week": "3/17-3/24", "month": "3/1-3/31", "last_month": "2/1-2/28"}` |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "today": 12.5,
    "yesterday": 10.3,
    "week": 85.2,
    "last_week": 78.1,
    "month": 320.6,
    "last_month": 290.4,
    "today_growth": 21.4,
    "week_growth": 9.1,
    "month_growth": 10.4,
    "today_in_token": 150000,
    "today_out_token": 80000,
    "yesterday_in_token": 130000,
    "yesterday_out_token": 70000,
    "week_in_token": 950000,
    "week_out_token": 520000,
    "last_week_in_token": 880000,
    "last_week_out_token": 480000,
    "month_in_token": 3800000,
    "month_out_token": 2100000,
    "last_month_in_token": 3500000,
    "last_month_out_token": 1900000,
    "today_inCacheToken": 30000,
    "yesterday_inCacheToken": 28000,
    "week_inCacheToken": 180000,
    "last_week_inCacheToken": 160000,
    "month_inCacheToken": 720000,
    "last_month_inCacheToken": 650000,
    "date_ranges": {
      "week": "3/24-3/31",
      "last_week": "3/17-3/24",
      "month": "3/1-3/31",
      "last_month": "2/1-2/28"
    }
  }
}
```

**数据口径说明**

| 项 | 说明 |
| --- | --- |
| 费用单位 | 美元（$），保留小数点后1～2位 |
| 时间口径 | 自然日（UTC+8），"今日"为当天0点至今 |
| "本周"定义 | 本周一至今天 |
| "本月"定义 | 本月1日至今天 |
| 环比增长率 | `(当前周期 - 上一周期) / 上一周期 * 100`，单位为% |
| Token统计 | 输入Token + 输出Token分别统计 |

**权限与安全（本接口）**

| 项 | 说明 |
| --- | --- |
| 行级权限 | 同 2.5，无额外约束 |
| 字段级权限 | 无 |
| 敏感字段说明 | 无 |
| 审计日志要求 | 同 2.5 |

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 固定返回单条汇总数据，约 1KB |

---

### 4.2 每日费用趋势

返回指定天数范围内的每日费用折线图数据，用于观察费用变化趋势。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/trend` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 费用趋势分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `days` | Integer | 否 | 天数范围，取值 1～365，默认 60 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，返回指定天数内的全部每日数据 |
| 是否支持批量 | 否 |
| 幂等性要求 | 幂等 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪；默认返回天数范围内全部数据，可通过 `days` 控制范围 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/trend?days=7' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `items` | Array\<TrendItem\> | 每日费用数据列表 |

**TrendItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `date` | String | 日期，格式 `YYYY-MM-DD` |
| `cost` | Number | 当日费用（$） |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "items": [
      { "date": "2026-03-25", "cost": 11.2 },
      { "date": "2026-03-26", "cost": 12.5 },
      { "date": "2026-03-27", "cost": 10.8 }
    ]
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 60 天数据（约 60 条），可通过 `days` 缩减；单条约 50 字节 |

---

### 4.3 周期对比数据

支持周环比/月环比费用对比，可按模型/产品/人员等维度查看，支持从父维度下钻到子维度。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/compare` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 费用环比分析、维度下钻 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `period` | String | 是 | 对比周期，枚举值：`today` / `yesterday` / `week` / `last_week` / `month` / `last_month` |
| `dimension` | String | 否 | 分析维度，枚举值：`company` / `model` / `product` / `person`，默认 `company` |
| `limit` | Integer | 否 | 图表显示数量，默认 10 |
| `parent_type` | String | 否 | 钻取父维度类型，枚举值：`model` / `product` / `person` |
| `parent_id` | String | 否 | 钻取父维度 ID，与 `parent_type` 配合使用 |
| `parent_name` | String | 否 | 钻取父维度名称，用于显示 |
| `child_dimension` | String | 否 | 子维度，枚举值：`product` / `model`（仅人员钻取时使用） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 钻取说明 | 传入 `parent_type` + `parent_id` + `child_dimension` 后，从父维度下钻到子维度查看费用分布 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制返回条数；默认 10 条 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/compare?period=week&dimension=model&limit=10' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `title` | String | 对比标题，如"费用对比（本周 vs 上周）" |
| `primary_label` | String | 主周期标签，如"本周" |
| `compare_label` | String | 对比周期标签，如"上周" |
| `chart_items` | Array\<CompareItem\> | 对比数据列表 |
| `rank_items` | Array\<CompareItem\> | 排行数据列表 |

**CompareItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 维度实体 ID |
| `name` | String | 维度实体名称 |
| `primary_cost` | Number | 主周期费用（$） |
| `compare_cost` | Number | 对比周期费用（$） |
| `growth_rate` | Number | 增长率（%），可能为 `null` 表示无对比数据 |
| `cost_delta` | Number | 费用差额（$） |
| `vendor` | String | 厂商名称（仅 model 维度） |
| `alert_level` | String | 告警级别，可能为 `null` |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "title": "费用对比（本周 vs 上周）",
    "primary_label": "本周",
    "compare_label": "上周",
    "chart_items": [
      {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "primary_cost": 85.6,
        "compare_cost": 78.3,
        "growth_rate": 9.3,
        "cost_delta": 7.3,
        "vendor": "OpenAI",
        "alert_level": null
      }
    ],
    "rank_items": []
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 10 条，可通过 `limit` 调整；单条约 150 字节 |

---

### 4.4 自定义时间段费用分布

查询任意时间段的费用分布，支持按模型/产品/人员等维度聚合，支持多维度筛选。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/custom-range` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 自定义时间段费用分析、多维度费用分布 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | String | 是 | 结束日期，格式 `YYYY-MM-DD` |
| `dimension` | String | 否 | 分析维度，枚举值：`company` / `model` / `product` / `person`，默认 `company` |
| `limit` | Integer | 否 | 返回数量，默认 50 |
| `model_id` | String | 否 | 模型 ID 过滤 |
| `product_id` | String | 否 | 产品 ID 过滤 |
| `person_id` | String | 否 | 人员 ID 过滤 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 筛选说明 | `model_id` / `product_id` / `person_id` 可组合使用，实现交叉过滤 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制返回条数；默认 50 条 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/custom-range?start_date=2026-03-01&end_date=2026-03-31&dimension=model&limit=10' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `title` | String | 分布标题，如"模型费用分布" |
| `date_range` | String | 日期范围，如 `2026-03-01 ~ 2026-03-31` |
| `dimension` | String | 当前分析维度 |
| `chart_items` | Array\<RangeItem\> | 图表数据列表 |
| `rank_items` | Array\<RangeItem\> | 排行数据列表 |

**RangeItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 维度实体 ID |
| `name` | String | 维度实体名称 |
| `cost` | Number | 费用（$） |
| `vendor` | String | 厂商名称（仅 model 维度） |
| `total_in_token` | Long | 输入 Token 总量 |
| `total_out_token` | Long | 输出 Token 总量 |
| `total_inCacheToken` | Long | 缓存输入 Token 总量 |
| `request_count` | Long | 请求次数 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "title": "模型费用分布",
    "date_range": "2026-03-01 ~ 2026-03-31",
    "dimension": "model",
    "chart_items": [
      {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "cost": 125.6,
        "vendor": "OpenAI",
        "total_in_token": 950000,
        "total_out_token": 520000,
        "total_inCacheToken": 180000,
        "request_count": 15000
      }
    ],
    "rank_items": [
      {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "cost": 125.6,
        "vendor": "OpenAI",
        "total_in_token": 950000,
        "total_out_token": 520000,
        "total_inCacheToken": 180000,
        "request_count": 15000
      },
      {
        "id": "claude-3.5",
        "name": "Claude 3.5",
        "cost": 89.3,
        "vendor": "Anthropic",
        "total_in_token": 620000,
        "total_out_token": 340000,
        "total_inCacheToken": 95000,
        "request_count": 8000
      }
    ]
  }
}
```

**数据流向**

- 返回的 `id`（当 `dimension=model` 时）可用于 **4.11 获取所有AI模型列表** 的模型 ID 匹配
- 返回的 `id` 可用于 **4.7 自定义时间段钻取** 的 `parent_id` 参数，实现下钻查询

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 50 条，最大 100 条；单条约 150 字节 |

---

### 4.5 自定义时间段费用趋势

查询任意时间段的每日费用趋势，按厂商分组返回。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/custom-range/trend` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 自定义时间段费用趋势分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | String | 是 | 结束日期，格式 `YYYY-MM-DD` |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，返回指定时间段内的全部每日数据 |
| 是否支持批量 | 否 |
| 幂等性要求 | 幂等 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪；可通过缩小 `start_date`/`end_date` 范围控制数据量 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/custom-range/trend?start_date=2026-03-01&end_date=2026-03-31' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `total` | Array\<TrendItem\> | 每日总费用趋势，TrendItem 结构见 4.2 |
| `total_cost` | Number | 时间段内总费用（$） |
| `companies` | Array\<CompanyTrend\> | 按厂商分组的每日费用趋势 |

**CompanyTrend** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `company` | String | 厂商名称 |
| `items` | Array\<TrendItem\> | 该厂商每日费用趋势 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": [
      { "date": "2026-03-25", "cost": 11.2 }
    ],
    "total_cost": 320.6,
    "companies": [
      {
        "company": "OpenAI",
        "items": [
          { "date": "2026-03-25", "cost": 7.5 }
        ]
      },
      {
        "company": "Anthropic",
        "items": [
          { "date": "2026-03-25", "cost": 3.7 }
        ]
      }
    ]
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 按时间段返回每日数据；建议查询范围不超过 90 天；单条约 50 字节 |

---

### 4.6 自定义时间段Token趋势

查询任意时间段的每日 Token 用量趋势，按厂商分组返回。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/custom-range/token-trend` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | Token 用量趋势分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | String | 是 | 结束日期，格式 `YYYY-MM-DD` |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，返回指定时间段内的全部每日数据 |
| 是否支持批量 | 否 |
| 幂等性要求 | 幂等 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪；可通过缩小 `start_date`/`end_date` 范围控制数据量 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/custom-range/token-trend?start_date=2026-03-01&end_date=2026-03-31' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `total` | Array\<TokenTrendItem\> | 每日总 Token 用量趋势 |
| `total_in_token` | Long | 时间段内输入 Token 总量 |
| `total_out_token` | Long | 时间段内输出 Token 总量 |
| `total_inCacheToken` | Long | 时间段内缓存输入 Token 总量 |
| `companies` | Array\<CompanyTokenTrend\> | 按厂商分组的每日 Token 用量趋势 |

**TokenTrendItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `date` | String | 日期，格式 `YYYY-MM-DD` |
| `in_token` | Long | 当日输入 Token 总量 |
| `out_token` | Long | 当日输出 Token 总量 |
| `inCacheToken` | Long | 当日缓存输入 Token 总量 |

**CompanyTokenTrend** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `company` | String | 厂商名称 |
| `total_in_token` | Long | 该厂商输入 Token 总量 |
| `total_out_token` | Long | 该厂商输出 Token 总量 |
| `total_inCacheToken` | Long | 该厂商缓存输入 Token 总量 |
| `items` | Array\<TokenTrendItem\> | 该厂商每日 Token 用量趋势 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": [
      { "date": "2026-03-25", "in_token": 150000, "out_token": 80000, "inCacheToken": 30000 },
      { "date": "2026-03-26", "in_token": 160000, "out_token": 85000, "inCacheToken": 32000 }
    ],
    "total_in_token": 3800000,
    "total_out_token": 2100000,
    "total_inCacheToken": 720000,
    "companies": [
      {
        "company": "OpenAI",
        "total_in_token": 2500000,
        "total_out_token": 1400000,
        "total_inCacheToken": 480000,
        "items": [
          { "date": "2026-03-25", "in_token": 100000, "out_token": 55000, "inCacheToken": 20000 },
          { "date": "2026-03-26", "in_token": 110000, "out_token": 58000, "inCacheToken": 22000 }
        ]
      },
      {
        "company": "Anthropic",
        "total_in_token": 1300000,
        "total_out_token": 700000,
        "total_inCacheToken": 240000,
        "items": [
          { "date": "2026-03-25", "in_token": 50000, "out_token": 25000, "inCacheToken": 10000 },
          { "date": "2026-03-26", "in_token": 50000, "out_token": 27000, "inCacheToken": 10000 }
        ]
      }
    ]
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 按时间段返回每日数据；建议查询范围不超过 90 天；单条约 80 字节 |

---

### 4.7 自定义时间段钻取

在自定义时间段内，从父维度下钻到子维度查看费用分布。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/custom-range/drilldown` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 多维度费用下钻分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | String | 是 | 结束日期，格式 `YYYY-MM-DD` |
| `parent_type` | String | 是 | 父维度类型，枚举值：`product` / `model` / `person` |
| `parent_id` | String | 是 | 父维度 ID，来自列表接口或费用分布接口的返回值 |
| `child_dimension` | String | 是 | 子维度，枚举值：`model` / `product` / `person` |
| `limit` | Integer | 否 | 返回数量，默认 50 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制返回条数；默认 50 条 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/custom-range/drilldown?start_date=2026-03-01&end_date=2026-03-31&parent_type=model&parent_id=gpt-4o&child_dimension=product' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

响应结构与 **4.4 自定义时间段费用分布** 一致，包含 `title`、`date_range`、`dimension`、`chart_items`、`rank_items` 字段。`chart_items` / `rank_items` 中元素为 RangeItem 结构（详见 5.2）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "title": "GPT-4o → 产品费用分布",
    "date_range": "2026-03-01 ~ 2026-03-31",
    "dimension": "product",
    "chart_items": [
      {
        "id": "llm-inference",
        "name": "LLM推理服务",
        "cost": 85.6,
        "vendor": null,
        "total_in_token": 650000,
        "total_out_token": 360000,
        "total_inCacheToken": 120000,
        "request_count": 9500
      },
      {
        "id": "llm-embedding",
        "name": "LLM Embedding服务",
        "cost": 40.0,
        "vendor": null,
        "total_in_token": 300000,
        "total_out_token": 160000,
        "total_inCacheToken": 55000,
        "request_count": 5500
      }
    ],
    "rank_items": [
      {
        "id": "llm-inference",
        "name": "LLM推理服务",
        "cost": 85.6,
        "vendor": null,
        "total_in_token": 650000,
        "total_out_token": 360000,
        "total_inCacheToken": 120000,
        "request_count": 9500
      },
      {
        "id": "llm-embedding",
        "name": "LLM Embedding服务",
        "cost": 40.0,
        "vendor": null,
        "total_in_token": 300000,
        "total_out_token": 160000,
        "total_inCacheToken": 55000,
        "request_count": 5500
      }
    ]
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 50 条，最大 100 条；单条约 150 字节 |

---

### 4.8 联动排行榜

查询指定过滤条件下的 Model / Product / Person 三维度排行榜，支持二级交叉过滤。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/custom-range/linked-rankings` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 多维度交叉排行分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | String | 是 | 结束日期，格式 `YYYY-MM-DD` |
| `filter_dimension` | String | 是 | 主过滤维度，枚举值：`model` / `product` / `person` |
| `filter_id` | String | 是 | 主过滤维度 ID |
| `second_filter_dimension` | String | 否 | 二级过滤维度，枚举值：`model` / `product` / `person` |
| `second_filter_id` | String | 否 | 二级过滤 ID |
| `limit` | Integer | 否 | 返回数量，默认 50 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 联动说明 | 同时返回三个维度（model / product / person）的排行榜数据，通过 `filter_dimension` + `filter_id` 进行交叉过滤 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制返回条数；默认 50 条 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/custom-range/linked-rankings?start_date=2026-03-01&end_date=2026-03-31&filter_dimension=model&filter_id=gpt-4o&limit=20' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，包含三个维度的排行榜：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `model` | Object | 模型维度排行榜，含 `title`、`chart_items`、`rank_items` |
| `product` | Object | 产品维度排行榜，含 `title`、`chart_items`、`rank_items` |
| `person` | Object | 人员维度排行榜，含 `title`、`chart_items`、`rank_items` |

每个维度内的 `chart_items` / `rank_items` 结构同 **4.4 RangeItem**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "model": {
      "title": "模型费用排行（GPT-4o 过滤后）",
      "chart_items": [
        {
          "id": "gpt-4o",
          "name": "GPT-4o",
          "cost": 125.6,
          "vendor": "OpenAI",
          "total_in_token": 950000,
          "total_out_token": 520000,
          "total_inCacheToken": 180000,
          "request_count": 15000
        }
      ],
      "rank_items": [
        {
          "id": "gpt-4o",
          "name": "GPT-4o",
          "cost": 125.6,
          "vendor": "OpenAI",
          "total_in_token": 950000,
          "total_out_token": 520000,
          "total_inCacheToken": 180000,
          "request_count": 15000
        }
      ]
    },
    "product": {
      "title": "产品费用排行（GPT-4o 过滤后）",
      "chart_items": [
        {
          "id": "llm-inference",
          "name": "LLM推理服务",
          "cost": 95.3,
          "vendor": null,
          "total_in_token": 720000,
          "total_out_token": 390000,
          "total_inCacheToken": 135000,
          "request_count": 11000
        },
        {
          "id": "llm-embedding",
          "name": "LLM Embedding服务",
          "cost": 30.3,
          "vendor": null,
          "total_in_token": 230000,
          "total_out_token": 130000,
          "total_inCacheToken": 45000,
          "request_count": 4000
        }
      ],
      "rank_items": [
        {
          "id": "llm-inference",
          "name": "LLM推理服务",
          "cost": 95.3,
          "vendor": null,
          "total_in_token": 720000,
          "total_out_token": 390000,
          "total_inCacheToken": 135000,
          "request_count": 11000
        },
        {
          "id": "llm-embedding",
          "name": "LLM Embedding服务",
          "cost": 30.3,
          "vendor": null,
          "total_in_token": 230000,
          "total_out_token": 130000,
          "total_inCacheToken": 45000,
          "request_count": 4000
        }
      ]
    },
    "person": {
      "title": "人员费用排行（GPT-4o 过滤后）",
      "chart_items": [
        {
          "id": "zhang.san",
          "name": "张三",
          "cost": 45.2,
          "vendor": null,
          "total_in_token": 340000,
          "total_out_token": 185000,
          "total_inCacheToken": 68000,
          "request_count": 5200
        },
        {
          "id": "li.si",
          "name": "李四",
          "cost": 32.8,
          "vendor": null,
          "total_in_token": 250000,
          "total_out_token": 140000,
          "total_inCacheToken": 50000,
          "request_count": 3800
        }
      ],
      "rank_items": [
        {
          "id": "zhang.san",
          "name": "张三",
          "cost": 45.2,
          "vendor": null,
          "total_in_token": 340000,
          "total_out_token": 185000,
          "total_inCacheToken": 68000,
          "request_count": 5200
        },
        {
          "id": "li.si",
          "name": "李四",
          "cost": 32.8,
          "vendor": null,
          "total_in_token": 250000,
          "total_out_token": 140000,
          "total_inCacheToken": 50000,
          "request_count": 3800
        }
      ]
    }
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认每个维度返回 50 条；三维度合计不超过 150 条；单条约 150 字节 |

---

### 4.9 二级钻取目标趋势

在二级过滤（A ∩ B）条件下，查询第三维度 C 的趋势与分布。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/custom-range/target-trend` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 高级多维交叉分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | String | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | String | 是 | 结束日期，格式 `YYYY-MM-DD` |
| `filter_dimension` | String | 是 | 主过滤维度，枚举值：`model` / `product` / `person` |
| `filter_id` | String | 是 | 主过滤维度 ID |
| `second_filter_dimension` | String | 是 | 二级过滤维度，枚举值：`model` / `product` / `person` |
| `second_filter_id` | String | 是 | 二级过滤 ID |
| `target_dimension` | String | 是 | 目标维度（第三维），枚举值：`model` / `product` / `person` |
| `limit` | Integer | 否 | 返回数量，默认 50 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制返回条数；默认 50 条 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/custom-range/target-trend?start_date=2026-03-01&end_date=2026-03-31&filter_dimension=model&filter_id=gpt-4o&second_filter_dimension=product&second_filter_id=llm-inference&target_dimension=person&limit=20' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

响应结构与 **4.4 自定义时间段费用分布** 一致，包含 `title`、`date_range`、`dimension`、`chart_items`、`rank_items` 字段。`chart_items` / `rank_items` 中元素为 RangeItem 结构（详见 5.2）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "title": "模型 GPT-4o ∩ 产品 llm-inference → 人员费用分布",
    "date_range": "2026-03-01 ~ 2026-03-31",
    "dimension": "person",
    "chart_items": [
      {
        "id": "zhang.san",
        "name": "张三",
        "cost": 38.5,
        "vendor": null,
        "total_in_token": 290000,
        "total_out_token": 160000,
        "total_inCacheToken": 58000,
        "request_count": 4200
      },
      {
        "id": "wang.wu",
        "name": "王五",
        "cost": 22.1,
        "vendor": null,
        "total_in_token": 168000,
        "total_out_token": 92000,
        "total_inCacheToken": 33000,
        "request_count": 2400
      }
    ],
    "rank_items": [
      {
        "id": "zhang.san",
        "name": "张三",
        "cost": 38.5,
        "vendor": null,
        "total_in_token": 290000,
        "total_out_token": 160000,
        "total_inCacheToken": 58000,
        "request_count": 4200
      },
      {
        "id": "wang.wu",
        "name": "王五",
        "cost": 22.1,
        "vendor": null,
        "total_in_token": 168000,
        "total_out_token": 92000,
        "total_inCacheToken": 33000,
        "request_count": 2400
      }
    ]
  }
}
```

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 50 条，最大 100 条；单条约 150 字节 |

---

### 4.10 产品用户费用统计

查询指定产品的用户费用分析，含每日用户数、人均费用、中位数、P10 分位数、最大费用等指标。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/product-user-stats` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 产品用户活跃度与费用分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `product` | String | 是 | 产品 bizCode，来自 **4.12 获取所有产品列表** 的返回值 |
| `days` | Integer | 否 | 天数，枚举值：`7` / `15` / `30`，与 `start_date`/`end_date` 二选一 |
| `start_date` | String | 否 | 开始日期，格式 `YYYY-MM-DD`，与 `days` 二选一 |
| `end_date` | String | 否 | 结束日期，格式 `YYYY-MM-DD`，与 `days` 二选一 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 幂等性要求 | 幂等 |
| 时间参数互斥 | `days` 与 `start_date`/`end_date` 二选一；若同时传入，优先使用 `days` |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪；可通过 `days` 缩减查询范围 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/product-user-stats?product=llm-inference&days=7' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `product_name` | String | 产品名称 |
| `product_id` | String | 产品 bizCode |
| `date_range` | Object | 查询的日期范围，含 `start`、`end` 字段 |
| `daily_stats` | Array\<DailyStat\> | 每日统计数据列表 |

**DailyStat** 结构：

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

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "product_name": "LLM推理服务",
    "product_id": "llm-inference",
    "date_range": { "start": "2026-03-25", "end": "2026-03-31" },
    "daily_stats": [
      {
        "date": "2026-03-31",
        "user_count": 45,
        "total_cost": 12.5,
        "avg_cost_per_user": 0.28,
        "median_cost": 0.15,
        "p10_cost": 0.02,
        "max_user_cost": 3.8,
        "total_in_token": 150000,
        "total_out_token": 80000,
        "total_in_cache_token": 30000
      }
    ]
  }
}
```

**数据流向**

- `product` 参数的值来自 **4.12 获取所有产品列表** 返回的 `id` 字段

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 按查询天数返回每日数据（默认 7 天）；单条约 100 字节 |

---

### 4.11 获取所有AI模型列表

返回所有 AI 模型的基础信息，含模型 ID、名称、厂商。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/models` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 获取模型 ID 列表，用于其他接口的 `model_id` / `filter_id` 参数 |

**请求参数**

无参数。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，返回全部模型 |
| 幂等性要求 | 幂等 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪，返回固定字段集 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/models' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `items` | Array\<ModelItem\> | 模型列表 |

**ModelItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 模型 ID，如 `gpt-4o` |
| `name` | String | 模型名称，如 `GPT-4o` |
| `vendor` | String | 厂商名称，如 `OpenAI` |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "items": [
      { "id": "gpt-4o", "name": "GPT-4o", "vendor": "OpenAI" },
      { "id": "claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "vendor": "Anthropic" }
    ]
  }
}
```

**数据流向**

- 返回的 `id` 可用于 **4.4 自定义时间段费用分布** 的 `model_id` 参数
- 返回的 `id` 可用于 **4.3 周期对比数据** 的 `parent_id` 参数（钻取场景）

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 返回全部数据，通常不超过 100 条；单条约 80 字节 |

---

### 4.12 获取所有产品列表

返回所有产品的基础信息，按历史费用排序，支持关键词搜索。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/products` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 获取产品 ID 列表，用于其他接口的 `product_id` / `filter_id` 参数 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `search` | String | 否 | 搜索关键词，按 ID 或名称模糊匹配 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，返回全部匹配结果 |
| 幂等性要求 | 幂等 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 不支持裁剪，返回固定字段集 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/products?search=llm' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `items` | Array\<ProductItem\> | 产品列表，按历史费用降序排列 |

**ProductItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 产品 bizCode，如 `llm-inference` |
| `name` | String | 产品名称，如 `LLM推理服务` |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "items": [
      { "id": "llm-inference", "name": "LLM推理服务" },
      { "id": "llm-embedding", "name": "LLM Embedding服务" }
    ]
  }
}
```

**数据流向**

- 返回的 `id` 用于 **4.10 产品用户费用统计** 的 `product` 参数
- 返回的 `id` 可用于 **4.4 自定义时间段费用分布** 的 `product_id` 参数

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 返回全部数据，通常不超过 100 条；单条约 80 字节 |

---

### 4.13 获取所有人员列表

返回所有人员的基础信息，支持关键词模糊搜索。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/persons` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 获取人员 ID 列表，用于其他接口的 `person_id` / `filter_id` 参数 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `search` | String | 否 | 搜索关键词，按 ID 或姓名模糊匹配 |
| `limit` | Integer | 否 | 返回数量上限，默认 100 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制返回条数；默认 100 条 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/persons?search=zhang&limit=20' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `items` | Array\<PersonItem\> | 人员列表 |

**PersonItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 人员 ID，如 `zhang.san` |
| `name` | String | 人员姓名，如 `张三` |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "items": [
      { "id": "zhang.san", "name": "张三" },
      { "id": "zhang.si", "name": "张四" }
    ]
  }
}
```

**数据流向**

- 返回的 `id` 可用于 **4.4 自定义时间段费用分布** 的 `person_id` 参数

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 100 条，可通过 `limit` 调整；单条约 60 字节 |

---

### 4.14 用户使用明细

查询指定用户在指定日期范围内的AI使用明细，包含总费用、总Token用量、按产品（含嵌套模型）的费用明细。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/user-usage` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 用户维度使用明细、个人费用分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `personId` | String | 否 | 用户ID（字符串型），不传则自动使用当前登录用户 |
| `startTime` | String | 否 | 开始日期，格式 `YYYY-MM-DD`，默认当天 |
| `endTime` | String | 否 | 结束日期，格式 `YYYY-MM-DD`，默认当天 |
| `limit` | Integer | 否 | 每个维度返回数量，默认 10，最大 100 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 日期范围限制 | 最大 90 天 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制产品和模型返回条数 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/user-usage?personId=11628&startTime=2026-03-25&endTime=2026-03-31' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `query` | UserUsageQuery | 查询条件，含 `personId`、`personName`、`startTime`、`endTime`、`currency` |
| `summary` | UserUsageSummary | 汇总数据，含 `personId`、`personName`、`inputTokens`、`outputTokens`、`inCacheToken`、`callCount`、`cost`、`currency` |
| `products` | Array\<ProductUsageItem\> | 按产品分组的明细列表，每个产品内嵌套 `models` 列表 |

**ProductUsageItem** 结构：

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
| `models` | Array\<ModelUsageItem\> | 该产品下各模型的使用明细 |

**ModelUsageItem** 结构：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `modelCode` | String | 模型代码（aiType） |
| `modelName` | String | 模型名称 |
| `inputTokens` | Long | 输入 Token 总量 |
| `outputTokens` | Long | 输出 Token 总量 |
| `inCacheToken` | Long | 缓存输入 Token 总量 |
| `callCount` | Long | 调用次数 |
| `cost` | Number | 费用（$） |
| `currency` | String | 货币单位 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "query": {
      "personId": "11628",
      "personName": "张三",
      "startTime": "2026-03-25",
      "endTime": "2026-03-31",
      "currency": "USD"
    },
    "summary": {
      "personId": "11628",
      "personName": "张三",
      "inputTokens": 950000,
      "outputTokens": 520000,
      "inCacheToken": 180000,
      "callCount": 15000,
      "cost": 125.6,
      "currency": "USD"
    },
    "products": [
      {
        "productId": "llm-inference",
        "productName": "LLM推理服务",
        "inputTokens": 800000,
        "outputTokens": 450000,
        "inCacheToken": 150000,
        "callCount": 12000,
        "cost": 100.3,
        "currency": "USD",
        "models": [
          {
            "modelCode": "gpt-4o",
            "modelName": "GPT-4o",
            "inputTokens": 600000,
            "outputTokens": 350000,
            "inCacheToken": 110000,
            "callCount": 8000,
            "cost": 65.2,
            "currency": "USD"
          },
          {
            "modelCode": "claude-3.5",
            "modelName": "Claude 3.5",
            "inputTokens": 200000,
            "outputTokens": 100000,
            "inCacheToken": 40000,
            "callCount": 4000,
            "cost": 35.1,
            "currency": "USD"
          }
        ]
      }
    ]
  }
}
```

**数据流向**

- `personId` 参数可从 **4.13 获取所有人员列表** 返回的 `id` 字段获取
- 返回的 `productId` 可用于 **4.16 产品使用明细** 的 `bizCode` 参数
- 返回的 `modelCode` 可用于 **4.15 模型使用明细** 的 `aiType` 参数

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 10 个产品×嵌套模型；单次响应约 2～5KB |

---

### 4.15 模型使用明细

查询指定模型在指定日期范围内的使用明细，包含总费用、总Token用量、被哪些产品使用、被哪些用户使用。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/model-usage` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 模型维度使用明细、模型成本分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `aiType` | String | 是 | 模型代码（aiType），来自 **4.11 获取所有AI模型列表** 的 `id` |
| `startTime` | String | 否 | 开始日期，格式 `YYYY-MM-DD`，默认当天 |
| `endTime` | String | 否 | 结束日期，格式 `YYYY-MM-DD`，默认当天 |
| `limit` | Integer | 否 | 每个维度返回数量，默认 10，最大 100 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 日期范围限制 | 最大 90 天 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制产品和用户返回条数 |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/model-usage?aiType=gpt-4o&startTime=2026-03-25&endTime=2026-03-31' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `query` | Object | 查询条件，含 `aiType`、`modelName`、`startTime`、`endTime`、`currency` |
| `summary` | Object | 汇总数据，含 `aiType`、`modelName`、`inputTokens`、`outputTokens`、`inCacheToken`、`callCount`、`cost`、`currency` |
| `products` | Array\<ProductFlatItem\> | 使用该模型的产品列表（平铺，不含嵌套） |
| `users` | Array\<UserUsageItem\> | 使用该模型的用户列表 |

**ProductFlatItem** 结构：

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

**UserUsageItem** 结构：

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

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "query": {
      "aiType": "gpt-4o",
      "modelName": "GPT-4o",
      "startTime": "2026-03-25",
      "endTime": "2026-03-31",
      "currency": "USD"
    },
    "summary": {
      "aiType": "gpt-4o",
      "modelName": "GPT-4o",
      "inputTokens": 950000,
      "outputTokens": 520000,
      "inCacheToken": 180000,
      "callCount": 15000,
      "cost": 125.6,
      "currency": "USD"
    },
    "products": [
      {
        "productId": "llm-inference",
        "productName": "LLM推理服务",
        "inputTokens": 800000,
        "outputTokens": 450000,
        "inCacheToken": 150000,
        "callCount": 12000,
        "cost": 100.3,
        "currency": "USD"
      }
    ],
    "users": [
      {
        "personId": "11628",
        "personName": "张三",
        "inputTokens": 600000,
        "outputTokens": 350000,
        "inCacheToken": 110000,
        "callCount": 8000,
        "cost": 65.2,
        "currency": "USD"
      }
    ]
  }
}
```

**数据流向**

- `aiType` 参数来自 **4.11 获取所有AI模型列表** 返回的 `id` 字段
- 返回的 `productId` 可用于 **4.16 产品使用明细** 的 `bizCode` 参数
- 返回的 `personId` 可用于 **4.14 用户使用明细** 的 `personId` 参数

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 10 条产品和 10 条用户；单次响应约 2～5KB |

---

### 4.16 产品使用明细

查询指定产品在指定日期范围内的使用明细，包含总费用、总Token用量、使用了哪些模型、被哪些用户使用。

**基本信息**

| 项目 | 说明 |
| --- | --- |
| 接口地址 | `/llm-cost/product-usage` |
| 请求方式 | `GET` |
| Content-Type | 不适用（GET 请求无 Body） |
| 接口负责人 | liuyanhua |
| 所属模块 | AI费用查询服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 产品维度使用明细、产品成本分析 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `bizCode` | String | 是 | 产品代码（bizCode），来自 **4.12 获取所有产品列表** 的 `id`。注意：部分 bizCode 包含斜杠，如 `/meetingChat/splitSummary` |
| `startTime` | String | 否 | 开始日期，格式 `YYYY-MM-DD`，默认当天 |
| `endTime` | String | 否 | 结束日期，格式 `YYYY-MM-DD`，默认当天 |
| `limit` | Integer | 否 | 每个维度返回数量，默认 10，最大 100 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否，通过 `limit` 控制返回数量 |
| 幂等性要求 | 幂等 |
| 日期范围限制 | 最大 90 天 |
| 是否支持批量 | 否 |
| 额外字段策略 | 不适用（无请求体） |
| 返回裁剪策略 | 通过 `limit` 控制模型和用户返回条数 |
| bizCode 含斜杠 | bizCode 作为查询参数传递，斜杠不影响路由（URL 编码为 `%2F`） |

**请求示例**

```bash
curl -X GET 'https://cwork-api-test.xgjktech.com.cn/open-api/llm-cost/product-usage?bizCode=llm-inference&startTime=2026-03-25&endTime=2026-03-31' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `Object`，字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `query` | Object | 查询条件，含 `bizCode`、`productName`、`startTime`、`endTime`、`currency` |
| `summary` | Object | 汇总数据，含 `bizCode`、`productName`、`inputTokens`、`outputTokens`、`inCacheToken`、`callCount`、`cost`、`currency` |
| `models` | Array\<ModelUsageItem\> | 该产品使用的各模型明细，结构见 4.14 ModelUsageItem |
| `users` | Array\<UserUsageItem\> | 使用该产品的各用户明细，结构见 4.15 UserUsageItem |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "query": {
      "bizCode": "llm-inference",
      "productName": "LLM推理服务",
      "startTime": "2026-03-25",
      "endTime": "2026-03-31",
      "currency": "USD"
    },
    "summary": {
      "bizCode": "llm-inference",
      "productName": "LLM推理服务",
      "inputTokens": 950000,
      "outputTokens": 520000,
      "inCacheToken": 180000,
      "callCount": 15000,
      "cost": 125.6,
      "currency": "USD"
    },
    "models": [
      {
        "modelCode": "gpt-4o",
        "modelName": "GPT-4o",
        "inputTokens": 600000,
        "outputTokens": 350000,
        "inCacheToken": 110000,
        "callCount": 8000,
        "cost": 65.2,
        "currency": "USD"
      }
    ],
    "users": [
      {
        "personId": "11628",
        "personName": "张三",
        "inputTokens": 600000,
        "outputTokens": 350000,
        "inCacheToken": 110000,
        "callCount": 8000,
        "cost": 65.2,
        "currency": "USD"
      }
    ]
  }
}
```

**数据流向**

- `bizCode` 参数来自 **4.12 获取所有产品列表** 返回的 `id` 字段
- 返回的 `modelCode` 可用于 **4.15 模型使用明细** 的 `aiType` 参数
- 返回的 `personId` 可用于 **4.14 用户使用明细** 的 `personId` 参数

**权限与安全（本接口）**

同 2.5，无额外约束。

**性能与稳定性（本接口）**

| 项 | 说明 |
| --- | --- |
| 目标 SLA | 遵循平台默认策略 |
| 超时阈值 | 建议客户端 5s |
| 限流策略 | 遵循平台默认策略 |
| 重试策略 | 可重试，退避 1s |
| 熔断策略 | 无 |
| 缓存策略 | 建议缓存 1～5 分钟 |
| token 控制策略 | 默认返回 10 条模型和 10 条用户；单次响应约 2～5KB |

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

---

## 六、错误码说明

| resultCode | 说明 |
| --- | --- |
| 1 | 请求成功 |
| 0 | 通用失败 |
| 500 | 系统异常 |

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
