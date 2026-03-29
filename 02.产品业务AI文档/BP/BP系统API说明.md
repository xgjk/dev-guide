# BP 目标管理 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |
| 1.1 | 2026-03-25 | 新增 4.13 获取BP完整Markdown内容接口 | 曾文哲 |
| 1.2 | 2026-03-27 | 新增 4.14~4.15 接口（根据目标/成果ID新增下级任务） | 刘会芳 |
| 1.3 | 2026-03-28 | 新增 4.16 接口（获取关键岗位详情） | 刘会芳 |
| 1.4 | 2026-03-28 | 更新 4.16 接口奖金系数单位（个人/部门/中心/集团）由 “月” 改为 “%” | 刘会芳 |
| 1.5 | 2026-03-29 | 废弃 4.16 获取关键岗位详情接口（单个/JSON），新增 4.17 批量获取关键岗位详情(Markdown)接口 | 曾文哲 |

## 一、概述

本文档描述了 BP（Business Plan）目标管理系统对外开放的全部 API 接口。通过这些接口，可以实现以下业务能力：

1. **查询周期列表** — 获取系统中所有 BP 周期（年度、季度等），用于确定当前启用的周期
2. **获取分组树** — 根据周期 ID 获取该周期下的完整分组树形结构（组织分组 + 个人分组）
3. **批量查询员工个人分组 ID** — 根据员工 ID 列表，快速获取每个员工在当前启用周期下的个人分组 ID
4. **查询任务树** — 根据分组 ID 获取完整的 BP 任务树形结构（目标 → 关键成果 → 关键举措）
5. **获取一组目标数据（包含下所有的关键成果、关键举措）** — 根据目标 ID 获取目标及其下所有关键成果、关键举措的完整数据
6. **获取一组关键成果（包含下所有的关键举措）** — 根据关键成果 ID 获取关键成果及其下所有关键举措的完整数据
7. **获取关键举措详情** — 根据关键举措 ID 获取关键举措的完整数据
8. **分页查询任务关联汇报** — 根据任务 ID 分页查询该任务关联的所有汇报（含手动汇报和 AI 汇报）
9. **发送 AI 延期提醒汇报** — 对未完成 BP 的员工发送延期提醒汇报
10. **查询延期提醒汇报历史** — 查询某员工历史收到的所有延期提醒汇报记录
11. **按名称模糊搜索任务** — 根据分组 ID 和名称关键字模糊搜索任务，返回任务基本信息、参与人及上下级任务信息
12. **按名称模糊搜索分组** — 根据周期 ID 和名称关键字模糊搜索分组，返回分组基本信息及上下级信息
13. **获取BP完整Markdown内容** — 根据分组 ID 获取该分组下完整 BP 的 Markdown 格式内容，包含本级目标树、上对齐关系、下对齐关系
14. **根据目标ID新增关键成果** — 纯新增成果，不影响该目标下已有的其他成果
15. **根据成果ID新增关键举措** — 纯新增举措，不影响该成果下已有的其他举措
16. ~~**获取关键岗位详情**~~ — ⚠️ 已废弃，请使用 4.17 接口替代
17. **批量获取关键岗位详情(Markdown)** — 批量查询关键岗位信息，返回 Markdown 格式，包含分组信息、奖金系数、目标名称+ID+权重

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境     | 域名                                        |
| -------- | ------------------------------------------- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` |

### 2.3 公共请求头

| Header   | 说明                       | 是否必填 |
| -------- | -------------------------- | -------- |
| `appKey` | 应用密钥，请联系管理员获取 | 是       |

### 2.4 通用响应结构

所有接口返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段         | 类型    | 说明                                        |
| ------------ | ------- | ------------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，其他值表示失败    |
| `resultMsg`  | String  | 提示信息，成功时为 `null`，失败时为错误描述 |
| `data`       | T       | 业务数据，不同接口类型不同，失败时为 `null` |

---

## 三、关键业务流程说明

以下通过具体业务场景，说明接口之间的调用顺序和参数传递关系。

### 场景一：查看某个部门的 BP 分组树

> 需求：获取当前启用周期下，某个部门（组织节点）及其下属员工（个人节点）的分组结构。

1. 调用 **4.1 查询周期列表**（`GET /bp/period/getAllPeriod`），获取所有周期，筛选 `status = 1` 的启用周期，拿到 `periodId`
2. 调用 **4.2 获取分组树**（`GET /bp/group/getTree?periodId={periodId}`），传入上一步的 `periodId`，返回完整的分组树
3. 在分组树中，`type = "org"` 的节点为组织分组（部门），`type = "personal"` 的节点为个人分组（员工），通过 `children` 递归遍历即可获取完整层级

### 场景二：查看某个员工的完整目标树

> 需求：已知员工 ID，查看该员工在当前启用周期下的所有目标、关键成果、关键举措。

1. 调用 **4.3 批量查询员工个人分组 ID**（`POST /bp/group/getPersonalGroupIds`），传入员工 ID 列表，返回 `Map<员工ID, 分组ID>`，拿到该员工的 `groupId`（若返回 `null`，说明该员工在当前周期未创建 BP）
2. 调用 **4.4 查询任务树**（`GET /bp/task/v2/getSimpleTree?groupId={groupId}`），传入上一步的 `groupId`，返回完整的任务树
3. 任务树为递归结构：目标（`type = "目标"`）→ 关键成果（`type = "关键成果"`）→ 关键举措（`type = "关键举措"`），通过 `children` 递归遍历

### 场景三：获取某个目标的完整详情（含关键成果和关键举措）

> 需求：已知目标 ID，获取该目标的详细信息，包括所有关键成果及其下的关键举措、对齐任务等。

1. 调用 **4.5 获取一组目标数据（包含下所有的关键成果、关键举措）**（`GET /bp/task/v2/getGoalAndKeyResult?id={目标ID}`），传入目标 ID
2. 返回的 `GoalAndKeyResultVO` 包含 `keyResults` 列表，每个关键成果又包含 `actions` 列表，一次调用即可获取目标下的完整数据
3. 如需进一步查看某个关键成果的详情（含对齐任务等），可取 `keyResults[].id` 调用 **4.6 获取一组关键成果（包含下所有的关键举措）**
4. 如需进一步查看某个关键举措的详情，可取 `actions[].id` 调用 **4.7 获取关键举措详情**

### 场景四：查看某个任务关联的汇报记录

> 需求：查看某个目标/关键成果/关键举措关联的所有汇报（包含手动汇报和 AI 汇报）。

1. 通过场景二或场景三获取到任务 ID（目标、关键成果、关键举措均可）
2. 调用 **4.8 分页查询所有汇报**（`POST /bp/task/relation/pageAllReports`），传入 `taskId` 及分页参数
3. 返回的 `PageInfo<TaskReportUnionVO>` 中，每条记录通过 `type` 区分：`manual` 为手动汇报，`ai` 为 AI 汇报

### 场景五：对延期员工发送 AI 提醒汇报并查看历史

> 需求：对未按时完成 BP 的员工发送延期提醒汇报，并查看该员工历史收到的所有提醒记录。

1. 通过业务逻辑或其他方式确定需要发送提醒的员工（如人工筛选、业务系统对接等）
2. 调用 **4.9 发送 AI 延期提醒汇报**（`POST /bp/delayReport/send`），传入 `receiverEmpId`（**注意：是员工 ID，不是分组 ID**）、`reportName`、`content`
3. 调用 **4.10 查询 AI 延期提醒汇报历史**（`GET /bp/delayReport/list?receiverEmpId={empId}`），可查看该员工历史收到的所有延期提醒记录，包括发送状态和失败原因

### 场景六：遍历全公司所有员工的 BP 完成情况

> 需求：批量获取全公司员工的 BP 目标及进度，用于全局统计或数据分析。

1. 调用 **4.1 查询周期列表**，获取启用周期的 `periodId`
2. 调用 **4.2 获取分组树**（`onlyPersonal = true`），只获取个人分组节点，每个节点的 `employeeId` 即为员工 ID
3. 遍历所有个人分组节点，依次调用 **4.4 查询任务树**，获取每个员工的目标树

### 场景七：从周期逐级下钻到关键举措详情

> 需求：从周期 → 分组 → 目标 → 关键举措，完整走一遍数据下钻流程。

1. 调用 **4.1 查询周期列表** → 拿到 `periodId`
2. 调用 **4.2 获取分组树** → 选择某个 `type = "personal"` 的节点，拿到 `groupId`
3. 调用 **4.4 查询任务树** → 拿到目标树，选择 `type = "目标"` 的节点 `id`
4. 调用 **4.5 获取一组目标数据（包含下所有的关键成果、关键举措）** → 返回的数据中已包含 `keyResults[].actions[].id`，可直接拿到关键举措 ID
5. 调用 **4.7 获取关键举措详情** → 传入上一步拿到的关键举措 `id`，查看完整关键举措数据（含对齐任务等）

> 说明：目标详情接口（4.5）一次返回了目标下所有关键成果及关键举措的 ID，无需额外调用 4.6 获取关键成果详情来获取举措 ID。

---

## 四、接口详细说明

---

### 4.1 查询周期列表

获取系统中所有 BP 周期信息，可选按名称模糊搜索。通常作为整个调用流程的**第一步**，用于获取 `periodId`。

**基本信息**

| 项目     | 说明                      |
| -------- | ------------------------- |
| 接口地址 | `/bp/period/getAllPeriod` |
| 请求方式 | `GET`                     |

**请求参数**

| 参数   | 类型   | 必填 | 说明                   |
| ------ | ------ | ---- | ---------------------- |
| `name` | String | 否   | 周期名称，支持模糊搜索 |

**响应参数**

`data` 类型为 `List<PeriodVO>`，每个周期字段如下：

| 字段     | 类型    | 说明                               |
| -------- | ------- | ---------------------------------- |
| `id`     | Long    | 周期 ID                            |
| `name`   | String  | 周期名称                           |
| `status` | Integer | 周期状态：`1` = 启用，`0` = 未启用 |

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
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/period/getAllPeriod?name=2026' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `id`（周期 ID）用于 **4.2 获取分组树** 的 `periodId` 入参。通常选择 `status = 1`（启用状态）的周期。

---

### 4.2 获取分组树

根据周期 ID 获取该周期下的完整分组树形结构，包含组织分组和个人分组。

**基本信息**

| 项目     | 说明                |
| -------- | ------------------- |
| 接口地址 | `/bp/group/getTree` |
| 请求方式 | `GET`               |

**请求参数**

| 参数           | 类型    | 必填 | 说明                                                      |
| -------------- | ------- | ---- | --------------------------------------------------------- |
| `periodId`     | Long    | 是   | 周期 ID（来自 **4.1 查询周期列表** 返回的 `PeriodVO.id`） |
| `onlyPersonal` | Boolean | 否   | 是否只查询个人分组，默认 `false`                          |

**响应参数**

`data` 类型为 `List<GroupTreeVO>`，为树形结构，每个节点字段如下：

| 字段          | 类型               | 说明                                              |
| ------------- | ------------------ | ------------------------------------------------- |
| `id`          | Long               | 分组 ID                                           |
| `name`        | String             | 分组名称                                          |
| `type`        | String             | 分组类型：`org` = 组织节点，`personal` = 个人节点 |
| `employeeId`  | Long               | 员工 ID（仅 `type = personal` 时有效）            |
| `parentId`    | Long               | 父节点 ID                                         |
| `levelNumber` | String             | 层级编码                                          |
| `children`    | List\<GroupTreeVO> | 子节点列表（递归结构）                            |

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
      "children": [
        {
          "id": "2014631829004371002",
          "name": "张三",
          "type": "personal",
          "employeeId": "1234567890123456789",
          "parentId": "2014631829004371001",
          "levelNumber": "1.1",
          "children": []
        }
      ]
    }
  ]
}
```

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/getTree?periodId=2014631829004370001&onlyPersonal=false' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的分组 `id` 用于 **4.4 查询任务树** 的 `groupId` 入参。其中 `type = personal` 的节点代表个人分组，`type = org` 的节点代表组织分组。

---

### 4.3 批量查询员工个人类型分组 ID

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

`data` 类型为 `Map<Long, Long>`，key 为员工 ID，value 为该员工在启用周期下的个人类型分组 ID。

| 字段            | 类型 | 说明                                                      |
| --------------- | ---- | --------------------------------------------------------- |
| `data.{员工ID}` | Long | 该员工的个人类型分组 ID；若为 `null`，说明该员工未创建 BP |

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

返回的 Map value（分组 ID）用于 **4.4 查询任务树** 的 `groupId` 入参。若 value 为 `null`，说明该员工在当前启用周期下尚未创建 BP。

---

### 4.4 查询任务树

根据分组 ID 查询该分组下的完整 BP 任务树形结构，包含目标（Goal）、关键成果（Key Result）、关键举措（Action）三个层级。

**基本信息**

| 项目     | 说明                        |
| -------- | --------------------------- |
| 接口地址 | `/bp/task/v2/getSimpleTree` |
| 请求方式 | `GET`                       |

**请求参数**

| 参数      | 类型 | 必填 | 说明                                                         |
| --------- | ---- | ---- | ------------------------------------------------------------ |
| `groupId` | Long | 是   | 分组 ID（来自 **4.2 获取分组树** 的 `GroupTreeVO.id`，或 **4.3 批量查询** 返回的 Map value） |

**响应参数**

`data` 类型为 `List<TaskTreeVO>`，为树形结构，每个节点字段如下：

| 字段       | 类型              | 说明                                                         |
| ---------- | ----------------- | ------------------------------------------------------------ |
| `id`       | Long              | 任务 ID                                                      |
| `name`     | String            | 任务名称                                                     |
| `groupId`  | Long              | 所属目标分组 ID                                              |
| `type`     | String            | 类型：`目标` / `关键成果` / `关键举措`                       |
| `children` | List\<TaskTreeVO> | 子节点列表（递归结构：目标下挂关键成果，关键成果下挂关键举措） |

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

- 树中 `type = "目标"` 的节点 `id` → 用于 **4.5 获取目标详情** 的 `id` 入参
- 树中 `type = "关键成果"` 的节点 `id` → 用于 **4.6 获取关键成果详情** 的 `id` 入参
- 树中 `type = "关键举措"` 的节点 `id` → 用于 **4.7 获取关键举措详情** 的 `id` 入参
- 树中任意节点的 `id` → 用于 **4.8 分页查询所有汇报** 的 `taskId` 入参

---

### 4.5 获取一组目标数据（包含下所有的关键成果、关键举措）

根据目标 ID 获取目标的完整详情，包含该目标下的所有关键成果及关键举措。相比 4.4 任务树的简要信息，本接口返回更丰富的字段（如对齐任务等）。

**基本信息**

| 项目     | 说明                              |
| -------- | --------------------------------- |
| 接口地址 | `/bp/task/v2/getGoalAndKeyResult` |
| 请求方式 | `GET`                             |

**请求参数**

| 参数 | 类型 | 必填 | 说明                                                         |
| ---- | ---- | ---- | ------------------------------------------------------------ |
| `id` | Long | 是   | 目标 ID（来自 **4.4 查询任务树** 中 `type = "目标"` 的节点 `id`） |

**响应参数**

`data` 类型为 `GoalAndKeyResultVO`（继承 `BaseTaskVO`，公共字段见 **五、公共数据结构**），自身特有字段如下：

| 字段         | 类型               | 说明                                                       |
| ------------ | ------------------ | ---------------------------------------------------------- |
| `keyResults` | List\<KeyResultVO> | 关键成果列表（每个 KeyResultVO 含 `actions` 关键举措列表） |

> `BaseTaskVO` 公共字段包括：`id`, `groupId`, `name`, `statusDesc`, `reportCycle`, `planDateRange`, `taskUsers`, `taskDepts`, `upwardTaskList`, `downTaskList`, `path`, `fullLevelNumber`。详见 **五、公共数据结构**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": "2014631829004374017",
    "groupId": "2014631829004374001",
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
        "groupId": "2014631829004374001",
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
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/getGoalAndKeyResult?id=2014631829004374017' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

- 返回的 `keyResults[].id` → 可用于 **4.6 获取关键成果详情** 的 `id` 入参
- 返回的 `keyResults[].actions[].id` → 可用于 **4.7 获取关键举措详情** 的 `id` 入参

---

### 4.6 获取一组关键成果（包含下所有的关键举措）

根据关键成果 ID 获取关键成果的完整详情，包含该关键成果下的所有关键举措。

**基本信息**

| 项目     | 说明                       |
| -------- | -------------------------- |
| 接口地址 | `/bp/task/v2/getKeyResult` |
| 请求方式 | `GET`                      |

**请求参数**

| 参数 | 类型 | 必填 | 说明                                                         |
| ---- | ---- | ---- | ------------------------------------------------------------ |
| `id` | Long | 是   | 关键成果 ID（来自 **4.4 查询任务树** 中 `type = "关键成果"` 的节点 `id`，或 **4.5** 返回的 `keyResults[].id`） |

**响应参数**

`data` 类型为 `KeyResultVO`（继承 `BaseTaskVO`），自身特有字段如下：

| 字段              | 类型            | 说明             |
| ----------------- | --------------- | ---------------- |
| `measureStandard` | String          | 衡量标准         |
| `actions`         | List\<ActionVO> | 关键举措列表     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": "2014631829004374018",
    "groupId": "2014631829004374001",
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
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/getKeyResult?id=2014631829004374018' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 `actions[].id` → 可用于 **4.7 获取关键举措详情** 的 `id` 入参。

---

### 4.7 获取关键举措详情

根据关键举措 ID 获取关键举措的完整详情。

**基本信息**

| 项目     | 说明                    |
| -------- | ----------------------- |
| 接口地址 | `/bp/task/v2/getAction` |
| 请求方式 | `GET`                   |

**请求参数**

| 参数 | 类型 | 必填 | 说明                                                         |
| ---- | ---- | ---- | ------------------------------------------------------------ |
| `id` | Long | 是   | 关键举措 ID（来自 **4.4 查询任务树** 中 `type = "关键举措"` 的节点 `id`，或 **4.6** 返回的 `actions[].id`） |

**响应参数**

`data` 类型为 `ActionVO`（继承 `BaseTaskVO`），无自身特有字段，所有字段均来自 `BaseTaskVO`。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": "2014631829004374019",
    "groupId": "2014631829004374001",
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
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/getAction?id=2014631829004374019' \
  -H 'appKey: XXXXXXXX'
```

---

### 4.8 分页查询所有汇报

根据任务 ID 分页查询该任务关联的所有汇报记录，包含手动汇报和 AI 汇报。

**基本信息**

| 项目         | 说明                               |
| ------------ | ---------------------------------- |
| 接口地址     | `/bp/task/relation/pageAllReports` |
| 请求方式     | `POST`                             |
| Content-Type | `application/json`                 |

**请求参数**

| 参数        | 类型    | 必填 | 说明                                                         |
| ----------- | ------- | ---- | ------------------------------------------------------------ |
| `taskId`    | Long    | 是   | BP 任务 ID（来自 **4.4 查询任务树** 中任意节点的 `id`，或 **4.5/4.6/4.7** 详情接口返回的 `id`） |
| `keyword`   | String  | 否   | 名称模糊搜索                                                 |
| `sortBy`    | String  | 否   | 排序字段：`relation_time`（关联时间，默认）、`business_time`（业务时间） |
| `sortOrder` | String  | 否   | 排序方向：`desc`（降序，默认）、`asc`（升序）                |
| `pageIndex` | Integer | 否   | 页码，默认 `1`                                               |
| `pageSize`  | Integer | 否   | 每页数量，默认 `10`                                          |

**请求体示例**

```json
{
  "taskId": 2014631829004374017,
  "keyword": null,
  "sortBy": "relation_time",
  "sortOrder": "desc",
  "pageIndex": 1,
  "pageSize": 10
}
```

**响应参数**

`data` 类型为 `PageInfo<TaskReportUnionVO>`，分页结构字段见 **五、公共数据结构 — 5.9 PageInfo**。

`TaskReportUnionVO` 每条汇报记录字段如下：

| 字段           | 类型   | 说明                                          |
| -------------- | ------ | --------------------------------------------- |
| `type`         | String | 汇报类型：`manual` = 手动汇报，`ai` = AI 汇报 |
| `main`         | String | 汇报标题                                      |
| `content`      | String | 汇报正文（纯文本）                            |
| `contentType`  | String | 正文类型：`html`（默认）、`markdown`          |
| `writeEmpName` | String | 写汇报人姓名                                  |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": 25,
    "list": [
      {
        "type": "manual",
        "main": "Q1业绩周报",
        "content": "本周完成客户拜访12家，签约2家。",
        "contentType": "html",
        "writeEmpName": "张三"
      },
      {
        "type": "ai",
        "main": "AI周报总结",
        "content": "根据本周数据分析，客户拜访进度良好。",
        "contentType": "html",
        "writeEmpName": "AI助手"
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
    "pageIndex": 1,
    "pageSize": 10
  }'
```

---

### 4.9 发送 AI 延期提醒汇报

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

| 字段   | 类型 | 说明              |
| ------ | ---- | ----------------- |
| `data` | Long | 生成的汇报记录 ID |

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

发送成功后返回的记录 ID 可通过 **4.10 查询延期汇报历史** 进行查询。

---

### 4.10 查询 AI 延期提醒汇报历史

查询某员工历史收到的所有延期提醒汇报记录。

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

`data` 类型为 `List<AiDelayReportRecordVO>`，每条记录字段如下：

| 字段             | 类型    | 说明                                  |
| ---------------- | ------- | ------------------------------------- |
| `id`             | Long    | 记录 ID                               |
| `receiverEmpId`  | Long    | 接收汇报人员工 ID                     |
| `reportContent`  | String  | 汇报内容                              |
| `reportRecordId` | Long    | 汇报记录 ID（发送成功后回写）         |
| `sendStatus`     | Integer | 发送状态：`0` = 失败，`1` = 成功      |
| `errorMsg`       | String  | 失败原因（发送成功时为 `null`）       |
| `createTime`     | String  | 创建时间，格式：`yyyy-MM-dd HH:mm:ss` |

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

### 4.11 按名称模糊搜索任务

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
| `name`    | String | 是   | 任务名称关键字 |

**响应参数**

`data` 类型为 `List<TaskSearchVO>`，每个搜索结果字段如下：

| 字段              | 类型               | 说明                                                                                  |
| ----------------- | ------------------ | ------------------------------------------------------------------------------------- |
| `id`              | Long               | 任务 ID                                                                               |
| `name`            | String             | 任务名称                                                                              |
| `groupId`         | Long               | 所属分组 ID                                                                           |
| `groupName`       | String             | 所属分组名称                                                                          |
| `type`            | String             | 类型：`目标` / `关键成果` / `关键举措`                                                |
| `statusDesc`      | String             | 任务状态（草稿/未启动/进行中/已关闭）                                               |
| `reportCycle`     | String             | 汇报周期，格式: `{ruleType}+{index}`，如 `week+1` 表示每周一                         |
| `planDateRange`   | String             | 计划时间区间，格式: `yyyy-MM-dd ~ yyyy-MM-dd`                                        |
| `fullLevelNumber` | String             | 任务完整编码                                                                          |
| `taskUsers`       | List\<TaskUserVO>  | 任务参与人列表                                                                        |
| `parentTask`      | TaskBriefVO        | 上级任务（父任务）                                                                    |
| `childTasks`      | List\<TaskBriefVO> | 下级任务列表                                                                          |

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/task/v2/searchByName?groupId=1993982002185506818&name=全栈' \
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

### 4.12 按名称模糊搜索分组

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
| `name`     | String | 是   | 分组名称关键字 |

**响应参数**

`data` 类型为 `List<GroupSearchVO>`，每个搜索结果字段如下：

| 字段          | 类型         | 说明                                              |
| ------------- | ------------ | ------------------------------------------------- |
| `id`          | Long         | 分组 ID                                           |
| `name`        | String       | 分组名称                                          |
| `periodId`    | Long         | 所属周期 ID                                       |
| `type`        | String       | 类型：`org` = 组织节点，`personal` = 个人节点     |
| `levelNumber` | String       | 层级编码                                          |
| `employeeId`  | Long         | 员工 ID（个人类型时有效）                         |
| `parentGroup` | GroupBriefVO | 上级分组                                          |
| `childCount`  | Integer      | 下级分组数量                                      |

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/group/searchByName?periodId=1993981738711912449&name=技术' \
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

### 4.13 获取BP完整Markdown内容

根据分组 ID 获取该分组下完整 BP 的 Markdown 格式内容，包含三部分：本级目标树（目标、关键成果、关键举措及参与人信息）、上对齐关系（本级任务对齐到的上级分组任务）、下对齐关系（下级分组任务对当前分组任务的承接情况）。

**基本信息**

| 项目     | 说明                          |
| -------- | ----------------------------- |
| 接口地址 | `/bp/document/getBpMarkdown` |
| 请求方式 | `GET`                         |

**请求参数**

| 参数      | 类型 | 必填 | 说明                                                         |
| --------- | ---- | ---- | ------------------------------------------------------------ |
| `groupId` | Long | 是   | 分组 ID（来自 **4.2 获取分组树** 的 `GroupTreeVO.id`，或 **4.3 批量查询** 返回的 Map value） |

**响应参数**

`data` 类型为 `String`，即完整的 Markdown 格式文本。

Markdown 内容结构如下：

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
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/bp/document/getBpMarkdown?groupId=2014631829004371001' \
  -H 'appKey: XXXXXXXX'
```

**数据流向**

返回的 Markdown 文本可直接用于 AI 分析、文档展示等场景。该接口整合了分组下的完整 BP 信息（目标树 + 对齐关系），是获取分组 BP 全貌的推荐接口。

---

### 4.14 根据目标ID新增关键成果

根据目标 ID 纯新增一个关键成果。不同于 4.15 的更新逻辑，本接口专门用于增量添加场景，不影响该目标下已有的其他成果，并返回新生成成果的任务 ID。

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

`data` 为 `Long`，代表新创建的关键成果任务 ID。

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

### 4.15 根据成果ID新增关键举措

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
| `uploadSpFileDTOS` | List\<UploadSpFileParam\>| 否   | 附件文件信息（同 4.14）                    |

**响应参数**

`data` 为 `Long`，代表新创建的关键举措任务 ID。

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

### 4.16 获取关键岗位详情（已废弃）

> **⚠️ 本接口已废弃，请使用 4.17 批量获取关键岗位详情(Markdown) 接口替代。**

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

`data` 类型为 `KeyPositionDetailVO`，字段如下：

| 字段                       | 类型               | 说明                         |
| -------------------------- | ------------------ | ---------------------------- |
| `groupId`                  | Long               | 分组 ID                      |
| `groupName`                | String             | 岗位名称（人员姓名）         |
| `keyPosition`              | Boolean            | 是否关键岗位                 |
| `keyPositionReason`        | String             | 设置为关键岗位的原因         |
| `bonusCoefficient`         | BigDecimal         | 奖金系数建议(月)             |
| `bonusCoefficientPersonal` | BigDecimal         | 个人奖金系数建议(%)         |
| `bonusCoefficientDept`     | BigDecimal         | 部门奖金系数建议(%)         |
| `bonusCoefficientCenter`   | BigDecimal         | 中心奖金系数建议(%)         |
| `bonusCoefficientGroup`    | BigDecimal         | 集团奖金系数建议(%)         |
| `bonusCoefficientReason`   | String             | 奖金系数建议原因             |
| `isParentAdmin`            | Boolean            | 是否为直接上级组织管理员     |
| `isDirectLeader`           | Boolean            | 是否为组织架构的直属上级领导 |
| `goals`                    | List\<GoalWeightVO\>  | 目标及权重列表               |

**GoalWeightVO 结构：**

| 字段      | 类型                    | 说明                                             |
| --------- | ----------------------- | ------------------------------------------------ |
| `taskId`  | Long                    | 目标任务 ID                                      |
| `name`    | String                  | 目标名称                                         |
| `status`  | Integer                 | 目标状态（0-草稿、1-待发布、2-进行中、3-已关闭） |
| `weight`  | BigDecimal              | 目标权重（0-100）                                |
| `results` | List\<ResultWeightVO\>  | 成果权重列表                                     |

**ResultWeightVO 结构：**

| 字段     | 类型       | 说明                                             |
| -------- | ---------- | ------------------------------------------------ |
| `taskId` | Long       | 成果任务 ID                                      |
| `name`   | String     | 成果名称                                         |
| `status` | Integer    | 成果状态（0-草稿、1-待发布、2-进行中、3-已关闭） |
| `weight` | BigDecimal | 成果权重（0-100）                                |

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

### 4.17 批量获取关键岗位详情(Markdown)

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

`data` 类型为 `String`，即 Markdown 格式文本。

Markdown 内容结构如下：

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

## 五、公共数据结构

以下为多个接口共用的数据结构定义，在各接口响应参数中通过名称引用。

---

### 5.1 BaseTaskVO（任务基础结构）

`GoalAndKeyResultVO`、`KeyResultVO`、`ActionVO` 均继承此结构。

| 字段              | 类型                | 说明                                                                                  |
| ----------------- | ------------------- | ------------------------------------------------------------------------------------- |
| `id`              | Long                | 任务 ID                                                                               |
| `groupId`         | Long                | 所属分组 ID                                                                           |
| `name`            | String              | 任务名称                                                                              |
| `statusDesc`      | String              | 任务状态（草稿/未启动/进行中/已关闭）                                               |
| `reportCycle`     | String              | 汇报周期，格式: `{ruleType}+{index}`，ruleType 可选值: weekday/week/month/doubleWeek/doubleMonth/threeMonth，如 `week+1` 表示每周一 |
| `planDateRange`   | String              | 计划时间区间，格式: `yyyy-MM-dd ~ yyyy-MM-dd`，如 `2024-01-01 ~ 2024-03-31`          |
| `taskUsers`       | List\<TaskUserVO>   | 任务参与人列表                                                                        |
| `taskDepts`       | List\<TaskDeptVO>   | 任务参与部门列表                                                                      |
| `upwardTaskList`  | List\<SimpleTaskVO> | 所有向上对齐任务                                                                      |
| `downTaskList`    | List\<SimpleTaskVO> | 所有向下对齐任务                                                                      |
| `path`            | String              | 路径                                                                                  |
| `fullLevelNumber` | String              | 任务完整编码                                                                          |

---

### 5.2 TaskUserVO（任务参与人）

| 字段      | 类型             | 说明                                                         |
| --------- | ---------------- | ------------------------------------------------------------ |
| `taskId`  | Long             | 任务 ID                                                      |
| `role`    | String           | 角色（中文）：`承接人` / `协办人` / `抄送人` / `监督人` / `观察人` |
| `empList` | List\<EmpBaseVO> | 该角色下的员工列表                                           |

---

### 5.3 EmpBaseVO（员工基础信息）

| 字段     | 类型   | 说明     |
| -------- | ------ | -------- |
| `id`     | Long   | 员工 ID  |
| `name`   | String | 员工姓名 |

---

### 5.4 TaskDeptVO（任务参与部门）

| 字段       | 类型          | 说明                                                         |
| ---------- | ------------- | ------------------------------------------------------------ |
| `taskId`   | Long          | 任务 ID                                                      |
| `role`     | String        | 角色（中文）：`承接人` / `协办人` / `抄送人` / `监督人` / `观察人` |
| `deptList` | List\<DeptVO> | 部门信息列表                                                 |

---

### 5.5 DeptVO（部门信息）

| 字段   | 类型   | 说明     |
| ------ | ------ | -------- |
| `id`   | Long   | 部门 ID  |
| `name` | String | 部门名称 |

---

### 5.6 SimpleTaskVO（简要任务信息）

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

### 5.7 TaskBriefVO（任务简要信息）

用于 `TaskSearchVO` 中的 `parentTask`（上级任务）和 `childTasks`（下级任务列表）。

| 字段         | 类型   | 说明                                    |
| ------------ | ------ | --------------------------------------- |
| `id`         | Long   | 任务 ID                                 |
| `name`       | String | 任务名称                                |
| `type`       | String | 类型：`目标` / `关键成果` / `关键举措`  |
| `statusDesc` | String | 任务状态（草稿/未启动/进行中/已关闭） |

---

### 5.8 GroupBriefVO（分组简要信息）

用于 `GroupSearchVO` 中的 `parentGroup`（上级分组）。

| 字段   | 类型   | 说明                                              |
| ------ | ------ | ------------------------------------------------- |
| `id`   | Long   | 分组 ID                                           |
| `name` | String | 分组名称                                          |
| `type` | String | 类型：`org` = 组织节点，`personal` = 个人节点     |

---

### 5.9 PageInfo（分页结构）

| 字段       | 类型     | 说明              |
| ---------- | -------- | ----------------- |
| `total`    | Long     | 总记录数          |
| `list`     | List\<T> | 结果集            |
| `pageNum`  | Integer  | 当前页，从 1 开始 |
| `pageSize` | Integer  | 每页的数量        |
| `size`     | Integer  | 当前页的数量      |

---

## 六、错误码说明

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

## 七、注意事项

1. **ID 精度问题**：所有 ID 字段均为 Long 类型（雪花算法生成），前端/调用方请使用字符串类型接收，避免 JavaScript 等语言中因 Number 精度不足导致的 ID 丢失问题。**严禁对 ID 进行 `parseInt`、`Number()` 等转换操作。**
2. **分组 ID 与员工 ID 的区别**：`getPersonalGroupIds` 接口入参为员工 ID，返回值中的 value 为分组 ID；`sendDelayReport` 接口中的 `receiverEmpId` 是员工 ID，不是分组 ID。
3. **任务树为递归结构**：`getSimpleTree` 返回的数据是树形递归结构（目标 → 关键成果 → 关键举措），遍历时需要递归处理 `children` 字段。
4. **详情接口与任务树的区别**：任务树（4.4）返回的是简要信息（`TaskTreeVO`），而详情接口（4.5/4.6/4.7）返回的是完整信息（继承 `BaseTaskVO`），包含对齐任务等更丰富的字段。
5. **周期状态**：查询分组树时需要传入 `periodId`，建议优先选择 `status = 1`（启用状态）的周期。
6. **分组树类型**：分组树中 `type = "org"` 为组织分组节点，`type = "personal"` 为个人分组节点。个人分组节点的 `employeeId` 字段标识了该分组对应的员工。
7. **汇报查询排序**：分页查询汇报（4.8）支持按 `relation_time`（关联时间）和 `business_time`（业务时间）排序，默认按关联时间降序。
