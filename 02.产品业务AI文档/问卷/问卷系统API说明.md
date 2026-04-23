# 问卷系统 Open API 接口定义

**配套文档**：[《问卷系统API调用说明》](./问卷系统API调用说明.md)（修订记录、概述、通用约定、接口索引、场景编排、注意事项）。  
本文聚焦：**数据模型、接口契约与参数/返回类型定义**。

---

## 一、数据模型与对象规格

### 1.1 通用响应

所有接口统一返回 `Result<T>`：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {}
}
```

### 1.2 核心请求对象

#### 1.2.1 OpenSubmissionListRequest

用于提交记录查询（分页/不分页复用）。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `surveyId` | Long | 是 | 问卷 ID |
| `department` | String | 否 | 部门名称，模糊匹配 |
| `departmentId` | Long | 否 | 部门 ID，精确匹配 |
| `employeeId` | Long | 否 | 工号 |
| `employeeName` | String | 否 | 姓名，模糊匹配 |
| `submitTimeBeginMillis` | Long | 否 | 交卷时间起（毫秒） |
| `submitTimeEndMillis` | Long | 否 | 交卷时间止（毫秒） |
| `startTimeBeginMillis` | Long | 否 | 开始答题时间起（毫秒） |
| `startTimeEndMillis` | Long | 否 | 开始答题时间止（毫秒） |
| `pageNum` | Long | 否 | 页码，从 1 开始，默认 1 |
| `pageSize` | Long | 否 | 每页条数，默认 20 |

#### 1.2.2 OpenNotifySendRequest

用于发送问卷活动通知。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeIds` | List\<Long\> | 否 | 仅通知这些员工 |
| `departmentIds` | List\<Long\> | 否 | 仅通知这些部门 ID 命中的员工 |
| `notifyMarkdown` | String | 否 | 通知文案 |
| `notifyTitle` | String | 否 | 通知标题（控制工作汇报 `main`；sendV2 场景必传） |

#### 1.2.3 SurveyTargetImportRequest

用于管理端导入活动名单。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeIdList` | List\<Long\> | 是 | 员工 ID 列表 |
| `replace` | Boolean | 否 | 是否全量覆盖，默认 `false` |
| `sourceType` | String | 否 | 来源标识，默认 `admin_import` |

### 1.3 核心响应对象（摘要）

> 完整字段释义可参考 [《问卷开放接口API说明》](./问卷开放接口API说明.md) 第六章与第八章。

- `OpenSubmissionStatusVO`：提交状态（`surveyId/submitted/submissionId/submitTimeMillis`）
- `OpenSubmissionDetailVO`：单次提交详情（含 `answers`）
- `OpenSubmissionListResponse`：分页结果（`total/pageNum/pageSize/records`）
- `OpenSubmissionListItemVO`：提交列表项
- `OpenStatisticsResponse`：统计结果（`overall/byDimension`）
- `OpenNotifySendResponse`：发送通知结果
- `OpenNotifyPressureResponse`：催办结果
- `OpenUnsubmittedParticipantVO`：未提交人员
- `SurveyTargetImportResponse`：名单导入结果（`processedCount/insertedCount/updatedCount`）
- `OpenSi2026SubmissionDetailVO`：社保专项单人提交详情（`answers` 为对象）
- `OpenSi2026StatisticsVO`：社保专项统计（`submissions` 为原始提交列表）
- `OpenSi2026SubmissionPayloadVO`：社保专项原始提交项（含 `payloadJson`）
- `OpenSi2026NotifySendResponse`：社保专项批量通知受理结果
- `OpenSi2026NotifyPressureResponse`：社保专项催办结果汇总
- `OpenSi2026NotifyPressureItemVO`：社保专项催办逐条结果

---

## 二、接口详细说明

以下接口均来自 `QuestionnaireController`（基路径：`/questionnaire`），并转发到下游 `questionnaire` 服务。

### 2.1 查询提交状态（getSubmissionStatus）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/submission/status` |
| 下游地址 | `/open/submission/status` |
| 返回类型 | `Result<OpenSubmissionStatusVO>` |

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `surveyId` | Long | 是 | 问卷 ID |
| `employeeId` | Long | 否 | 工号，与 `employeeName` 二选一 |
| `employeeName` | String | 否 | 姓名，与 `employeeId` 二选一 |

### 2.2 查询提交详情（getSubmissionDetail）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/submission/detail` |
| 下游地址 | `/open/submission/detail` |
| 返回类型 | `Result<OpenSubmissionDetailVO>` |

请求参数：`submissionId`（Long，必填）。

### 2.3 查询提交列表（分页）（listSubmissions）

| 项目 | 说明 |
|------|------|
| 方法 | `POST` |
| 接口地址 | `/questionnaire/submission/list` |
| 下游地址 | `/open/submission/list` |
| 返回类型 | `Result<OpenSubmissionListResponse>` |

请求体：`OpenSubmissionListRequest`。

### 2.4 查询统计数据（getStatistics）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/statistics` |
| 下游地址 | `/open/statistics` |
| 返回类型 | `Result<OpenStatisticsResponse>` |

请求参数：`surveyId`（必填）、`groupBy`（可选，`survey`/`dimension`）。

### 2.5 发送问卷活动通知（sendNotify）

| 项目 | 说明 |
|------|------|
| 方法 | `POST` |
| 接口地址 | `/questionnaire/notify/send` |
| 下游地址 | `/open/notify/send` |
| 返回类型 | `Result<OpenNotifySendResponse>` |

请求体：`OpenNotifySendRequest`。

### 2.6 问卷活动催办（pressureNotify）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/notify/pressure` |
| 下游地址 | `/open/notify/pressure` |
| 返回类型 | `Result<OpenNotifyPressureResponse>` |

请求参数：`surveyId`（Long，必填）。

### 2.7 查询已提交人员（按条件，不分页）（listSubmittedByCondition）

| 项目 | 说明 |
|------|------|
| 方法 | `POST` |
| 接口地址 | `/questionnaire/surveys/submitted` |
| 下游地址 | `/open/surveys/submitted` |
| 返回类型 | `Result<List<OpenSubmissionListItemVO>>` |

请求体：`OpenSubmissionListRequest`。

### 2.8 活动名单维度-已提交人员列表（listSubmittedParticipants）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/surveys/participants/submitted/list` |
| 下游地址 | `/open/surveys/participants/submitted/list` |
| 返回类型 | `Result<List<OpenSubmissionListItemVO>>` |

请求参数：`surveyId`（Long，必填）。

### 2.9 活动名单维度-未提交人员列表（listUnsubmittedParticipants）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/surveys/participants/unsubmitted/list` |
| 下游地址 | `/open/surveys/participants/unsubmitted/list` |
| 返回类型 | `Result<List<OpenUnsubmittedParticipantVO>>` |

请求参数：`surveyId`（Long，必填）。

### 2.10 导入问卷活动名单（importSurveyTargets）

| 项目 | 说明 |
|------|------|
| 方法 | `POST` |
| 接口地址 | `/questionnaire/admin/surveys/targets/import` |
| 下游地址 | `/admin/surveys/targets/import` |
| 返回类型 | `Result<SurveyTargetImportResponse>` |

请求体：`SurveyTargetImportRequest`。

### 2.11 2026 人事社保专项-查询提交详情（getSi2026SubmissionDetail）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/social-insurance/submission/detail` |
| 下游地址 | `/open/social-insurance-2026/submission/detail` |
| 返回类型 | `Result<OpenSi2026SubmissionDetailVO>` |

请求参数：`employeeId`（Long，必填）。

### 2.12 2026 人事社保专项-查询统计（getSi2026Statistics）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/social-insurance/statistics` |
| 下游地址 | `/open/social-insurance-2026/statistics` |
| 返回类型 | `Result<OpenSi2026StatisticsVO>` |

请求参数：无（按全量口径统计）。

### 2.13 2026 人事社保专项-批量发送专项通知（sendSi2026Notify）

| 项目 | 说明 |
|------|------|
| 方法 | `POST` |
| 接口地址 | `/questionnaire/social-insurance/notify/send` |
| 下游地址 | `/open/social-insurance-2026/notify/send` |
| 返回类型 | `Result<OpenSi2026NotifySendResponse>` |

请求参数：无（按专项通知名单异步受理发送）。

### 2.14 2026 人事社保专项-专项通知催办（pressureSi2026Notify）

| 项目 | 说明 |
|------|------|
| 方法 | `GET` |
| 接口地址 | `/questionnaire/social-insurance/notify/pressure` |
| 下游地址 | `/open/social-insurance-2026/notify/pressure` |
| 返回类型 | `Result<OpenSi2026NotifyPressureResponse>` |

请求参数：无（按专项通知发送结果进行催办）。

---

## 三、一致性说明（调用说明是否需要改）

已核对 `QuestionnaireController` 实际路径与 [《问卷系统API调用说明》](./问卷系统API调用说明.md)：

- 已覆盖 14 个接口；
- 已对齐社保专项外部路径为 `/questionnaire/social-insurance/**`；
- 已对齐专项统计接口无 `formCode` 入参；
- 已对齐专项通知发送/催办接口（对应下游文档 8.4/8.5）。

补充说明：下游文档 `8.3` 为 `payload_json` 结构说明，不是独立 HTTP 接口。

当前调用说明无需额外修改。若后续控制器路径再调整，请同步更新两份文档中的“本服务路径”与“下游路径”映射。

