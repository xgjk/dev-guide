# BD快评 `inner_bd_quick_cn` 全链路详解（模版 -> 成报）

> 生成时间：2026-03-27  
> 依据：`ai-report` 服务真实代码实现 + 生产实测模板数据  
> 目标：只按 `ai-report` 实际路由/参数/执行逻辑，说明 `inner_bd_quick_cn` 从模版到报告的完整过程（含每一步输入/输出/状态流转）

---

## 1. 数据来源与口径（仅 ai-report）

- **代码口径（唯一准绳）**：
  - `backend/src/controller/task_ctrller.py`
  - `backend/src/controller/moban_ctrller.py`
  - `backend/src/service/task_service.py`
  - `backend/src/ai_report_v2/ai_report_tool_v3.py`
  - `backend/src/core/param_entity.py`
- **生产数据校验（用于确认模板现状）**：
  - 查询动作：模板详情 `mobanDetail`
  - 校验对象：`inner_bd_quick_cn`
  - 校验目标：确保模板字段、章节、题目与文档描述一致

---

## 2. 模版实时快照（生产环境实测）

## 2.1 基本字段

- `mobanId`: `inner_bd_quick_cn`
- `name`: `BD研究快评报告`
- `desc`: `简化版药品分析方案，适合初步筛选和快速决策`
- `bizCode`: `bd_ai_report`
- `mode`: `quick`
- `language`: `zh_CN`
- `mobanTypeId`: `inner_deep`
- `state`: `1`（启用）
- `public`: `1`（公开）
- `enableImageGeneration`: `0`（默认不启用图片生成）
- `requireContext`: `["公司名","产品名"]`

## 2.2 章节与题目结构

- 共 `5` 个章节、`6` 个子章节。
- 子章节（按返回顺序）：
  1. 产品综合信息 / 产品标识
  2. 产品综合信息 / 公司介绍
  3. 产品力分析 / 靶点认可度
  4. 市场潜力分析 / 专利分析（`withNet=true`，`dataSrc.srcType=知识库`）
  5. 商业价值分析 / 上市时间预估（`withNet=true`，`dataSrc.srcType=知识库`）
  6. 风险提示 / 市场规模风险（`withNet=true`，`dataSrc.srcType=知识库`）

## 2.3 Prompt 配置

- 顶层 `prompt`：医药研究分析师总提示词（含来源优先级、引用规范、风险要求）。
- `promptConfig.defaultTemplate`：任务级拼装模板，变量包括：
  - `opportunity_summary`
  - `company_name`
  - `product_name`
  - `question_section`
  - `question_title`
  - `question_content`
- `promptConfig.sceneTemplate`：包含 `market_analysis` 与 `technical_analysis` 场景模板。
- `promptConfig.system`：`你是一个专业的医药研究分析师...`

---

## 3. ai-report 实际接口与参数契约

以下全部是 `ai-report` 后端真实路由（不是代理层路径）。

## 3.1 读取模版详情（真实入口）

- **接口**：`POST /moban/mobanDetail`
- **请求体（最小）**：
```json
{
  "mobanId": "inner_bd_quick_cn"
}
```
- **控制器**：`moban_ctrller.mobanDetail()`
- **服务**：`moban_service.moban_detail(mobanId)`
- **返回**：模板全量结构（基本信息 + `requireContext` + `promptConfig` + `sectionList`）

## 3.2 发起报告任务（真实入口）

- **接口**：`POST /task/startTask`
- **请求体（建议）**：
```json
{
  "mobanId": "inner_bd_quick_cn",
  "taskName": "BD快评-某公司-某产品",
  "context": {
    "公司名": "XX公司",
    "产品名": "XX产品",
    "机会概述": "建议补充，提升可用性"
  }
}
```
- **控制器**：`task_ctrller.startTask()`
- **服务**：`task_service.start_task(param, h)`
- **实际入参对象**：`TaskStartParam`
  - 常见字段：`context/mobanId/bizCode/mode/language/questionList/taskName/aiType/temperature`
  - 回调字段：`gptsSessionId/callbackUrl/editCallbackUrl/fileName`
  - 报告属性：`reportType`（1普通，2定时，3系统）
  - 高级字段：`questionDataSrc/enableImageGeneration/runtimeContextDeps`
- **返回**：`data = taskId`

## 3.3 查询执行状态（真实入口）

- **接口**：`POST /task/checkTask`（兼容入口还有 `/task/open/checkTask`）
- **请求体**：`{"taskId":"..."}`（`taskId` 必填）
- **返回（核心）**：
```json
{
  "state": 1,
  "finalReport": "...",
  "uploadInfo": {},
  "err": null
}
```
- **state 语义（ai-report）**：
  - `1`: 进行中
  - `2`: 成功
  - `3`: 失败

## 3.4 查询结构化详情（真实入口）

- **接口**：`POST /task/taskDetailV2`
- **请求体**：`{"taskId":"..."}`
- **返回**：任务主信息 + `sectionList[].questionList[]` + 重跑记录 + 版本历史

## 3.5 人工修订子章节（可选，真实入口）

- **接口**：`POST /task/updateQuestionResult`
- **请求体**：
```json
{
  "questionId": "来自taskDetailV2的子章节_id",
  "result": "新的Markdown内容"
}
```
- **关键行为**：不仅改一段文字，还会触发整份报告重组与新文件上传。

---

## 4. 从模版到成报：逐步执行链路（内部真实过程）

## Step 0：入口与鉴权（ai-report）

1. 客户端直接调用 `ai-report` 路由：
   - `POST /moban/mobanDetail`
   - `POST /task/startTask`
   - `POST /task/checkTask`
   - `POST /task/taskDetailV2`
2. 控制器统一通过 `quartUtil.parse_header(request.headers)` 解析头信息。
3. 对外集成场景可走兼容入口（如 `/task/open/checkTask`），但核心执行逻辑一致。

### 输入
- Header：用户身份相关头（经 `parse_header` 解析）
- Body：对应 JSON 参数

### 输出
- 统一包裹：`resultCode/resultMsg/data`

---

## Step 1：拉模版（`mobanDetail`）

### 代码链路
- `moban_ctrller.mobanDetail()`
- `moban_service.moban_detail(mobanId)`

### 输入
- `mobanId`

### 输出
- 模版定义：`requireContext/prompt/promptConfig/sectionList/questionList/...`

### 注意
- `requireContext` 目前只声明 `公司名/产品名`，但题目中存在 `{机会概述}` 占位符，生产调用建议一并传入。

---

## Step 2：提交任务（`startTask`）

### 代码链路
- `task_ctrller.startTask()`
- `task_service.start_task(param, h)`
- `ai_report_tool_v3.create_task(param, personId, creatorName, userId)`

### 输入（关键字段）
- 必需：`mobanId`、`context`（业务上至少有 `公司名`、`产品名`）
- 建议：`taskName`
- 可选：`aiType/temperature/questionDataSrc/reportType/runtimeContextDeps/...`

### create_task 内部动作
1. 按 `mobanId` 查模板（无则报错“模版不存在”）。
2. 取题目列表（入参未覆盖时用模板默认题目）。
3. 视模板配置动态注入：
   - 章节总结题（`doSectionSummary`）
   - 全文总结题（`doSummary`）
4. 合成任务主记录 `ReportTask` 并落库（含上下文、模型、回调、章节结构等）。
5. 为每个题目创建 `TaskQuestion` 落库，处理：
   - `templateQuestionId/contextDeps`
   - `questionDataSrc` 覆盖 `dataSrc` 与 `withNet`
   - `runtimeContextDeps` 运行时依赖覆盖
6. 注册 RAG 文档源（若有文件数据源）。
7. 投递队列：`report_queue_tool.add_task(taskId)`（异步）。

### 输出
- `taskId`（字符串）

---

## Step 3：异步执行任务（`start_task(taskId)`）

### 代码链路
- `ai_report_tool_v3.start_task(taskId)`

### 任务状态流转
1. 置 `state=1`（运行中）
2. 执行问题分析
3. 聚合最终报告并上传文件
4. 成功置 `state=2`；异常置 `state=3` 并写 `err`

### 调度模式判断
- 若任一问题有 `contextDeps`：走 DAG 分层调度（按依赖层并行执行）
- 否则走兼容调度：
  - **Phase 1**：章节并行，章节内“普通问题 -> 章节总结”
  - **Phase 2**：最后执行报告总结题（若有）
  - **Phase 3**：统一聚合成报告

### 并发参数（快评关键）
- `do_question_list` 并发 worker：默认 `5`
- 生产环境：`15`
- 特定模型会降并发（如 `aiType=37` 时为 `1`）

---

## Step 4：单题执行（`handle_question`）

### 输入
- `TaskQuestion`（含 `section/title/content/prompt/dataSrc/withNet/...`）
- `ReportTask`（含 `context/prompt/aiType/...`）

### 处理
1. 问题置 `state=1`
2. 调用 `ReportAnalyzer.do_analysis(q)`
3. 记录答案与成本（`answer/costMoney`）
4. 题目置 `state=2`；异常置 `state=3`

### 输出（落库）
- `TaskQuestion.result`
- `TaskQuestion.costMoney`
- `TaskQuestion.state`

---

## Step 5：聚合与文件产出

### 代码链路
- `generate(results)`：按 `section -> title -> result` 拼接 Markdown
- `upload_task_res(taskId, finalReport)`：
  1. Markdown -> HTML
  2. HTML -> PDF
  3. 上传 PDF（返回 `resourceId/suffix/...`）
  4. 尝试生成并上传 Word（成功则附加 `wordResourceId/wordSuffix`）

### 输出
- 任务写回：
  - `finalReport`
  - `costMoney`（题目成本求和）
  - `uploadInfo`
  - `state=2`

---

## Step 6：任务收尾钩子（`on_task_end`）

成功任务会触发：
- 回调通知（`callbackUrl`）
- 订阅触发检查（`subscribe_tool`）
- 结构化解析（`struct_parse`，若配置）
- GPTS 消息回推（若有 `gptsSessionId`）
- RAG 入库（按题目分块写入）

---

## Step 7：外部轮询与取详情

## 7.1 轮询 `checkTask`

### 输入
- `taskId`

### 输出
- `state/finalReport/uploadInfo/err`

### 推荐策略
- 每 5 秒轮询一次
- `state=2` 完成，读取 `uploadInfo.resourceId`
- `state=3` 失败，读取 `err`

## 7.2 查询 `taskDetailV2`

内部会：
1. 读取任务主记录
2. 回填 `mobanType` 和 `moban` 详情
3. 将题目按章节归并到 `sectionList[].questionList`
4. 附加 `rerunList/resultVersionList`（并补用户信息）

---

## 8. 编辑与版本分支（可选但重要）

## 8.1 章节重跑（`rerunQuestion/useRerun`，真实实现）

- **重跑接口**：
  - `POST /task/rerunQuestion`
  - 入参：`taskQuestionId`、可选覆盖 `prompt/section/title/content`
  - 动作：创建 rerun 记录并异步执行 `ai_report_tool_v3.do_rerun`
- **采用接口**：
  - `POST /task/useRerun`
  - 入参：`rerunQuestionId`
  - 限制：仅 `state=2`（成功重跑）可采用
- **采用结果动作**：把 rerun 结果覆盖回原始 `TaskQuestion`（题目内容、提示词、结果一并更新）

## 8.2 直接编辑（`updateQuestionResult`）

### 输入
- `questionId`
- `result`

### 内部动作（强副作用）
1. 校验问题存在
2. 若无初始版本，先保存初始版本 `v0`
3. 保存当前编辑版本
4. 重建整份 `finalReport`
5. 重新上传文件并更新 `uploadInfo`
6. 若有 `editCallbackUrl`，发送编辑结果回调

### 输出
- `true`（但背后是整报重算与链接更新）

---

## 9. 快评生成中提示词如何作用（按实际代码）

提示词生效核心在 `backend/src/ai_report_v2/rep_analyzer.py` 的 `ReportAnalyzer._build_prompt()`。

## 9.1 生效时机

- 每个子章节问题在执行 `handle_question -> do_analysis -> _run_question` 时，都会调用一次 `_build_prompt()`。
- 这意味着提示词是“**单题级生效**”，不是“整篇只拼一次”。

## 9.2 作用优先级（普通问题与报告总结）

对普通问题（以及 `toSummary` 报告总结题），提示词模板按以下优先级取值：

1. `question.prompt`（问题级）
2. `section.prompt`（章节级）
3. `task.prompt`（任务级，来源于模板 `moban.prompt`）

代码逻辑等价于：

```python
prompt_template = question.prompt or self.sectionMap.get(question.section) or self.task.prompt
```

## 9.3 章节总结题的特殊链路（`toSectionSummary`）

- 章节总结题不走上面的通用兜底链。
- 它使用：
  1. `question.prompt`（若有）
  2. `DEFAULT_SECTION_SUMMARY_PROMPT`（默认章节总结提示词）
- 然后会额外拼接“该章节已完成子题结果”，让章节总结基于本章内容汇总。

## 9.4 提示词最终拼装结构

无论普通题还是总结题，都会在模板后追加统一问题块（`QUESTION_FORMAT`）：

- 当前日期
- 分析对象（`context`）
- 当前问题：`question_section/question_title/question_content`

其中 `question_content` 先执行：

```python
processed_content = question.content.format(**self.context)
```

也就是先用 `context` 替换题目中的变量占位符（如 `{公司名}`、`{产品名}`、`{机会概述}`）。

## 9.5 `contextDeps` 的作用范围（跨题背景注入）

- 若问题配置了 `contextDeps`，系统会把“依赖子章节结果”作为背景块追加到该题最终 prompt 末尾。
- 这是快评里“前序题影响后序题”的主要机制，作用范围是“当前题的额外背景上下文”。

## 9.6 数据源与联网对提示词的影响

- `withNet` 与 `dataSrc` 不直接改写提示词模板本身，但会改变模型调用方式：
  - 影响是否联网检索
  - 影响是否注入知识库/RAG/MCP/深度搜索结果
- 最终表现是：同一提示词模板下，模型可用上下文来源不同，结果深度会变化。

## 9.7 当前实现中“配置有但未直接作为主拼装入口”的字段

从运行链路看，模板里常见的以下字段当前不直接参与 `_build_prompt()` 主拼装：

- `promptConfig.system`
- `promptConfig.defaultTemplate`
- `promptConfig.sceneTemplate`

当前主拼装仍以 `moban.prompt + section.prompt + question.prompt` 这条链为核心。

---

## 10. “快评为什么快”——当前实现层面的原因

1. **模板问题规模小**：`inner_bd_quick_cn` 仅 6 个子章节。
2. **并发高**：生产默认 `QUEST_SIZE=15`。
3. **调度优化**：章节间并行 + 章节内分阶段执行。
4. **异步化**：`startTask` 只负责入队，客户端轮询 `checkTask`。
5. **模板定位偏初筛**：深度与广度控制在快评节奏内。

---

## 11. 建议的最小调用顺序（生产）

1. `POST /moban/mobanDetail`：确认 `requireContext`、章节结构和提示词
2. `POST /task/startTask`：提交任务并拿 `taskId`
3. `POST /task/checkTask`：轮询状态直到完成
4. `POST /task/taskDetailV2`：获取结构化详情（含章节、版本、重跑记录）
5. （可选）`POST /task/updateQuestionResult`：人工修订并触发整报重组

---

## 12. 关键字段对照（调用侧最常关心）

- `mobanId`: 模版主键（本次为 `inner_bd_quick_cn`）
- `context`: 模版变量注入源（建议覆盖所有题目占位符）
- `taskId`: 任务主键（后续所有状态/详情接口都依赖）
- `questionId`: 子章节主键（仅编辑/版本接口需要）
- `state`: 任务状态（1运行中，2成功，3失败）
- `uploadInfo`: 成品文件资源信息（PDF/Word）

---

## 13. 风险与排查建议

1. **context 不全**：题目出现未替换变量，报告质量显著下降。
2. **误用 questionId**：必须来自 `taskDetailV2` 的真实子章节 `_id`。
3. **把编辑当轻量操作**：`updateQuestionResult` 实际会重算整报并重传文件。
4. **仅看 finalReport 不看 err**：失败场景要优先检查 `err`。
5. **忽略模板动态注入**：若模板启用 `doSummary/doSectionSummary`，实际任务题目数会变化。

---

## 14. 本文结论

`inner_bd_quick_cn` 当前快评链路是一个“**模板驱动 + 异步队列 + 并行求解 + 后处理上传**”的标准生产流水线。  
核心输入是 `mobanId + context`，核心过程是 `create_task -> queue -> start_task -> generate/upload -> check/detail`，核心可控点是 `context 完整性、模型参数、并发策略、后编辑策略`。

