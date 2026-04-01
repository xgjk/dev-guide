# BP 接口重设计文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-04-01 | 初版创建：接口分层设计、对象 Simple/Full 规格定义、接口清单 | 诸葛 |

---

## 一、背景与目标

### 1.1 现状问题

现有 BP 接口存在以下问题：

1. **读写比例失衡**：17 个接口中，写接口仅 2 个（新增关键成果、新增关键举措），目标本身无法新增/修改/删除，BP 全生命周期管理不完整。
2. **轻重颗粒度不清**：`getSimpleTree` 节点数据过轻（缺编码、缺状态），但递归结构又非真正的「轻量」；详情接口和树接口的职责边界模糊。
3. **全量拉取能力不足**：没有统一的全量子树接口，无法一次获取指定节点的完整数据而不依赖递归调用。
4. **组织 BP 与个人 BP 未区分**：Group 节点含 `org`（组织）和 `personal`（个人）两类型，现有接口未明确区分处理逻辑。
5. **taskUsers 信息分散**：责任人、协办人、监督人、抄送人、观察人等信息在不同接口中的暴露程度不一，AI Agent 调用时容易遗漏。

### 1.2 设计目标

接口封装为 AI Agent Skill 服务，核心目标：

- **易于组合调用**：接口职责单一，命名统一，Agent 可根据场景自由拼接调用路径。
- **Token 成本可控**：轻接口（list*）和重接口（get*Detail）分离，Agent 按需选择，避免过度拉取。
- **全量能力**：提供一次拿满的数据接口，不依赖多次递归。
- **信息完整性**：taskUsers 等核心字段在 Simple 级别即应暴露，不遗漏。

---

## 二、BP 数据模型

### 2.1 实体关系

```
Period（周期）
  └─ Group（分组）
       ├─ type=org（组织节点，如部门/中心/集团）
       └─ type=personal（个人节点）
            └─ Goal（目标）
                 └─ KeyResult（关键成果）
                      └─ Action（关键举措）
```

- **组织 BP**：以 `type=org` 的 Group 为根节点，其下可挂目标。
- **个人 BP**：以 `type=personal` 的 Group 为根节点，其下直接挂目标。
- 对齐关系：`upwardTaskList`（上对齐）和 `downTaskList`（下对齐）贯穿目标、关键成果、关键举措三个层级。

### 2.2 任务参与者角色

| 角色 | 说明 |
|------|------|
| 承接人 | 主责执行人 |
| 协办人 | 协助执行 |
| 抄送人 | 知情 |
| 监督人 | 监督进展 |
| 观察人 | 旁听 |

---

## 三、对象规格定义

每个 BP 对象分为 **Simple（轻量）** 和 **Full（完整）** 两套规格。

> 原则：Simple 包含 AI Agent 高频决策所需字段（id、name、type、编码、状态、taskUsers），不包含需二次查询的嵌套数据和低频字段。

### 3.1 Period（周期）

| 字段 | Simple | Full | 说明 |
|------|--------|------|------|
| id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| status | ✅ | ✅ | 1=启用，0=未启用 |

> Simple = Full，周期本身无复杂结构。

---

### 3.2 Group（分组）

| 字段 | Simple | Full | 说明 |
|------|--------|------|------|
| id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| type | ✅ | ✅ | `org`（组织节点）/ `personal`（个人节点） |
| fullLevelNumber | ✅ | ✅ | 完整层级编码，如 `A4-1` |
| employeeId | ✅ | ✅ | 个人分组时有效，标识对应员工 |
| parentId | — | ✅ | 父分组 ID |
| childCount | — | ✅ | 直接下级分组数量 |
| children | — | ✅ | 递归子分组（Full Group 结构） |

> `listGroups` 接口返回 Full Group 树（含递归 children），但**不含任何任务数据**，仅包含分组层级结构。

---

### 3.3 Goal（目标）

| 字段 | Simple | Full | 说明 |
|------|--------|------|------|
| id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| fullLevelNumber | ✅ | ✅ | 目标编码，如 `A4-1` |
| statusDesc | ✅ | ✅ | 进行中/已关闭/未启动/草稿 |
| reportCycle | ✅ | ✅ | 汇报周期，如 `week+1`（每周一） |
| planDateRange | ✅ | ✅ | 计划起止，格式 `yyyy-MM-dd ~ yyyy-MM-dd` |
| taskUsers | ✅ | ✅ | **【每次必拉】** 承接/协办/抄送/监督/观察人 |
| krCount | ✅ | — | 快速预览用，Token 极低 |
| actionCount | ✅ | — | 快速预览用，Token 极低 |
| measureStandard | — | ✅ | 衡量标准 |
| description | — | ✅ | 目标详细描述 |
| taskDepts | — | ✅ | 参与部门列表 |
| upwardTaskList | — | ✅ | 上对齐任务列表 |
| downTaskList | — | ✅ | 下对齐任务列表 |
| path | — | ✅ | 路径 |
| keyResults（内嵌） | — | ✅ | **Full 模式下内嵌完整 KR 列表** |

---

### 3.4 KeyResult（关键成果）

| 字段 | Simple | Full | 说明 |
|------|--------|------|------|
| id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| fullLevelNumber | ✅ | ✅ | KR 编码，如 `A4-1.1` |
| statusDesc | ✅ | ✅ | |
| measureStandard | ✅ | ✅ | 衡量标准（KR 核心字段） |
| reportCycle | ✅ | ✅ | |
| planDateRange | ✅ | ✅ | |
| taskUsers | ✅ | ✅ | **【每次必拉】** |
| actionCount | ✅ | — | 快速预览 |
| weight | — | ✅ | 权重（0-100） |
| description | — | ✅ | 描述 |
| taskDepts | — | ✅ | |
| upwardTaskList | — | ✅ | |
| downTaskList | — | ✅ | |
| actions（内嵌） | — | ✅ | **Full 模式下内嵌完整 Action 列表** |

---

### 3.5 Action（关键举措）

| 字段 | Simple | Full | 说明 |
|------|--------|------|------|
| id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| fullLevelNumber | ✅ | ✅ | 举措编码，如 `A4-1.1.1` |
| statusDesc | ✅ | ✅ | |
| reportCycle | ✅ | ✅ | |
| planDateRange | ✅ | ✅ | |
| taskUsers | ✅ | ✅ | **【每次必拉】** |
| weight | — | ✅ | 权重（0-100） |
| measureStandard | — | ✅ | |
| description | — | ✅ | |
| taskDepts | — | ✅ | |
| upwardTaskList | — | ✅ | |
| downTaskList | — | ✅ | |

---

## 四、接口规划

### 4.1 设计原则

1. **轻重分离**：list* = 轻量索引，get*Detail = 单节点完整详情，getFull* = 全量子树
2. **命名统一**：`list` 前缀=列表/树，`get` 前缀=详情，`getFull` 前缀=全量
3. **响应结构一致**：所有接口统一 `Result<T>` 结构
4. **taskUsers 必暴露**：Simple 级别即包含，不因「轻量」而丢失

### 4.2 接口清单

| 编号 | 接口名 | 方法 | 路径 | 返回规格 | 场景 |
|------|--------|------|------|----------|------|
| G1 | listPeriods | GET | `/bp/period/list` | Simple Period 列表 | 查询可用周期 |
| G2 | listGroups | GET | `/bp/group/list` | Full Group 树（无任务） | 查询组织结构或个人分组 |
| G3 | listGoals | GET | `/bp/goal/list` | Simple Goal 列表 | 快速预览某人有哪些目标 |
| G4 | listKeyResults | GET | `/bp/keyResult/list` | Simple KR 列表 | 快速预览某目标有哪些 KR |
| G5 | listActions | GET | `/bp/action/list` | Simple Action 列表 | 快速预览某 KR 有哪些举措 |
| D1 | getGoalDetail | GET | `/bp/goal/{goalId}/detail` | Full Goal（含 Full KR + Full Action） | 分析单个目标的完整数据 |
| D2 | getKeyResultDetail | GET | `/bp/keyResult/{keyResultId}/detail` | Full KR（含 Full Action） | 分析单个 KR 的完整数据 |
| D3 | getActionDetail | GET | `/bp/action/{actionId}/detail` | Full Action | 分析单个举措的完整数据 |
| F1 | getFullSubtree | GET | `/bp/tree/full` | 指定节点的 Full 子树（递归内嵌） | 一次拿满，不递归 |
| R1 | listTaskReports | POST | `/bp/task/relation/pageAllReports` | 分页汇报 | 查询任务关联的所有汇报 |
| R2 | listDelayReports | GET | `/bp/delayReport/list` | 延期提醒历史 | 查询某员工收到的延期提醒 |

**共 11 个接口。**

---

## 五、接口详细说明

---

### G1：listPeriods

查询周期列表。用于确认当前启用的 BP 周期，是所有 BP 操作的起点。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/period/list` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | String | 否 | 周期名称，支持模糊搜索 |

**响应**

`data` 类型为 `List<PeriodSimpleVO>`

```json
{
  "resultCode": 1,
  "data": [
    { "id": "2014631829004370001", "name": "2026年Q1", "status": 1 },
    { "id": "2014631829004370002", "name": "2026年Q2", "status": 0 }
  ]
}
```

---

### G2：listGroups

获取分组树（Full Group 结构，无任务数据）。

用于确认组织架构，或获取某员工在当前周期下的个人分组 ID。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/group/list` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| periodId | Long | 是 | 周期 ID |
| onlyPersonal | Boolean | 否 | 是否只返回个人分组，默认 false |

**响应**

`data` 类型为 `List<GroupFullVO>`，递归树结构。

```json
{
  "resultCode": 1,
  "data": [
    {
      "id": "2014631829004371001",
      "name": "技术中心",
      "type": "org",
      "fullLevelNumber": "A4",
      "employeeId": null,
      "parentId": null,
      "childCount": 3,
      "children": [
        {
          "id": "2014631829004371002",
          "name": "张三",
          "type": "personal",
          "fullLevelNumber": "A4-1",
          "employeeId": "1234567890123456789",
          "parentId": "2014631829004371001",
          "childCount": 0,
          "children": []
        }
      ]
    }
  ]
}
```

> 返回 Full Group 结构，**不含任何 Goal/KeyResult/Action 数据**。

---

### G3：listGoals

获取指定分组下的目标轻量列表。

扁平列表，不内嵌 KR 和 Action，含 krCount/actionCount 供 Agent 预判数据量。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/goal/list` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| groupId | Long | 是 | 分组 ID |

**响应**

`data` 类型为 `List<GoalSimpleVO>`

```json
{
  "resultCode": 1,
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
        },
        {
          "taskId": "2014631829004374017",
          "role": "协办人",
          "empList": [{ "id": "9876543210987654321", "name": "李四" }]
        }
      ]
    }
  ]
}
```

---

### G4：listKeyResults

获取指定目标下的关键成果轻量列表。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/keyResult/list` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goalId | Long | 是 | 目标 ID |

**响应**

`data` 类型为 `List<KeyResultSimpleVO>`

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
      "taskUsers": [
        {
          "taskId": "2014631829004374018",
          "role": "承接人",
          "empList": [{ "id": "1234567890123456789", "name": "张三" }]
        }
      ]
    }
  ]
}
```

---

### G5：listActions

获取指定关键成果下的关键举措轻量列表。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/action/list` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyResultId | Long | 是 | 关键成果 ID |

**响应**

`data` 类型为 `List<ActionSimpleVO>`

```json
{
  "resultCode": 1,
  "data": [
    {
      "id": "2014631829004374019",
      "name": "每周拜访5家客户",
      "fullLevelNumber": "A4-1.1.1",
      "statusDesc": "进行中",
      "reportCycle": "week+1",
      "planDateRange": "2026-01-01 ~ 2026-02-28",
      "taskUsers": [
        {
          "taskId": "2014631829004374019",
          "role": "承接人",
          "empList": [{ "id": "1234567890123456789", "name": "张三" }]
        },
        {
          "taskId": "2014631829004374019",
          "role": "监督人",
          "empList": [{ "id": "1112223334445556667", "name": "王五" }]
        }
      ]
    }
  ]
}
```

---

### D1：getGoalDetail

获取目标完整详情，内嵌所有关键成果和关键举措。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/goal/{goalId}/detail` |

**响应**

`data` 类型为 `GoalFullVO`

```json
{
  "resultCode": 1,
  "data": {
    "id": "2014631829004374017",
    "name": "Q1 业绩目标",
    "fullLevelNumber": "A4-1",
    "statusDesc": "进行中",
    "reportCycle": "week+1",
    "planDateRange": "2026-01-01 ~ 2026-03-31",
    "measureStandard": "...",
    "description": "...",
    "taskUsers": [...],
    "taskDepts": [...],
    "upwardTaskList": [...],
    "downTaskList": [...],
    "path": "...",
    "keyResults": [
      {
        "id": "2014631829004374018",
        "name": "客户拜访量达到50家",
        "fullLevelNumber": "A4-1.1",
        "statusDesc": "进行中",
        "measureStandard": "拜访记录数 >= 50",
        "reportCycle": "week+1",
        "planDateRange": "2026-01-01 ~ 2026-02-28",
        "weight": 40.0,
        "taskUsers": [...],
        "taskDepts": [],
        "upwardTaskList": [],
        "downTaskList": [],
        "actions": [
          {
            "id": "2014631829004374019",
            "name": "每周拜访5家客户",
            "fullLevelNumber": "A4-1.1.1",
            "statusDesc": "进行中",
            "reportCycle": "week+1",
            "planDateRange": "2026-01-01 ~ 2026-02-28",
            "weight": 100.0,
            "taskUsers": [...],
            "taskDepts": [],
            "upwardTaskList": [],
            "downTaskList": []
          }
        ]
      }
    ]
  }
}
```

---

### D2：getKeyResultDetail

获取关键成果完整详情，内嵌所有关键举措。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/keyResult/{keyResultId}/detail` |

---

### D3：getActionDetail

获取关键举措完整详情。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/action/{actionId}/detail` |

---

### F1：getFullSubtree

全量子树接口。指定任意节点，一次返回该节点的完整子树下所有节点的 Full 规格数据。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/tree/full` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nodeId | Long | 是 | 任意节点 ID |
| nodeType | String | 否 | `group` / `goal` / `keyResult` / `action`，不传则自动推断 |

**响应规则**

| nodeType | 返回 |
|----------|------|
| `group` | Full Group + 内嵌 Full Goal（含 Full KR + Full Action） |
| `goal` | Full Goal + 内嵌 Full KR + Full Action |
| `keyResult` | Full KR + 内嵌 Full Action |
| `action` | Full Action（无 children） |

**统一返回结构**

```json
{
  "resultCode": 1,
  "data": {
    "nodeInfo": { /* Full 规格当前节点 */ },
    "children": [
      {
        "nodeInfo": { /* Full 规格子节点 */ },
        "children": [
          {
            "nodeInfo": { /* Full 规格孙节点 */ },
            "children": []
          }
        ]
      }
    ]
  }
}
```

> 递归深度 = 实际 BP 层级。所有节点均为 Full 规格，Agent 无需二次查询。

---

### R1：listTaskReports

分页查询任务关联的所有汇报记录（含手动汇报和 AI 汇报）。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | POST |
| 路径 | `/bp/task/relation/pageAllReports` |
| Content-Type | `application/json` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| taskId | Long | 是 | BP 任务 ID |
| keyword | String | 否 | 标题模糊搜索 |
| sortBy | String | 否 | `relation_time`（默认）/ `business_time` |
| sortOrder | String | 否 | `desc`（默认）/ `asc` |
| pageIndex | Integer | 否 | 默认 1 |
| pageSize | Integer | 否 | 默认 10 |

---

### R2：listDelayReports

查询某员工收到的所有延期提醒汇报历史。

**基本信息**

| 项目 | 说明 |
|------|------|
| 方法 | GET |
| 路径 | `/bp/delayReport/list` |

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| receiverEmpId | Long | 是 | 接收人员工 ID |

---

## 六、拉取路径模式

### 路径A：渐进式（按需拉取）

```
G2 listGroups → 确定分组
G3 listGoals  → 看 krCount/actionCount 预判数据量
               → 数据量小：直接 D1 getGoalDetail
               → 数据量大：先 G4 listKeyResults
                           → 再按需 D2 getKeyResultDetail
                           → 或先 G5 listActions
                           → 再按需 D3 getActionDetail
```

**Token 最优，但调用次数多。适合精准分析场景。**

### 路径B：全量式（一次拿满）

```
F1 getFullSubtree(groupId=xxx)
```

**一次 HTTP 请求拿到完整 BP 子树（含所有目标→KR→Action），无递归调用。适合全面分析、大盘统计场景。**

### 路径C：快速预览

```
G3 listGoals(groupId=xxx)
→ 查看 krCount / actionCount
→ 判断该目标是否值得拉 Full 详情
```

**最小化 Token 消耗，Agent 可据此决策是否继续深入。**

---

## 七、公共数据结构

### 7.1 TaskUserVO（任务参与者）

每个节点 taskUsers 字段的结构。

| 字段 | 类型 | 说明 |
|------|------|------|
| taskId | Long | 任务 ID |
| role | String | 角色：承接人/协办人/抄送人/监督人/观察人 |
| empList | List\<EmpBaseVO> | 该角色下的员工列表 |

### 7.2 EmpBaseVO（员工基础信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 员工 ID |
| name | String | 员工姓名 |

### 7.3 DeptVO（部门信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 部门 ID |
| name | String | 部门名称 |

### 7.4 SimpleTaskVO（上/下对齐任务）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 任务 ID |
| name | String | 任务名称 |
| groupInfo | BaseInfo | 所属分组基础信息 |

### 7.5 BaseInfo

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | ID |
| name | String | 名称 |

---

## 八、通用说明

### 8.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

生产环境：`https://sg-al-cwork-web.mediportal.com.cn`

### 8.2 公共请求头

| Header | 说明 | 必填 |
|--------|------|------|
| appKey | 应用密钥 | 是 |

### 8.3 通用响应结构

所有接口统一 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| resultCode | Integer | 1=成功，其他=失败 |
| resultMsg | String | 失败时的错误描述，成功时为 null |
| data | T | 业务数据 |

### 8.4 ID 精度说明

所有 ID 为 Long 类型（雪花算法），前端/调用方须使用字符串接收，禁止 parseInt 转换。

### 8.5 错误码

| resultCode | 说明 |
|------------|------|
| 1 | 成功 |
| 0 | 通用失败 |
| 500 | 系统异常 |
| 610002 | appKey 无效 |
| 610015 | 无访问权限 |

---

## 九、待补充接口（不在本次设计范围内）

以下接口目前未提供，属于 BP 写操作和完整生命周期管理范畴，本次设计仅聚焦查询层。

| 待补充接口 | 说明 |
|------------|------|
| 创建目标 | 在指定分组下新建目标 |
| 更新目标 | 修改目标内容/状态/负责人 |
| 删除目标 | 删除目标及其下所有 KR 和 Action |
| 创建关键成果 | 在指定目标下新建 KR |
| 更新关键成果 | 修改 KR |
| 删除关键成果 | 删除 KR 及其下所有 Action |
| 创建关键举措 | 在指定 KR 下新建 Action |
| 更新关键举措 | 修改 Action |
| 删除关键举措 | 删除 Action |
| 更新任务状态 | 推进/关闭/重开 BP 节点 |
| 批量更新负责人 | 批量修改任务的承接人/协办人等 |
| 上传附件 | 上传 BP 相关文件 |
| 获取关键岗位详情 | 奖金系数、目标权重等（4.16/4.17 升级版） |

---

## 十、附录：与现有接口的对应关系

| 新接口 | 现有接口 | 变化说明 |
|--------|----------|----------|
| listPeriods | 4.1 getAllPeriod | 重命名，无实质变化 |
| listGroups | 4.2 getTree | Full Group 结构，不含任务；新增 childCount |
| listGoals | 无（新增） | 直接获取目标列表，无递归树结构 |
| listKeyResults | 无（新增） | 直接获取 KR 列表 |
| listActions | 无（新增） | 直接获取 Action 列表 |
| getGoalDetail | 4.5 getGoalAndKeyResult | 路径重命名，规格不变 |
| getKeyResultDetail | 4.6 getKeyResult | 路径重命名，规格不变 |
| getActionDetail | 4.7 getAction | 路径重命名，规格不变 |
| getFullSubtree | 无（新增） | 整合 4.2（递归）+ 4.5（Full节点）合二为一 |
| listTaskReports | 4.8 pageAllReports | 重命名，无实质变化 |
| listDelayReports | 4.10 delayReport/list | 重命名，无实质变化 |

---

*文档状态：初稿，待评审*
