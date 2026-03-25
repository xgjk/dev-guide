## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |

---

**User**


---

**Cursor**

## Skill 1：`BP.CORE.GenerateEvalDraft`（评价草稿生成：关键岗原因与奖金系数原因的标记装配；草稿正文不做 AI 生成）

### 1. 基本信息
- Skill 名称：评价草稿生成（关键岗原因与奖金系数原因标记 + 草稿正文装配）
- Skill 编码：`BP.CORE.GenerateEvalDraft`
- 版本号：`1.0.0`
- 所属业务域：`BP评价`
- 负责人：待你指定
- 适用 Agent 列表：`BP 评价助手`

### 2. Skill 定位
- 业务目的：为“单个被评价人”生成评价结果，其中正文不需要 AI 生成，而是由评价者在输入里直接声明；同时把评价者提供的“关键岗设置原因/关键岗员工奖金系数原因”按声明关系完成标记与呈现。
- 解决什么动作：参数校验 + 规则/配置项建议值校验（如需）+ 文本装配与标记 + 输出草稿结构
- Skill 分类：执行类（装配/标记）

### 3. 输入输出契约（自然语言，不输出代码）

#### 3.1 输入参数清单
- 评价任务定位（至少满足一项）
  - `bpId`（可选）
  - `evalCycleId`（可选）
  - `evalTableId`（可选）
- 被评价人
  - `userId`（必填）
- 请求标识
  - `requestId`（必填）
- 评价者输入（本次关键点：草稿正文来自评价者输入，不做 AI 生成）
  - 关键岗设置
    - `keyPostSettings`：关键岗列表
      - 每条包含：关键岗标识（keyPostId/或你们系统真实字段）、`keyPostReason`（关键岗设置原因，必填）
  - 关键岗员工奖金系数设置
    - `keyPostBonusCoeffSettings`：关键岗对应奖金系数设置列表
      - 每条包含：与关键岗可匹配的标识、奖金系数取值（bonusCoeff）、`bonusCoeffReason`（原因，必填）
  - 关键岗与评价项的“声明映射”
    - 由评价者在输入里直接声明：哪些关键岗用于标记哪些评价项（mapping 声明由你们系统要求的字段来表达）
  - 草稿正文声明（决定“这里不需要 AI 生成”的落地）
    - `itemDraftDeclarations`：按评价项声明的草稿文本
      - 每条包含：`itemId`、`draftContent`（该评价项草稿正文，必填）
      - 并包含用于标记的归属信息（例如该评价项草稿正文要引用哪些关键岗原因与哪些奖金系数原因；归属关系字段由你们系统输入约定）

- 生成选项
  - `recommendationMode`（必填，当前为“生成草稿态结果（装配 + 标记）”）
  - `failIfAnyItemCannotGenerate`（必填）：任一评价项因缺失声明/装配失败时是否整体失败

#### 3.2 参数校验规则
- `userId` 去空后长度必须大于 0
- 定位标识：`bpId/evalCycleId/evalTableId` 至少提供一个
- `keyPostReason`、`bonusCoeffReason` 均需去空后非空
- 草稿正文声明校验
  - 每个进入装配的 `itemDraftDeclarations` 必须包含对应 `itemId` 与非空 `draftContent`
  - 若某评价项没有被评价者声明草稿正文，则该评价项按“未声明”处理（见第 9 点异常与部分成功策略）
- 映射校验（由评价者在输入里直接声明）
  - 声明的关键岗必须在 `keyPostSettings` 中存在
  - 声明的奖金系数条目必须能匹配到 `keyPostBonusCoeffSettings`
- 量化约束校验（如你们系统要求）
  - 奖金系数区间约束：若奖金系数不满足配置约束，按失败处理

#### 3.3 输出结构
- 顶层输出
  - 包含 `requestId`
  - `users`：数组（单人场景通常只有 1 个元素）
- `users[]` 下包含
  - `userId`
  - `evalDraft`
    - `items`：成功装配的评价项列表
      - 每个 item 包含：
        - `itemId`、`itemName`
        - `draftContent`：直接使用评价者声明的草稿正文
        - `suggestWeight`、`suggestBonusCoeff`（若你们系统要求在草稿态同时输出“建议/校验后的取值”）
        - `weight`、`bonusCoeff`（如能读取当前值则输出；不可读则允许为空）
    - `failedItems`：失败评价项标注（仅在部分成功或需要解释失败时出现）
      - 包含：`itemId`、`errorCode`、`message`
    - `generationSummary`：成功/失败计数
- 草稿正文约束（你选的三点落地）
  - 不输出 `score` 与 `resultStatus`
  - 草稿正文不做 AI 生成：`draftContent` 必须来自评价者输入声明
  - 对不在关键岗映射范围内的评价项：按你的选择为 “A”（空字符串或不返回该项；本契约按“该项不进入 items”处理，必要时进入 failedItems 标注缺失声明）

#### 3.4 错误码结构
- 错误码前缀：`BP_EVAL_*`
- 建议错误码语义：
  - 参数错误（Bad Request）
  - 定位不到任务（Task Not Found）
  - 输入缺失（Input Empty / Missing Declaration）
  - 权限不足（Permission Denied）
  - 规则/约束冲突（Rule Conflict：如奖金系数不满足区间）
  - 依赖超时（Dependency Timeout）
  - 草稿装配失败（Generation Failed）

#### 3.5 失败返回格式
- 使用系统统一失败返回契约（固定键名集合为：`code/message/traceId/details`）

### 4. 前置条件
- 业务条件
  - 调用方具备：为该被评价人生成/提交草稿所需的输入权限与校验权限
  - 评价者输入包含关键岗原因、奖金系数原因以及草稿正文声明所需信息
- 依赖上下文
  - 能定位评价表、评价项清单、权重/奖金系数约束（若用于校验/填充 suggest 字段）
- 依赖外部数据
  - 评价表评价项信息（itemId/itemName 等）
  - 权重与奖金系数规则/区间约束（用于校验 bonusCoeff 或填充建议取值）

### 5. 执行逻辑说明
- 主流程
  1. 定位解析：由 `bpId/evalCycleId/evalTableId` 确定评价上下文
  2. 读取评价表并拿到评价项清单（用于校验评价者声明的 itemId 是否有效）
  3. 校验关键岗输入
     - keyPostSettings 的关键岗原因非空
     - keyPostBonusCoeffSettings 的奖金系数与原因非空
  4. 校验关键岗映射声明（由评价者输入直接声明）
     - 确认每个需要标记的评价项能匹配到对应关键岗与奖金系数原因
  5. 草稿装配（不做 AI 生成）
     - 对每个在评价者输入中声明了 `itemDraftDeclarations` 的评价项：
       - 直接写入 `draftContent`（草稿正文来自评价者输入）
       - 同步把关键岗原因/奖金系数原因用于“标记呈现”（标记呈现规则由系统模板或约定格式决定）
  6. 建议取值/约束校验（如果输出层要求 suggest 字段）
     - suggestWeight/suggestBonusCoeff 若需要：由系统规则/配置推导或读取；不走 AI 文本生成
  7. 输出结构化结果：items + failedItems（按是否允许部分成功）
- 是否调用多个 API：是（定位解析 + 评价项清单读取 + 约束/配置读取）
- 数据清洗/聚合/转换：是（主要是“校验/映射装配”，不含文本 AI 生成）
- 是否规则引擎判断：是（奖金系数区间/规则校验属于规则判断）
- 是否涉及缓存：可选（配置/规则类可缓存）

### 6. 所依赖的业务 API 清单
- 上下文解析：用于把定位标识解析到评价任务上下文
- 评价表与评价项读取：用于校验评价者声明的 itemId 有效性
- 约束/规则读取：用于验证奖金系数区间与获取权重/奖金系数建议所需配置
- （如需）建议值计算/取值接口：用于输出 `suggestWeight/suggestBonusCoeff` 与 `weight/bonusCoeff` 的可读结果
- 不依赖“草稿文本 AI 生成”类能力

### 7. 结果可信度与解释
- 输出是否需要附证据：否
- 是否返回来源字段：否
- 是否返回口径说明：否
- 是否支持追溯原始数据：由系统链路做即可；本 Skill 输出只负责结构与装配结果

### 8. 安全与权限
- 读/写：本 Skill 只负责生成返回结果与装配；落库写入由编排层/系统接口完成
- 是否涉及脱敏：不涉及额外脱敏（由系统统一策略处理）
- 是否记录审计日志：建议记录（requestId、userId、评价者输入摘要）
- 是否要求二次确认：否
- 是否要求审批令牌：由系统统一处理

### 9. 异常处理
- 参数错误：
  - keyPostReason/bonusCoeffReason 为空
  - 草稿正文 itemDraftDeclarations 缺失或内容为空
  - itemId 无法校验到评价项清单
- 数据缺失：
  - 某评价项没有评价者草稿声明：按“该项不返回 items”处理
- API 超时：依赖超时失败
- 权限不足：失败
- 业务规则冲突：
  - 奖金系数不满足区间约束：该项失败或整体失败（取决于 `failIfAnyItemCannotGenerate`）
- 部分成功如何返回（你前面选择 B 的策略）
  - `failIfAnyItemCannotGenerate=false`：返回已装配 items + failedItems 标注
  - `failIfAnyItemCannotGenerate=true`：任一项无法装配则整体失败

### 10. 测试与验收
- 单元测试样例
  - 评价者未提供任何 `itemDraftDeclarations`：整体失败或按部分成功策略进入 failedItems（看 failIfAnyItemCannotGenerate）
  - 关键岗映射声明缺失：对应评价项装配失败
  - 奖金系数超区间：装配失败并返回对应 errorCode
  - 草稿正文确认不会触发 AI 生成：draftContent 必须与评价者输入一致（验收点）
- 业务场景测试样例
  - 评价者配置关键岗原因与关键岗员工奖金系数原因：装配后的 draftContent 能正确体现“标记呈现”
  - 对未在关键岗映射范围内的评价项：不进入 items（按你选的 A）
- 回归测试要求
  - 输出不包含 `score` 与 `resultStatus`
  - draftContent 完全来自评价者输入声明
  - 不出现任何 `suggest*` 之外的新增字段（若你们有字段白名单约束）

---


**User**

Skill 2：BP.CORE.TrackEvalStatus（评价状态查询：只读展示系统当前状态）,按照上面格式，输出这个skill的规范文档，输入和输出内容精简，产品看得懂，不要代码

---

**Cursor**

## Skill 2：`BP.CORE.TrackEvalStatus`（评价状态查询：只读展示系统当前状态）

### 1. 基本信息
- Skill 名称：评价状态跟踪查询
- Skill 编码：`BP.CORE.TrackEvalStatus`
- 版本号：`1.0.0`
- 所属业务域：BP 评价
- 负责人：待你指定
- 适用 Agent 列表：BP 评价助手

### 2. Skill 定位
- 业务目的：给定“评价任务 + 被评价人”，查询并展示当前评价进度状态
- 解决什么动作：查询（只读）
- Skill 类型：查询类（Read-only）

### 3. 输入输出契约（自然语言，不输出代码）

#### 3.1 输入参数
- 评价任务定位（可选其一或组合，至少提供一项）
  - `bpId`（业务计划 ID）
  - `evalCycleId`（评价周期 ID）
  - `evalTableId`（评价表模板 ID）
- 被评价人
  - `userId`（必填）
- 请求标识
  - `requestId`（必填，用于链路追踪）
- 查询选项
  - `includeLagStatus`：是否包含“滞后展示字段”（可选，默认为不返回或为空）

**参数校验规则**
- `userId` 不能为空
- 评价任务定位三项至少有一项非空
- `includeLagStatus` 为布尔值

#### 3.2 输出结构
- 输出包含：
  - `requestId`
  - `users`：数组（本 Skill 通常对应单个被评价人，但按接口设计仍以数组输出）
  - 每个 `users[]` 包含：
    - `userId`
    - `status`（只读字段）：
      - `evalStatus`：评价状态枚举
      - `progressPercent`：进度百分比（如系统有）
      - `lastUpdateTime`：最后更新时间（如系统有）
      - `lagStatus`：滞后展示字段（仅当 `includeLagStatus=true` 且系统支持时返回）

**状态枚举（只读，不由 AI 推导）**
- `NOT_STARTED`：未开始
- `IN_PROGRESS`：进行中（已填写草稿）
- `SUBMITTED`：已提交（待审批）
- `APPROVED`：已审批
- `COMPLETED`：已完成（奖金已核算）

### 4. 前置条件
- 调用方权限：必须允许读取评价状态信息（评价者/评价者领导可读；被评价者不触发调用场景）
- 依赖上下文：
  - `bpId/evalCycleId/evalTableId` 用于定位评价任务
  - `userId` 用于定位被评价人
- 依赖外部数据：
  - 系统已记录的 `evalStatus/progressPercent/lastUpdateTime`（以及可选的 `lagStatus`）

### 5. 执行逻辑说明（只读）
- 解析定位信息（评价任务上下文 + 被评价人）
- 查询系统当前评价状态与进度
- 若 `includeLagStatus=true`：返回系统已有的 `lagStatus`；不做任何衍生判断
- 返回给产品用于展示

### 6. 所依赖的业务 API 清单（自然语言抽象）
- 评价上下文解析接口：根据 `bpId/evalCycleId/evalTableId` 确定评价任务
- 评价状态读取接口：读取当前 `evalStatus/progressPercent/lastUpdateTime`（可选 `lagStatus`）

### 7. 结果可信度与解释
- 不需要附证据
- 不返回口径说明/来源字段（只读返回系统已有数据）

### 8. 安全与权限
- 只读：不写库、不更新任何状态
- 脱敏：不在 Skill 内额外处理（由系统返回/展示策略控制）
- 审计日志：建议记录 `requestId/userId/traceId`
- 二次确认：不需要
- 审批令牌：由系统统一鉴权处理，本 Skill 不负责

### 9. 异常处理
- 参数错误：返回系统统一失败契约（`code/message/traceId/details`）
- 定位不到评价任务：失败
- 权限不足：失败
- 依赖超时：失败
- 部分成功：不适用（这是单人状态查询）

### 10. 测试与验收
- 单元测试样例
  - `userId` 为空：失败
  - 三个定位字段都为空：失败
  - `includeLagStatus=false`：输出不包含滞后字段或为空
- 业务场景测试样例
  - 对不同 `evalStatus` 枚举均能正确返回
  - 系统返回 `lagStatus` 时仅在 `includeLagStatus=true` 时展示
- 回归测试要求
  - 不计算、不生成衍生状态（只返回系统已有字段）


---



