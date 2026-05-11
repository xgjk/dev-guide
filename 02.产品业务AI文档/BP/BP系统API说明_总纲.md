# BP 目标管理 Open API 接口定义

**配套文档**：
- [《通用约定与业务流程》](API接口明细/_通用约定.md)（修订记录、概述、通用说明、接口清单索引、场景编排、注意事项、错误码）
- **本文仅描述数据模型、对象规格与接口索引。**

---

## 一、数据模型与对象规格

本节给出与开放接口一致的实体关系与 **Simple / Full** 字段规格。路径与调用约定详见 [《通用约定与业务流程》](API接口明细/_通用约定.md)。

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
| deptId      | —      | ✅   | 关联部门 ID（`type=org` 时有效）    |
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
>
> **关于对齐任务类型**：`upwardTaskList` / `downTaskList` 使用 `SimpleTaskVO`，其中包含 `type` 字段，可用于区分对齐任务是 `目标`、`关键成果` 还是 `关键举措`。

---

## 二、接口索引

| 编号 | 能力域 | 接口数量 | 文档链接 | 简要说明 |
|------|--------|---------|---------|---------|
| 01 | 周期与分组管理 | 4 | [01-周期与分组管理.md](API接口明细/01-周期与分组管理.md) | 查询周期列表、获取分组树、批量查询个人分组、搜索分组 |
| 02 | 任务树与详情查询 | 9 | [02-任务树与详情查询.md](API接口明细/02-任务树与详情查询.md) | 任务树、目标/成果/举措详情、Markdown导出、轻量列表、子树骨架 |
| 03 | 汇报与搜索 | 6 | [03-汇报与搜索.md](API接口明细/03-汇报与搜索.md) | 分页查询汇报、AI延期提醒、搜索任务、关键岗位详情(含废弃) |
| 04 | 目标创建与对齐 | 6 | [04-目标创建与对齐.md](API接口明细/04-目标创建与对齐.md) | 新增关键成果/举措、待承接任务树、创建承接目标、任务对齐/修改 |
| 05 | 月度管理与版本 | 11 | [05-月度管理与版本.md](API接口明细/05-月度管理与版本.md) | 月度汇报CRUD、版本历史/快照/回退、月报查询、AI月报保存 |

> 通用约定（访问地址、环境信息、接口清单、场景流程、注意事项、错误码等）请参阅 [通用约定与业务流程](API接口明细/_通用约定.md)。公共数据结构已下放到各子文档。
