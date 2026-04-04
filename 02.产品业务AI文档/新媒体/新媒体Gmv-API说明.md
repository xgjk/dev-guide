# 新媒体GMV Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-26 | 初版创建 | — |
| 1.1 | 2026-03-26 | 按规范重构文档结构，补全通用说明、错误码、注意事项等章节 | — |

为便于人与 AI 追溯变更历史，所有修订记录必须使用统一格式的四列表格，包含以下字段：**版本**、**日期**、**变更摘要**、**变更人**。

**核心规则：**
- 每次内容变更**必须在表格末尾追加新行**，不得修改、覆盖或删除任何历史行。

---

## 一、概述

本文档描述了**新媒体 GMV 数据看板**模块对外开放的全部 API 接口。通过这些接口，可以实现以下业务能力：

1. **GMV 总览** — 查询所有品牌（或指定品牌）在指定年月下的 GMV 目标、实际完成、达成率汇总，以及各平台明细
2. **GMV 明细** — 通过 `type` 参数灵活查询年/季/月维度下各平台的目标或完成矩阵，以及每日明细
3. **每日聚合明细** — 查询底层每日汇总表，返回逐行原始记录，适合数据核查与导出

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/api/{接口地址}
```

### 2.2 环境信息

| 环境 | Base URL |
|------|----------|
| 测试环境 | `https://xg-node.xgjktech.com.cn/api` |

### 2.3 公共请求头

| Header | 说明 | 是否必填 |
|--------|------|---------|
| `Authorization` | Bearer Token，格式：`Bearer {token}`，请联系管理员获取 | 是 |

### 2.4 通用响应结构

所有接口返回统一结构：

```json
{
  "data": { }
}
```

| 字段 | 说明 |
|------|------|
| `data` | 业务数据，不同接口类型不同；失败时接口返回对应 HTTP 状态码 |

---

## 三、关键业务流程说明

### 概览：我应该查哪个接口？

| 我想查什么 | 用哪个接口 | type 参数 |
|-----------|-----------|----------|
| 某品牌/全部品牌的年/季/月 GMV 目标与达成汇总 | `GET /kol/gmv-dashboard/overview` | — |
| 某品牌全年12个月 × 各平台的**目标**分解 | `GET /kol/gmv-dashboard/detail` | `yearTarget` |
| 某品牌今年1~N月 × 各平台的**实际完成**分解 | `GET /kol/gmv-dashboard/detail` | `yearActual` |
| 某品牌当前季度3个月 × 各平台的**目标**分解 | `GET /kol/gmv-dashboard/detail` | `quarterTarget` |
| 某品牌某月各平台的**目标** | `GET /kol/gmv-dashboard/detail` | `monthTarget` |
| 某品牌某月各平台的**实际完成** | `GET /kol/gmv-dashboard/detail` | `monthActual` |
| 某品牌某平台某月**每天**的 GMV | `GET /kol/gmv-dashboard/detail` | `dailyActual` |
| 查看中转表中的每日聚合明细（逐行原始记录） | `GET /kol/gmv-dashboard/gmv-summary` | — |

### 平台与渠道说明

| 渠道 | 平台名（接口中使用的值） |
|------|----------------------|
| O2O | 美团、饿了么、京东到家 |
| B2C | 阿里、京东、抖音、拼多多 |

`overview` 接口返回的 `platforms` 对象键名格式为 `平台名 + "GMV"`，例如 `"美团GMV"`、`"阿里GMV"`。

### 关键计算逻辑说明

> 理解这些计算规则，才能正确解读接口返回的数值。

#### 累计达成率

`overview` 接口返回的 `yearRate`、`quarterRate`、`monthRate` 均为**累计达成率**，含义是：**从周期起点到今天的实际完成值，占整个周期完整目标的百分比**。

```
年累计达成率  = yearActual（1月1日~今天的完成）  / yearTarget（全年12个月目标之和）  × 100
季累计达成率  = quarterActual（季初~今天的完成）  / quarterTarget（当季3个月目标之和）  × 100
月累计达成率  = monthActual（月初1日~今天的完成） / monthTarget（当月完整目标）         × 100
```

**重点：分子是截至今天的累计实际值，分母是完整周期的目标总量。**
例如：3月26日，月目标50万，截至今天完成18万 → 月累计达成率 = 18/50 = 36%（不是100%，因为月还没结束）。

#### 时间进度（timeProgress）

用于判断达成是否"跑赢进度"。

```
yearProgress    = (今天 - 1月1日的天数)   / 全年总天数   × 100
quarterProgress = (今天 - 季初第1天的天数) / 当季总天数   × 100
monthProgress   = (今日日期 - 1)          / 本月总天数   × 100
```

**使用方式：达成率 ≥ 时间进度 → 跑赢进度（好），达成率 < 时间进度 → 落后进度（差）。**

#### 渠道占比（b2cRate / o2oRate）

```
b2cRate = B2C渠道年累计完成 / 该品牌年总完成 × 100
o2oRate = O2O渠道年累计完成 / 该品牌年总完成 × 100
```

两者之和 = 100%（均基于年度实际完成值，非目标）。

---

## 四、接口详细说明

---

### 4.1 GMV 总览

返回所有品牌（或指定品牌）在指定年月下的 GMV 目标、实际完成、达成率汇总，以及各平台明细。这是最常用的入口接口。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/kol/gmv-dashboard/overview` |
| 请求方式 | `GET` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| year | Number | 否 | 年份，默认当前年 |
| month | Number | 否 | 月份（1-12），默认当前月。影响"当月"和"季度"的计算范围 |
| brand | String | 否 | 品牌名。不传或空字符串 = 返回全部品牌。**⚠️ 中文必须 URL 编码（UTF-8）** |

**响应参数**

| 字段 | 说明 |
|------|------|
| `timeProgress.yearProgress` | 年度时间进度（%）：今天已过全年天数的占比，与 yearRate 对比判断是否跑赢 |
| `timeProgress.quarterProgress` | 季度时间进度（%） |
| `timeProgress.monthProgress` | 月度时间进度（%） |
| `yearTarget` | 全年目标（元）= 1~12月目标之和 |
| `yearActual` | 年累计完成（元）：1月1日到今天的实际 GMV 合计 |
| `yearRate` | 年累计达成率（%）= yearActual / yearTarget × 100 |
| `quarterTarget` | 当前季度目标（元）= 季内3个月目标之和 |
| `quarterActual` | 季度累计完成（元）：季初到今天 |
| `quarterRate` | 季度累计达成率（%）= quarterActual / quarterTarget × 100 |
| `monthTarget` | 当月完整目标（元） |
| `monthActual` | 月累计完成（元）：月初1日到今天 |
| `monthRate` | 月累计达成率（%）= monthActual / monthTarget × 100，月未结束时通常 < 100% |
| `b2cActual` | 年度 B2C 渠道完成合计（元） |
| `o2oActual` | 年度 O2O 渠道完成合计（元） |
| `b2cRate` | B2C 占年度总完成的比例（%）= b2cActual / yearActual × 100 |
| `o2oRate` | O2O 占年度总完成的比例（%）= o2oActual / yearActual × 100 |
| `platforms` | 各平台的目标/完成/达成率三维度明细，键名 = 平台名 + "GMV"（如 "美团GMV"） |
| `total` | 所有品牌的汇总行，结构同 brands 中单项 |

**响应示例**

```json
{
  "data": {
    "timeProgress": {
      "currentDate": "2026-03-26",
      "currentQuarter": 1,
      "currentMonth": 3,
      "yearProgress": 22.74,
      "quarterProgress": 25.50,
      "monthProgress": 35.48
    },
    "brands": [
      {
        "brand": "亿活",
        "yearTarget": 5000000,
        "yearActual": 1200000,
        "yearRate": 24.00,
        "quarterTarget": 1500000,
        "quarterActual": 360000,
        "quarterRate": 24.00,
        "monthTarget": 500000,
        "monthActual": 180000,
        "monthRate": 36.00,
        "b2cActual": 800000,
        "o2oActual": 400000,
        "b2cRate": 66.67,
        "o2oRate": 33.33,
        "platforms": {
          "美团GMV": {
            "type": "O2O",
            "monthTarget": 100000,
            "monthActual": 60000,
            "monthRate": 60.00,
            "quarterTarget": 300000,
            "quarterActual": 120000,
            "quarterRate": 40.00,
            "yearTarget": 1200000,
            "yearActual": 350000,
            "yearRate": 29.17
          },
          "饿了么GMV": { "...": "同上结构" },
          "京东到家GMV": { "...": "同上结构" },
          "阿里GMV": { "...": "同上结构" },
          "京东GMV": { "...": "同上结构" },
          "抖音GMV": { "...": "同上结构" },
          "拼多多GMV": { "...": "同上结构" }
        }
      }
    ],
    "total": {
      "brand": "合计",
      "yearTarget": 15000000,
      "yearActual": 3500000,
      "yearRate": 23.33,
      "...": "结构同 brands 中单项"
    }
  }
}
```

**请求示例**

```bash
curl -X GET 'https://xg-node.xgjktech.com.cn/api/kol/gmv-dashboard/overview?year=2026&month=3' \
  -H 'Authorization: Bearer {token}'
```

**数据流向**

返回的 `brands[*].brand` 品牌名可作为 **4.2 GMV 明细** 的 `brand` 入参。

---

### 4.2 GMV 明细

一个多用途接口，通过 `type` 参数决定返回内容。支持查询目标矩阵、按月/平台拆分的完成值、每日明细。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/kol/gmv-dashboard/detail` |
| 请求方式 | `GET` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| year | Number | 是 | 年份 |
| month | Number | 是 | 月份（1-12） |
| brand | String | 是 | 品牌名。传 `"合计"` 表示查所有品牌的合计。**⚠️ 中文必须 URL 编码（UTF-8）** |
| type | String | 是 | 查询类型，见下方说明 |
| platform | String | type=`dailyActual` 时必填 | 平台名，如 `"美团"` |

**type 参数取值**

| type | 查询内容 | 返回格式 |
|------|---------|---------|
| `yearTarget` | 全年12个月 × 各平台的**目标**矩阵 | 矩阵（见下方"矩阵格式"） |
| `yearActual` | 今年1月至当前月 × 各平台的**实际完成**矩阵 | 矩阵 |
| `quarterTarget` | 当前季度3个月 × 各平台的**目标**矩阵 | 矩阵 |
| `monthTarget` | 当月各平台的**目标**列表 | 列表（见下方"列表格式"） |
| `monthActual` | 当月各平台的**实际完成**列表 | 列表 |
| `dailyActual` | 指定平台指定月份每天的 GMV | 列表 |

**矩阵格式返回值（yearTarget / yearActual / quarterTarget）**

行 = 时间维度（月份），列 = 平台 + 合计。

```json
{
  "data": {
    "columns": [
      { "key": "label", "label": "月份" },
      { "key": "美团", "label": "美团" },
      { "key": "饿了么", "label": "饿了么" },
      { "key": "京东到家", "label": "京东到家" },
      { "key": "阿里", "label": "阿里" },
      { "key": "京东", "label": "京东" },
      { "key": "抖音", "label": "抖音" },
      { "key": "拼多多", "label": "拼多多" },
      { "key": "合计", "label": "合计" }
    ],
    "rows": [
      { "label": "1月", "美团": 100000, "饿了么": 80000, "合计": 500000 },
      { "label": "2月", "美团": 110000, "饿了么": 85000, "合计": 520000 }
    ],
    "totalRow": { "label": "合计", "美团": 1200000, "饿了么": 960000, "合计": 6000000 }
  }
}
```

> `yearTarget` 固定12行；`yearActual` 行数 = 当前月份数；`quarterTarget` 固定3行。

**列表格式返回值（monthTarget / monthActual）**

行 = 平台，每行一个金额值。

```json
{
  "data": {
    "rows": [
      { "label": "美团", "type": "O2O", "value": 100000 },
      { "label": "饿了么", "type": "O2O", "value": 80000 },
      { "label": "京东到家", "type": "O2O", "value": 50000 },
      { "label": "阿里", "type": "B2C", "value": 150000 },
      { "label": "京东", "type": "B2C", "value": 120000 },
      { "label": "抖音", "type": "B2C", "value": 90000 },
      { "label": "拼多多", "type": "B2C", "value": 60000 }
    ],
    "totalRow": { "label": "合计", "value": 650000 }
  }
}
```

**列表格式返回值（dailyActual）**

行 = 日期，每行一个金额值。只返回有数据的日期。

```json
{
  "data": {
    "rows": [
      { "label": "03-01", "value": 15000 },
      { "label": "03-02", "value": 18000 },
      { "label": "03-15", "value": 22000 }
    ],
    "totalRow": { "label": "合计", "value": 350000 }
  }
}
```

> `label` 格式为 `"MM-DD"`，金额单位为元。

**请求示例**

```bash
# 查询亿活品牌全年目标矩阵
# brand 参数：原始值"亿活"，URL 编码后：%E4%BA%BF%E6%B4%BB
curl -X GET 'https://xg-node.xgjktech.com.cn/api/kol/gmv-dashboard/detail?year=2026&month=3&brand=%E4%BA%BF%E6%B4%BB&type=yearTarget' \
  -H 'Authorization: Bearer {token}'

# 查询亿活品牌美团平台3月每日完成
curl -X GET 'https://xg-node.xgjktech.com.cn/api/kol/gmv-dashboard/detail?year=2026&month=3&brand=%E4%BA%BF%E6%B4%BB&type=dailyActual&platform=%E7%BE%8E%E5%9B%A2' \
  -H 'Authorization: Bearer {token}'
```

---

### 4.3 每日聚合明细（逐行查询）

查询底层的每日汇总表，返回逐行记录（每行 = 某天某品牌某平台的 GMV）。适合用于数据核查、导出。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/kol/gmv-dashboard/gmv-summary` |
| 请求方式 | `GET` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | String | 否 | 平台名筛选，如 `"美团"` |
| brand | String | 否 | 品牌名筛选。**⚠️ 中文必须 URL 编码（UTF-8）** |
| startDate | String | 否 | 开始日期，格式 `YYYY-MM-DD` |
| endDate | String | 否 | 结束日期，格式 `YYYY-MM-DD` |
| page | Number | 否 | 页码，默认 1 |
| pageSize | Number | 否 | 每页条数，默认 20 |

**响应参数**

| 字段 | 说明 |
|------|------|
| `list[*].summary_date` | 日期，`YYYY-MM-DD` |
| `list[*].brand` | 品牌名 |
| `list[*].platform` | 平台名 |
| `list[*].platform_type` | 渠道：`O2O` 或 `B2C` |
| `list[*].gmv_amount` | 当日该平台该品牌的 GMV（元） |
| `total` | 总记录数 |
| `page` | 当前页码 |
| `pageSize` | 每页条数 |

**响应示例**

```json
{
  "data": {
    "list": [
      {
        "id": 1,
        "summary_date": "2026-03-25",
        "brand": "亿活",
        "platform": "美团",
        "platform_type": "O2O",
        "gmv_amount": 15000.50
      }
    ],
    "total": 3000,
    "page": 1,
    "pageSize": 20
  }
}
```

**请求示例**

```bash
# brand 参数：原始值"亿活"，URL 编码后：%E4%BA%BF%E6%B4%BB
curl -X GET 'https://xg-node.xgjktech.com.cn/api/kol/gmv-dashboard/gmv-summary?brand=%E4%BA%BF%E6%B4%BB&startDate=2026-03-01&endDate=2026-03-31&page=1&pageSize=20' \
  -H 'Authorization: Bearer {token}'
```

---

## 五、公共数据结构

### 5.1 平台明细对象（platforms 子项）

`overview` 接口返回的 `brands[*].platforms` 中每个平台键对应的对象结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | String | 渠道类型：`O2O` 或 `B2C` |
| `monthTarget` | Number | 当月目标（元） |
| `monthActual` | Number | 当月累计完成（元） |
| `monthRate` | Number | 当月累计达成率（%） |
| `quarterTarget` | Number | 当季目标（元） |
| `quarterActual` | Number | 当季累计完成（元） |
| `quarterRate` | Number | 当季累计达成率（%） |
| `yearTarget` | Number | 全年目标（元） |
| `yearActual` | Number | 年累计完成（元） |
| `yearRate` | Number | 年累计达成率（%） |

---

## 六、错误码说明

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 401 | 鉴权失败，Authorization 头缺失或 token 无效 |
| 400 | 请求参数错误（如必填参数缺失、type 值非法） |
| 500 | 系统异常，请稍后重试 |

---

## 七、注意事项

1. **认证 Token**：所有接口必须在请求头中携带 `Authorization: Bearer {token}`，token 请联系管理员获取，不得将真实 token 提交至代码仓库或文档。
2. **金额单位**：所有 GMV 金额字段单位均为**元**，前端展示时按需换算为万元。
3. **达成率含义**：`yearRate`、`quarterRate`、`monthRate` 均为**累计达成率**（分子为截至今天的实际值，分母为完整周期目标），在周期未结束时通常小于 100%，不代表最终完成率。
4. **时间进度对比**：`timeProgress` 中的 `yearProgress`/`quarterProgress`/`monthProgress` 用于与对应达成率对比，达成率 ≥ 时间进度为跑赢，否则为落后。
5. **dailyActual 必填 platform**：`type=dailyActual` 时 `platform` 参数为必填，且只返回有数据的日期（无数据的日期不返回行）。
6. **分页页码从 1 开始**：`gmv-summary` 接口的 `page` 参数从 1 开始计数。
