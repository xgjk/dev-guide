# OPS 系统 Open API 调用说明

**配套文档**：[《OPS 系统 Open API 接口定义》](./OPS系统API说明.md)（数据模型 **一、1.x**、接口契约 **二、2.1～2.3**）。

本文承担：**修订记录、能力概述、通用约定、接口索引、编排场景、注意事项与历史路径**；**不重复**各接口的请求/响应字段表（以《接口定义》为准）。

---

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-04-16 | 新增 OPS 查询接口调用说明（项目列表/任务列表/任务详情） | OpenAPI-Agent |

---

## 一、概述

OPS（Operations / 运维/运营类任务体系）对外开放 HTTP 查询接口后，调用方可实现下列能力（与《接口定义》**二、2.x** 一一对应）：

1. **queryProjects** — 查询分组及项目列表（获取 `projectId`）
2. **queryTasks** — 根据项目 ID 查询项目内任务列表（获取 `taskId`）
3. **queryTaskDetail** — 根据任务 ID 查询任务详细信息（用于 AI/Agent 深度分析与生成）

字段级 **VO** 约定见《接口定义》**一、1.x**；接口契约（参数/响应结构）见《接口定义》**二、2.1～2.3**。

---

## 二、给 AI / Agent 的阅读顺序

1. **本文「四、通用说明」**：`Result<T>`、`appKey`、环境与 URL 形态。
2. **本文「五、接口清单（索引）」**：快速定位调用路径。
3. **《接口定义》一、1.x**：所有响应字段的**唯一权威**（特别是 Date 字段格式）。
4. **《接口定义》二、2.1～2.3**：具体方法的参数表、示例与 `data` 类型声明。
5. 需要**调用链**时读本文 **七、关键业务流程**；需要**省 Token / 推荐拉取路径**时读本文 **六、推荐拉取路径**。

---

## 三、关键词与别名

| 用语 | 英文路径片段 | 说明 |
|------|--------------|------|
| 项目 | `project` | `queryProjects` / `projectId` |
| 任务 | `task` | `queryTasks` / `taskId` |
| 任务详情 | `detail` | `queryTaskDetail` |

---

## 四、通用说明

### 4.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

### 4.2 环境信息

| 环境     | 域名 |
| -------- | ------------------------------------------- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` |

### 4.3 公共请求头

| Header   | 说明 | 是否必填 |
| -------- | ---- | -------- |
| `appKey` | 应用密钥，请联系管理员获取 | 是（兼容性见下） |

**兼容性**：某些场景下，header 有 `access-token` 但没有 `appKey`，系统也能兼容。

### 4.4 通用响应结构

所有接口返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段         | 类型    | 说明 |
| ------------ | ------- | ---- |
| `resultCode` | Integer | `1` 表示成功，其他值表示失败 |
| `resultMsg`  | String  | 成功时为 `null`，失败时为错误描述 |
| `data`        | T       | 业务数据；失败时为 `null` |

---

## 五、接口清单（索引）

下表为 **全部** 开放接口与《接口定义》小节号对照。

| 小节 | 规范命名 | 方法 | 现用路径 | 读写 | 摘要 |
|------|----------|------|----------|------|------|
| 2.1 | queryProjects | GET | `/ops/queryProjects` | 读 | 分组及项目列表 |
| 2.2 | queryTasks | GET | `/ops/queryTasks` | 读 | 项目内任务列表 |
| 2.3 | queryTaskDetail | GET | `/ops/queryTaskDetail` | 读 | 任务详情 |

---

## 六、推荐拉取路径（Agent）

**路径 A（标准渐进式）**：**2.1** → **2.2** → **2.3**  
用于“先定位项目，再定位任务，最后拿详情深度分析”的绝大多数场景。

**路径 B（跳过列表直接深挖）**：已知 `taskId` 时直接调用 **2.3**  
适合外部系统已带任务 ID、无需额外检索上下文的情况。

---

## 七、关键业务流程说明

### 场景一：按名称检索项目并生成任务洞察

> 需求：只知道某个关键词（项目/分组名称）时，找到相关项目，拉取任务列表，再针对关键任务做深度分析。

1. **2.1**（`GET /ops/queryProjects?name={keyword}`）→ 选择目标 `projectId`
2. **2.2**（`GET /ops/queryTasks?projectId={projectId}`）→ 遍历拿到 `taskId`
3. **按需 2.3**（`GET /ops/queryTaskDetail?taskId={taskId}`）→ 获得任务详情（责任人/监督人/前置任务/汇报计划等）

### 场景二：已知 taskId 的单任务深挖与摘要

> 需求：外部系统先筛选任务（如告警/工单系统），Open API 只做“单任务详情拉取与总结”。

1. **2.3**（`GET /ops/queryTaskDetail?taskId={taskId}`）
2. 用返回的 `taskName/taskRemark/requirement/preTasks/reportInfoList/reportPlan` 进行摘要生成与上下文组织

---

## 八、注意事项

1. **ID 精度**：Long 型雪花 ID 在 JS 等环境须按**字符串**处理，禁止使用 `parseInt` / `Number()` 直接整段当数值解析。
2. **name 参数**：当 `name` 包含中文时务必 URL 编码（UTF-8）。
3. **Date 字段格式**：`startTime/endTime/planStartDate/planEndDate` 使用 `yyyy-MM-dd HH:mm:ss` 约定；如你的调用方只支持 ISO，请在前端/Agent 层做格式转换。

