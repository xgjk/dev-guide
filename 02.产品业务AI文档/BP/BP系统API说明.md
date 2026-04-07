# BP 目标管理 Open API 接口定义

**配套文档**：[《BP 目标管理 Open API 调用说明》](./BP系统API调用说明.md)（修订记录、概述、通用约定、接口清单索引、场景编排、注意事项与历史路径）。**本文仅描述数据模型、接口契约与公共类型。**

---

## 一、数据模型与对象规格

本节给出与开放接口一致的实体关系与 **Simple / Full** 字段规格。路径与调用约定详见 [《BP 目标管理 Open API 调用说明》](./BP系统API调用说明.md)。

### 1.1 设计要点（摘要）

1. **轻重分离**：`list*` 系列返回 **Simple（轻量）** 索引数据；`get*Detail`（及任务树 **二、2.4**）用于按需拉取完整或树形结构，避免单次响应过大。
2. **taskUsers 在 Simple 中即应完整**：承接人、协办人、抄送人、监督人、观察人等角色在轻量列表中同样需要返回，避免 Agent 遗漏责任人信息。
3. **组合优先于隐式递归**：在具备 `listGoals` / `listKeyResults` / `listActions` 后，可按「先预览计数与参与者 → 再拉详情」的方式控制 Token；全分组正文场景优先使用 **getGroupMarkdown（二、2.13）**。

### 1.2 实体关系

```
Period（周期）
  └─ Group（分组）
       ├─ type=org（组织节点，如部门/中心/集团）
       └─ type=personal（个人节点）
            └─ Goal（目标）
                 └─ KeyResult（关键成果）
                      └─ Action（关键举措）
```

- **组织 BP**：以 `type=org` 的 Group 为根，其下可挂目标。
- **个人 BP**：以 `type=personal` 的 Group 为根，其下直接挂目标。
- **对齐关系**：`upwardTaskList`（上对齐）与 `downTaskList`（下对齐）贯穿目标、关键成果、关键举措三层。

### 1.3 任务参与者角色

| 角色   | 说明     |
| ------ | -------- |
| 承接人 | 主责执行 |
| 协办人 | 协助执行 |
| 抄送人 | 知情     |
| 监督人 | 监督进展 |
| 观察人 | 旁听     |

### 1.4 对象规格：Simple 与 Full

各对象分为 **Simple（轻量）** 与 **Full（完整）** 两套规格。原则：**Simple** 包含 Agent 高频决策所需字段（`id`、`name`、`type` 或类型语义、`fullLevelNumber`、状态类字段、`taskUsers` 等），不包含需二次展开的大段嵌套；**Full** 在 Simple 基础上增加衡量标准、描述、参与部门、对齐列表、路径及子对象嵌套等。

#### 1.4.1 Period（周期）

| 字段     | Simple | Full | 说明              |
| -------- | ------ | ---- | ----------------- |
| id       | ✅     | ✅   | 周期 ID           |
| name     | ✅     | ✅   | 周期名称          |
| status   | ✅     | ✅   | 1=启用，0=未启用 |

> Simple 与 Full 一致。

#### 1.4.2 Group（分组）

| 字段        | Simple | Full | 说明                                |
| ----------- | ------ | ---- | ----------------------------------- |
| id          | ✅     | ✅   | 分组 ID                             |
| name        | ✅     | ✅   | 分组名称                            |
| type        | ✅     | ✅   | `org` / `personal`                  |
| levelNumber | ✅     | ✅   | 完整层级编码（如 `A4-1`）；部分响应字段名可能为 `fullLevelNumber`，语义相同 |
| employeeId  | ✅     | ✅   | 个人分组时有效                      |
| parentId    | —      | ✅   | 父分组 ID                           |
| childCount  | —      | ✅   | 直接下级分组数量                    |
| children    | —      | ✅   | 递归子分组（仅分组树，不含任务）    |

> **二、2.2 获取分组树** 返回 **Full Group 树**（含 `children`），**不含** Goal / KeyResult / Action。

#### 1.4.3 Goal（目标）

| 字段            | Simple | Full | 说明                         |
| --------------- | ------ | ---- | ---------------------------- |
| id              | ✅     | ✅   |                              |
| name            | ✅     | ✅   |                              |
| fullLevelNumber | ✅     | ✅   | 目标编码                     |
| statusDesc      | ✅     | ✅   | 进行中/已关闭/未启动/草稿等  |
| reportCycle     | ✅     | ✅   | 如 `week+1`                  |
| planDateRange   | ✅     | ✅   | `yyyy-MM-dd ~ yyyy-MM-dd`    |
| taskUsers       | ✅     | ✅   | **每次建议拉取**             |
| krCount         | ✅     | —    | 下属 KR 数量（仅 Simple 列表） |
| actionCount     | ✅     | —    | 下属举措总数（仅 Simple 列表） |
| measureStandard | —      | ✅   | 衡量标准                     |
| description     | —      | ✅   | 描述                         |
| taskDepts       | —      | ✅   | 参与部门                     |
| upwardTaskList  | —      | ✅   | 上对齐                       |
| downTaskList    | —      | ✅   | 下对齐                       |
| path            | —      | ✅   | 路径                         |
| keyResults      | —      | ✅   | Full 下内嵌完整 KR 列表      |

> **`GoalFullVO`**：`getGoalDetail`（**二、2.5**）响应 `data` 的类型，**由本表标为 Full（✅）的字段组成**，**不继承**已废弃的 `BaseTaskVO`。`keyResults` 中每个元素为 **`KeyResultFullVO`**（见 **一、1.4.4** Full，且含 `actions`）。

#### 1.4.4 KeyResult（关键成果）

| 字段            | Simple | Full | 说明           |
| --------------- | ------ | ---- | -------------- |
| id              | ✅     | ✅   |                |
| name            | ✅     | ✅   |                |
| fullLevelNumber | ✅     | ✅   | KR 编码        |
| statusDesc      | ✅     | ✅   |                |
| measureStandard | ✅     | ✅   | KR 核心字段    |
| reportCycle     | ✅     | ✅   |                |
| planDateRange   | ✅     | ✅   |                |
| taskUsers       | ✅     | ✅   | **每次建议拉取** |
| actionCount     | ✅     | —    | 下属举措数量   |
| weight          | —      | ✅   | 权重 0–100     |
| description     | —      | ✅   |                |
| taskDepts       | —      | ✅   |                |
| upwardTaskList  | —      | ✅   |                |
| downTaskList    | —      | ✅   |                |
| actions         | —      | ✅   | Full 下内嵌举措 |

> **`KeyResultFullVO`**：`getKeyResultDetail`（**二、2.6**）响应 `data` 的类型，**由本表标为 Full（✅）的字段组成**，**不继承** `BaseTaskVO`。`actions` 中每个元素为 **`ActionFullVO`**（见 **一、1.4.5** Full）。

#### 1.4.5 Action（关键举措）

| 字段            | Simple | Full | 说明           |
| --------------- | ------ | ---- | -------------- |
| id              | ✅     | ✅   |                |
| name            | ✅     | ✅   |                |
| fullLevelNumber | ✅     | ✅   | 举措编码       |
| statusDesc      | ✅     | ✅   |                |
| reportCycle     | ✅     | ✅   |                |
| planDateRange   | ✅     | ✅   |                |
| taskUsers       | ✅     | ✅   | **每次建议拉取** |
| weight          | —      | ✅   | 权重 0–100     |
| measureStandard | —      | ✅   |                |
| description     | —      | ✅   |                |
| taskDepts       | —      | ✅   |                |
| upwardTaskList  | —      | ✅   |                |
| downTaskList    | —      | ✅   |                |

> **`ActionFullVO`**：`getActionDetail`（**二、2.7**）响应 `data` 的类型，**由本表标为 Full（✅）的字段组成**，**不继承** `BaseTaskVO`。

> **关于 `groupId`**：**二、2.5 / 2.6 / 2.7** 返回的 `GoalFullVO` / `KeyResultFullVO` / `ActionFullVO` **均不在响应体中带 `groupId`**。分组 ID 请在调用链中从 **二、2.2 / 2.3 / 2.4** 等前置结果保留；或结合 `path`、`upwardTaskList` / `downTaskList` 中 `SimpleTaskVO.groupInfo` 等字段使用。

---

## 二、接口详细说明

以下各小节在标题或**基本信息**中标注 **规范命名**（如 `listPeriods`），与《调用说明》中的**规划命名对照表**及**历史路径**一致。

---

### 2.1 查询周期列表（listPeriods）

获取系统中所有 BP 周期信息，可选按名称模糊搜索。通常作为整个调用流程的**第一步**，用于获取 `periodId`。

**规范命名**：`listPeriods`（规划 G1）。

**基本信息**

| 项目     | 说明                 |
| -------- | -------------------- |
| 接口地址 | `/bp/period/list`    |
| 请求方式 | `GET`                |

**请求参数**

| 参数   | 类型   | 必填 | 说明                   |
| ------ | ------ | ---- | ---------------------- |
| `name` | String | 否   | 周期名称，支持模糊搜索。**⚠️ 中文必须 URL 编码（UTF-8）** |

**响应参数**

`data`：`List<PeriodVO>`，元素字段见 **一、1.4.1 Period**（Simple 与 Full 相同）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2014631829004370001",
      "name": "2026年Q1",
      "status": 1
    },
    {
      "id": "2014631829004370002",
      "name": "2026年Q2",
      "status": 0
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/period/list?name=2026' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `id`（周期 ID）用于 **2.2 获取分组树** 的 `periodId` 入参。通常选择 `status = 1`（启用状态）的周期。

---

### 2.2 获取分组树（listGroups）

根据周期 ID 获取该周期下的完整分组树形结构，包含组织分组和个人分组；**仅分组层级，不含任何 Goal / KeyResult / Action**。

**规范命名**：`listGroups`（规划 G2）。

**基本信息**

| 项目     | 说明               |
| -------- | ------------------ |
| 接口地址 | `/bp/group/list`   |
| 请求方式 | `GET`              |

**请求参数**

| 参数           | 类型    | 必填 | 说明                                                      |
| -------------- | ------- | ---- | --------------------------------------------------------- |
| `periodId`     | Long    | 是   | 周期 ID（来自 **2.1 查询周期列表** 返回的 `PeriodVO.id`） |
| `onlyPersonal` | Boolean | 否   | 是否只查询个人分组，默认 `false`                          |

**响应参数**

`data`：`List<GroupTreeVO>`，树节点字段见 **一、1.4.2 Group**（Full 树节点，含递归 `children`）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2014631829004371001",
      "name": "技术中心",
      "type": "org",
      "employeeId": null,
      "parentId": null,
      "levelNumber": "1",
      "childCount": 1,
      "children": [
        {
          "id": "2014631829004371002",
          "name": "张三",
          "type": "personal",
          "employeeId": "1234567890123456789",
          "parentId": "2014631829004371001",
          "levelNumber": "1.1",
          "childCount": 0,
          "children": []
        }
      ]
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/list?periodId=2014631829004370001&onlyPersonal=false' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的分组 `id` 用于 **2.4 查询任务树**、**2.18** 等的 `groupId` 入参。其中 `type = "personal"` 的节点代表个人分组，`type = "org"` 的节点代表组织分组。

---

### 2.3 批量查询员工个人类型分组 ID

根据员工 ID 列表，查询每个员工在当前启用周期下的个人类型分组 ID。这是一种快捷方式，无需先查周期再查分组树，可直接获取员工的个人分组 ID。

**基本信息**

| 项目         | 说明                            |
| ------------ | ------------------------------- |
| 接口地址     | `/bp/group/getPersonalGroupIds` |
| 请求方式     | `POST`                          |
| Content-Type | `application/json`              |

**请求参数**

请求体为 JSON 数组，元素为员工 ID（Long 类型）：

```json
[1234567890123456789, 1234567890123456790, 1234567890123456791]
```

| 参数   | 类型         | 必填 | 说明         |
| ------ | ------------ | ---- | ------------ |
| (body) | `List<Long>` | 是   | 员工 ID 列表 |

**响应参数**

`data`：`Map<Long, Long>`，key 为员工 ID，value 为该员工在启用周期下的个人分组 ID；value 为 `null` 表示该员工未创建 BP。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "1234567890123456789": "2014631829004374001",
    "1234567890123456790": null,
    "1234567890123456791": "2014631829004374003"
  }
}
```

**请求示例**

```bash
curl -X POST 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/getPersonalGroupIds' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '[1234567890123456789, 1234567890123456790]'
```

**数据流向**

返回的 Map value（分组 ID）用于 **2.4 查询任务树** 的 `groupId` 入参。若 value 为 `null`，说明该员工在当前启用周期下尚未创建 BP。

---

### 2.4 查询BP任务树(完整任务树简要信息)

根据分组 ID 查询该分组下的完整 BP 任务树形结构，包含目标（Goal）、关键成果（Key Result）、关键举措（Action）三个层级。

**基本信息**

| 项目     | 说明                        |
| -------- | --------------------------- |
| 接口地址 | `/bp/task/v2/getSimpleTree` |
| 请求方式 | `GET`                       |

**请求参数**

| 参数      | 类型 | 必填 | 说明                                                         |
| --------- | ---- | ---- | ------------------------------------------------------------ |
| `groupId` | Long | 是   | 分组 ID（来自 **2.2 获取分组树** 的 `GroupTreeVO.id`，或 **2.3 批量查询** 返回的 Map value） |

**响应参数**

`data`：`List<TaskTreeVO>`，节点定义见 **三、3.1 TaskTreeVO**（简要树形索引，**非** Simple/Full 业务规格）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2014631829004374017",
      "name": "Q1 业绩目标",
      "groupId": "2014631829004374001",
      "type": "目标",
      "children": [
        {
          "id": "2014631829004374018",
          "name": "客户拜访量达到50家",
          "groupId": "2014631829004374001",
          "type": "关键成果",
          "children": [
            {
              "id": "2014631829004374019",
              "name": "每周拜访5家客户",
              "groupId": "2014631829004374001",
              "type": "关键举措",
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/getSimpleTree?groupId=2014631829004374001' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

- 树中 `type = "目标"` 的节点 `id` → 用于 **2.5 获取目标详情** 的路径参数 `goalId`
- **2.18 获取目标轻量列表** 返回的 `id` → 同上，作为 **2.5** 的 `goalId`
- 树中 `type = "关键成果"` 的节点 `id` → 用于 **2.6 获取关键成果详情** 的 `keyResultId` 入参
- 树中 `type = "关键举措"` 的节点 `id` → 用于 **2.7 获取关键举措详情** 的 `actionId` 入参
- 树中任意节点的 `id` → 用于 **2.8 分页查询所有汇报** 的 `taskId` 入参

---

### 2.5 获取目标详情（getGoalDetail）

根据目标 ID 获取目标的完整详情（**Full Goal**，内嵌关键成果与关键举措），包含该目标下的所有关键成果及关键举措。相比 2.4 任务树的简要信息，本接口返回更丰富的字段（如对齐任务等）。

**规范命名**：`getGoalDetail`（规划 D1）。

**基本信息**

| 项目     | 说明                                    |
| -------- | --------------------------------------- |
| 接口地址 | `/bp/goal/{goalId}/detail`              |
| 请求方式 | `GET`                                   |

**路径参数**

| 参数      | 类型 | 必填 | 说明                                                         |
| --------- | ---- | ---- | ------------------------------------------------------------ |
| `goalId`  | Long | 是   | 目标 ID（来自 **2.4 查询任务树** 中 `type = "目标"` 的节点 `id`，或 **2.18** 列表中的 `id`） |

**响应参数**

`data`：`GoalFullVO`，见 **一、1.4.3**、**三、3.2**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": "2014631829004374017",    
    "name": "Q1 业绩目标",
    "statusDesc": "进行中",
    "reportCycle": "week+1",
    "planDateRange": "2026-01-01 ~ 2026-03-31",
    "fullLevelNumber": "1",
    "taskUsers": [
      {
        "taskId": "2014631829004374017",
        "role": "承接人",
        "empList": [
          { "id": "1234567890123456789", "name": "张三" }
        ]
      }
    ],
    "taskDepts": [],
    "upwardTaskList": [],
    "downTaskList": [],
    "keyResults": [
      {
        "id": "2014631829004374018",       
        "name": "客户拜访量达到50家",
        "measureStandard": "拜访记录数 >= 50",
        "statusDesc": "进行中",
        "reportCycle": "week+1",
        "planDateRange": "2026-01-01 ~ 2026-02-28",
        "fullLevelNumber": "1.1",
        "taskUsers": [],
        "taskDepts": [],
        "actions": [
          {
            "id": "2014631829004374019",
            "name": "每周拜访5家客户",
            "statusDesc": "进行中",
            "reportCycle": "week+1",
            "planDateRange": "2026-01-01 ~ 2026-02-28",
            "fullLevelNumber": "1.1.1",
            "taskUsers": []
          }
        ]
      }
    ]
  }
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/goal/2014631829004374017/detail' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

- 返回的 `keyResults[].id` → 可用于 **2.6 获取关键成果详情** 的路径参数 `keyResultId`
- 返回的 `keyResults[].actions[].id` → 可用于 **2.7 获取关键举措详情** 的路径参数 `actionId`

---

### 2.6 获取关键成果详情（getKeyResultDetail）

根据关键成果 ID 获取关键成果的完整详情（**Full KeyResult**，内嵌关键举措）。

**规范命名**：`getKeyResultDetail`（规划 D2）。

**基本信息**

| 项目     | 说明                                      |
| -------- | ----------------------------------------- |
| 接口地址 | `/bp/keyResult/{keyResultId}/detail`      |
| 请求方式 | `GET`                                     |

**路径参数**

| 参数           | 类型 | 必填 | 说明                                                         |
| -------------- | ---- | ---- | ------------------------------------------------------------ |
| `keyResultId`  | Long | 是   | 关键成果 ID（来自 **2.4 查询任务树** 中 `type = "关键成果"` 的节点 `id`，或 **2.5** / **2.19** 返回的 `id`） |

**响应参数**

`data`：`KeyResultFullVO`，见 **一、1.4.4**、**三、3.2**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": "2014631829004374018",   
    "name": "客户拜访量达到50家",
    "measureStandard": "拜访记录数 >= 50",
    "statusDesc": "进行中",
    "reportCycle": "week+1",
    "planDateRange": "2026-01-01 ~ 2026-02-28",
    "fullLevelNumber": "1.1",
    "taskUsers": [
      {
        "taskId": "2014631829004374018",
        "role": "承接人",
        "empList": [
          { "id": "1234567890123456789", "name": "张三" }
        ]
      }
    ],
    "taskDepts": [],
    "upwardTaskList": [
      { "id": "2014631829004374017", "name": "Q1 业绩目标", "groupInfo": { "id": "2014631829004374001", "name": "张三" } }
    ],
    "downTaskList": [],
    "actions": [
      {
        "id": "2014631829004374019",
        "name": "每周拜访5家客户",
        "statusDesc": "进行中",
        "reportCycle": "week+1",
        "planDateRange": "2026-01-01 ~ 2026-02-28",
        "fullLevelNumber": "1.1.1",
        "taskUsers": []
      }
    ]
  }
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/keyResult/2014631829004374018/detail' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `actions[].id` → 可用于 **2.7 获取关键举措详情** 的路径参数 `actionId`。

---

### 2.7 获取关键举措详情（getActionDetail）

根据关键举措 ID 获取关键举措的完整详情（**Full Action**）。

**规范命名**：`getActionDetail`（规划 D3）。

**基本信息**

| 项目     | 说明                               |
| -------- | ---------------------------------- |
| 接口地址 | `/bp/action/{actionId}/detail`     |
| 请求方式 | `GET`                              |

**路径参数**

| 参数        | 类型 | 必填 | 说明                                                         |
| ----------- | ---- | ---- | ------------------------------------------------------------ |
| `actionId`  | Long | 是   | 关键举措 ID（来自 **2.4 查询任务树** 中 `type = "关键举措"` 的节点 `id`，或 **2.6** / **2.20** 返回的 `id`） |

**响应参数**

`data`：`ActionFullVO`，见 **一、1.4.5**、**三、3.2**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": "2014631829004374019",  
    "name": "每周拜访5家客户",
    "statusDesc": "进行中",
    "reportCycle": "week+1",
    "planDateRange": "2026-01-01 ~ 2026-02-28",
    "fullLevelNumber": "1.1.1",
    "taskUsers": [
      {
        "taskId": "2014631829004374019",
        "role": "承接人",
        "empList": [
          { "id": "1234567890123456789", "name": "张三" }
        ]
      }
    ],
    "taskDepts": [],
    "upwardTaskList": [
      { "id": "2014631829004374018", "name": "客户拜访量达到50家", "groupInfo": { "id": "2014631829004374001", "name": "张三" } }
    ],
    "downTaskList": []
  }
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/action/2014631829004374019/detail' \
  -H 'appKey: XXXXXXXX'
```

---

### 2.8 分页查询所有汇报（listTaskReports）

根据任务 ID 分页查询该任务关联的所有汇报记录，包含手动汇报和 AI 汇报。

**规范命名**：`listTaskReports`（规划 R1）。

**基本信息**

| 项目         | 说明                               |
| ------------ | ---------------------------------- |
| 接口地址     | `/bp/task/relation/pageAllReports` |
| 请求方式     | `POST`                             |
| Content-Type | `application/json`                 |

**请求参数**

| 参数        | 类型    | 必填 | 说明                                                         |
| ----------- | ------- | ---- | ------------------------------------------------------------ |
| `taskId`            | Long    | 是   | BP 任务 ID（来自 **2.4 查询任务树**、**2.18~2.20** 列表，或 **2.5/2.6/2.7** 详情接口返回的 `id`） |
| `keyword`           | String  | 否   | 汇报标题模糊搜索（对应响应字段 `main`）                      |
| `sortBy`            | String  | 否   | 排序字段：`relation_time`（关联时间，默认）、`business_time`（业务时间） |
| `sortOrder`         | String  | 否   | 排序方向：`desc`（降序，默认）、`asc`（升序）                |
| `businessTimeStart` | String  | 否   | 业务时间范围-开始，格式：`yyyy-MM-dd HH:mm:ss`。手动汇报按汇报时间过滤，AI 汇报按创建时间过滤 |
| `businessTimeEnd`   | String  | 否   | 业务时间范围-结束，格式：`yyyy-MM-dd HH:mm:ss`              |
| `relationTimeStart` | String  | 否   | 关联时间范围-开始，格式：`yyyy-MM-dd HH:mm:ss`。仅对手动汇报生效（AI 汇报无关联时间） |
| `relationTimeEnd`   | String  | 否   | 关联时间范围-结束，格式：`yyyy-MM-dd HH:mm:ss`              |
| `pageIndex`         | Integer | 否   | 页码，默认 `1`                                               |
| `pageSize`          | Integer | 否   | 每页数量，默认 `10`                                          |

**请求体示例**

```json
{
  "taskId": 2014631829004374017,
  "keyword": null,
  "sortBy": "relation_time",
  "sortOrder": "desc",
  "businessTimeStart": "2026-01-01 00:00:00",
  "businessTimeEnd": "2026-03-31 23:59:59",
  "relationTimeStart": null,
  "relationTimeEnd": null,
  "pageIndex": 1,
  "pageSize": 10
}
```

**响应参数**

`data`：`PageInfo<TaskReportUnionVO>`。分页字段见 **三、3.11 PageInfo**；`list` 元素见 **三、3.12 TaskReportUnionVO**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": 25,
    "list": [
      {
        "bizId": "2014631829004375100",
        "typeDesc": "手动汇报"
      },
      {
        "bizId": "2014631829004375200",
        "typeDesc": "AI汇报"
      }
    ],
    "pageNum": 1,
    "pageSize": 10,
    "size": 2
  }
}
```

**请求示例**

```bash
curl -X POST 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/relation/pageAllReports' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "taskId": 2014631829004374017,
    "businessTimeStart": "2026-01-01 00:00:00",
    "businessTimeEnd": "2026-03-31 23:59:59",
    "pageIndex": 1,
    "pageSize": 10
  }'
```

---

### 2.9 发送 AI 延期提醒汇报

对未完成 BP 的员工发送延期提醒汇报。

**基本信息**

| 项目         | 说明                   |
| ------------ | ---------------------- |
| 接口地址     | `/bp/delayReport/send` |
| 请求方式     | `POST`                 |
| Content-Type | `application/json`     |

**请求参数**

| 参数            | 类型   | 必填 | 说明                                                    |
| --------------- | ------ | ---- | ------------------------------------------------------- |
| `receiverEmpId` | Long   | 是   | 接收汇报人的员工 ID（**注意：是员工 ID，不是分组 ID**） |
| `reportName`    | String | 是   | 汇报名称                                                |
| `content`       | String | 是   | 汇报内容                                                |

**请求体示例**

```json
{
  "receiverEmpId": 1234567890123456789,
  "reportName": "BP延期提醒 - 张三",
  "content": "您负责的关键成果【客户拜访量达到50家】已延期，计划结束日期为2026-02-28，请尽快跟进处理。"
}
```

**响应参数**

`data`：`Long`，生成的汇报记录 ID。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "2014631829004375001"
}
```

**请求示例**

```bash
curl -X POST 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/delayReport/send' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "receiverEmpId": 1234567890123456789,
    "reportName": "BP延期提醒 - 张三",
    "content": "您负责的关键成果【客户拜访量达到50家】已延期，计划结束日期为2026-02-28，请尽快跟进处理。"
  }'
```

**数据流向**

发送成功后返回的记录 ID 可通过 **2.10 查询延期汇报历史** 进行查询。

---

### 2.10 查询 AI 延期提醒汇报历史（listDelayReports）

查询某员工历史收到的所有延期提醒汇报记录。

**规范命名**：`listDelayReports`（规划 R2）。

**基本信息**

| 项目     | 说明                   |
| -------- | ---------------------- |
| 接口地址 | `/bp/delayReport/list` |
| 请求方式 | `GET`                  |

**请求参数**

| 参数            | 类型 | 必填 | 说明              |
| --------------- | ---- | ---- | ----------------- |
| `receiverEmpId` | Long | 是   | 接收汇报人员工 ID |

**响应参数**

`data`：`List<AiDelayReportRecordVO>`，元素见 **三、3.13**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2014631829004375001",
      "receiverEmpId": "1234567890123456789",
      "reportContent": "您负责的关键成果【客户拜访量达到50家】已延期，计划结束日期为2026-02-28，请尽快跟进处理。",
      "reportRecordId": "2014631829004375100",
      "sendStatus": 1,
      "errorMsg": null,
      "createTime": "2026-03-10 14:30:00"
    },
    {
      "id": "2014631829004375002",
      "receiverEmpId": "1234567890123456789",
      "reportContent": "您负责的关键举措【每周拜访5家客户】进度滞后，请及时更新进展。",
      "reportRecordId": null,
      "sendStatus": 0,
      "errorMsg": "员工已离职",
      "createTime": "2026-03-08 10:15:00"
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/delayReport/list?receiverEmpId=1234567890123456789' \
  -H 'appKey: XXXXXXXX'
```

---

### 2.11 按名称模糊搜索任务

根据分组 ID 和名称关键字模糊搜索任务，返回任务基本信息、参与人及上下级任务信息。

**基本信息**

| 项目     | 说明                        |
| -------- | --------------------------- |
| 接口地址 | `/bp/task/v2/searchByName` |
| 请求方式 | `GET`                       |

**请求参数**

| 参数      | 类型   | 必填 | 说明           |
| --------- | ------ | ---- | -------------- |
| `groupId` | Long   | 是   | 分组 ID        |
| `name`    | String | 是   | 任务名称关键字。**⚠️ 中文必须 URL 编码（UTF-8）** |

**响应参数**

`data`：`List<TaskSearchVO>`，元素见 **三、3.14 TaskSearchVO**。

**请求示例**

```bash
# 示例：搜索任务名称包含"全栈"的任务
# 原始参数：name=全栈
# URL 编码后（UTF-8）：name=%E5%85%A8%E6%A0%88
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/searchByName?groupId=1993982002185506818&name=%E5%85%A8%E6%A0%88' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2001628713670279169",
      "name": "全栈交付项目模式探索",
      "groupId": "1993982002185506818",
      "groupName": "技术部",
      "type": "目标",
      "statusDesc": "进行中",
      "reportCycle": "doubleMonth+1",
      "planDateRange": "2025-01-07 ~ 2025-02-02",
      "fullLevelNumber": "A4-1",
      "taskUsers": [
        {
          "taskId": "2001628713670279169",
          "role": "承接人",
          "empList": [
            { "id": "1512393131319586817", "name": "刘会芳" }
          ]
        }
      ],
      "parentTask": null,
      "childTasks": [
        { "id": "2001628715230560258", "name": "AODW工作方式的探索与实践", "type": "关键成果", "statusDesc": "进行中" }
      ]
    }
  ]
}
```

---

### 2.12 按名称模糊搜索分组

根据周期 ID 和名称关键字模糊搜索分组，返回分组基本信息及上下级信息。

**基本信息**

| 项目     | 说明                     |
| -------- | ------------------------ |
| 接口地址 | `/bp/group/searchByName` |
| 请求方式 | `GET`                    |

**请求参数**

| 参数       | 类型   | 必填 | 说明           |
| ---------- | ------ | ---- | -------------- |
| `periodId` | Long   | 是   | 周期 ID        |
| `name`     | String | 是   | 分组名称关键字。**⚠️ 中文必须 URL 编码（UTF-8）** |

**响应参数**

`data`：`List<GroupSearchVO>`，元素见 **三、3.15 GroupSearchVO**。

**请求示例**

```bash
# 示例：搜索分组名称包含"技术"的分组
# 原始参数：name=技术
# URL 编码后（UTF-8）：name=%E6%8A%80%E6%9C%AF
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/searchByName?periodId=1993981738711912449&name=%E6%8A%80%E6%9C%AF' \
  -H 'appKey: XXXXXXXX'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "1993982002185506818",
      "name": "技术部",
      "periodId": "1993981738711912449",
      "type": "org",
      "levelNumber": "A4",
      "employeeId": null,
      "parentGroup": {
        "id": "1993981993016758274",
        "name": "集团",
        "type": "org"
      },
      "childCount": 6
    }
  ]
}
```

---

### 2.13 获取分组完整 BP 的 Markdown（getGroupMarkdown）

根据分组 ID 获取该分组下完整 BP 的 Markdown 格式内容，包含三部分：本级目标树（目标、关键成果、关键举措及参与人信息）、上对齐关系（本级任务对齐到的上级分组任务）、下对齐关系（下级分组任务对当前分组任务的承接情况）。**适合大模型单次通读，避免超大 JSON 树。**

**规范命名**：`getGroupMarkdown`（规划 M1）。

**基本信息**

| 项目     | 说明                    |
| -------- | ----------------------- |
| 接口地址 | `/bp/group/markdown`    |
| 请求方式 | `GET`                   |

**请求参数**

| 参数      | 类型 | 必填 | 说明                                                         |
| --------- | ---- | ---- | ------------------------------------------------------------ |
| `groupId` | Long | 是   | 分组 ID（来自 **2.2 获取分组树** 的 `GroupTreeVO.id`，或 **2.3 批量查询** 返回的 Map value） |

**响应参数**

`data`：`String`（Markdown 正文）。下文为正文**结构示意**（非 JSON 字段表）。

**Markdown 结构示意**

```
## 分组信息
- 分组名称：xxx
- 分组类型：部门
- 层级编码：A4

## 目标与关键成果、举措
### 目标1：xxx
- 编码：A4-1
- 任务ID：xxx
- 责任人：张三
- 起止时间：2026-01-01 至 2026-12-31
- 汇报周期：每月（15日）
- 状态：进行中

#### 关键成果1.1：xxx
- 编码：A4-1.1
- 衡量标准：xxx
...

##### 关键举措1.1.1：xxx
- 编码：A4-1.1.1
- 承接人：李四
...

# 上对齐关系
## 上对齐分组：集团 (层级编码: A)
本级关键举措「xxx」(编码: A4-1.1.1) 对齐到：
#### [关键举措] xxx
- 编码：A-1.1.1
- 分组：集团
- 承接人：王五
...

# 下对齐关系
## 下级承接分组：技术一部 (层级编码: A4-1, 类型: 部门)
本级关键举措「xxx」(编码: A4-1.1.1) 被以下下级任务承接：
...
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "## 分组信息\n- 分组名称：技术中心\n- 分组类型：部门\n- 层级编码：A4\n\n## 目标与关键成果、举措\n### 目标1：Q1 业绩目标\n- 编码：A4-1\n..."
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/markdown?groupId=2014631829004371001' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 Markdown 文本可直接用于 AI 分析、文档展示等场景。该接口整合了分组下的完整 BP 信息（目标树 + 对齐关系），是获取分组 BP 全貌的推荐接口。

---

### 2.14 根据目标ID新增关键成果

根据目标 ID **纯新增**一条关键成果记录；**2.15** 为在关键成果下纯新增关键举措，二者均为写接口中的增量新增，**非**「更新/编辑」已有节点。本接口不影响该目标下已有其他成果，并返回新创建关键成果的任务 ID。

**基本信息**

| 项目     | 说明                          |
| -------- | ----------------------------- |
| 接口地址 | `/bp/task/v2/addKeyResult`    |
| 请求方式 | `POST`                        |

**请求参数（Request Body，JSON 对象）**

| 字段               | 类型                     | 必填 | 说明                                                                             |
| ------------------ | ------------------------ | ---- | -------------------------------------------------------------------------------- |
| `goalId`           | Long                     | 是   | 目标 ID                                                                          |
| `name`             | String                   | 是   | 关键成果名称                                                                     |
| `ruleType`         | String                   | 否   | 汇报周期类型，可选：`weekday` / `week` / `month` / `doubleWeek` / `doubleMonth` / `threeMonth` |
| `requiredIndex`    | String                   | 否   | 汇报日（与 ruleType 组合使用）                                                   |
| `planStartDate`    | String                   | 否   | 计划开始日期，格式 `yyyy-MM-dd`                                                  |
| `planEndDate`      | String                   | 否   | 计划结束日期，格式 `yyyy-MM-dd`                                                  |
| `ownerIds`         | List\<Long\>             | 否   | 承接人 ID 列表                                                                   |
| `ownerDeptIds`     | List\<Long\>             | 否   | 承接人部门 ID 列表                                                               |
| `collaboratorIds`  | List\<Long\>             | 否   | 协办人 ID 列表                                                                   |
| `copyToIds`        | List\<Long\>             | 否   | 抄送人 ID 列表                                                                   |
| `supervisorIds`    | List\<Long\>             | 否   | 监督人 ID 列表                                                                   |
| `observerIds`      | List\<Long\>             | 否   | 观察人 ID 列表                                                                   |
| `upwardTaskIdList` | List\<Long\>             | 否   | 向上对齐任务 ID 列表                                                             |
| `weight`           | BigDecimal               | 否   | 权重（0-100）                                                                    |
| `description`      | String                   | 否   | 关键成果详细描述                                                                 |
| `measureStandard`  | String                   | 否   | 衡量标准                                                                         |
| `actionPlan`       | String                   | 否   | 行动计划                                                                         |
| `uploadSpFileDTOS` | List\<UploadSpFileParam\>| 否   | 附件文件信息                                                                     |

**UploadSpFileParam 结构：**

| 字段         | 类型   | 必填 | 说明                         |
| ------------ | ------ | ---- | ---------------------------- |
| `name`       | String | 是   | 文件名称                     |
| `type`       | String | 是   | 文件类型，固定值：`file`     |
| `resourceId` | String | 否   | 文件唯一标识 ID              |
| `suffix`     | String | 否   | 文件后缀                     |
| `fSize`      | Long   | 否   | 文件大小（字节）             |

**响应参数**

`data`：`Long`，新创建的关键成果任务 ID。

**请求示例**

```bash
curl -X POST 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/addKeyResult' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "goalId": "2014631829004374017",
    "name": "新增 Q2 业绩增长点",
    "description": "通过下沉市场获取新增用户",
    "planStartDate": "2026-04-01",
    "planEndDate": "2026-06-30"
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "2014631829004376001"
}
```

---

### 2.15 根据成果ID新增关键举措

根据关键成果 ID 纯新增一个关键举措。不影响该成果下已有的其他举措，并返回新生成举措的任务 ID。

**基本信息**

| 项目     | 说明                      |
| -------- | ------------------------- |
| 接口地址 | `/bp/task/v2/addAction`   |
| 请求方式 | `POST`                    |

**请求参数（Request Body，JSON 对象）**

| 字段               | 类型                     | 必填 | 说明                                       |
| ------------------ | ------------------------ | ---- | ------------------------------------------ |
| `keyResultId`      | Long                     | 是   | 分组/成果 ID（此处为关键成果任务 ID）      |
| `name`             | String                   | 是   | 关键举措名称                               |
| `ruleType`         | String                   | 否   | 汇报周期类型                               |
| `requiredIndex`    | String                   | 否   | 汇报日                                     |
| `planStartDate`    | String                   | 否   | 计划开始日期                               |
| `planEndDate`      | String                   | 否   | 计划结束日期                               |
| `ownerIds`         | List\<Long\>             | 否   | 承接人 ID 列表                             |
| `upwardTaskIdList` | List\<Long\>             | 否   | 向上对齐任务 ID 列表                       |
| `weight`           | BigDecimal               | 否   | 权重（0-100）                              |
| `description`      | String                   | 否   | 关键举措描述                               |
| `measureStandard`  | String                   | 否   | 衡量标准                                   |
| `uploadSpFileDTOS` | List\<UploadSpFileParam\>| 否   | 附件文件信息（同 2.14）                    |

**响应参数**

`data`：`Long`，新创建的关键举措任务 ID。

**请求示例**

```bash
curl -X POST 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/addAction' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "keyResultId": "2014631829004374018",
    "name": "拓展三线城市分销商",
    "measureStandard": "签约 10 家以上"
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "2014631829004376002"
}
```

---

### 2.16 获取关键岗位详情（已废弃）

> **⚠️ 本接口已废弃，请使用 2.17 批量获取关键岗位详情(Markdown) 接口替代。**

获取关键岗位详情：返回当前关键岗位状态、原因以及节点下所有目标和成果（含已有权重）。通常用于关键岗位设置弹窗的初始化。

**基本信息**

| 项目     | 说明                             |
| -------- | -------------------------------- |
| 接口地址 | `/bp/group/getKeyPositionDetail` |
| 请求方式 | `GET`                            |

**请求参数**

| 参数      | 类型 | 必填 | 说明    |
| --------- | ---- | ---- | ------- |
| `groupId` | Long | 是   | 分组 ID |

**响应参数**

`data`：`KeyPositionDetailVO`，见 **三、3.16**（本接口已废弃，结构仅供参考）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "groupId": "2014631829004371002",
    "groupName": "张三",
    "keyPosition": true,
    "keyPositionReason": "业务核心负责人",
    "bonusCoefficient": 1.2,
    "bonusCoefficientPersonal": 1.0,
    "bonusCoefficientDept": 1.1,
    "bonusCoefficientCenter": 1.0,
    "bonusCoefficientGroup": 1.0,
    "bonusCoefficientReason": "表现优异",
    "isParentAdmin": true,
    "isDirectLeader": false,
    "goals": [
      {
        "taskId": "2014631829004374017",
        "name": "Q1业绩目标",
        "status": 2,
        "weight": 60,
        "results": [
          {
            "taskId": "2014631829004374018",
            "name": "客户拜访量达到50家",
            "status": 2,
            "weight": 100
          }
        ]
      }
    ]
  }
}
```

---

### 2.17 批量获取关键岗位详情(Markdown)

批量查询关键岗位信息，返回 Markdown 格式字符串。包含每个分组的基本信息（分组ID、分组名称）、关键岗位状态及原因、奖金系数相关字段、以及目标列表（目标ID + 目标名称 + 权重）。不包含关键成果和关键举措。

**基本信息**

| 项目         | 说明                                       |
| ------------ | ------------------------------------------ |
| 接口地址     | `/bp/group/batchGetKeyPositionMarkdown`    |
| 请求方式     | `POST`                                     |
| Content-Type | `application/json`                         |

**请求参数**

请求体为 JSON 数组，元素为分组 ID（Long 类型，个人类型分组）：

```json
[2014631829004371002, 2014631829004371003]
```

| 参数   | 类型         | 必填 | 说明                     |
| ------ | ------------ | ---- | ------------------------ |
| (body) | `List<Long>` | 是   | 分组 ID 列表（个人类型） |

**响应参数**

`data`：`String`（Markdown 正文）。下文为正文**结构示意**。

**Markdown 结构示意**

```
# 关键岗位详情（批量）

## 张三

| 项目 | 内容 |
|------|------|
| 分组ID | 2014631829004371002 |
| 分组名称 | 张三 |
| 是否关键岗位 | 是 |
| 关键岗位原因 | 业务核心负责人 |
| 奖金系数建议(月) | 1.2 |
| 个人奖金系数建议(月) | 1.0 |
| 部门奖金系数建议(月) | 1.1 |
| 中心奖金系数建议(月) | 1.0 |
| 集团奖金系数建议(月) | 1.0 |
| 奖金系数建议原因 | 表现优异 |

### 目标列表

| 目标ID | 目标名称 | 权重 |
|--------|----------|------|
| 2014631829004374017 | Q1业绩目标 | 60 |

---
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "# 关键岗位详情（批量）\n\n## 张三\n\n| 项目 | 内容 |\n|------|------|\n| 分组ID | 2014631829004371002 |\n| 分组名称 | 张三 |\n..."
}
```

**请求示例**

```bash
curl -X POST 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/batchGetKeyPositionMarkdown' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '[2014631829004371002, 2014631829004371003]'
```

**数据流向**

返回的 Markdown 文本可直接用于 AI 分析、文档展示等场景。该接口整合了多个分组的关键岗位信息，适用于批量查看关键岗位及目标权重分配情况。

---

### 2.18 获取目标轻量列表（listGoals）

按分组 ID 返回该分组下目标的 **Simple** 扁平列表（不内嵌 KR / Action），含 `krCount`、`actionCount`、`taskUsers`，便于 Agent 预判规模后再调用 **2.5**。

**规范命名**：`listGoals`（规划 G3）。

**基本信息**

| 项目     | 说明              |
| -------- | ----------------- |
| 接口地址 | `/bp/goal/list`   |
| 请求方式 | `GET`             |

**请求参数**

| 参数      | 类型 | 必填 | 说明                                                         |
| --------- | ---- | ---- | ------------------------------------------------------------ |
| `groupId` | Long | 是   | 分组 ID（来自 **2.2** 的节点 `id`，或 **2.3** 返回的 Map value） |

**响应参数**

`data`：`List<GoalSimpleVO>`，元素字段见 **一、1.4.3** **Simple（✅）** 列。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2014631829004374017",
      "name": "Q1 业绩目标",
      "fullLevelNumber": "A4-1",
      "statusDesc": "进行中",
      "reportCycle": "week+1",
      "planDateRange": "2026-01-01 ~ 2026-03-31",
      "krCount": 3,
      "actionCount": 8,
      "taskUsers": [
        {
          "taskId": "2014631829004374017",
          "role": "承接人",
          "empList": [{ "id": "1234567890123456789", "name": "张三" }]
        }
      ]
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/goal/list?groupId=2014631829004374001' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `id` → **2.5 获取目标详情** 的路径参数 `goalId`。

---

### 2.19 获取关键成果轻量列表（listKeyResults）

按目标 ID 返回关键成果的 **Simple** 扁平列表。

**规范命名**：`listKeyResults`（规划 G4）。

**基本信息**

| 项目     | 说明                   |
| -------- | ---------------------- |
| 接口地址 | `/bp/keyResult/list`   |
| 请求方式 | `GET`                  |

**请求参数**

| 参数     | 类型 | 必填 | 说明                                    |
| -------- | ---- | ---- | --------------------------------------- |
| `goalId` | Long | 是   | 目标 ID（来自 **2.4** / **2.18** 等） |

**响应参数**

`data`：`List<KeyResultSimpleVO>`，元素字段见 **一、1.4.4** **Simple（✅）** 列。

**响应示例**

```json
{
  "resultCode": 1,
  "data": [
    {
      "id": "2014631829004374018",
      "name": "客户拜访量达到50家",
      "fullLevelNumber": "A4-1.1",
      "statusDesc": "进行中",
      "measureStandard": "拜访记录数 >= 50",
      "reportCycle": "week+1",
      "planDateRange": "2026-01-01 ~ 2026-02-28",
      "actionCount": 2,
      "taskUsers": []
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/keyResult/list?goalId=2014631829004374017' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `id` → **2.6 获取关键成果详情** 的路径参数 `keyResultId`。

---

### 2.20 获取关键举措轻量列表（listActions）

按关键成果 ID 返回关键举措的 **Simple** 扁平列表。

**规范命名**：`listActions`（规划 G5）。

**基本信息**

| 项目     | 说明                |
| -------- | ------------------- |
| 接口地址 | `/bp/action/list`   |
| 请求方式 | `GET`               |

**请求参数**

| 参数          | 类型 | 必填 | 说明                                      |
| ------------- | ---- | ---- | ----------------------------------------- |
| `keyResultId` | Long | 是   | 关键成果 ID（来自 **2.4** / **2.19** 等） |

**响应参数**

`data`：`List<ActionSimpleVO>`，元素字段见 **一、1.4.5** **Simple（✅）** 列。

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/action/list?keyResultId=2014631829004374018' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `id` → **2.7 获取关键举措详情** 的路径参数 `actionId`。

---

### 2.21 获取任务子树骨架（listTaskChildren）

传入目标 ID 或关键成果 ID，返回其下级子树的 **id** 和 **名称**，用于 AI 了解 BP 的层级结构骨架（不含衡量标准、参与人、汇报周期等详细信息）。

**规范命名**：`listTaskChildren`（规划 G6）。

**基本信息**

| 项目     | 说明                |
| -------- | ------------------- |
| 接口地址 | `/bp/task/children` |
| 请求方式 | `GET`               |

**请求参数**

| 参数       | 类型 | 必填 | 说明                                                                    |
| ---------- | ---- | ---- | ----------------------------------------------------------------------- |
| `parentId` | Long | 是   | 目标 ID 或关键成果 ID（来自 **2.4** / **2.18** / **2.19** 等返回的 `id`） |

**响应参数**

`data`：`List<TaskSkeletonVO>`，元素见 **三、3.17 TaskSkeletonVO**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2014631829004374018",
      "name": "客户拜访量达到50家",
      "type": "关键成果",
      "children": [
        { "id": "2014631829004374019", "name": "每周拜访5家客户", "type": "关键举措", "children": null },
        { "id": "2014631829004374020", "name": "建立拜访记录系统", "type": "关键举措", "children": null }
      ]
    },
    {
      "id": "2014631829004374021",
      "name": "签约客户数达到20家",
      "type": "关键成果",
      "children": [
        { "id": "2014631829004374022", "name": "重点客户专项跟进", "type": "关键举措", "children": null }
      ]
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/children?parentId=2014631829004374017' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

- 返回的子节点 `id` → 可用于 **2.5 / 2.6 / 2.7** 获取详情，或 **2.8** 查询汇报
- 本接口有数据权限校验（PMS 端 `withPermission=true`），无权限时返回空列表

---

## 三、公共数据结构

以下为多个接口共用的数据结构定义。**第二章「接口详细说明」的响应参数**一般只写出 `data` 的类型；字段与嵌套类型以**本章**及**第一章 1.4**为准，不在接口处重复展开。

---

### 3.1 TaskTreeVO（对应接口二、2.4）

用于 **二、2.4 查询任务树**（`getSimpleTree`）返回的递归树节点；仅承载**树形导航**所需的少量字段，**不等同于** `GoalSimpleVO` / `GoalFullVO` 等业务规格。

| 字段       | 类型              | 说明                                                         |
| ---------- | ----------------- | ------------------------------------------------------------ |
| `id`       | Long              | 任务 ID（目标 / 关键成果 / 关键举措）                        |
| `name`     | String            | 任务名称                                                     |
| `groupId`  | Long              | 所属分组 ID                                                  |
| `type`     | String            | 类型：`目标` / `关键成果` / `关键举措`                       |
| `children` | List\<TaskTreeVO> | 子节点（目标下挂关键成果，关键成果下挂关键举措；叶节点为空数组） |

---

### 3.2 GoalFullVO、KeyResultFullVO、ActionFullVO（详情响应）

| 类型 | 对应接口 | 字段来源 |
| ---- | -------- | -------- |
| `GoalFullVO` | 二、2.5 `getGoalDetail` | 「**一、1.4.3**」表 **Full（✅）**；`keyResults` 为 `List<KeyResultFullVO>` |
| `KeyResultFullVO` | 二、2.6 `getKeyResultDetail` | 「**一、1.4.4**」表 **Full（✅）**；`actions` 为 `List<ActionFullVO>` |
| `ActionFullVO` | 二、2.7 `getActionDetail` | 「**一、1.4.5**」表 **Full（✅）** |

上述类型**均不按** `BaseTaskVO` **继承建模**；嵌套字段与 **Full** 列一致；**响应体不含 `groupId`**（见 **一、1.4.3~1.4.5** 下方说明）。`taskUsers` 见 **三、3.4 TaskUserVO**，`taskDepts` 见 **三、3.6 TaskDeptVO**，`upwardTaskList` / `downTaskList` 见 **三、3.8 SimpleTaskVO**（内含 `BaseInfo`）。

旧版实现曾使用 `BaseTaskVO`、`GoalAndKeyResultVO`、`KeyResultVO`、`ActionVO` 等命名，**已废弃**，请勿再以「继承 BaseTaskVO」理解当前接口。

---

### 3.3 BaseTaskVO（已废弃，仅历史对照）

历史详情接口曾统一以 `BaseTaskVO` 描述公共字段。当前规范以 **一、1.4.x** 的 **Full** 列与 **三、3.1 / 3.2** 为准；新对接**禁止**依赖 `BaseTaskVO` 继承关系。

---

### 3.4 TaskUserVO（任务参与人）

| 字段      | 类型             | 说明                                                         |
| --------- | ---------------- | ------------------------------------------------------------ |
| `taskId`  | Long             | 任务 ID                                                      |
| `role`    | String           | 角色（中文）：`承接人` / `协办人` / `抄送人` / `监督人` / `观察人` |
| `empList` | List\<EmpBaseVO> | 该角色下的员工列表                                           |

---

### 3.5 EmpBaseVO（员工基础信息）

| 字段     | 类型   | 说明     |
| -------- | ------ | -------- |
| `id`     | Long   | 员工 ID  |
| `name`   | String | 员工姓名 |

---

### 3.6 TaskDeptVO（任务参与部门）

| 字段       | 类型          | 说明                                                         |
| ---------- | ------------- | ------------------------------------------------------------ |
| `taskId`   | Long          | 任务 ID                                                      |
| `role`     | String        | 角色（中文）：`承接人` / `协办人` / `抄送人` / `监督人` / `观察人` |
| `deptList` | List\<DeptVO> | 部门信息列表                                                 |

---

### 3.7 DeptVO（部门信息）

| 字段   | 类型   | 说明     |
| ------ | ------ | -------- |
| `id`   | Long   | 部门 ID  |
| `name` | String | 部门名称 |

---

### 3.8 SimpleTaskVO（简要任务信息）

用于 `upwardTaskList`（向上对齐任务）和 `downTaskList`（向下对齐任务）。

| 字段        | 类型     | 说明         |
| ----------- | -------- | ------------ |
| `id`        | Long     | 任务 ID      |
| `name`      | String   | 任务名称     |
| `groupInfo` | BaseInfo | 所属分组信息 |

**BaseInfo 结构：**

| 字段   | 类型   | 说明 |
| ------ | ------ | ---- |
| `id`   | Long   | ID   |
| `name` | String | 名称 |

---

### 3.9 TaskBriefVO（任务简要信息）

用于 `TaskSearchVO` 中的 `parentTask`（上级任务）和 `childTasks`（下级任务列表）。

| 字段         | 类型   | 说明                                    |
| ------------ | ------ | --------------------------------------- |
| `id`         | Long   | 任务 ID                                 |
| `name`       | String | 任务名称                                |
| `type`       | String | 类型：`目标` / `关键成果` / `关键举措`  |
| `statusDesc` | String | 任务状态（草稿/未启动/进行中/已关闭） |

---

### 3.10 GroupBriefVO（分组简要信息）

用于 `GroupSearchVO` 中的 `parentGroup`（上级分组）。

| 字段   | 类型   | 说明                                              |
| ------ | ------ | ------------------------------------------------- |
| `id`   | Long   | 分组 ID                                           |
| `name` | String | 分组名称                                          |
| `type` | String | 类型：`org` = 组织节点，`personal` = 个人节点     |

---

### 3.11 PageInfo（分页结构）

| 字段       | 类型     | 说明              |
| ---------- | -------- | ----------------- |
| `total`    | Long     | 总记录数          |
| `list`     | List\<T> | 结果集            |
| `pageNum`  | Integer  | 当前页，从 1 开始 |
| `pageSize` | Integer  | 每页的数量        |
| `size`     | Integer  | 当前页的数量      |

---

### 3.12 TaskReportUnionVO（汇报联合项 — 二、2.8 分页 `list` 元素）

| 字段       | 类型   | 说明                                      |
| ---------- | ------ | ----------------------------------------- |
| `bizId`    | Long   | 汇报ID                                   |
| `typeDesc` | String | 汇报类型（中文）：`手动汇报` / `AI汇报`  |

---

### 3.13 AiDelayReportRecordVO（AI 延期提醒记录 — 二、2.10）

| 字段             | 类型    | 说明                                  |
| ---------------- | ------- | ------------------------------------- |
| `id`             | Long    | 记录 ID                               |
| `receiverEmpId`  | Long    | 接收汇报人员工 ID                     |
| `reportContent`  | String  | 汇报内容                              |
| `reportRecordId` | Long    | 汇报记录 ID（发送成功后回写）         |
| `sendStatus`     | Integer | 发送状态：`0` = 失败，`1` = 成功      |
| `errorMsg`       | String  | 失败原因（发送成功时为 `null`）       |
| `createTime`     | String  | 创建时间，格式：`yyyy-MM-dd HH:mm:ss` |

---

### 3.14 TaskSearchVO（任务搜索结果 — 二、2.11）

| 字段              | 类型               | 说明                                                                                  |
| ----------------- | ------------------ | ------------------------------------------------------------------------------------- |
| `id`              | Long               | 任务 ID                                                                               |
| `name`            | String             | 任务名称                                                                              |
| `groupId`         | Long               | 所属分组 ID                                                                           |
| `groupName`       | String             | 所属分组名称                                                                          |
| `type`            | String             | 类型：`目标` / `关键成果` / `关键举措`                                                |
| `statusDesc`      | String             | 任务状态（草稿/未启动/进行中/已关闭）                                                 |
| `reportCycle`     | String             | 汇报周期，格式: `{ruleType}+{index}`，如 `week+1`                                     |
| `planDateRange`   | String             | 计划时间区间，格式: `yyyy-MM-dd ~ yyyy-MM-dd`                                        |
| `fullLevelNumber` | String             | 任务完整编码                                                                          |
| `taskUsers`       | List\<TaskUserVO>  | 任务参与人列表（见 **三、3.4**）                                                          |
| `parentTask`      | TaskBriefVO        | 上级任务（见 **三、3.9**）                                                                |
| `childTasks`      | List\<TaskBriefVO> | 下级任务列表（见 **三、3.9**）                                                            |

---

### 3.15 GroupSearchVO（分组搜索结果 — 二、2.12）

| 字段          | 类型         | 说明                                              |
| ------------- | ------------ | ------------------------------------------------- |
| `id`          | Long         | 分组 ID                                           |
| `name`        | String       | 分组名称                                          |
| `periodId`    | Long         | 所属周期 ID                                       |
| `type`        | String       | 类型：`org` = 组织节点，`personal` = 个人节点     |
| `levelNumber` | String       | 层级编码                                          |
| `employeeId`  | Long         | 员工 ID（个人类型时有效）                         |
| `parentGroup` | GroupBriefVO | 上级分组（见 **三、3.10**）                           |
| `childCount`  | Integer      | 下级分组数量                                      |

---

### 3.16 KeyPositionDetailVO（关键岗位详情 — 二、2.16 已废弃，结构备查）

| 字段                       | 类型                  | 说明                         |
| -------------------------- | --------------------- | ---------------------------- |
| `groupId`                  | Long                  | 分组 ID                      |
| `groupName`                | String                | 岗位名称（人员姓名）         |
| `keyPosition`              | Boolean               | 是否关键岗位                 |
| `keyPositionReason`        | String                | 设置为关键岗位的原因         |
| `bonusCoefficient`         | BigDecimal            | 奖金系数建议(月)             |
| `bonusCoefficientPersonal` | BigDecimal            | 个人奖金系数建议(%)          |
| `bonusCoefficientDept`     | BigDecimal            | 部门奖金系数建议(%)          |
| `bonusCoefficientCenter`   | BigDecimal            | 中心奖金系数建议(%)          |
| `bonusCoefficientGroup`    | BigDecimal            | 集团奖金系数建议(%)          |
| `bonusCoefficientReason`   | String                | 奖金系数建议原因             |
| `isParentAdmin`            | Boolean               | 是否为直接上级组织管理员     |
| `isDirectLeader`           | Boolean               | 是否为组织架构的直属上级领导 |
| `goals`                    | List\<GoalWeightVO>   | 目标及权重列表               |

**GoalWeightVO**

| 字段      | 类型                   | 说明                                             |
| --------- | ---------------------- | ------------------------------------------------ |
| `taskId`  | Long                   | 目标任务 ID                                      |
| `name`    | String                 | 目标名称                                         |
| `status`  | Integer                | 目标状态（0-草稿、1-待发布、2-进行中、3-已关闭） |
| `weight`  | BigDecimal             | 目标权重（0-100）                                |
| `results` | List\<ResultWeightVO>  | 成果权重列表                                     |

**ResultWeightVO**

| 字段     | 类型       | 说明                                             |
| -------- | ---------- | ------------------------------------------------ |
| `taskId` | Long       | 成果任务 ID                                      |
| `name`   | String     | 成果名称                                         |
| `status` | Integer    | 成果状态（0-草稿、1-待发布、2-进行中、3-已关闭） |
| `weight` | BigDecimal | 成果权重（0-100）                                |

---

### 3.17 TaskSkeletonVO（任务骨架节点 — 二、2.21）

用于 **二、2.21 获取任务子树骨架** 返回的递归树节点；仅包含 `id` 和 `name`，供 AI 了解 BP 层级结构。

| 字段       | 类型                    | 说明                                        |
| ---------- | ----------------------- | ------------------------------------------- |
| `id`       | Long                    | 任务 ID                                     |
| `name`     | String                  | 任务名称                                    |
| `type`     | String                  | 类型：`目标` / `关键成果` / `关键举措`      |
| `children` | List\<TaskSkeletonVO\>  | 子节点（叶节点为 `null`）                   |

---

## 四、错误码说明

| resultCode | 说明                                         |
| ---------- | -------------------------------------------- |
| 1          | 请求成功                                     |
| 0          | 通用失败                                     |
| 500        | 系统异常，请稍后重试                         |
| 610002     | appKey 无效                                  |
| 610003     | appSecret 无效                               |
| 610005     | sign 签名无效                                |
| 610006     | access_key 无效或不是最新的                  |
| 610007     | access_key 授权已达上限                      |
| 610008     | 请求 URL 不在白名单内                        |
| 610009     | 请求方法不支持                               |
| 610010     | nonce 无效                                   |
| 610011     | timestamp 无效（与服务器时间差超过 30 分钟） |
| 610012     | 请求太过频繁，请稍候再试                     |
| 610013     | 请求 URL 未找到                              |
| 610014     | 应用已被禁用                                 |
| 610015     | 无访问权限                                   |
| 610016     | openUserId 无效                              |
| 610017     | 根据 openId 获取用户信息错误                 |
| 610018     | 非当前企业的用户                             |
| 610019     | 用户已被禁用                                 |
| 610020     | 根据 appKey 获取用户信息错误                 |
| 610030     | 重复的请求（nonce 已使用过）                 |

---
