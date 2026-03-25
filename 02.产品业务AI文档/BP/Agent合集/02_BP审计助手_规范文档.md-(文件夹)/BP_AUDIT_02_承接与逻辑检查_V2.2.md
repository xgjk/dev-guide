# BP承接与逻辑检查能力

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |

## 1. 基本信息
- Skill名称：BP承接与逻辑检查能力
- Skill编码：BP_AUDIT_02
- 版本号：V2.2
- 所属业务域：BP管理 / 审计
- 负责人：BP审计助手团队
- 适用 Agent 列表：`BP审计助手`

## 2. Skill 定位
- 业务目的：判断 BP 在上下级组织体系中的“承接关系是否成立”，并校验承接链路在语义与结构上是否闭环。
- 解决动作：
  - 向上承接检查（上级对象是否被当前目标承接）
  - 向下拆解承接检查（当前对象是否被下级目标承接）
  - 内部逻辑链检查（目标 → 成果 → 举措）
- 类型：分析类 Skill（只输出问题清单，不做拍板/不修改 BP）

## 3. 输入输出契约

### 3.1 输入参数清单
> 默认契约使用“层级+对象+承接证据”的方式，避免固定写死“只承接举措/只承接成果”。

#### 入参：必填
- `currentOrgLevel`（字符串枚举，必填）
  - 枚举值：`group`（集团）/ `center`（中心）/ `dept`（一级部门）/ `employee`（核心员工）
  - 用途：决定向上/向下检查的“对象粒度”（关键成果 vs 关键举措）。
- `currentBP`（对象，必填）
  - 含：当前 BP 的任务结构（至少可枚举目标→关键成果→关键举措的名称与结构）。
- `checkMode`（字符串枚举，必填）
  - 枚举值：`upward` / `downward` / `bidirectional`
  - 用途：决定执行向上/向下哪部分检查。
- `upstreamShouldAlignTasks`（对象数组，视 checkMode 与层级必填）
  - 定义：上级侧“按理应被承接”的任务集合（用于漏对齐差集）。
  - 当 `checkMode` 包含 upward 时通常需要。
  - 当层级按口径跳过向上检查时可为空。
- `upstreamActuallyAlignedTasks`（对象数组，视 checkMode 与层级必填）
  - 定义：当前组织“实际已向上对齐了哪些对象”（对应承接记录证据）。
  - 当 `checkMode` 包含 upward 时通常需要。
  - 当层级按口径跳过向上检查时可为空。

#### 入参：可选
- `upstreamBP`（对象，可选）
  - 用于补全上级节点的完整结构/描述文本（若调用方已在 `upstreamShouldAlignTasks/upstreamActuallyAlignedTasks` 中给足，则可不提供）。
- `downstreamBPs`（对象集合，可选）
  - 用于向下拆解承接检查。
  - 仅当 `checkMode` 包含 downward 时建议提供。
- `downstreamActuallyAlignedTargets`（对象数组，可选）
  - 定义：下级实际承接了当前哪些对象（用于承接正确性 + 断层判断）。
  - 仅当存在下级承接数据且需要进行向下检查时提供。
- `orgResponsibilityText`（字符串，可选）
  - 用途：解释“为何按理应承接”（用于漏对齐的合理性确认）。
- `currentBPDescriptionContext`（字符串，可选）
  - 用途：当语义承接仅凭命名无法判断时，提供补充上下文（尽量基于事实）。

### 3.2 参数类型与校验规则
#### 校验：currentOrgLevel
- 必须属于枚举集合：`group|center|dept|employee`
- 不合法：返回 `resultCode=0`，`errorCode=40001`（参数错误）。

#### 校验：checkMode
- 必须属于枚举集合：`upward|downward|bidirectional`
- 不合法：返回 `resultCode=0`，`errorCode=40001`

#### 校验：currentBP 任务结构
- `currentBP` 必须能枚举出至少一条结构链（目标→关键成果→关键举措），否则：
  - 返回 `resultCode=0`，`errorCode=40002`（数据缺失）。

#### 校验：向上检查所需数据
- 若 `checkMode` 包含 upward 且该层级按口径不跳过，但缺少 `upstreamShouldAlignTasks` 或 `upstreamActuallyAlignedTasks`：
  - 不返回硬失败，降级为 `resultCode=1` + issues 中输出 `dataMissing`（低优先级），并提示补齐对齐证据。

#### 校验：向下检查所需数据
- 若 `checkMode` 包含 downward 且该层级按口径需要向下检查，但缺少 `downstreamBPs` 或 `downstreamActuallyAlignedTargets`：
  - 降级为 issues 输出 `dataMissing`（低优先级），并跳过向下判定细项。

### 3.3 输出结构（标准化 JSON）
> 建议与 `BP_AUDIT_04` 的分级/去重策略对齐：每条问题稳定提供 `checkRule` 与 `severity`。

成功返回：
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "conclusion": "可审计",
    "summary": { "highCount": 0, "mediumCount": 0, "lowCount": 0 },
    "issues": [
      {
        "severity": "high|medium|low",
        "issueType": "upwardAlignment|downwardAlignment|internalLogic|dataMissing",
        "checkRule": "UP_01|UP_02|DOWN_01|DOWN_02|LOG_01|DATA_01",
        "locationPath": "目标『...』/关键成果『...』/关键举措『...』",
        "description": "问题描述（为什么不成立）",
        "evidence": "证据（引用：上级对象/当前对象/下级承接对象的名称与关键结构判断点）",
        "suggestion": "修复建议（怎么改）"
      }
    ]
  }
}
```

失败返回（resultCode=0）：
```json
{
  "resultCode": 0,
  "resultMsg": "参数错误或系统处理失败原因",
  "data": null,
  "error": { "errorCode": "40001", "detail": "..." }
}
```

### 3.4 错误码结构
- `40001`：参数错误（枚举/必填缺失/格式不正确）
- `40002`：数据缺失（currentBP 结构无法遍历）
- `50001`：API 或依赖服务超时（如调用方需要补全上/下级结构）
- `50002`：权限不足（调用方无读取权限）
- `50003`：业务规则冲突（层级与 checkMode 不可兼容）

## 4. 前置条件
- 调用前必须满足：
  - BP已创建且 `currentBP` 可枚举目标→关键成果→关键举措结构
  - 存在上下级关系（需要向上/向下检查时）
- 依赖哪些上下文：
  - `currentOrgLevel`：决定对象粒度与跳过规则
  - `checkMode`：决定执行方向
  - 向上：需要“应承接集合”和“实际承接集合”
  - 向下：需要“下级承接证据”
- 依赖权限：
  - 只读权限（不允许修改 BP）
- 外部数据：
  - 可选使用 Open API 补全上/下级任务结构（见第 6 节）

## 5. 执行逻辑说明

### 5.1 主要处理流程
1. 层级适用性判断（确定向上/向下对象粒度与是否跳过）
2. 向上承接检查（如 checkMode 包含 upward，且层级需要向上检查）
   - 承接正确性：必须结合“目标→关键成果(衡量标准)→关键举措(交付动作)”判断
   - 漏对齐检查：对比 `upstreamShouldAlignTasks` 与 `upstreamActuallyAlignedTasks` 差集
3. 向下拆解承接检查（如 checkMode 包含 downward）
   - 承接断层：当前对象是否被下级目标承接
   - 正确性：同样不能只看名称，需看下级目标结构是否支撑当前对象要求
4. 内部逻辑链检查（始终执行或按层级跳过颗粒度不适用项）
5. 去重与输出：按 `checkRule + locationPath` 去重，并统计高/中/低数量

### 5.2 对象粒度规则（关键口径）
#### 向上对齐对象
- `group`：向上跳过
- `center`：检查上级关键成果是否被当前目标承接
- `dept` / `employee`：检查上级关键举措是否被当前目标承接

#### 向下承接对象
- `group`：检查当前关键成果是否被中心目标承接
- 非 `group`：检查当前关键举措是否被下级目标承接

### 5.3 规则引擎判断（启发式 vs 必判）
- 必判（高严重）：断链/承接无法支撑上级核心要求
- 启发式（中/低）：可能漏对齐、承接支撑不足（证据链弱而非完全缺失）

## 6. 所依赖的业务 API 清单
> 该 Skill 可以不直接调用 API（取决于调用方是否已提供解析后的任务结构与承接证据）。若需要补全结构，可按顺序调用。

- `4.1 查询周期列表`
  - 用途：定位启用周期（若调用方需要从周期维度获取任务）
  - 调用顺序：1
  - 超时要求：30s（单次）
  - 降级策略：跳过周期补全，输出 `DATA_01` 低问题
- `4.2 获取分组树`
  - 用途：定位当前组织及上/下级分组
  - 调用顺序：2
  - 超时要求：30s
  - 降级策略：无法定位则输出 `DATA_01`
- `4.4 查询任务树`
  - 用途：获取当前/上/下级的目标→关键成果→关键举措简要结构
  - 调用顺序：3
  - 超时要求：30s
  - 降级策略：只做内部逻辑链检查 + 输出数据缺失问题
- `4.5 获取一组目标数据（含关键成果与举措）`
  - 用途：补全关键成果衡量口径、关键举措交付动作以支持语义承接判断
  - 调用顺序：4
  - 超时要求：30s
  - 降级策略：若补全失败，只输出低/中“证据不足”问题

## 7. 结果可信度与解释
- 输出是否需要附证据：是
  - `evidence` 必须至少包含：上级对象名称/当前对象名称/关键结构判断点（例如：关键成果衡量口径 + 举措交付动作是否能支撑）
- 是否返回来源字段：建议在 `evidence` 中体现“来自上级/来自当前/来自下级”的来源方向
- 是否返回口径说明：在 `description/suggestion` 中明确“为何不成立”和“如何修复”
- 是否支持追溯原始数据：建议提供 `locationPath` 的结构路径定位

## 8. 安全与权限
- 只读：只生成问题清单，不修改 BP 数据
- 是否涉及脱敏：输出仅使用名称与结构路径，不输出内部 ID
- 是否记录审计日志：由系统侧记录（文档层面无需实现，但需符合只读原则）
- 是否要求二次确认：不要求（仅审计输出）
- 是否要求审批令牌：不要求

## 9. 异常处理
- 参数错误（40001）
  - 直接失败返回 `resultCode=0`，`error.errorCode=40001`
- 数据缺失（40002 或 DATA_01）
  - 若 `currentBP` 无法遍历：失败返回 `40002`
  - 若仅缺承接证据：返回成功 `resultCode=1`，issues 中输出 `DATA_01`（low）
- API 超时（50001）
  - 降级策略：跳过补全上/下级细节，只做内部逻辑链检查，并输出 `DATA_01`
- 权限不足（50002）
  - 失败返回 `resultCode=0`
- 业务规则冲突（50003）
  - 例如：层级与 checkMode 不兼容导致对象粒度无法确定时
  - 返回 `resultCode=0` 或降级为 `dataMissing`（视系统策略）
- 部分成功如何返回
  - 允许：内部逻辑链检查 + 证据不足问题并存（`high` 为主缺陷）

## 10. 测试与验收

### 10.1 单元测试样例
1. `UP_01 向上承接未承接（高）`
   - `currentOrgLevel=center`：上级关键成果未被任何当前目标结构支撑 → high
2. `UP_02 向上承接挂名不支撑（高）`
   - 名称对齐但关键成果衡量口径与关键举措交付动作支撑不住上级核心要求 → high
3. `UP_L01 可能漏对齐（中/低）`
   - 应承接集合与实际对齐集合差集非空，结合 `orgResponsibilityText` → medium
4. `DOWN_01 向下拆解断层（高）`
   - `currentOrgLevel=group`：关键成果无下级目标承接证据 → high
   - 非group：关键举措无下级目标承接证据 → high
5. `DOWN_02 向下承接结构跑偏（高）`
   - 下级结构无法通过完整目标→成果→举措支撑当前对象要求 → high
6. `LOG_01 内部逻辑断链（高）`
   - 缺关键成果或缺关键举措 → high
7. `DATA_01 证据不足（低）`
   - 缺向上应承接/实际承接集合或缺向下承接证据 → low

### 10.2 业务场景测试样例
1. 个人BP（employee）+ upward
   - 校验：承接对象粒度为“上级关键举措”
2. 部门BP（dept）+ bidirectional
   - 校验：向上检查“关键举措”，向下检查“关键举措”
3. 中心BP（center）+ bidirectional
   - 校验：向上检查“关键成果”，向下检查“关键举措”
4. 集团BP（group）+ downward
   - 校验：向下检查“关键成果”

### 10.3 边界/异常场景
1. group + checkMode 包含 upward
   - 向上部分自动跳过，不输出“对象粒度错误”的问题
2. currentBP 结构缺失（不可遍历）
   - 返回 `resultCode=0`，`errorCode=40002`
3. 仅缺承接证据（可遍历但证据缺失）
   - resultCode=1 + `DATA_01`（low）

### 10.4 回归测试要求
- `checkRule` 必须稳定：便于 `BP_AUDIT_04` 去重与分级合并
- `locationPath` 必须可定位到结构节点：避免不可追溯问题

