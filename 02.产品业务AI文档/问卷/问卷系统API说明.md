# 问卷系统 Open API 说明

**配套文档**：[《问卷系统API调用说明》](./问卷系统API调用说明.md)（修订记录、概述、通用约定、接口索引、场景编排、注意事项）。  
本文聚焦：**数据模型、接口契约与参数/返回类型定义**。

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|---|---|---|---|
| 1.0 | 2026-05-06 | 初版创建，基于规范重写，整合网关接口与原始定义 | AI助手 |

---

## 一、概述

本系统提供问卷收集、统计及活动的触达能力。当前能力涵盖：
1. 一般问卷的提交状态查询、分页明细查询、数据统计及名单维度的提交人员对比。
2. 问卷活动通知的发送与催办。
3. 2026 人事社保专项问卷的独立查询、统计与批量通知催办。

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境 | Base URL | 备注 |
|---|---|---|
| 生产 | `https://sg-al-cwork-web.mediportal.com.cn` | - |
| 测试 | `https://cwork-api-test.xgjktech.com.cn` | - |

### 2.3 公共请求头

| Header | 必填 | 说明 |
|---|---|---|
| `appKey` | 是 | 应用密钥（部分场景传 access-token 可兼容） |
| `Content-Type` | POST/PUT 必填 | `application/json` |

### 2.4 通用响应结构

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `resultCode` | Integer | `1` = 成功，其他 = 失败 |
| `resultMsg` | String | 成功时 `null`，失败时错误描述 |
| `data` | T | 业务数据，失败时 `null` |

### 2.5 认证与错误码

所有接口通过请求头 `appKey` 鉴权。错误码：
| resultCode | 说明 | AI 处理动作 |
|---|---|---|
| 1 | 成功 | 读取 data |
| 0 | 通用失败 | 读取 resultMsg 展示给用户 |
| 401 | 鉴权失败 | 停止重试，提示用户检查 appKey |
| 500 | 系统异常 | 稍后重试，最多 3 次 |

---

## 三、业务流程

1. **状态查询与明细**：
   `4.1 查询提交状态` -> 若已提交 -> `4.2 查询提交详情` 拉取答卷明细。
2. **列表与统计**：
   `4.3 查询提交列表`（分页） / `4.4 查询统计数据`（看板展示）。
3. **触达闭环**：
   `4.10 导入活动名单` -> `4.5 发送通知` -> `4.6 活动催办` -> `4.8/4.9 对比已/未提交名单`。
4. **2026 社保专项闭环**：
   `4.15 查询通知名单` -> `4.13 批量发送专项通知` -> `4.14 专项通知催办` -> `4.11 / 4.12 专项详情与统计复盘`。

---

## 四、接口详细说明

### 4.1 查询提交状态（getSubmissionStatus）

查询指定员工是否已提交该问卷。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/submission/status` |
| 下游地址 | `/open/submission/status` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeId` | Long | 否 | 工号，与 employeeName 二选一 |
| `employeeName` | String | 否 | 姓名，与 employeeId 二选一 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/submission/status?surveyId=1001&employeeId=123' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `OpenSubmissionStatusVO`：

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |
| `submitted` | Boolean | 是 | 是否已提交 |
| `submissionId` | Long | 是 | 提交记录 ID |
| `submitTimeMillis` | Long | 否 | (已废弃，待迁移ISO 8601) 交卷时间戳 |

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "surveyId": 1001,
    "submitted": true,
    "submissionId": 5001,
    "submitTimeMillis": 1713966600000
  }
}
```

**数据流向**

- 返回的 `submissionId` 用作 **4.2 查询提交详情** 的入参。

---

### 4.2 查询提交详情（getSubmissionDetail）

获取单次问卷提交的完整答题详情。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/submission/detail` |
| 下游地址 | `/open/submission/detail` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `submissionId` | Long | 是 | 提交记录 ID |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/submission/detail?submissionId=5001' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `OpenSubmissionDetailVO`：

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `submissionId` | Long | 是 | 提交记录 ID |
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeId` | Long | 是 | 提交人员工 ID |
| `answers` | Object | 是 | 答卷内容 JSON |

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "submissionId": 5001,
    "surveyId": 1001,
    "employeeId": 123,
    "answers": {"q1": "A"}
  }
}
```

---

### 4.3 查询提交列表（分页）（listSubmissions）

分页查询指定问卷的提交人员记录。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/submission/list` |
| 下游地址 | `/open/submission/list` |
| 请求方式 | POST |
| Content-Type | application/json |

**请求参数**

请求体为 `OpenSubmissionListRequest`（见第五章 5.1）。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/questionnaire/submission/list' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"surveyId": 1001, "pageNum": 1, "pageSize": 20}'
```

**响应参数**

`data` 类型为 `OpenSubmissionListResponse`（分页对象，包含 `total`, `records`）。
其中 `records` 的元素类型为 `OpenSubmissionListItemVO`（见第五章 5.2）。

**对比说明**

本接口与 4.7 查询已提交人员 的区别：
- 返回差异：本接口分页返回（包裹 total 等字段），4.7 直接返回全量列表。
- 场景建议：前端列表展示用 4.3，大模型数据导出或后台统计用 4.7。

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "total": 1,
    "records": [
      {
        "submissionId": 5001,
        "employeeId": 123,
        "employeeName": "张三",
        "departmentName": "研发部"
      }
    ]
  }
}
```

---

### 4.4 查询统计数据（getStatistics）

获取问卷的整体评分或维度评分统计。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/statistics` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |
| `groupBy` | String | 否 | `survey`（整卷）/ `dimension`（按维度） |

**响应参数**

`data` 类型为 `OpenStatisticsResponse`（包含 overall、byDimension 分布）。

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/statistics?surveyId=1001' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "overall": 95,
    "byDimension": {"服务态度": 98, "专业能力": 92}
  }
}
```

---

### 4.5 发送问卷活动通知（sendNotify）

向指定人员或部门发送问卷活动通知。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/notify/send` |
| 请求方式 | POST |
| Content-Type | application/json |

**请求参数**

请求体为 `OpenNotifySendRequest`（见第五章 5.3）。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/questionnaire/notify/send' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"surveyId": 1001, "employeeIds": [123]}'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {"successCount": 1}
}
```

---

### 4.6 问卷活动催办（pressureNotify）

对未提交问卷的活动名单人员发送催办通知。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/notify/pressure` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/notify/pressure?surveyId=1001' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {"successCount": 1}
}
```

---

### 4.7 查询已提交人员（按条件，不分页）

按条件全量获取已提交名单。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/surveys/submitted` |
| 请求方式 | POST |
| Content-Type | application/json |

**请求参数**

同 4.3，使用 `OpenSubmissionListRequest`（不传分页参数）。

**响应参数**

`data` 类型为 `List<OpenSubmissionListItemVO>`。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/questionnaire/surveys/submitted' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"surveyId": 1001}'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": [
    {
      "submissionId": 5001,
      "employeeId": 123,
      "employeeName": "张三",
      "departmentName": "研发部"
    }
  ]
}
```

---

### 4.8 活动名单维度-已提交人员列表

基于活动名单计算并返回已提交的人员列表。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/surveys/participants/submitted/list` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/surveys/participants/submitted/list?surveyId=1001' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": [
    {
      "submissionId": 5001,
      "employeeId": 123,
      "employeeName": "张三",
      "departmentName": "研发部"
    }
  ]
}
```

---

### 4.9 活动名单维度-未提交人员列表

基于活动名单计算并返回未提交的人员列表。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/surveys/participants/unsubmitted/list` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/surveys/participants/unsubmitted/list?surveyId=1001' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": [
    {
      "employeeId": 124,
      "employeeName": "李四",
      "departmentName": "研发部"
    }
  ]
}
```

---

### 4.10 导入问卷活动名单（importSurveyTargets）

管理端导入活动受邀名单。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/admin/surveys/targets/import` |
| 请求方式 | POST |
| Content-Type | application/json |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeIdList` | List<Long> | 是 | 员工 ID 列表 |
| `replace` | Boolean | 否 | 是否全量覆盖，默认 false |
| `sourceType` | String | 否 | 来源标识，默认 admin_import |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/questionnaire/admin/surveys/targets/import' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"surveyId": 1001, "employeeIdList": [123, 124], "replace": false}'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "processedCount": 2,
    "insertedCount": 2,
    "updatedCount": 0
  }
}
```

---

### 4.11 2026 人事社保专项-查询提交详情

获取单人的 2026 社保专项提报详情。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/social-insurance/submission/detail` |
| 请求方式 | GET |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `employeeId` | Long | 是 | 员工 ID |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/social-insurance/submission/detail?employeeId=123' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "employeeId": 123,
    "answers": {"si_base": 5000}
  }
}
```

---

### 4.12 2026 人事社保专项-查询统计

拉取全员的社保专项提报统计概览。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/social-insurance/statistics` |
| 请求方式 | GET |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/social-insurance/statistics' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "totalSubmitted": 1500,
    "submissions": []
  }
}
```

---

### 4.13 2026 人事社保专项-批量发送专项通知

后台异步发送社保专项通知。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/social-insurance/notify/send` |
| 请求方式 | POST |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/questionnaire/social-insurance/notify/send' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {"batchNo": "BN20260101"}
}
```

---

### 4.14 2026 人事社保专项-专项通知催办

无参触发社保专项的催办动作。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/social-insurance/notify/pressure` |
| 请求方式 | GET |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/social-insurance/notify/pressure' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {"pressureCount": 300}
}
```

---

### 4.15 2026 人事社保专项-通知名单查询

获取专项需通知的底表名单。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/social-insurance/notify/targets` |
| 请求方式 | GET |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/social-insurance/notify/targets' \
  -H 'appKey: XXXXXXXX'
```

**响应参数**

`data` 类型为 `OpenSi2026EmployeeListResponse`（包含 items 数组）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "requestedCount": 2,
    "returnedCount": 2,
    "items": [
      {
        "employeeId": 10001,
        "employeeName": "张三",
        "cloudEmployeeId": 10001
      },
      {
        "employeeId": 10002,
        "employeeName": "李四",
        "cloudEmployeeId": 10002
      }
    ]
  }
}
```

---

### 4.16 2026 人事社保专项-已完成填写名单查询

获取专项已完成提报的人员名单。

**基本信息**

| 项目 | 说明 |
|---|---|
| 接口地址 | `/questionnaire/social-insurance/submission/completed` |
| 请求方式 | GET |

---

## 五、公共数据结构

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/questionnaire/social-insurance/submission/completed' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "data": {
    "requestedCount": 1,
    "returnedCount": 1,
    "items": [
      {
        "employeeId": 10003,
        "employeeName": "王五",
        "cloudEmployeeId": 10003
      }
    ]
  }
}
```


### 5.1 OpenSubmissionListRequest

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |
| `department` | String | 否 | 部门名称（模糊） |
| `departmentId` | Long | 否 | 部门 ID |
| `employeeId` | Long | 否 | 员工 ID |
| `employeeName` | String | 否 | 员工姓名 |
| `pageNum` | Long | 否 | 页码 |
| `pageSize` | Long | 否 | 每页条数 |
| `submitTimeBeginMillis` | Long | 否 | (已废弃) 提交时间范围起点 |
| `submitTimeEndMillis` | Long | 否 | (已废弃) 提交时间范围止点 |

### 5.2 OpenSubmissionListItemVO

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `submissionId` | Long | 是 | 提交 ID |
| `employeeId` | Long | 是 | 员工 ID |
| `employeeName` | String | 是 | 员工姓名 |
| `departmentName` | String | 是 | 所属部门 |

### 5.3 OpenNotifySendRequest

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeIds` | List<Long> | 否 | 员工范围 |
| `departmentIds` | List<Long> | 否 | 部门范围 |
| `notifyMarkdown` | String | 否 | 通知文案 |
| `notifyTitle` | String | 否 | 通知标题 |

---

## 六、变更管理

| 项 | 约定 |
|---|---|
| 新增字段 | 必须可选（有默认值），不得破坏现有 AI 解析 |
| 删除字段 | 先标注废弃 ≥ 2 周，再下线 |
| null 处理 | null 与字段缺失等价 |
| 时间字段规范 | 遗留参数（包含 Millis）已标记废弃，新版本请统一重构为 ISO 8601 UTC 格式 |
