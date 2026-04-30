# BP 目标管理 Open API 接口定义

**配套文档**：[《BP 目标管理 Open API 调用说明》](./BP系统API调用说明.md)（修订记录、概述、通用约定、接口清单索引、场景编排、注意事项与历史路径）。**本文仅描述数据模型、接口契约与公共类型。**

> **最新变更（v1.22）**：新增 2.35 保存目标月报信息（`saveTaskMonthlyReading`）和 2.36 查询目标月报信息（`getTaskMonthlyReading`），支持按任务 ID + 月份保存和查询目标月报阅读内容。

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

---


---

## 接口索引

| 编号 | 能力域 | 接口数量 | 文档链接 | 简要说明 |
|------|--------|---------|---------|---------|
| 01 | 周期与分组管理 | 4 | [01-周期与分组管理.md](API接口明细/01-周期与分组管理.md) | 查询周期列表、获取分组树、批量查询个人分组、搜索分组 |
| 02 | 任务树与详情查询 | 9 | [02-任务树与详情查询.md](API接口明细/02-任务树与详情查询.md) | 任务树、目标/成果/举措详情、Markdown导出、轻量列表、子树骨架 |
| 03 | 汇报与搜索 | 6 | [03-汇报与搜索.md](API接口明细/03-汇报与搜索.md) | 分页查询汇报、AI延期提醒、搜索任务、关键岗位详情(含废弃) |
| 04 | 目标创建与对齐 | 6 | [04-目标创建与对齐.md](API接口明细/04-目标创建与对齐.md) | 新增关键成果/举措、待承接任务树、创建承接目标、任务对齐/修改 |
| 05 | 月度管理与版本 | 11 | [05-月度管理与版本.md](API接口明细/05-月度管理与版本.md) | 月度汇报CRUD、版本历史/快照/回退、月报查询、AI月报保存 |

> 通用约定（访问地址、环境信息等）请参阅配套文档 [BP系统API调用说明.md](./BP系统API调用说明.md)。

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

### 3.18 MonthlyReportSimpleVO（月度汇报轻量信息 — 二、2.23）

| 字段            | 类型   | 说明       |
| --------------- | ------ | ---------- |
| `groupId`       | Long   | 个人分组ID |
| `reportContent` | String | 汇报内容   |

---


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

---

## 三、公共对象模型

... (此处省略 3.1 ~ 3.18)

### 3.19 UndertakeTaskTreeVO 对象

| 字段          | 类型               | 说明                             |
| ------------- | ------------------ | -------------------------------- |
| totalCount    | Integer            | 总指派任务数                     |
| acceptedCount | Integer            | 已承接数                         |
| pendingCount  | Integer            | 待承接（未对齐）数               |
| groups        | List<GroupTaskVO>  | 分组任务列表                     |

**GroupTaskVO (内部类)**

| 字段           | 类型              | 说明                             |
| -------------- | ----------------- | -------------------------------- |
| groupId        | Long              | 分组 ID                          |
| groupName      | String            | 分组名称                         |
| tasks          | List<TaskNodeVO>  | 该分组下的扁平任务列表           |

**TaskNodeVO (内部类)**

| 字段           | 类型              | 说明                             |
| -------------- | ----------------- | -------------------------------- |
| id             | Long              | 任务 ID                          |
| name           | String            | 任务名称                         |
| type           | String            | 类型（目标、关键成果、关键举措） |
| accepted       | Boolean           | 是否已承接                       |
| goalId         | Long              | 所属上级目标 ID                  |
| goalName       | String            | 所属上级目标名称                 |
| krId           | Long              | 所属上级关键成果 ID (若有)       |
| krName         | String            | 所属上级关键成果名称 (若有)      |
| fullPath       | String            | 溯源展示路径（如：目标 / 成果 / 举措） |

---

### 3.20 TaskVersionSnapshotVO 对象

| 字段         | 类型                | 说明                                      |
| ------------ | ------------------- | ----------------------------------------- |
| id           | Long                | 快照唯一 ID (回滚时使用)                  |
| taskId       | Long                | 任务 ID                                   |
| version      | Integer             | 版本流水号                                |
| createTime   | String              | 修改/快照生成时间                         |
| creatorName  | String              | 操作人名称                                |
| snapshotData | Object (Map)        | 全量快照数据 (含名称、时间、人员、对齐等) |