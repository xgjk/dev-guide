# OPS 系统 Open API 接口定义

**配套控制器**：`OpsQueryController`（`/ops/**`）。本说明仅覆盖当前已开放的 3 个查询接口（项目列表、任务列表、任务详情），用于 AI/集成方按统一方式调用。

---

## 一、数据模型概览

### 1.1 OpsProjectListVO（项目列表项）

| 字段            | 类型        | 说明                                               |
| --------------- | ----------- | -------------------------------------------------- |
| `projectId`     | Long        | 项目 ID                                            |
| `projectName`   | String      | 项目名称                                           |
| `groupName`     | String      | 所属分组名称（如业务线/部门分组）                 |
| `projectStatus` | Integer     | 项目状态：0=草稿，2=进行中，9=已完成              |
| `projectManager`| EmpBaseVO   | 项目负责人（id、name、avatar）                    |
| `startTime`     | Date        | 项目开始时间，格式 `yyyy-MM-dd HH:mm:ss`          |
| `endTime`       | Date        | 项目结束时间，格式 `yyyy-MM-dd HH:mm:ss`          |

> `EmpBaseVO` 结构：`id`（Long），`name`（String），`avatar`（String，头像 URL）。

### 1.2 OpsTaskListVO（任务列表项）

| 字段           | 类型              | 说明                                                        |
| -------------- | ----------------- | ----------------------------------------------------------- |
| `taskId`       | Long              | 任务 ID                                                     |
| `taskName`     | String            | 任务名称                                                    |
| `taskType`     | String            | 任务类型（如里程碑任务/普通任务等，具体值由 PMS 端定义）   |
| `status`       | Integer           | 任务状态：0=未开始，2=进行中，9=已完成(关闭)                |
| `executeEmps`  | List\<EmpBaseVO\> | 任务责任人列表                                             |
| `parentNames`  | List\<String\>    | 任务层级路径名称（从第一级开始，例如 `[项目, 目标, 子任务]`） |
| `planStartDate`| Date              | 计划开始时间，格式 `yyyy-MM-dd HH:mm:ss`                   |
| `planEndDate`  | Date              | 计划结束时间，格式 `yyyy-MM-dd HH:mm:ss`                   |

### 1.3 OpsTaskDetailVO（任务详情）

| 字段              | 类型                | 说明                                          |
| ----------------- | ------------------- | --------------------------------------------- |
| `taskName`        | String              | 任务名称                                      |
| `taskRemark`      | String              | 任务描述                                      |
| `requirement`     | String              | 衡量标准/任务要求                             |
| `createReportPlan`| Boolean             | 是否需要配置汇报计划                          |
| `executeEmps`     | List\<EmpBaseVO\>   | 责任人列表                                    |
| `dutyEmps`        | List\<EmpBaseVO\>   | 监督人列表                                    |
| `reportEmps`      | List\<EmpBaseVO\>   | 汇报人列表                                    |
| `planStartDate`   | Date                | 计划开始时间，格式 `yyyy-MM-dd HH:mm:ss`     |
| `planEndDate`     | Date                | 计划结束时间，格式 `yyyy-MM-dd HH:mm:ss`     |
| `preTasks`        | List\<Object\>      | 前置任务关系列表（具体结构参见 PMS 系统文档） |
| `reportInfoList`  | List\<Object\>      | 汇报记录及回复简要信息列表                    |
| `reportPlan`      | Object              | 汇报周期与通知设置（结构由工作汇报域定义）   |

> 详细字段结构（如前置任务、汇报计划等）以 PMS 与工作汇报服务的领域模型为准，本文只展示 Open API 透出的顶层字段。

---

## 二、接口详细说明

以下接口均要求通过网关鉴权（appKey 或 access-token），并带上 `employeeId`、`corpId` 等上下文信息，由网关自动透传至 PMS 服务。

---

### 2.1 分组及项目列表查询（queryProjects）

根据名称关键字查询当前员工有权限看到的分组及项目列表，可用于“先选项目，再看项目内任务”的第一步。

**规范命名**：`queryProjects`。

**基本信息**

| 项目     | 说明                    |
| -------- | ----------------------- |
| 接口地址 | `/ops/queryProjects`    |
| 请求方式 | `GET`                   |

**请求参数**

| 参数    | 类型   | 必填 | 说明                                             |
| ------- | ------ | ---- | ------------------------------------------------ |
| `name`  | String | 否   | 分组/项目名称关键字，支持模糊搜索。中文需 URL 编码（UTF-8）。 |

**响应参数**

`data`：`List<OpsProjectListVO>`，结构见 **一、1.1**。

**响应示例（简化）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "projectId": 123,
      "projectName": "XX 项目一期",
      "groupName": "技术中心 · AI 平台组",
      "projectStatus": 2,
      "projectManager": {
        "id": 10001,
        "name": "张三",
        "avatar": "https://example.com/avatar/zs.png"
      },
      "startTime": "2026-01-01 09:00:00",
      "endTime": "2026-03-31 18:00:00"
    }
  ]
}
```

**典型用法**

- 让 AI/前端根据关键字查找目标项目；
- 结合 `projectId` 继续调用 **2.2 项目内任务列表查询**。

---

### 2.2 项目内任务列表查询（queryTasks）

根据项目 ID 查询该项目下所有任务的列表信息，用于“项目内任务一览”“为大模型提供任务上下文索引”等场景。

**规范命名**：`queryTasks`。

**基本信息**

| 项目     | 说明                   |
| -------- | ---------------------- |
| 接口地址 | `/ops/queryTasks`      |
| 请求方式 | `GET`                  |

**请求参数**

| 参数        | 类型 | 必填 | 说明                   |
| ----------- | ---- | ---- | ---------------------- |
| `projectId` | Long | 是   | 项目 ID（来自 **2.1**） |

**响应参数**

`data`：`List<OpsTaskListVO>`，结构见 **一、1.2**。

**响应示例（简化）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "taskId": 20001,
      "taskName": "需求梳理与评审",
      "taskType": "task",
      "status": 2,
      "executeEmps": [
        { "id": 10002, "name": "李四", "avatar": "" }
      ],
      "parentNames": ["XX 项目一期", "目标：交付 V1.0"],
      "planStartDate": "2026-01-05 09:00:00",
      "planEndDate": "2026-01-10 18:00:00"
    }
  ]
}
```

**典型用法**

- 为 AI 生成项目进展总结时，先获取当前项目的所有任务列表；
- 结合 `taskId` 继续调用 **2.3 任务详情查询** 拿到更完整的描述与汇报记录。

---

### 2.3 任务详情查询（queryTaskDetail）

根据任务 ID 查询任务的详细信息，包括责任人/监督人/汇报人、计划时间、前置任务、汇报信息和汇报计划等，用于“单任务深度分析”和“结合工作汇报记录生成总结”等场景。

**规范命名**：`queryTaskDetail`。

**基本信息**

| 项目     | 说明                    |
| -------- | ----------------------- |
| 接口地址 | `/ops/queryTaskDetail`  |
| 请求方式 | `GET`                   |

**请求参数**

| 参数    | 类型 | 必填 | 说明        |
| ------- | ---- | ---- | ----------- |
| `taskId`| Long | 是   | 任务 ID     |

**响应参数**

`data`：`OpsTaskDetailVO`，结构见 **一、1.3**。

**响应示例（极简）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "taskName": "需求梳理与评审",
    "taskRemark": "对接业务方梳理需求，并完成评审记录",
    "requirement": "明确范围与验收标准",
    "createReportPlan": true,
    "executeEmps": [{ "id": 10002, "name": "李四", "avatar": "" }],
    "dutyEmps": [{ "id": 10001, "name": "张三", "avatar": "" }],
    "reportEmps": [{ "id": 10003, "name": "王五", "avatar": "" }],
    "planStartDate": "2026-01-05 09:00:00",
    "planEndDate": "2026-01-10 18:00:00",
    "preTasks": [],
    "reportInfoList": [],
    "reportPlan": null
  }
}
```

**典型用法**

- 为单个任务生成自然语言说明（包含目标、要求、责任人、监督人）；
- 结合 `reportInfoList` 与工作汇报系统，生成任务完成情况总结或评审报告。

---

## 三、错误码说明

| resultCode | 说明 |
| ---------- | ---- |
| 1 | 请求成功 |
| 0 | 通用失败 |
| 500 | 系统异常，请稍后重试 |
| 610002 | appKey 无效 |
| 610003 | appSecret 无效 |
| 610005 | sign 签名无效 |
| 610006 | access_key 无效或不是最新的 |
| 610007 | access_key 授权已达上限 |
| 610008 | 请求 URL 不在白名单内 |
| 610009 | 请求方法不支持 |
| 610010 | nonce 无效 |
| 610011 | timestamp 无效（与服务器时间差超过 30 分钟） |
| 610012 | 请求太过频繁，请稍候再试 |
| 610013 | 请求 URL 未找到 |
| 610014 | 应用已被禁用 |
| 610015 | 无访问权限 |
| 610016 | openUserId 无效 |
| 610017 | 根据 openId 获取用户信息错误 |
| 610018 | 非当前企业的用户 |
| 610019 | 用户已被禁用 |
| 610020 | 根据 appKey 获取用户信息错误 |
| 610030 | 重复的请求（nonce 已使用过） |
