# 问卷系统 Open API 调用说明

**配套文档**：
- [《问卷开放接口API说明》](./问卷开放接口API说明.md)（questionnaire 下游原始接口与数据结构定义）
- [《BP系统API调用说明》](./BP系统API调用说明.md)（调用说明体例参考）
- [《OPS系统API调用说明》](./OPS系统API调用说明.md)（本仓新增文档体例参考）

本文承担：**修订记录、能力概述、通用约定、接口索引、编排场景、注意事项**；字段级结构以《问卷开放接口API说明》为准。

---

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-04-21 | 基于本次新增 `QuestionnaireController` + `QuestionnaireFeign` 生成调用说明 | OpenAPI-Agent |
| 1.1 | 2026-04-21 | 新增管理端导入接口（`/questionnaire/admin/surveys/targets/import`）调用说明 | OpenAPI-Agent |
| 1.2 | 2026-04-21 | `sendNotify` 请求体新增通知文案字段 `notifyMarkdown` | OpenAPI-Agent |
| 1.3 | 2026-04-21 | `sendNotify` 请求体新增通知标题字段 `notifyTitle`（sendV2 场景必传） | OpenAPI-Agent |
| 1.4 | 2026-04-21 | 新增 2026 人事社保专项查询接口（提交详情、专项统计）调用说明 | OpenAPI-Agent |
| 1.5 | 2026-04-21 | `getSi2026Statistics` 移除 `formCode` 传参，统一按全量口径查询 | OpenAPI-Agent |
| 1.6 | 2026-04-21 | 对齐实际代码路径：专项接口外部路径修正为 `/questionnaire/social-insurance/**` | OpenAPI-Agent |

---

## 一、概述

本服务在 `open-api` 网关层新增了问卷聚合控制器：`QuestionnaireController`，对外统一暴露 `/questionnaire/**` 路径，并透传到下游 `questionnaire` 服务的 `/open/**` 接口。

当前开放能力共 12 个（与当前代码一致）：

1. `getSubmissionStatus` — 查询提交状态
2. `getSubmissionDetail` — 查询提交详情
3. `listSubmissions` — 查询提交列表（分页）
4. `getStatistics` — 查询统计数据
5. `sendNotify` — 发送问卷活动通知
6. `pressureNotify` — 问卷活动催办
7. `listSubmittedByCondition` — 查询已提交人员（按条件，不分页）
8. `listSubmittedParticipants` — 活动名单维度-已提交人员列表
9. `listUnsubmittedParticipants` — 活动名单维度-未提交人员列表
10. `importSurveyTargets` — 导入问卷活动名单（管理端补充）
11. `getSi2026SubmissionDetail` — 2026 人事社保专项提交详情（按 employeeId）
12. `getSi2026Statistics` — 2026 人事社保专项统计

---

## 二、给 AI / Agent 的阅读顺序

1. 先看本文 **四、通用说明**（鉴权头、统一响应结构、路径规则）。
2. 再看本文 **五、接口清单（索引）**（本服务路径与下游路径映射）。
3. 需要字段细节时，再看 [《问卷开放接口API说明》](./问卷开放接口API说明.md) 的“六、公共数据结构”。
4. 需要调用链路编排时，看本文 **七、关键业务流程说明**。

---

## 三、关键词与别名

| 用语 | 英文路径片段 | 说明 |
|------|--------------|------|
| 问卷 | `survey` | 问卷主标识为 `surveyId` |
| 提交记录 | `submission` | 提交主键为 `submissionId` |
| 已提交名单 | `submitted` | 可按条件或按活动名单口径查询 |
| 未提交名单 | `unsubmitted` | 活动名单口径下的差集人员 |
| 通知/催办 | `notify` / `pressure` | 问卷活动触达能力 |
| 名单导入 | `targets/import` | 活动名单导入，支持增量与全量覆盖 |
| 社保专项 | `social-insurance` | 2026 人事社保专项查询能力（下游仍为 `social-insurance-2026`） |

---

## 四、通用说明

### 4.1 访问地址

```text
https://{域名}/open-api/{接口地址}
```

### 4.2 环境信息

| 环境 | 域名                                          |
|------|---------------------------------------------|
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` |
| 测试环境 | `https://cwork-api-test.xgjktech.com.cn` |

### 4.3 公共请求头

| Header | 说明 | 是否必填 |
|--------|------|----------|
| `appKey` | 应用访问凭证（网关统一校验） | 是（兼容性见下） |

**兼容性**：部分场景下若传入合法 `access-token`，即使不带 `appKey` 也可兼容通过（由网关鉴权链路处理）。

### 4.4 通用响应结构

所有接口统一返回 `Result<T>`：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `resultCode` | Integer | `1` 表示成功，其他值表示失败 |
| `resultMsg` | String | 失败时返回可读错误信息 |
| `data` | T | 业务数据 |

### 4.5 时间字段口径

- 与下游文档一致：问卷域时间字段使用**毫秒时间戳**（例如 `submitTimeMillis`）。

---

## 五、接口清单（索引）

> 下表左侧“本服务路径”为 `open-api` 暴露路径（`QuestionnaireController`），右侧“下游路径”为 `questionnaire` 服务路径（`QuestionnaireFeign`）。

| 小节 | 规范命名 | 方法 | 本服务路径 | 下游路径 | 读写 | 摘要 |
|------|----------|------|------------|----------|------|------|
| 5.1 | getSubmissionStatus | GET | `/questionnaire/submission/status` | `/open/submission/status` | 读 | 查询提交状态 |
| 5.2 | getSubmissionDetail | GET | `/questionnaire/submission/detail` | `/open/submission/detail` | 读 | 查询提交详情 |
| 5.3 | listSubmissions | POST | `/questionnaire/submission/list` | `/open/submission/list` | 读 | 提交列表分页 |
| 5.4 | getStatistics | GET | `/questionnaire/statistics` | `/open/statistics` | 读 | 评分统计 |
| 5.5 | sendNotify | POST | `/questionnaire/notify/send` | `/open/notify/send` | 写 | 发送活动通知 |
| 5.6 | pressureNotify | GET | `/questionnaire/notify/pressure` | `/open/notify/pressure` | 写 | 问卷催办 |
| 5.7 | listSubmittedByCondition | POST | `/questionnaire/surveys/submitted` | `/open/surveys/submitted` | 读 | 条件已提交名单 |
| 5.8 | listSubmittedParticipants | GET | `/questionnaire/surveys/participants/submitted/list` | `/open/surveys/participants/submitted/list` | 读 | 活动名单口径已提交 |
| 5.9 | listUnsubmittedParticipants | GET | `/questionnaire/surveys/participants/unsubmitted/list` | `/open/surveys/participants/unsubmitted/list` | 读 | 活动名单口径未提交 |
| 5.10 | importSurveyTargets | POST | `/questionnaire/admin/surveys/targets/import` | `/admin/surveys/targets/import` | 写 | 导入活动名单（管理端） |
| 5.11 | getSi2026SubmissionDetail | GET | `/questionnaire/social-insurance/submission/detail` | `/open/social-insurance-2026/submission/detail` | 读 | 2026 社保专项提交详情 |
| 5.12 | getSi2026Statistics | GET | `/questionnaire/social-insurance/statistics` | `/open/social-insurance-2026/statistics` | 读 | 2026 社保专项统计 |

---

## 六、推荐拉取路径（Agent）

**路径 A（状态先行）**：`5.1 -> 5.2`  
适合已知员工/提交记录，先判定是否提交，再拉详情。

**路径 B（统计看板）**：`5.4`  
直接获取整卷或维度统计，用于看板与 AI 摘要。

**路径 C（名单运营）**：`5.5 -> 5.6 -> 5.8/5.9`  
先通知，再催办，最后复盘已提交与未提交名单。

**路径 D（明细导出）**：`5.3` 或 `5.7`  
- 需要分页：走 `5.3`  
- 需要按条件全量已提交：走 `5.7`

**路径 E（名单初始化）**：`5.10 -> 5.5 -> 5.6`  
先导入活动名单，再发送通知，最后对未提交对象催办。

**路径 F（社保专项分析）**：`5.11 -> 5.12`  
先按员工查询单人提交详情，再直接拉取专项全量统计做横向分析。

---

## 七、关键业务流程说明

### 场景一：查询某员工是否已完成问卷

1. 调 `5.1`：`GET /questionnaire/submission/status?surveyId={id}&employeeId={empId}`
2. 若 `submitted=true` 且返回 `submissionId`，继续调 `5.2` 拉取答卷详情

### 场景二：按部门筛选提交明细并分页查看

1. 调 `5.3`：`POST /questionnaire/submission/list`
2. 请求体带 `surveyId + department/departmentId + pageNum/pageSize`
3. 基于响应中的 `records` 渲染列表

### 场景三：问卷活动通知与催办闭环

1. 调 `5.5` 发送通知（可按员工或部门筛选触达范围；可通过 `notifyTitle`/`notifyMarkdown` 自定义标题与文案）
2. 调 `5.6` 对未提交且已通知人员发起催办
3. 调 `5.8` / `5.9` 分别获取活动名单口径下的已提交/未提交名单做复盘

### 场景四：统计分析（整卷/维度）

1. 调 `5.4`，传 `groupBy=survey` 获取整卷分值分布
2. 调 `5.4`，传 `groupBy=dimension` 获取分维度分值分布

### 场景五：管理端导入活动名单

1. 调 `5.10`：`POST /questionnaire/admin/surveys/targets/import`
2. 请求体包含：`surveyId`、`employeeIdList`、`replace`、`sourceType`
3. 当 `replace=true` 时按“全量覆盖”导入；`replace=false` 时按增量导入
4. 导入完成后可衔接 `5.5` 发送通知

### 场景六：2026 人事社保专项查询与统计

1. 调 `5.11`：`GET /questionnaire/social-insurance/submission/detail?employeeId={employeeId}`
2. 获取 `answers`（对应下游 `payload_json` 反序列化结构）用于单人问卷研判
3. 调 `5.12`：`GET /questionnaire/social-insurance/statistics`
4. 基于 `totalSubmitted`、`firstSubmitTimeMillis`、`latestSubmitTimeMillis`、`submissions[].payloadJson` 进行专项统计与复盘

---

## 八、注意事项

1. **路径不要混淆**：外部调用本服务必须用 `/questionnaire/**`，`/open/**` 是下游 `questionnaire` 内部路径。
2. **ID 精度**：`surveyId/submissionId/employeeId` 等 Long 字段在 JS 端建议按字符串处理。
3. **筛选条件优先级**：提交状态查询中 `employeeId` 与 `employeeName` 同时传入时，按下游约定优先工号。
4. **名单口径**：活动名单维度接口（`5.8/5.9`）与条件筛选接口（`5.7`）口径不同，报表侧不要混用。
5. **催办属于副作用接口**：`5.6` 虽为 GET，但业务语义为“触发催办”，请按写操作治理调用频率与审计。
6. **导入接口需要有效员工身份**：`5.10` 若缺少登录员工上下文，可能返回“未登录或缺少员工身份”。
7. **导入列表不能为空**：`employeeIdList` 为空会触发业务错误“员工ID列表不能为空”。
8. **通知文案字段**：`5.5` 新增 `notifyMarkdown`，建议控制文本长度并使用简洁 Markdown（纯文本同样可用）。
9. **通知标题字段**：`5.5` 新增 `notifyTitle`，控制工作汇报 `main`；在 sendV2 场景应作为必填参数处理。
10. **专项明细与统计口径**：`5.11` 以 `employeeId` 查询单人详情，`5.12` 不接收筛选参数、统一返回专项全量统计；两者时间均为毫秒时间戳。
11. **专项 payload 解析**：`5.11` 的 `answers` 为对象，`5.12` 的 `submissions[].payloadJson` 为原始 JSON 字符串，调用方需按场景选择解析策略。

---

## 九、附录：与下游接口编号对照

本服务 12 个接口与 [《问卷开放接口API说明》](./问卷开放接口API说明.md) 编号一一对应：

- 本文 `5.1~5.10` 对应下游文档 `4.1~4.10`。
- 本文 `5.11~5.12` 对应下游文档 `8.1~8.2`。

