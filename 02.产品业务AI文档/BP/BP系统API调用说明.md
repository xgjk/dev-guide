# BP 目标管理 Open API 调用说明

**配套文档**：[《BP 目标管理 Open API 接口定义》](./BP系统API说明.md)（数据模型 **一、1.4**、**二、2.1～2.23** 接口契约、**三、3.x** 公共类型、**四、错误码**）。

本文承担：**修订记录、能力概述、通用约定、接口索引、编排场景、注意事项与历史路径**；**不重复**各接口的请求/响应字段表（以《接口定义》为准）。

---

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建（原合并于《BP系统API说明》） | 成伟 |
| 1.1 | 2026-03-25 | 新增 2.13 获取分组完整 BP 的 Markdown | 曾文哲 |
| 1.2 | 2026-03-27 | 新增 2.14～2.15（根据目标/成果 ID 新增下级任务） | 刘会芳 |
| 1.3 | 2026-03-28 | 新增 2.16（获取关键岗位详情） | 刘会芳 |
| 1.4 | 2026-03-28 | 更新 2.16 奖金系数单位由「月」改为「%」 | 刘会芳 |
| 1.5 | 2026-03-29 | 废弃 2.16（单个/JSON），新增 2.17 批量关键岗位 Markdown | 曾文哲 |
| 1.6 | 2026-04-02 | 整合重设计约定：Simple/Full、规范命名与路径、2.18～2.20 轻量列表；附录历史路径 | 成伟 |
| 1.7 | 2026-04-02 | 校对：1.4.3～1.4.5 Full 不返回 `groupId`；2.14/2.15 关系描述；场景与注意事项用语 | 成伟 |
| 1.8 | 2026-04-02 | 响应参数引用约定；公共类型 **三、3.12～3.16**（当时曾记为 4.12～4.16） | 成伟 |
| 1.9 | 2026-04-02 | 《接口定义》公共数据结构小节与章号对齐为 **三、3.1～3.16**（曾记为 4.1～4.16） | 成伟 |
| 1.10 | 2026-04-02 | 接口小节与章号对齐（原 4.x 误用已改为 3.x，见当时单文件版） | 成伟 |
| 1.11 | 2026-04-02 | **拆分**：本《调用说明》与《接口定义》双文档；接口正文小节 **二、2.1～2.20**，公共类型 **三、3.1～3.16** | 成伟 |
| 1.12 | 2026-04-02 | 《接口定义》章内序号与章号对齐：**一、1.1～1.4.x**、**二、2.1～2.20**、**三、3.1～3.16**；同步《调用说明》与 Agent 引用 | 成伟 |
| 1.13 | 2026-04-03 | 2.8 汇报接口精简（仅返回 `bizId` + `typeDesc`，去除标题/正文/contentType/写汇报人）；新增 2.21 获取任务子树骨架（`listTaskChildren`） | 曾文哲 |
| 1.14 | 2026-04-07 | 2.8 分页查询所有汇报新增 `businessTimeStart/End`、`relationTimeStart/End` 四个时间范围过滤参数 | 曾文哲 |
| 1.15 | 2026-04-07 | 新增 2.22 保存月度汇报（`saveMonthlyReport`）、2.23 根据分组和月份获取月度汇报（`getMonthlyReportByMonth`）；公共类型新增 **三、3.18 MonthlyReportSimpleVO** | 曾文哲 |

> **关于小节号**：版本 **1.10 及以前**的变更摘要若仍写「5.x」「第六章」或「3.x/4.x 接口与类型」，指当时**单文件**或旧版双文档编号；与当前《接口定义》对照时，接口为 **二、2.1～2.23**，公共类型为 **三、3.1～3.18**，字段规格为 **一、1.4.x**。

---

## 一、概述

BP（Business Plan）目标管理系统对外开放 HTTP 接口后，调用方可实现下列能力（与《接口定义》**二、2.x** 一一对应）：

1. **listPeriods** — 查询周期，获取 `periodId`
2. **listGroups** — 按周期拉分组树（仅分组，不含任务）
3. **批量查询员工个人分组 ID** — 员工 ID → 个人 `groupId`
4. **getSimpleTree** — 按分组拉目标 → 关键成果 → 关键举措**简要树**
5. **getGoalDetail** — 按目标 ID 拉 Full 目标（含 KR、举措）
6. **getKeyResultDetail** — 按关键成果 ID 拉 Full
7. **getActionDetail** — 按关键举措 ID 拉 Full
8. **listTaskReports** — 按任务 ID 分页查汇报（任务id指目标或者关键成果或者举措id,只获取本任务关联的汇报信息，不含下级任务。仅返回汇报 ID 和类型，不含正文/标题/附件/回复。支持按业务时间范围和关联时间范围过滤）
9. **发送 AI 延期提醒汇报** — 写操作
10. **listDelayReports** — 查询延期提醒历史
11. **按名称模糊搜索任务**
12. **按名称模糊搜索分组**
13. **getGroupMarkdown** — 分组维度的 Markdown 全文（含目标、关键成果和举措，适合模型通读）
14. **根据目标 ID 新增关键成果** — 写操作
15. **根据成果 ID 新增关键举措** — 写操作
16. ~~**获取关键岗位详情（JSON）**~~ — 已废弃，请用 **2.17**
17. **批量获取关键岗位详情（Markdown）**
18. **listGoals** — 目标 Simple 列表
19. **listKeyResults** — 关键成果 Simple 列表
20. **listActions** — 关键举措 Simple 列表
21. **listTaskChildren** — 任务子树骨架（仅 id + 名称，用于 AI 了解 BP 层级结构）
22. **saveMonthlyReport** — 保存月度汇报（写操作，基于分组+月份唯一键 upsert）
23. **getMonthlyReportByMonth** — 根据分组和月份获取月度汇报

字段级 **Simple / Full** 约定见《接口定义》**一、1.4**。历史 HTTP 路径见本文 **九、附录**。

---

## 二、给 AI / Agent 的阅读顺序

1. **本文「三、通用说明」**：`Result<T>`、`appKey`、环境与 URL 形态。
2. **本文「四、接口清单」**：按任务快速定位小节号与路径。
3. **《接口定义》一、1.4**：所有响应字段的**唯一权威**（含 `groupId` 是否在详情中出现等）。
4. **《接口定义》二、2.1～2.23**：具体方法的参数表、示例与 `data` 类型声明。
5. **《接口定义》三、3.1～3.18**：嵌套 VO 的补充说明（与 **一、1.4** 互为引用）。
6. **《接口定义》四、错误码**：失败时 `resultCode` / `resultMsg`。
7. 需要**调用链**时读本文 **七、关键业务流程**；需要**省 Token / 通读策略**时读本文 **六、推荐拉取路径**。

**写操作（有副作用，默认只读场景勿调用）**：**2.9** 发送延期提醒、**2.14** 新增关键成果、**2.15** 新增关键举措、**2.22** 保存月度汇报。

---

## 三、关键词与别名

| 用语 | 同义 / 英文路径片段 |
|------|---------------------|
| 关键成果 | KR、`keyResult`、`/keyResult/` |
| 关键举措 | Action、`action`、`/action/` |
| 目标 | Goal、`goal`、`/goal/` |
| 分组 | Group、`group`、`groupId`（**不是**员工 ID） |
| `receiverEmpId`（2.9） | **员工 ID**，勿与 `groupId` 混淆 |
| `TaskTreeVO`（2.4） | 简要树节点，**不等于** `GoalFullVO` / Simple 列表元素 |
| `getGroupMarkdown`（2.13） | 单请求拉分组级 Markdown，与超大 JSON 树二选一或互补 |

---

## 四、通用说明

### 4.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

### 4.2 环境信息

| 环境     | 域名                                        |
| -------- | ------------------------------------------- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` |

### 4.3 公共请求头

| Header   | 说明                       | 是否必填 |
| -------- | -------------------------- | -------- |
| `appKey` | 应用密钥，请联系管理员获取 | 是       |

**兼容性**：某些场景下，header有access-token但是没有appKey,系统也能兼容。

### 4.4 通用响应结构

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

## 五、接口清单（索引）

下表为 **全部** 开放接口与《接口定义》小节号对照。**规范命名**列留空表示暂无统一规划英文名（以路径为准）。

> **与本节「附：规划命名子集」的关系**：规划表（G1～R2）仅覆盖轻量列表、详情、Markdown 与汇报类接口；**上方主表才是全集**，避免 Agent 误以为「只有规划表里的接口」。

| 小节 | 规范命名（若有） | 方法 | 现用路径 | 读写 | 摘要 |
|------|------------------|------|----------|------|------|
| 2.1 | listPeriods | GET | `/bp/period/list` | 读 | 周期列表 |
| 2.2 | listGroups | GET | `/bp/group/list` | 读 | 分组树 |
| 2.3 | — | POST | `/bp/group/getPersonalGroupIds` | 读 | 员工 → 个人分组 ID |
| 2.4 | —（实现名 getSimpleTree） | GET | `/bp/task/v2/getSimpleTree` | 读 | 任务简要树 |
| 2.5 | getGoalDetail | GET | `/bp/goal/{goalId}/detail` | 读 | Full 目标 |
| 2.6 | getKeyResultDetail | GET | `/bp/keyResult/{keyResultId}/detail` | 读 | Full 关键成果 |
| 2.7 | getActionDetail | GET | `/bp/action/{actionId}/detail` | 读 | Full 关键举措 |
| 2.8 | listTaskReports | POST | `/bp/task/relation/pageAllReports` | 读 | 任务关联汇报分页 |
| 2.9 | — | POST | `/bp/delayReport/send` | **写** | AI 延期提醒 |
| 2.10 | listDelayReports | GET | `/bp/delayReport/list` | 读 | 延期提醒历史 |
| 2.11 | — | GET | `/bp/task/v2/searchByName` | 读 | 按名称搜任务 |
| 2.12 | — | GET | `/bp/group/searchByName` | 读 | 按名称搜分组 |
| 2.13 | getGroupMarkdown | GET | `/bp/group/markdown` | 读 | 分组 BP Markdown |
| 2.14 | — | POST | `/bp/task/v2/addKeyResult` | **写** | 新增关键成果 |
| 2.15 | — | POST | `/bp/task/v2/addAction` | **写** | 新增关键举措 |
| 2.16 | —（已废弃） | GET | `/bp/task/v2/getKeyPositionDetail` | 读 | 勿用，改 2.17 |
| 2.17 | — | POST | `/bp/group/batchGetKeyPositionMarkdown` | 读 | 关键岗位 Markdown 批量 |
| 2.18 | listGoals | GET | `/bp/goal/list` | 读 | 目标 Simple 列表 |
| 2.19 | listKeyResults | GET | `/bp/keyResult/list` | 读 | 关键成果 Simple 列表 |
| 2.20 | listActions | GET | `/bp/action/list` | 读 | 关键举措 Simple 列表 |
| 2.21 | listTaskChildren | GET | `/bp/task/children` | 读 | 任务子树骨架（仅 id + 名称） |
| 2.22 | saveMonthlyReport | POST | `/bp/monthly/report/save` | **写** | 保存月度汇报（upsert） |
| 2.23 | getMonthlyReportByMonth | GET | `/bp/monthly/report/getByMonth` | 读 | 根据分组+月份获取月度汇报 |

---

## 六、推荐拉取路径（Agent）

**路径 A（渐进式、省 Token）**：**2.2** → **2.18**（看 `krCount` / `actionCount`）→ 若规模可控则 **2.5**，否则经 **2.19** / **2.20** 再按需 **2.6** / **2.7**。

**路径 B（单请求拿分组正文）**：**2.13** `getGroupMarkdown`，适合模型通读、归纳，避免超大 JSON。

**路径 C（需要树形索引）**：**2.4** `TaskTreeVO` 递归树，与 Simple 列表互补；详情仍以 **2.5～2.7** 为准。

---

## 七、关键业务流程说明

以下说明接口之间的**推荐调用顺序**与参数传递；契约细节见《接口定义》**二、2.x**。

### 场景一：查看某个部门的 BP 分组树

> 需求：启用周期下，某组织节点及其下个人分组的结构。

1. **2.1**（`GET /bp/period/list`）→ 取 `status = 1` 的 `periodId`
2. **2.2**（`GET /bp/group/list?periodId={periodId}`）→ 分组树
3. `type = "org"` 为组织，`type = "personal"` 为个人，按 `children` 遍历

### 场景二：查看某个员工的完整目标树

> 需求：已知员工 ID，看其个人 BP 结构。

1. **2.3**（`POST /bp/group/getPersonalGroupIds`）→ `groupId`
2. **任选**：**2.4** 任务树，或 **2.18**（可再接 **2.19 / 2.20** 或 **2.5 / 2.6 / 2.7**）
3. 若用 **2.4**：`目标` → `关键成果` → `关键举措`，`children` 递归

### 场景三：获取某个目标的完整详情

1. **2.5**（`GET /bp/goal/{goalId}/detail`）
2. 可选 **2.6** / **2.7** 按 ID 再下钻

### 场景四：查看某个任务关联的汇报

1. 由场景二或三取得任务 ID
2. **2.8**（`POST /bp/task/relation/pageAllReports`）

### 场景五：延期提醒与历史

1. **2.9**（`POST /bp/delayReport/send`），`receiverEmpId` 为员工 ID
2. **2.10**（`GET /bp/delayReport/list?receiverEmpId=...`）

### 场景六：遍历全公司员工 BP

1. **2.1** → **2.2**（如 `onlyPersonal = true`）
2. 对每个个人分组 **2.4** 或 **2.18**（再按需 **2.5**）

### 场景七：从周期下钻到关键举措详情

1. **2.1** → **2.2** → 取个人 `groupId`
2. **2.4** → 取目标 `id` → **2.5**（已含 `keyResults[].actions[].id`）→ **2.7**

> **2.5** 已返回下属举措 ID 时，不必仅为取举措 ID 再调 **2.6**。

---

## 八、注意事项

1. **ID 精度**：Long 型雪花 ID 在 JS 等环境须按**字符串**处理，**禁止** `parseInt` / `Number()` 整段当数值解析。
2. **分组 ID 与员工 ID**：**2.3** 入参为员工 ID、出参为分组 ID；**2.9** 的 `receiverEmpId` 为员工 ID。
3. **2.4 与 2.18～2.20**：树 vs 扁平 Simple 列表，按场景选用。
4. **2.4 与 2.5～2.7**：`TaskTreeVO` 为简要导航；详情字段以《接口定义》**一、1.4.3～1.4.5** Full 列与 **三、3.2** 为准，勿按已废弃的 `BaseTaskVO` 继承理解。
5. **周期**：**2.2** 需 `periodId`，建议选用启用周期。
6. **分组类型**：`org` / `personal` 含义见场景一。
7. **2.8 排序与时间过滤**：支持 `relation_time` / `business_time` 排序，默认关联时间降序。支持 `businessTimeStart/End` 和 `relationTimeStart/End` 按时间范围过滤：业务时间过滤对手动汇报和 AI 汇报均生效（AI 汇报按 `create_time` 过滤）；关联时间过滤仅对手动汇报生效（AI 汇报无关联时间）。

---

