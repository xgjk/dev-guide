# 工作协同 Open API 接口文档

## 修订记录

| 版本  | 日期       | 变更摘要                                         | 变更人 |
|-----| ---------- |----------------------------------------------| ------ |
| 1.0 | 2026-03-25 | 初版创建                                         | 成伟   |
| 1.1 | 2026-03-25 | 新增获取指定用户分组接口                                 | 付光伟   |
| 1.2 | 2026-03-26 | 新增个人分组创建与成员管理接口、重构文档结构及序号                    | 付光伟 |
| 1.3 | 2026-03-26 | 在获取分组及管理成员接口中增加按姓名搜索员工 ID 的说明                | 付光伟 |
| 1.4 | 2026-03-28 | 新增「新增草稿相关接口，5.23-5.27」                       | 成伟   |
| 1.5 | 2026-03-30 | 补充「将草稿转为正式汇报发出」接口的内部路由实现与文档说明状态同步            | 付光伟 |
| 1.6 | 2026-03-30 | 修复接口序号错位，并补充汇报/草稿通用参数说明及接口交叉引用               | 付光伟 |
| 1.7 | 2026-03-30 | 汇报提交参数新增节点级填写要求（requirement）字段               | 付光伟 |
| 1.8 | 2026-03-30 | 新增「批量删除草稿」接口（5.28）                           | 付光伟 |
| 1.9 | 2026-03-31 | 业务单元管理专题：开放保存/更新、分页查询、删除及详情获取接口 (5.29-5.32) | 付光伟 |
| 2.1 | 2026-04-07 | 新增个人标签关联汇报系列接口 (5.34-5.37) | 付光伟 |
| 2.2 | 2026-04-07 | 汇报回复(5.2)与完成待办(5.18)接口新增 contentType 参数支持 | 付光伟 |
| 2.3 | 2026-04-07 | 获取汇报内容(5.5)接口响应参数增加汇报人名称与id (writeEmpId, writeEmpName) | 付光伟 |
| 2.4 | 2026-04-10 | 汇报提交接口(5.1)参数增加虚拟员工提交人id (virtualEmpId) | 付光伟 |
| 2.5 | 2026-04-11 | 草稿提交接口(5.23)开放支持虚拟员工代理提交 (virtualEmpId) | 付光伟 |
| 2.6 | 2026-04-15 | 新增「编辑汇报正文」接口并支持自定义日志前缀 (5.42) | 付光伟 |
| 2.7 | 2026-04-15 | 获取汇报内容(5.5)接口响应参数增加正文富文本与正文类型 (contentHtml, contentType) | 付光伟 |
| 2.8 | 2026-04-16 | 汇报流程节点(6.1)参数增加按钮配置 (buttonConfig) | 付光伟 |
| 2.9 | 2026-04-16 | 汇报提交(5.1)与草稿保存(5.23)接口响应数据由 BaseInfo 更改为 Long (主键 ID) | 付光伟 |
| 3.0 | 2026-04-16 | 汇报提交(5.1)与草稿保存(5.23)接口新增流程类型参数 (flowType) | 付光伟 |
| 3.1 | 2026-04-17 | 获取汇报内容(5.5)接口响应参数增加汇报标题 (main) | 付光伟 |
| 3.2 | 2026-04-20 | 新增汇报催办与工作任务催办接口 (5.43-5.44) | 龙继海 |
| 3.3 | 2026-04-21 | 获取汇报正文附件回复邮件信息与创建汇报或工作任务的分享连接 (5.45-5.46) | 龙继海 |
| 3.4 | 2026-04-22 | 新增获取/绑定/解绑/邮箱、同步邮箱数据、邮件分页、汇报搜索接口 (5.47-5.52)| 龙继海 |




为便于人与 AI 追溯变更历史，所有修订记录必须使用统一格式的四列表格，包含以下字段：**版本**、**日期**、**变更摘要**、**变更人**。

**核心规则：**
- 每次内容变更**必须在表格末尾追加新行**，不得修改、覆盖或删除任何历史行。
- 行级差异以 Git 记录为准，无需在表格中体现具体代码差异。


## 一、概述

---


**基础服务接口：**
1. [**按姓名搜索全部员工(带外部联系人)**](#41-按姓名搜索全部员工带外部联系人) — 模糊查询员工姓名以获取 `empId`。
2. [**上传本地文件**](#42-上传本地文件) — 上传二进制文件并获取 `fileId` 用于发送附件。
3. [**获取指定用户的所有分组及成员**](#43-获取指定用户的所有分组及成员) — 获取指定用户的分组及成员，支持按成员过滤。
4. [**快捷创建或更新个人分组**](#44-快捷创建或更新个人分组) — 支持快速新建或对已有分组更名。
5. [**增量管理个人分组成员**](#45-增量管理个人分组成员) — 对个人分组进行加人/减人的批量操作。

**工作协同服务接口：**

1. [**发送汇报**](#51-发送汇报) — 创建并提交一条汇报记录（可关联任务/事项，可指定接收人/抄送人/多级节点）。
2. [**汇报回复**](#52-汇报回复) — 对指定汇报进行回复（可带附件）。
3. [**收件箱分页查询**](#53-收件箱分页查询) — 分页获取当前用户收件箱汇报列表（支持筛选条件）。
4. [**待处理列表分页查询**](#54-待处理列表分页查询) — 分页获取当前用户待办列表（任务/签批/指引/反馈等）。
5. [**获取汇报内容**](#55-获取汇报内容) — 获取指定汇报正文及回复列表。
6. [**获取事项列表**](#56-获取事项列表) — 查询最近处理过的事项（用于发起汇报选事项）。
7. [**根据事项 ID 列表获取事项信息**](#57-根据事项-id-列表获取事项信息) — 批量查询事项简易信息。
8. [**获取待办及未读汇报列表（新的待办和汇报）**](#58-获取待办及未读汇报列表新的待办和汇报) — 插件场景：一次获取最新待办 + 未读汇报聚合。
9. [**获取最新待办列表**](#59-获取最新待办列表) — 插件场景：分页获取最新待办列表。
10. [**获取未读汇报列表**](#510-获取未读汇报列表) — 插件场景：分页获取未读汇报列表。
11. [**工作任务列表查询**](#511-工作任务列表查询) — 分页查询工作任务列表（支持按状态/关键词/标签等筛选）。
12. [**获取用户创建的反馈类型待办列表**](#512-获取用户创建的反馈类型待办列表) — 查询某员工（默认登录用户）创建的反馈待办。
13. [**任务简易信息 VO**](#513-任务简易信息-vo) — 获取任务简易信息及其关联汇报简易列表。
14. [**发件箱**](#514-发件箱) — 分页获取当前用户发件箱汇报列表（支持筛选条件）。
15. [**分页获取当前用户的决策/建议/反馈待办列表**](#515-分页获取当前用户的决策建议反馈待办列表) — 汇报待办列表（决策/建议/反馈）。
16. [**分页获取当前用户的未读汇报列表**](#516-分页获取当前用户的未读汇报列表) — 汇报未读列表。
17. [**判断员工对指定汇报是否已读**](#517-判断员工对指定汇报是否已读) — 根据汇报 ID 与员工 ID 判断已读状态。
18. [**完成待办（建议/决策）**](#518-完成待办建议决策) — 对指定待办提交建议/决策内容（决策需传同意/不同意）。
19. [**汇报内容 AI 问答（流式返回）**](#519-汇报内容-ai-问答流式返回) — 对指定汇报集合进行 AI SSE 问答/编辑。
20. [**创建工作任务**](#520-创建工作任务) — 通过 OpenAPI 创建高级工作任务，并分配汇报人员和其他干系人（责任人/协办人等）。
21. [**获取我的新消息列表**](#521-获取我的新消息列表) — 列表获取当前用户的新读消息列表。
22. [**阅读汇报（清除未读/新消息）**](#522-阅读汇报清除未读新消息) — 标记汇报为已读并清除相关新消息通知。
23. [**新增或更新汇报草稿**](#523-新增或更新汇报草稿) — 保存汇报草稿。
24. [**草稿箱分页查询**](#524-草稿箱分页查询) — 分页获取当前用户的草稿箱列表。
25. [**草稿汇报详情**](#525-草稿汇报详情) — 根据汇报 ID 获取草稿态汇报详情。
26. [**删除草稿**](#526-删除草稿) — 按草稿 ID 删除草稿箱中的一条草稿。
27. [**将草稿转为正式汇报发出**](#527-将草稿转为正式汇报发出) — 将指定的草稿转为正式发布状态。
28. [**批量删除草稿**](#528-批量删除草稿) — 按时间范围或草稿 ID 列表批量删除草稿。
29. [**保存/更新业务单元汇报方案**](#529-保存更新业务单元汇报方案) — 创建或修改业务单元（小组）的汇报流配置方案。
30. [**分页查询我的业务单元方案列表**](#530-分页查询我的业务单元方案列表) — 分页获取当前用户归属的汇报方案列表（默认 PageSize 为 50）。
31. [**获取业务单元方案详情**](#531-获取业务单元方案详情) — 获取单个方案及其配置节点的完整信息。
32. [**删除业务单元方案**](#532-删除业务单元方案) — 物理删除指定的业务单元汇报配置方案。
33. [**获取汇报信息（包含节点与处理意见）**](#533-获取汇报信息包含节点与处理意见) — 获取汇报完整详情、节点流转状态及处理人意见。
34. [**汇报关联个人标签**](#534-汇报关联个人标签) — 为指定的汇报绑定自定义标签。
35. [**删除汇报与标签的关联**](#535-删除汇报与标签的关联) — 解除某条汇报与特定标签的绑定关系。
36. [**删除个人标签及其关联所有的汇报**](#536-删除个人标签及其关联所有的汇报) — 彻底清理某标签及其与收件箱中所有汇报的关联（物理删除）。
37. [**获取个人标签下的汇报列表**](#537-获取个人标签下的汇报列表) — 按标签筛选获取归属于该分类的汇报集合。
42. [**编辑汇报正文**](#542-编辑汇报正文) — 修改汇报内容并生成操作日志。
43. [**汇报催办**](#543-汇报催办) — 对汇报处理人发送催办。
44. [**工作任务催办**](#544-工作任务催办) — 对工作任务处理人发送催办。
45. [**获取汇报正文、附件、回复、关联汇报、关联邮件信息**](#545-获取汇报正文附件回复关联汇报关联邮件信息) — 根据汇报ID和类型列表获取汇报正文、附件、回复、关联汇报、关联邮件信息。
46. [**创建汇报或工作任务的分享连接**](#546-创建汇报或工作任务的分享连接) — 创建汇报或工作任务的分享连接。
47. [**获取绑定的邮箱账号**](#547-获取绑定的邮箱账号) — 获取当前用户绑定的外部邮箱与同步概览信息。
48. [**绑定邮箱账号**](#548-绑定邮箱账号) — 为当前用户绑定外部邮箱以获取邮箱邮件信息。
49. [**解绑邮箱账号**](#549-解绑邮箱账号) — 按已绑定邮箱主键解绑。
50. [**同步邮箱数据**](#550-同步邮箱数据) — 按绑定邮箱主键主动触发一次该账号邮件数据同步。
51. [**分页查询收件箱/发件箱邮件列表**](#551-分页查询收件箱发件箱邮件列表) — 按关键词、邮件类型分页查询已同步的邮件记录。
52. [**分页搜索汇报列表**](#552-分页搜索汇报列表) — 按时间、关键词、分类与人员等条件分页搜索汇报。

> **延伸阅读**：关于个人标签名称的“增删改查”基础定义管理，请参阅 **[《基础服务 — 标签管理接口》](../基础服务/API接口明细/04-个人标签管理.md)**。




---

## 二、通用说明

---

## 二、通用说明

通用约定（访问地址、环境信息、公共请求头、响应结构）已提取至 [_通用约定.md](API接口明细/_通用约定.md)。

---

## 三、关键业务流程说明


### 场景一：发送汇报 或 新增/更新草稿 通用参数说明

> **重要说明**：发送正式汇报（见 **5.1**）与新增或更新汇报草稿（见 **5.23**）共用一套核心参数逻辑（如多级接收人、分组选取及附件列表）。本节介绍的业务流及参数结构通用于这两个接口。

> 需求：向多名员工同步工作进展（或保存草稿以便后续发送），并允许他们在汇报上回复讨论。

1. 若你只有“姓名”而非 `empId`（员工 ID），先调用 **4.1 按姓名搜索全部员工(带外部联系人)**（`GET /cwork-user/searchEmpByName`）获取员工列表。
2. 若发汇报需要关联附件，先调用 **4.2 上传本地文件**（`POST /cwork-file/uploadWholeFile`）上传二进制文件，获取返回的 `fileId`。该 `fileId` 即为后续发送汇报参数中 `fileVOList` 里的 `fileId`。
    - **关于 `type` 的说明**：
        - **`type="file"`** (常用)：代表真实的本地文件。必须先上传文件获取 `fileId`。
        - **`type="url"`**：代表外部超链接。无需上传文件，直接在 `url` 字段传入链接，`fileId` 可为空。
3. 根据业务场景调用接口：
    - **正式提交**：调用 **5.1 发送汇报**（`POST /work-report/report/record/submit`）。
    - **保存草稿**：调用 **5.23 新增或更新汇报草稿**（`POST /work-report/draftBox/saveOrUpdate`）。

   上述接口均需传入 `main`、`contentHtml`、`reportLevelList`，若有附件则传入 **`fileVOList`**（可选）。**接收人由 `reportLevelList` 决定**。
    - **支持按分组选取人员**：除 `levelUserList`（单人列表）外，还可使用 `groupIdList` 直接指定分组 ID。若使用分组，该分组下的所有成员都将收到汇报。
    - **获取分组 ID**：先调用 **4.3 获取指定用户的所有分组及成员**（`POST /cwork-user/group/queryTargetUserGroups`）获取符合条件的 `groupId`。
    - **指定节点填写要求 (AI 要求)**：针对每一层级节点，可在 `reportLevelList[].requirement` 传入具体的 AI 引导词或处理要求。

   示例一：按单个人员（`levelUserList`）指定接收人：

```json
{
  "main": "标题",
  "contentHtml": "markdown正文内容",
  "contentType": "markdown",
  "reportLevelList": [
    {
      "level": 1,
      "levelUserList": [
        {
          "empId": 1512393035869810690
        }
      ],
      "nodeName": "建议人",
      "type": "suggest"
    }
  ]
}
```

示例二：按分组（`groupIdList`）指定接收人：

```json
{
  "main": "标题",
  "contentHtml": "markdown正文内容",
  "contentType": "markdown",
  "reportLevelList": [
    {
      "level": 1,
      "groupIdList": [2036325013120483329],
      "nodeName": "接收人",
      "type": "read"
    }
  ]
}
```

示例三：综合示例（多层级、分组、附件与外部链接）：

```json
{
  "main": "项目周报",
  "contentHtml": "markdown正文内容",
  "contentType": "markdown",
  "reportLevelList": [
    {
      "level": 1,
      "levelUserList": [
        {
          "empId": 1512393035869810690
        }
      ],
      "nodeName": "建议人",
      "type": "suggest"
    },
    {
      "level": 2,
      "groupIdList": [123456789],
      "nodeName": "决策人组",
      "type": "decide"
    }
  ],
  "fileVOList": [
    {
      "fileId": "2036325013120483329",
      "name": "产品需求文档.md",
      "type": "file",
      "fsize": 120834
    },
    {
      "name": "百度搜索",
      "type": "url",
      "url": "https://www.baidu.com"
    }]
}
```

示例四：使用业务单元 ID（`businessUnitId`）动态指定流程：

> **提示**：当传入 `businessUnitId` 时，接口将自动使用该业务单元预设的审批、传阅节点，**忽略**请求中手动传入的 `reportLevelList`、`acceptEmpIdList` 等配置。这适用于已经在系统后台配置好固定流程的业务场景。

```json
{
  "main": "标题",
  "contentHtml": "本次汇报将按照指定业务单元(ID:1001)的预设流程进行流转",
  "businessUnitId": 1001,
  "reportLevelList":[]
}
```

示例五：指定节点填写要求 (AI 要求)：

```json
{
  "main": "标题",
  "contentHtml": "汇报正文",
  "reportLevelList": [
    {
      "level": 1,
      "levelUserList": [{"empId": 10001}],
      "nodeName": "建议人",
      "type": "suggest",
      "requirement": "请建议人根据汇报内容评价风险等级，并给出避险措施。"
    },
    {
      "level": 2,
      "levelUserList": [{"empId": 10002}],
      "nodeName": "决策人",
      "type": "decide",
      "requirement": "决策人需明确是否同意该避险方案。"
    }
  ]
}
```

3. 接收人通过系统内查看收件箱：调用 **5.3 收件箱分页查询**（`POST /work-report/report/record/inbox`），按时间/类型等筛选获取列表。
4. 需要查看具体正文与回复列表时，调用 **5.5 获取汇报内容**（`GET /work-report/report/info`），传入 `reportId`。
5. 对汇报进行讨论回复时，调用 **5.2 汇报回复**（`POST /work-report/report/record/reply`），传入 `reportRecordId` 与 `contentHtml`（可带附件）。

### 场景二：处理决策/建议/反馈待办

> 需求：获取当前用户需要处理的待办，并完成待办（建议/决策）。

1. 调用 **5.15 分页获取决策/建议/反馈待办列表**（`POST /work-report/reportInfoOpenQuery/todoList`）获取待办列表项（含 `todoId`、`todoType` 等）。
2. 查看待办详情对象（AI 摘要/进展/是否需要当前处理人操作）在列表项的 `detail` 字段中（见 **6.10 ReportTodoDetailVO**）。
3. 完成待办时，调用 **5.18 完成待办（建议/决策）**（`POST /work-report/open-platform/todo/completeTodo`），传入 `todoId` 与 `content`；当 `todoType` 为决策类时需额外传 `operate=agree/disagree`。

---

### 场景三：用户想要通过 业务单元 进行汇报

> **AI 智能意图匹配指引**：当用户在自然语言/上下文中表达“我要按照某个特定的业务组/汇报链规则交这份报告”（如提示了业务组名称信息）时，大模型应该主动接管以下分析编排。

**核心链路设计（AI Agent 执行建议）：**

1. **智能探查与匹配（核心**）：
    - **Step 1**：大模型主动调用 **5.30 全量查询我的业务单元方案列表(含节点)**，拉取当前用户预设好的所有方案及相关节点上下文配置。
    - **Step 2**：**大模型自主推理**——将用户上下文中提及的“业务单元名称、职责提示”与查到的列表项 `name`、`description` 等信息进行**语义/模糊匹配**。
    - **Step 3**：**确定性校验机制**——
        - **极具确定性**：若语义高度匹配且唯一（如原文提到了绝对一致或强相关的名称），直接提取该方案对应的唯一 `id`，进入下一步自动填充。
        - **存在歧义/不确定**：若匹配度较低，或同时命中多个相似候选，**绝不可盲目自动填充**，必须将候选项展示给用户，由用户做出最终选择。
2. **引用发送**：
    - 在发起提交逻辑时，调用 **5.1 发送汇报** 或 **5.23 新增或者更新汇报草稿**。
    - 将获取或确认的 `businessUnitId` 传入参数，后端服务将自动按方案规则接管流程。
3. **（扩展）未命中时的自动创建询问**：
    - 若经过排查，列表中**没有任何方案吻合用户的意图**，且用户在上下文中仅给出了新的人员指派关系：
    - 大模型**必须先主动询问用户**是否需要将此次的流转规则永久保存为新的业务单元方案。
    - 在获得用户明确同意后，大模型先调用 **4.1 按姓名搜索全部员工** 置换出人员 `empId`。
    - 随后通过 **5.29 保存/更新业务单元汇报方案** 创建新方案并获取新 `id`，最后再回退完成执行第 2 步的发送环节。

---

## 四、基础服务接口

---

## 接口索引

| 编号 | 能力域 | 接口数量 | 文档链接 | 简要说明 |
|------|--------|---------|---------|---------|
| 01 | 员工与分组管理 | 5 | [01-员工与分组管理.md](API接口明细/01-员工与分组管理.md) | 搜索员工、上传文件、分组创建/查询/管理 |
| 02 | 汇报提交与阅读 | 6 | [02-汇报提交与阅读.md](API接口明细/02-汇报提交与阅读.md) | 发送/回复/获取汇报、标记已读、编辑正文 |
| 03 | 收件箱与待办查询 | 12 | [03-收件箱与待办查询.md](API接口明细/03-收件箱与待办查询.md) | 收件箱/发件箱/待办/未读/消息列表查询 |
| 04 | 草稿管理 | 6 | [04-草稿管理.md](API接口明细/04-草稿管理.md) | 草稿 CRUD、草稿转正式汇报、批量删除 |
| 05 | 业务单元与标签管理 | 8 | [05-业务单元与标签管理.md](API接口明细/05-业务单元与标签管理.md) | 业务单元方案管理、个人标签关联 |
| 06 | 工作任务与高级功能 | 16 | [06-工作任务与高级功能.md](API接口明细/06-工作任务与高级功能.md) | 工作任务创建/查询、催办、邮箱管理、搜索 |

---

## 六、公共数据结构


### 6.1 ReportLevelParam

| 字段名          | 类型                        | 说明                                                 |
| --------------- | --------------------------- | ---------------------------------------------------- |
| `type`          | String                      | 类型：read-传阅、suggest-建议、decide-决策           |
| `level`         | Integer                     | 层级：1-20                                           |
| `nodeCode`      | String                      | 节点编码（表单权限节点编码，startNode 表示发起节点） |
| `nodeName`      | String                      | 节点名称                                             |
| `levelUserList` | List\<ReportLevelUserParam> | 当前层级用户列表（见下表）                           |
| `groupIdList`   | List\<Long>                 | 分组 ID 列表（通过 **4.3** 接口获取）               |
| `requirement`   | String                      | 节点填写要求：AI会对节点下的员工输入内容做总结评价                  |
| `buttonConfig`  | NodeButtonConfig            | 按钮配置：自定义节点按钮显隐与事件，见 **6.31**                     |

`ReportLevelUserParam`：

| 字段名        | 类型   | 说明    |
| ------------- | ------ | ------- |
| `empId`       | Long   | 员工 id |

### 6.2 ReportReplyInnerParam.ReportFileVO

| 字段名   | 类型    | 说明                                                                                                     |
| -------- | ------- | -------------------------------------------------------------------------------------------------------- |
| `fileId` | String  | 文件 id                                                                                                  |
| `fsize`  | Integer | 文件大小                                                                                                 |
| `name`   | String  | 文件名称（链接描述）                                                                                     |
| `type`   | String  | file=附件、url=超链、audio=音频、document=文档（带版本）、document-database=知识库（fileId 为知识库 id） |

### 6.3 PageInfo\<T>

| 字段名     | 类型     | 说明              |
| ---------- | -------- | ----------------- |
| `total`    | long     | 总记录数          |
| `list`     | List\<T> | 结果集            |
| `pageNum`  | int      | 当前页，从 1 开始 |
| `pageSize` | int      | 每页数量          |
| `size`     | int      | 当前页数量        |

### 6.4 ReportRecordPageVO

| 字段名             | 类型          | 说明                                                                    |
| ------------------ | ------------- | ----------------------------------------------------------------------- |
| `id`               | Long          | 汇报 id                                                                 |
| `reportRecordType` | Integer       | 工作汇报类型：1-工作交流、2-工作指引、3-文件签批、4-AI 汇报、5-工作汇报 |
| `type`             | String        | 业务类型                                                                |
| `typeId`           | Long          | 业务类型 id                                                             |
| `main`             | String        | 汇报主题                                                                |
| `content`          | String        | 汇报内容（纯文本）                                                      |
| `grade`            | String        | 优先级：一般/紧急                                                       |
| `hasNewReply`      | Boolean       | 是否有新回复                                                            |
| `sendEmpId`        | Long          | 发送人 userid                                                           |
| `laterRead`        | Boolean       | 稍后阅读                                                                |
| `mark`             | Boolean       | 星标汇报                                                                |
| `myStatus`         | Integer       | 1 已读 0 未读 2 已回复（仅部分场景）                                    |
| `replyCount`       | Integer       | 回复总数                                                                |
| `fileCount`        | Long          | 上传附件数                                                              |
| `userStatus`       | String        | 状态                                                                    |
| `reportEventVO`    | ReportEventVO | 汇报事件对象（见 **6.20**）                                             |

### 6.5 TodoTaskDetailVO

字段较多，常用字段如下：

| 字段名             | 类型      | 说明                                     |
| ------------------ | --------- | ---------------------------------------- |
| `todoId`           | Long      | 待办 id                                  |
| `id`               | Long      | 汇报 id                                  |
| `reportRecordType` | Integer   | 工作汇报类型                             |
| `planId`           | Long      | 任务 id                                  |
| `reportRecordId`   | Long      | 汇报 id                                  |
| `sourceId`         | Long      | 数据源 id（不同类型含义不同）            |
| `status`           | Integer   | 0-未完成、1-已完成、2-已取消、3-稍后处理 |
| `executorEmpId`    | Long      | 执行员工 id                              |
| `executionResult`  | String    | 执行结果                                 |
| `laterRemindTime`  | Timestamp | 稍后提醒时间（status=3）                 |
| `type`             | String    | 待办类型                                 |
| `feedbackReplyId`  | Long      | 待反馈的评论 id                          |
| `main`             | String    | 主题                                     |
| `writeEmpId`       | Long      | 填写汇报员工 id                          |
| `writeEmpName`     | String    | 写汇报员工名称                           |
| `content`          | String    | 汇报内容                                 |
| `todoContent`      | String    | 待办内容                                 |
| `ruleType`         | String    | once/day/week/month/n_week               |
| `requiredIndex`    | String    | 提醒日                                   |
| `requiredValue`    | String    | 提醒时间（HH:mm:ss）                     |
| `orderCreateTime`  | Timestamp | 待办创建时间                             |
| `orderUpdateTime`  | Timestamp | 待办更新时间                             |
| `reportStatus`     | Integer   | 0-关闭、1-待汇报、2-已汇报、3-逾期       |

### 6.6 ReportDTO

| 字段名       | 类型            | 说明     |
| ------------ | --------------- | -------- |
| `reportId`   | Long            | 汇报 ID  |
| `main`       | String          | 汇报标题 |
| `content`    | String          | 汇报正文 (纯文本) |
| `contentHtml`| String          | 汇报内容 (富文本) |
| `contentType`| String          | 正文类型：`html`/`markdown` |
| `writeEmpId` | Long            | 汇报人 ID |
| `writeEmpName`| String          | 汇报人姓名 |
| `createTime` | Timestamp       | 创建时间 |
| `replies`    | List\<ReplyDTO> | 回复列表 |

`ReplyDTO`：

| 字段名         | 类型      | 说明       |
| -------------- | --------- | ---------- |
| `replyId`      | Long      | 回复 ID    |
| `content`      | String    | 回复内容 (纯文本)  |
| `contentHtml`  | String    | 回复内容 (富文本)  |
| `contentType`  | String    | 正文类型：`html`/`markdown` |
| `replyEmpId`   | Long      | 回复人 ID  |
| `replyEmpName` | String    | 回复人姓名 |
| `createTime`   | Timestamp | 创建时间   |

### 6.7 RecentTemplateResultVO

| 字段名                   | 类型                    | 说明                               |
| ------------------------ | ----------------------- | ---------------------------------- |
| `recentOperateTemplates` | List\<RecentTemplateVO> | 最近操作过的事项列表（见 **6.8**） |

### 6.8 RecentTemplateVO

| 字段名       | 类型   | 说明     |
| ------------ | ------ | -------- |
| `templateId` | Long   | 事项 ID  |
| `main`       | String | 事项名称 |

### 6.9 TemplateSimpleVO

| 字段名       | 类型   | 说明     |
| ------------ | ------ | -------- |
| `templateId` | Long   | 事项 ID  |
| `main`       | String | 事项名称 |

### 6.10 ReportTodoDetailVO

| 字段名                  | 类型          | 说明                                                    |
| ----------------------- | ------------- | ------------------------------------------------------- |
| `aiSummary`             | String        | AI 摘要                                                 |
| `progressList`          | List\<String> | 当前进展列表（格式：谁在什么时间回复类型，内容为：xxx） |
| `needAction`            | String        | 是否需要当前操作人决策/建议/反馈（如“需要决策”）        |
| `hasSubsequentDecision` | Boolean       | 后续是否还有决策建议节点                                |

### 6.11 PluginReportAllVO

| 字段名             | 类型             | 说明                        |
| ------------------ | ---------------- | --------------------------- |
| `latestTodoList`   | PluginItemListVO | 最新待办列表（见 **6.12**） |
| `unreadReportList` | PluginItemListVO | 未读汇报列表（见 **6.12**） |

### 6.12 PluginItemListVO

| 字段名   | 类型                      | 说明                |
| -------- | ------------------------- | ------------------- |
| `total`  | Integer                   | 总数                |
| `hasNew` | Boolean                   | 是否有新数据        |
| `list`   | List\<PluginItemDetailVO> | 列表（见 **6.13**） |

### 6.13 PluginItemDetailVO

| 字段名             | 类型      | 说明                                                                |
| ------------------ | --------- | ------------------------------------------------------------------- |
| `todoId`           | Long      | 待办 id                                                             |
| `id`               | Long      | 汇报 id                                                             |
| `main`             | String    | 标题                                                                |
| `content`          | String    | 内容                                                                |
| `reportRecordType` | Integer   | 汇报类型：1-工作交流、2-工作指引、3-文件签批、4-AI 汇报、5-工作汇报 |
| `writeEmpName`     | String    | 创建人                                                              |
| `createTime`       | Timestamp | 创建时间                                                            |
| `levelType`        | String    | 节点类型：suggest-建议节点、decide-决策节点                         |
| `employee`         | String    | 人员名称                                                            |

### 6.14 ReportPlanSearchPageVO

字段较多，常用字段如下：

| 字段名              | 类型                    | 说明                                 |
| ------------------- | ----------------------- | ------------------------------------ |
| `id`                | Long                    | 任务 id                              |
| `createTime`        | Timestamp               | 创建时间                             |
| `main`              | String                  | 任务名称                             |
| `target`            | String                  | 任务目标                             |
| `budget`            | BigDecimal              | 任务预算                             |
| `needful`           | String                  | 任务描述                             |
| `type`              | String                  | 业务类型                             |
| `typeId`            | Long                    | 业务类型 id                          |
| `status`            | Integer                 | 任务状态：0-关闭、1-进行中、2-未启动 |
| `ruleType`          | String                  | once/day/week/month/n_week           |
| `lastReportTime`    | Timestamp               | 任务最后一次汇报提交时间             |
| `reportStatus`      | Integer                 | 0-关闭、1-待汇报、2-已汇报、3-逾期   |
| `reportSubmitCount` | Integer                 | 已提交汇报数量                       |
| `reportTotalCount`  | Integer                 | 需要提交的汇报总数                   |
| `duration`          | Integer                 | 执行时长（天）                       |
| `stageName`         | String                  | 阶段名称                             |
| `planLevel`         | Integer                 | 任务级别                             |
| `parentName`        | String                  | 父任务名称                           |
| `templateId`        | Long                    | 事项 id                              |
| `reporterList`      | List\<EmployeeSimpleVO> | 汇报人信息（见 **6.21**）            |
| `isRead`            | Integer                 | 0-未读、1-已读                       |

### 6.15 TodoTaskCreatedFeedbackVO

| 字段名       | 类型       | 说明                                     |
| ------------ | ---------- | ---------------------------------------- |
| `todoId`     | Long       | 待办 ID                                  |
| `reportId`   | Long       | 待办关联的汇报 ID                        |
| `status`     | Integer    | 0 未处理，1 已处理，2 已取消，3 稍后提醒 |
| `type`       | String     | 待办类型                                 |
| `executor`   | JSONObject | 待办处理人                               |
| `content`    | String     | 待办内容                                 |
| `createTime` | Timestamp  | 待办创建时间                             |
| `updateTime` | Timestamp  | 待办处理时间                             |

### 6.16 ReportPlanSimpleInfoVO

| 字段名                    | 类型                      | 说明                                       |
| ------------------------- | ------------------------- | ------------------------------------------ |
| `id`                      | Long                      | 任务 ID                                    |
| `createTime`              | Timestamp                 | 任务创建时间                               |
| `corpId`                  | Long                      | 企业 id                                    |
| `main`                    | String                    | 任务名称                                   |
| `needful`                 | String                    | 任务描述                                   |
| `target`                  | String                    | 任务目标                                   |
| `reportFormatRequirement` | String                    | 汇报格式要求                               |
| `type`                    | String                    | 业务类型                                   |
| `typeId`                  | Long                      | 业务类型 id                                |
| `planLevel`               | Integer                   | 1-普通任务、2-高级任务、3-AI 任务          |
| `reportMethod`            | Integer                   | 1-按要求汇报、2-按阶段汇报                 |
| `status`                  | Integer                   | 0-关闭、1-进行中、2-草稿、3-未启动、4-搁置 |
| `endTime`                 | Timestamp                 | 计划结束时间（NULL 表示任务始终不结束）    |
| `lastReportTime`          | Timestamp                 | 最后一次汇报提交时间                       |
| `linkIds`                 | String                    | 关联汇报 id（多个逗号分割）                |
| `templateId`              | Long                      | 事项 id                                    |
| `formTemplateId`          | Long                      | 表单模板 id                                |
| `reportList`              | List\<ReportSimpleInfoVO> | 任务提交的汇报信息（见 **6.17**）          |

### 6.17 ReportSimpleInfoVO

| 字段名             | 类型      | 说明                                 |
| ------------------ | --------- | ------------------------------------ |
| `id`               | Long      | 汇报 ID                              |
| `createTime`       | Timestamp | 汇报创建时间                         |
| `corpId`           | Long      | 企业 id                              |
| `planId`           | Long      | 工作任务 id                          |
| `reportRecordType` | Integer   | 工作汇报类型                         |
| `reportCode`       | String    | 唯一编码                             |
| `type`             | String    | 业务类型                             |
| `typeId`           | Long      | 业务类型 id                          |
| `status`           | Integer   | 1-已提交、2-暂存、3-已撤回、6-已驳回 |
| `main`             | String    | 汇报主题                             |
| `grade`            | String    | 优先级：一般/紧急                    |
| `privacyLevel`     | String    | 密级：非涉密/涉密                    |
| `content`          | String    | 内容（纯文本）                       |
| `contentHtml`      | String    | 内容（富文本）                       |
| `contentType`      | String    | html/markdown                        |
| `writeEmpId`       | Long      | 写汇报员工 id                        |
| `writeEmpName`     | String    | 写汇报员工姓名                       |
| `linkIds`          | String    | 关联汇报 id（多个逗号分割）          |
| `linkPlanIds`      | String    | 关联任务 id（多个逗号分割）          |
| `templateId`       | Long      | 事项 id                              |
| `formTemplateId`   | Long      | 表单模板 id                          |

### 6.18 ReportTodoListItemVO

| 字段名             | 类型               | 说明                                               |
| ------------------ | ------------------ | -------------------------------------------------- |
| `reportId`         | Long               | 汇报 id                                            |
| `reportRecordType` | Integer            | 工作汇报类型                                       |
| `main`             | String             | 汇报主题                                           |
| `writeEmpName`     | String             | 汇报员工姓名                                       |
| `createTime`       | Timestamp          | 汇报时间                                           |
| `todoType`         | String             | 待办类型：decide-决策、suggest-建议、feedback-反馈 |
| `todoId`           | Long               | 待办 id                                            |
| `detail`           | ReportTodoDetailVO | 详情对象（见 **6.10**）                            |

### 6.19 ReportUnreadListItemVO

| 字段名             | 类型               | 说明                    |
| ------------------ | ------------------ | ----------------------- |
| `reportId`         | Long               | 汇报 id                 |
| `reportRecordType` | Integer            | 工作汇报类型            |
| `main`             | String             | 汇报主题                |
| `writeEmpName`     | String             | 汇报员工姓名            |
| `createTime`       | Timestamp          | 汇报时间                |
| `detail`           | ReportTodoDetailVO | 详情对象（见 **6.10**） |

### 6.20 ReportEventVO

| 字段名 | 类型      | 说明     |
| ------ | --------- | -------- |
| `name` | String    | 事件名称 |
| `time` | Timestamp | 事件时间 |

### 6.21 EmployeeSimpleVO

| 字段名 | 类型   | 说明    |
| ------ | ------ | ------- |
| `id`   | Long   | 员工 id |
| `name` | String | 姓名    |

### 6.22 OpenPlatformNewMsgSummaryVO

| 字段名     | 类型                           | 说明         |
| ---------- | ------------------------------ | ------------ |
| `total`    | Integer                        | 新消息总数   |
| `msgList`  | List\<OpenPlatformNewMsgVO>    | 新消息列表（见 **6.23**）   |

### 6.23 OpenPlatformNewMsgVO

| 字段名                       | 类型      | 说明                                                                                          |
| ---------------------------- | --------- | --------------------------------------------------------------------------------------------- |
| `unReadCount`                | Integer   | 汇报下新消息数                                                                                |
| `reportId`                   | Long      | 汇报id                                                                                        |
| `reportTitle`                | String    | 汇报标题                                                                                      |
| `lastReportReplyId`          | Long      | 最近一条回复id                                                                                |
| `lastReplyContent`           | String    | 最近一条回复内容                                                                              |
| `lastReplyTime`              | String    | 最近一条回复时间                                                                              |
| `replyEmployeeName`          | String    | 发送消息人员姓名                                                                              |
| `replyEmployeeDeptAndTitle`  | String    | 发送消息人员部门职位信息(例如: `[开发组-Web开发工程师]`)                                        |
| `type`                       | String    | 通知类型中文描述(我收到的回复/@我的回复/指引/签批/反馈/写汇报通知/汇报提交通知/其他消息) |

### 6.24 OpenPlatformFileVO

| 字段名   | 类型   | 说明                                           |
| -------- | ------ | ---------------------------------------------- |
| `fileId` | String | 文件 id                                        |
| `name`   | String | 文件名称                                       |
| `type`   | String | 文件类型：file=附件、url=超链、audio=音频      |
| `fsize`  | Long   | 文件大小                                       |
| `url`    | String | 文件链接（超链类型的 url，或附件的直接下载链接） |

### 6.25 TargetUserGroupVO

| 字段名      | 类型             | 说明                       |
| ----------- | ---------------- | -------------------------- |
| `groupId`   | Long             | 分组 ID                    |
| `groupName` | String           | 分组名称                   |
| `ownType`   | Integer          | 归属类型, 1: 个人; 2: 公司 |
| `members`   | List\<MemberVO> | 成员列表（见 **6.26 MemberVO**）    |

### 6.26 MemberVO

| 字段名 | 类型   | 说明    |
| ------ | ------ | ------- |
| `id`   | Long   | 人员 ID |
| `name` | String | 姓名    |
| `title`| String | 职位    |

### 6.27 DraftBoxListVO

草稿箱列表单行数据（**5.24 草稿箱分页查询** 中 `list` 元素类型）。

| 字段名        | 类型      | 说明                                                                 |
| ------------- | --------- | -------------------------------------------------------------------- |
| `id`          | Long      | 草稿 ID                                                              |
| `bizType`     | String    | 业务类型：`report`-汇报、`plan`-任务                                 |
| `businessId`  | Long      | `bizType=report` 时为汇报 id；`bizType=plan` 时为任务 id               |
| `title`       | String    | 标题                                                                 |
| `content`     | String    | 正文摘要（仅展示约前 200 个字符）                                    |
| `grade`       | String    | 优先等级：一般、紧急                                                 |
| `existsFiles` | Integer   | 附件状态：`0`-无附件，`1`-有附件                                     |
| `status`      | Integer   | 草稿箱状态：`1`-有效，`2`-无效，`3`-删除                             |
| `createTime`  | Timestamp | 创建时间                                                             |
| `updateTime`  | Timestamp | 更新时间                                                             |

### 6.28 汇报详情VO

**5.25 草稿汇报详情** 成功时 `data` 的类型（OpenAPI：`汇报详情VO`）。与 **6.1 ReportLevelParam** 不同，本结构用于**详情查询结果**：接收人/抄送为 `EmployeeSimpleVO` 列表，多级节点为 `ReportLevelVO`（内含 `empList`），附件字段名为 `fileList`。

| 字段名                 | 类型                      | 说明                                                                 |
| ---------------------- | ------------------------- | -------------------------------------------------------------------- |
| `id`                   | Long                      | 汇报 ID                                                              |
| `main`                 | String                    | 汇报主题                                                             |
| `contentHtml`          | String                    | 汇报内容（富文本）                                                   |
| `contentType`          | String                    | 正文类型：`html`、`markdown`                                         |
| `typeId`               | Long                      | 业务类型 id                                                          |
| `templateId`           | Long                      | 事项 id                                                              |
| `planId`               | Long                      | 工作任务 id                                                          |
| `grade`                | String                    | 优先级：一般、紧急                                                   |
| `privacyLevel`         | String                    | 密级：非涉密、涉密（涉密下载需申请）                                 |
| `reportCode`           | String                    | 唯一编码                                                             |
| `reportRecordType`     | Integer                   | 工作汇报类型：1-工作交流、2-工作指引、3-文件签批、4-AI 汇报、5-工作汇报 |
| `status`               | Integer                   | 状态：1-已提交、2-暂存（草稿）、3-已撤回、6-已驳回                   |
| `acceptEmployeeList`   | List\<EmployeeSimpleVO> | 接收人信息列表（见 **6.21 EmployeeSimpleVO**）                       |
| `copyEmployeeList`     | List\<EmployeeSimpleVO> | 抄送人员列表（见 **6.21 EmployeeSimpleVO**）                       |
| `reportLevelList`      | List\<ReportLevelVO>      | 工作指引/签批多级用户列表（见下表 **ReportLevelVO**）                |
| `fileList`             | List\<OpenPlatformFileVO> | 关联附件；元素结构同 **6.24 OpenPlatformFileVO**（OpenAPI 模型名：`工作汇报-附件信息`） |

**ReportLevelVO**（`reportLevelList` 元素，查询结果形态；提交时仍使用 **6.1 ReportLevelParam**）：

| 字段名     | 类型                       | 说明                                                         |
| ---------- | -------------------------- | ------------------------------------------------------------ |
| `type`     | String                     | 类型：`read`-传阅、`suggest`-建议、`decide`-决策             |
| `level`    | Integer                    | 层级：1–20                                                   |
| `nodeCode` | String                     | 节点编码；签批事项表单权限节点，`startNode` 表示发起节点     |
| `nodeName` | String                     | 节点名称                                                     |
| `empList`  | List\<ReportLevelUserVO>   | 当前层级用户列表（见下表）                                   |

**ReportLevelUserVO**（`empList` 元素）：

| 字段名        | 类型   | 说明    |
| ------------- | ------ | ------- |
| `empId`       | Long   | 员工 id |
| `name`        | String | 姓名    |
| `requirement` | String | AI 要求 |

### 6.29 ReportBusinessUnitDetailVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 方案 ID |
| `name` | String | 方案名称 |
| `description` | String | 方案说明 |
| `nodeList` | List\<ReportBusinessUnitConfigVO> | 节点配置列表 |

**ReportBusinessUnitConfigVO**

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `nodeName` | String | 节点名称 |
| `nodeDescription` | String | 职责说明 |
| `nodeType` | String | 节点类型：read/suggest/decide |
| `level` | Integer | 节点层级 |
| `empList` | List\<BaseInfo> | 人员列表（含 id/name） |

### 6.30 ReportNodeDetailVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 汇报 ID |
| `main` | String | 汇报标题 |
| `content` | String | 汇报正文 |
| `writeEmpId` | Long | 汇报人 ID |
| `writeEmpName` | String | 汇报人姓名 |
| `createTime` | Timestamp | 发起时间 |
| `nodeList` | List\<NodeInfo> | 节点列表 |

`NodeInfo`：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `nodeName` | String | 节点名称 |
| `type` | String | 节点类型中文 (建议/决策/传阅) |
| `status` | String | 节点状态中文 (未开始/已完成/进行中/已取消) |
| `level` | Integer | 节点层级 |
| `userList` | List\<UserInfo> | 节点下的操作人列表 |

`UserInfo`：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 节点处理人关联 ID |
| `empId` | Long | 员工 ID |
| `name` | String | 姓名 |
| `status` | String | 处理状态中文 (待处理/已处理等) |
| `operate` | String | 操作动作中文 (同意/不同意/建议等) |
| `content` | String | 处理意见/理由 |
| `finishTime` | Timestamp | 完成时间 |

### 6.31 NodeButtonConfig

用于自定义汇报流程中各节点的按钮样式与交互逻辑。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `systemButtons` | SystemNodeButtonConfig | 系统默认按钮配置 |
| `customButtons` | List\<CustomNodeButton> | 自定义按钮配置列表 |

**SystemNodeButtonConfig**：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `showSuggestButton` | Boolean | 是否显示建议按钮 |
| `suggestButtons` | List\<SystemNodeButton> | 建议按钮配置列表 (仅在 showSuggestButton 为 true 时有效) |
| `showAddFlowUserButton` | Boolean | 是否显示“添加流程人员”按钮 |
| `showIgnoreOrTransferTodoButton` | Boolean | 是否显示“忽略或转办”按钮 |

**CustomNodeButton**：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `type` | String | 按钮类型 |
| `name` | String | 按钮名称 |
| `style` | String | 按钮样式：`blue_background_white_font`(蓝底白字)、`white_background_blue_font`(白底蓝字) |
| `url` | String | 跳转链接 |
| `openMethod` | String | 跳转方式：`new_window`(新窗口)、`popup`(弹窗)、`no_operation`(无操作) |
| `displayTiming` | String | 显示时机：`always`(一直显示)、`after_activate`(节点激活后显示) |
| `clickEffect` | String | 点击后效果：`repeatable`(可重复点击)、`once_hide`(点击后隐藏)、`once_disable`(点击后禁用) |

### 6.32 ReportRecordAssociatedContentSimpleVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `fileList` | List\<ReportFileSimpleVO> | 关联附件列表（见 **6.33**） |

### 6.33 ReportFileSimpleVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `downloadUrl` | String | 下载 URL |
| `fileName` | String | 文件名 |
| `fileSummary` | String | 文件摘要 |
| `resourceId` | Long | 资源 ID |
| `size` | Long | 文件大小（字节） |
| `suffix` | String | 文件后缀 |
| `duration` | Integer | 音频时长（秒） |
| `translationWord` | String | 语音转译文字 |

### 6.34 ReportReplySimpleVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `content` | String | 回复内容 |
| `createTime` | Timestamp | 回复时间 |
| `fileList` | List\<ReportFileSimpleVO> | 回复附件（见 **6.33**） |
| `replyEmpName` | String | 回复人 |
| `title` | String | 回复人职位 |
| `type` | String | 回复类型：`common`、`suggest`、`decide_agree`、`decide_disagree`、`sign`、`lead`、`feedback`、`plan_feedback`、`rebut`、`file_audit`、`business` |

### 6.35 MailBoxAssociatedVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `content` | String | 邮件内容（JSON 字符串，如 `{"content":"<div>abc</div>"}`） |
| `id` | Long | 主键 ID |
| `realContent` | String | 解析后的邮件内容（不带 js） |
| `subject` | String | 邮件主题 |

### 6.36 ReportPlanAISimpleVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 主键 ID |
| `main` | String | 任务名称 |
| `needful` | String | 任务描述 |
| `requirement` | String | 任务要求（AI 要求） |
| `target` | String | 任务目标 |

### 6.37 ReportRecordSimpleVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `content` | String | 汇报内容 |
| `createTime` | Timestamp | 创建时间 |
| `leadContent` | String | 指引内容 |
| `main` | String | 汇报主题 |
| `reportRecordType` | Integer | 工作汇报类型：`1`-工作交流、`2`-工作指引、`3`-文件签批、`4`-AI 汇报、`5`-工作汇报 |
| `updateTime` | Timestamp | 修改时间 |

### 6.38 ReportSimpleInfoByTypeVO

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `associatedContent` | ReportRecordAssociatedContentSimpleVO | 关联内容（见 **6.32**） |
| `associatedReportList` | List\<ReportSimpleInfoByTypeVO> | 关联汇报列表（递归结构） |
| `createTime` | Timestamp | 汇报时间 |
| `mailBoxList` | List\<MailBoxAssociatedVO> | 关联邮件列表（见 **6.35**） |
| `planIdList` | List\<Long> | 任务 ID 列表 |
| `planList` | List\<ReportPlanAISimpleVO> | 任务列表（见 **6.36**） |
| `replyList` | List\<ReportReplySimpleVO> | 回复信息（见 **6.34**） |
| `reportRecord` | ReportRecordSimpleVO | 汇报信息（见 **6.37**） |
| `reportRecordId` | Long | 汇报 ID |
| `writeEmpId` | Long | 写汇报员工 ID |
| `writeEmpName` | String | 汇报人 |

### 6.39 EmployeeMailInfoVO

获取绑定邮箱信息接口（**5.47**）成功时 `data` 的对象类型。`id` 为空或缺失时表示尚未绑定外部邮箱（以服务端实现为准）。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 绑定的邮箱 ID；**空表示未绑定** |
| `name` | String | 用户名称 |
| `nickname` | String | 昵称 |
| `corpId` | Long | 企业 id |
| `emailAddress` | String | 绑定的邮箱地址 |
| `avatar` | String | 头像 URL |
| `personId` | Long | 用户 personId（与企业无关） |
| `telephone` | String | 手机号 |
| `title` | String | 职位 |
| `status` | Integer | 状态：`1`-正常、`2`-禁用（含离职等） |
| `inboxCount` | Integer | 收件箱已同步数量 |
| `lastSyncTime` | String | 最近同步时间，格式 `yyyy-MM-ddTHH:mm:ss.SSSXXX`（含时区偏移） |
| `managerEmpId` | Long | 直属主管员工 id |
| `outboxCount` | Integer | 发件箱已同步数量 |
| `syncStatus` | Integer | 同步状态：`0`-正在同步中、`1`-同步已结束 |

### 6.40 BandingMailParam

绑定邮箱（**5.48**）请求体对象。字段在 OpenAPI 中可为空，**实际落库/同步前通常需要有效邮箱与密码**。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `emailAddress` | String | 邮箱地址 |
| `emailPwd` | String | 邮箱密码（传输与存储以服务端安全策略为准） |

### 6.41 SearchMailParam

邮件分页（**5.51**）请求体对象。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `keyWord` | String | 搜索主题与邮件内容 |
| `mailType` | Integer | 邮件类型：`1`-收件箱、`2`-发件箱 |
| `pageIndex` | Integer | 当前页号，**从 1 开始** |
| `pageSize` | Integer | 每页记录数 |

### 6.42 MailPageItemVO

已同步邮件列表分页（**5.51**）`PageInfo` 的 `list` 元素类型。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 邮件记录主键 id |
| `employeeMailId` | Long | 绑定的邮箱 id |
| `mailAccount` | String | 邮箱账号 |
| `mailType` | Integer | 邮件类型：`1`-收件箱、`2`-发件箱 |
| `msgId` | String | 邮件 Message-ID |
| `uid` | String | 邮件 UID（与协议/服务端实现相关） |
| `subject` | String | 主题 |
| `fromMail` | String | 发件人 |
| `toMails` | String | 收件人；多人时逗号分隔 |
| `ccMails` | String | 抄送人；多人时逗号分隔 |
| `replyTo` | String | 回复时使用的收件人 |
| `content` | String | 邮件内容，通常为 JSON 字符串，如 `{"content":"<div>abc</div>"}` |
| `realContent` | String | 解析后的正文（不含可执行脚本） |
| `attachments` | String | 附件，JSON 数组字符串，如 `[{"name":"abc","url":"http://ab.c"}]` |
| `sendTime` | String | 发件时间，格式 `yyyy-MM-ddTHH:mm:ss.SSSXXX` |
| `createTime` | String | 创建时间 |
| `updateTime` | String | 修改时间 |

### 6.43 SearchReportRecordPageParam

汇报搜索分页（**5.52**）请求体对象。

| 字段名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `beginTime` | Long | 否 | 汇报开始时间（毫秒时间戳） |
| `endTime` | Long | 否 | 汇报结束时间（毫秒时间戳） |
| `keyWord` | String | 否 | 关键词：主题、唯一编码、发汇报人、内容等 |
| `pageIndex` | Integer | 是 | 页码，**从 0 开始** |
| `pageSize` | Integer | 是 | 每页条数 |
| `classificationIdList` | List\<Long> | 否 | 汇报分类 id 列表 |
| `fromEmpIdList` | List\<String> | 否 | 发汇报人（写汇报人）员工 id 列表 |
| `toEmpIdList` | List\<String> | 否 | 接收汇报人员工 id 列表 |

### 6.44 ReportRecordSearchItemVO

汇报搜索分页（**5.52**）`PageInfo` 的 `list` 元素类型（OpenAPI/检索返回字段可能扩展，以实际响应为准）。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String | 汇报 id |
| `code` | String | 汇报唯一编码 |
| `main` | String | 汇报主题（标题） |
| `title` | String | 计划标题 |
| `needful` | String | 计划汇报内容要求 |
| `textContent` | String | 汇报内容 |
| `type` | String | 汇报类型（如业务线名称/类型描述） |
| `status` | Integer | 状态，如 `1` 已提交（以产品定义为准） |
| `reportTime` | Long | 汇报时间（毫秒时间戳） |
| `corpId` | String / Long | 企业 id；序列化中可能出现字符串，对接建议按 Long/字符串双兼容 |
| `label` | String | 标签，多个以分号分隔 |
| `projectName` | String | 关联业务名，多个以分号分隔 |
| `isLead` | Integer | 是否指引汇报：`0` 否、`1` 是 |
| `isSign` | Integer | 是否文件签批：`0` 否、`1` 是 |
| `mailSubject` | String | 关联邮件主题 |
| `mailRealContent` | String | 关联邮件解析正文（无 js） |
| `leadContent` | String | 需指引内容 |
| `fileList` | List\<EsWorkFile> | 附件/超链列表（见 **6.47**） |
| `fromEmp` | EsEmpInfo | 写汇报人（见 **6.45**） |
| `toEmpList` | List\<EsEmpInfo> | 接收汇报人列表（见 **6.45**） |
| `classificationObjectList` | List\<EsClassification> | 分类列表（见 **6.46**） |

### 6.45 EsEmpInfo

搜索汇报项中的参与人简要信息（**5.52 / 6.44**）。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 员工 id |
| `name` | String | 姓名 |
| `corpId` | Long / String | 企业 id；序列化中可能出现字符串，对接按 Long/字符串兼容 |
| `deptQueryCodeList` | List\<String> | 部门 queryCode 集合（以接口返回为准，可为空） |

### 6.46 EsClassification

搜索汇报项中的分类信息（**5.52 / 6.44**）。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Long | 分类 id |
| `name` | String | 分类名称 |

### 6.47 EsWorkFile

搜索汇报项中的附件或超链（**5.52 / 6.44**）。含义与 `OpenPlatformFileVO`（**6.24**）类似，为检索侧（ES）返回的简化结构。

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `fileId` | String | 文件/资源 id |
| `name` | String | 名称或链接描述 |
| `type` | String | 类型（如 `file`/`url` 等，以返回为准） |
| `url` | String | 链接或下载地址 |


---

## 七、错误码说明

---


> 以下为通用与鉴权相关错误码示例，具体以平台配置与返回为准。

| resultCode | 说明                                                     |
| ---------- | -------------------------------------------------------- |
| 1          | 请求成功                                                 |
| 401        | 鉴权失败/缺少访问凭证（如缺少 appKey、Token 校验失败等） |
| 60001      | 内部接口，禁止外部访问                                   |
| 60002      | 禁止访问                                                 |

---

## 八、注意事项

---


1. **ID 精度**：所有 ID 建议按 Long/字符串处理，前端请避免用 JS Number 直接承载超大整数。
2. **时间戳单位**：文档中 `beginTime/endTime/lastUpdateTime/timestamp` 均为 **毫秒**。
3. **SSE 接口**：`/work-report/open-platform/report/aiSseQaV2` 为 `text/event-stream`，客户端需使用支持 SSE 的方式持续读取流。
4. **汇报内容字段**：提交汇报时建议只传 `contentHtml`，服务端会生成纯文本 `content`；回复同理。
