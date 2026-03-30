# 工作协同 Open API 接口文档

## 修订记录

| 版本  | 日期       | 变更摘要 | 变更人 |
|-----| ---------- | -------- | ------ |
| 1.0 | 2026-03-25 | 初版创建 | 成伟   |
| 1.1 | 2026-03-25 | 新增获取指定用户分组接口 | 付光伟   |
| 1.2 | 2026-03-26 | 新增个人分组创建与成员管理接口、重构文档结构及序号 | 付光伟 |
| 1.3 | 2026-03-26 | 在获取分组及管理成员接口中增加按姓名搜索员工 ID 的说明 | 付光伟 |
| 1.4 | 2026-03-28 | 新增「新增草稿相关接口，5.23-5.27」 | 成伟   |
| 1.5 | 2026-03-30 | 补充「将草稿转为正式汇报发出」接口的内部路由实现与文档说明状态同步 | 付光伟 |
| 1.6 | 2026-03-30 | 修复接口序号错位，并补充汇报/草稿通用参数说明及接口交叉引用 | 付光伟 |




为便于人与 AI 追溯变更历史，所有修订记录必须使用统一格式的四列表格，包含以下字段：**版本**、**日期**、**变更摘要**、**变更人**。

**核心规则：**
- 每次内容变更**必须在表格末尾追加新行**，不得修改、覆盖或删除任何历史行。
- 行级差异以 Git 记录为准，无需在表格中体现具体代码差异。


## 一、概述

**基础服务接口：**
1. **按姓名搜索全部员工(带外部联系人)** — 模糊查询员工姓名以获取 `empId`。
2. **上传本地文件** — 上传二进制文件并获取 `fileId` 用于发送附件。
3. **获取指定用户的所有分组及成员** — 获取指定用户的分组及成员，支持按成员过滤。
4. **快捷创建或更新个人分组** — 支持快速新建或对已有分组更名。
5. **增量管理个人分组成员** — 对个人分组进行加人/减人的批量操作。

**工作协同服务接口：**

1. **发送汇报** — 创建并提交一条汇报记录（可关联任务/事项，可指定接收人/抄送人/多级节点）。
2. **汇报回复** — 对指定汇报进行回复（可带附件）。
3. **收件箱分页查询** — 分页获取当前用户收件箱汇报列表（支持筛选条件）。
4. **待处理列表分页查询** — 分页获取当前用户待办列表（任务/签批/指引/反馈等）。
5. **获取汇报内容** — 获取指定汇报正文及回复列表。
6. **获取事项列表** — 查询最近处理过的事项（用于发起汇报选事项）。
7. **根据事项 ID 列表获取事项信息** — 批量查询事项简易信息。
8. **获取待办及未读汇报列表（新的待办和汇报）** — 插件场景：一次获取最新待办 + 未读汇报聚合。
9. **获取最新待办列表** — 插件场景：分页获取最新待办列表。
10. **获取未读汇报列表** — 插件场景：分页获取未读汇报列表。
11. **工作任务列表查询** — 分页查询工作任务列表（支持按状态/关键词/标签等筛选）。
12. **获取用户创建的反馈类型待办列表** — 查询某员工（默认登录用户）创建的反馈待办。
13. **任务简易信息 VO** — 获取任务简易信息及其关联汇报简易列表。
14. **发件箱** — 分页获取当前用户发件箱汇报列表（支持筛选条件）。
15. **分页获取当前用户的决策/建议/反馈待办列表** — 汇报待办列表（决策/建议/反馈）。
16. **分页获取当前用户的未读汇报列表** — 汇报未读列表。
17. **判断员工对指定汇报是否已读** — 根据汇报 ID 与员工 ID 判断已读状态。
18. **完成待办（建议/决策）** — 对指定待办提交建议/决策内容（决策需传同意/不同意）。
19. **汇报内容 AI 问答（流式返回）** — 对指定汇报集合进行 AI SSE 问答/编辑。
20. **创建工作任务** — 通过 OpenAPI 创建高级工作任务，并分配汇报人员和其他干系人（责任人/协办人等）。
21. **获取我的新消息列表** — 列表获取当前用户的新读消息列表。
22. **阅读汇报（清除未读/新消息）** — 标记汇报为已读并清除相关新消息通知。
23. **新增或更新汇报草稿** — 保存汇报草稿（**更新必须传汇报 `id`**，且为**全量更新**，缺省字段会清空原草稿中对应数据；正式发送请用发送汇报接口）。
24. **草稿箱分页查询** — 分页获取当前用户的草稿箱列表。
25. **草稿汇报详情** — 根据汇报 ID 获取草稿态汇报详情（正文、接收人/抄送、多级节点、附件等）。
26. **删除草稿** — 按草稿 ID 删除草稿箱中的一条草稿。
27. **将草稿转为正式汇报发出** — 将指定的草稿转为正式发布状态。



---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

本文档中所有接口地址均为 **相对路径**（如 `/work-report/report/record/inbox`），需与上面的 `https://{域名}/open-api` 拼接后访问。

### 2.2 环境信息

| 环境     | 域名/Base URL                               |
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

| 字段         | 类型    | 说明                                            |
| ------------ | ------- | ----------------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，其他值表示失败        |
| `resultMsg`  | String  | 提示信息，成功时通常为 `null`，失败时为错误描述 |
| `data`       | T       | 业务数据，失败时通常为 `null`                   |

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

3. 接收人通过系统内查看收件箱：调用 **5.3 收件箱分页查询**（`POST /work-report/report/record/inbox`），按时间/类型等筛选获取列表。
4. 需要查看具体正文与回复列表时，调用 **5.5 获取汇报内容**（`GET /work-report/report/info`），传入 `reportId`。
5. 对汇报进行讨论回复时，调用 **5.2 汇报回复**（`POST /work-report/report/record/reply`），传入 `reportRecordId` 与 `contentHtml`（可带附件）。

### 场景二：处理决策/建议/反馈待办

> 需求：获取当前用户需要处理的待办，并完成待办（建议/决策）。

1. 调用 **5.15 分页获取决策/建议/反馈待办列表**（`POST /work-report/reportInfoOpenQuery/todoList`）获取待办列表项（含 `todoId`、`todoType` 等）。
2. 查看待办详情对象（AI 摘要/进展/是否需要当前处理人操作）在列表项的 `detail` 字段中（见 **6.10 ReportTodoDetailVO**）。
3. 完成待办时，调用 **5.18 完成待办（建议/决策）**（`POST /work-report/open-platform/todo/completeTodo`），传入 `todoId` 与 `content`；当 `todoType` 为决策类时需额外传 `operate=agree/disagree`。

---

## 四、基础服务接口

### 4.1 按姓名搜索全部员工(带外部联系人)

按姓名模糊搜索全部员工，包含内部员工与外部联系人；用于将“姓名”转换为工作协同接口所需的 `empId`。

**基本信息**

| 项目     | 说明                          |
| -------- | ----------------------------- |
| 接口地址 | `/cwork-user/searchEmpByName` |
| 请求方式 | `GET`                         |

**请求参数**

| 参数名      | 类型   | 必填 | 说明                           |
| ----------- | ------ | ---- | ------------------------------ |
| `searchKey` | String | 是   | 搜索关键词：支持按姓名模糊搜索 |

**响应参数**

`data` 类型为 `SearchAddressbookVO`，典型结构如下：

- `inside.empList[]`：内部员工列表（常用字段：`id` 员工 ID、`personId` 人员 ID、`name` 姓名、`title` 职务、`mainDept` 主部门等）
- `outside`：外部联系人列表

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/cwork-user/searchEmpByName?searchKey=%E5%BC%A0%E4%B8%89' \
  -H 'appKey: {appKey}'
```

**数据流向**

- 返回的 `inside.empList[].id` 可直接作为工作协同接口中 `reportLevelList[].levelUserList[].empId` 的取值。


### 4.2 上传本地文件

上传本地文件到协同平台文件服务器，返回文件资源 ID（`fileId`）。该 ID 在发送汇报接口 `fileVOList` 中作为 `fileId` 传入（此时 `type` 需设为 `file`）。

**基本信息**

| 项目         | 说明                          |
| ------------ | ----------------------------- |
| 接口地址     | `/cwork-file/uploadWholeFile` |
| 请求方式     | `POST`                        |
| Content-Type | `multipart/form-data`         |

**请求参数**

- **请求体 (Body)**

| 参数名 | 类型          | 必填 | 说明         |
| ------ | ------------- | ---- | ------------ |
| `file` | binary (File) | 是   | 要上传的文件 |

**响应参数**

`data` 类型为 `Long`，代表**文件资源 ID**。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/cwork-file/uploadWholeFile' \
  -H 'appKey: {appKey}' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/file.png'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": 2036325013120483329
}
```

---

### 4.3 获取指定用户的所有分组及成员

获取指定用户（及其实权覆盖的）所有分组以及分组成员简要信息。支持通过 `checkEmpId` 过滤仅包含该特定成员的分组列表。

> **说明**：若你只有“姓名”而非 `empId`（员工 ID），先调用 **4.1 按姓名搜索全部员工(带外部联系人)**（`GET /cwork-user/searchEmpByName`）获取员工列表。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/cwork-user/group/queryTargetUserGroups` |
| 请求方式     | `POST`                              |
| Content-Type | `application/json`                  |

**请求参数**

| 参数名        | 类型 | 必填 | 说明                                                                                              |
| ------------- | ---- | ---- | ------------------------------------------------------------------------------------------------- |
| `checkEmpId`  | Long | 否   | 校验是否在分组中的用户 ID。如果传入，则只返回包含该员工的分组列表（常用于查询 B 是否在 A 的分组中）。 |

**响应参数**

`data` 类型为 `List<TargetUserGroupVO>`（结构见 **6.25 TargetUserGroupVO**）。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/cwork-user/group/queryTargetUserGroups' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "checkEmpId": 1512393035869810001
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": [
    {
      "groupId": 123456789,
      "groupName": "协同开发组",
      "ownType": 1,
      "members": [
        {
          "id": 1512393035869810690,
          "name": "张三",
          "title": "高级架构师"
        },
        {
          "id": 1512393035869810001,
          "name": "李四",
          "title": "资深开发工程师"
        }
      ]
    }
  ]
}
```

---

### 4.4 快捷创建或更新个人分组

用于快速创建一个新的个人分组，或对已存在的个人分组进行重命名。会自动归类到当前用户的“默认个人类别”中。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/cwork-user/group/saveOrUpdatePersonalGroup` |
| 请求方式     | `POST`                              |
| Content-Type | `application/json`                  |

**请求参数**

| 参数名 | 类型   | 必填 | 说明                                 |
| ------ | ------ | ---- | ------------------------------------ |
| `id`   | Long   | 否   | 分组 ID。不传则为新增；传则为更名。 |
| `name` | String | 是   | 分组名称。                           |

**响应参数**

`data` 类型为 `Long`，返回操作成功后的分组 ID。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/cwork-user/group/saveOrUpdatePersonalGroup' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "name": "新项目协同组"
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": 1512393035869810691
}
```

---

### 4.5 增量管理个人分组成员

对指定分组的人员进行增量添加或移除。支持在单次请求中同时执行加人和减人操作。

> **说明**：若你只有“姓名”而非 `empId`（员工 ID），先调用 **4.1 按姓名搜索全部员工(带外部联系人)**（`GET /cwork-user/searchEmpByName`）获取员工列表。

**基本信息**

| 项目         |说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/cwork-user/group/manageGroupMembers` |
| 请求方式     | `POST`                              |
| Content-Type | `application/json`                  |

**请求参数**

| 参数名         | 类型         | 必填 | 说明           |
| -------------- | ------------ | ---- | -------------- |
| `groupId`      | Long         | 是   | 分组 ID。      |
| `addEmpIds`    | List\<Long\> | 否   | 待加入员工 ID 列表。 |
| `removeEmpIds` | List\<Long\> | 否   | 待移除员工 ID 列表。 |

**响应参数**

`data` 类型为 `Boolean`，成功返回 `true`。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/cwork-user/group/manageGroupMembers' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "groupId": 123456789,
    "addEmpIds": [1512393035869810690],
    "removeEmpIds": [1512393035869810001]
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": true
}
```


---

## 五、工作协同服务接口

### 5.1 发送汇报

用于创建并提交一条汇报记录，支持关联任务/事项、接收人/抄送人、多级节点（指引/签批/决策/建议链路）。

> **业务流程说明**：关于如何按层级/分组指定接收人以及如何上传并关联附件，请阅读 **[场景一：发送汇报 或 新增/更新草稿 通用参数说明](#场景一发送汇报-或-新增更新草稿-通用参数说明)**。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/work-report/report/record/submit` |
| 请求方式     | `POST`                              |
| Content-Type | `application/json`                  |

**请求参数**

请求体为 JSON，字段如下（见 `SubmitReportParam`）：

| 参数名            | 类型                    | 必填 | 说明                                                                                                                |
| ----------------- | ----------------------- | ---- | ------------------------------------------------------------------------------------------------------------------- |
| `id`          | Long                    | 否   | 汇报的id，只用于将草稿状态的汇报发出的场景，非草稿的汇报不要传此参数                                                                                                         |
| `planId`          | Long                    | 否   | 工作任务 id                                                                                                         |
| `templateId`      | Long                    | 否   | 事项 id                                                                                                             |
| `typeId`          | Long                    | 否   | 业务类型 id，默认 `9999`（代表其他汇报）                                                                            |
| `main`            | String                  | 是   | 汇报标题                                                                                                            |
| `grade`           | String                  | 否   | 优先级：一般/紧急，默认“一般”                                                                                       |
| `privacyLevel`    | String                  | 否   | 密级：非涉密/涉密（涉密下载文件需要申请），默认“非涉密”                                                             |
| `contentType`     | String                  | 否   | 正文类型：`html`/`markdown`，默认 `html`                                                                            |
| `contentHtml`     | String                  | 是   | 汇报内容（富文本/字符串）                                                                                           |
| `acceptEmpIdList` | List\<Long>             | 否   | 接收人员 id 列表；仅在 `reportLevelList` 为空时作为兜底：系统会用该列表自动生成 1 级“read 接收人”节点               |
| `copyEmpIdList`   | List\<Long>             | 否   | 抄送人员 id 列表                                                                                                    |
| `reportLevelList` | List\<ReportLevelParam> | 否   | 多级用户列表（read-传阅、suggest-建议、decide-决策等节点）；**接收人以该字段为准**；结构见 **6.1 ReportLevelParam** |
| `fileVOList`      | List\<OpenPlatformFileVO> | 否   | 关联附件列表；结构见 **6.24 OpenPlatformFileVO** |

> 注意：服务端会将 `contentHtml` 去除 HTML 标签生成 `content`（纯文本）后提交；调用方无需传 `content`。

**响应参数**

`data` 类型为 `BaseInfo`（主要字段是主键 id）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": 1234567890L
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/report/record/submit' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "main": "本周工作进展",
    "contentHtml": "<p>已完成接口联调</p>",
    "contentType": "html",
    "reportLevelList": [
      {
        "level": 1,
        "levelUserList": [
          {
            "empId": 10001
          },
          {
            "empId": 10002
          }
        ],
        "nodeName": "接收人",
        "type": "read"
      }
    ],
    "copyEmpIdList": [10003],
    "fileVOList": [
      {
        "fileId": "2036325013120483329",
        "name": "产品需求文档.md",
        "type": "file",
        "fsize": 120834
      },
      {
        "fileId": "",
        "name": "百度搜索",
        "type": "url",
        "url": "https://www.baidu.com"
      }
    ]
  }'
```

**数据流向**

- 返回 `data.id`（若平台返回）可用于后续通过 **5.5 获取汇报内容** 查询详情（入参 `reportId`）。

---

### 5.2 汇报回复

对指定汇报进行回复，可携带附件列表。

**基本信息**

| 项目         | 说明                               |
| ------------ | ---------------------------------- |
| 接口地址     | `/work-report/report/record/reply` |
| 请求方式     | `POST`                             |
| Content-Type | `application/json`                 |

**请求参数**

请求体为 JSON，字段如下（见 `ReportReplyInnerParam`）：

| 参数名           | 类型                | 必填 | 说明                                                        |
| ---------------- | ------------------- | ---- | ----------------------------------------------------------- |
| `reportRecordId` | String              | 是   | 工作汇报 id                                                 |
| `isMedia`        | Integer             | 否   | 是否带附件：0-没有（默认）、1-有                            |
| `mediaVOList`    | List\<ReportFileVO> | 否   | 附件集合，结构见 **6.2 ReportReplyInnerParam.ReportFileVO** |
| `contentHtml`    | String              | 是   | 回复内容                                                    |
| `sendMsg`        | Boolean             | 否   | 是否发送通知到填写汇报人，默认 `true`                       |
| `addEmpIdList`   | List\<String>       | 否   | 被 @ 的员工 id 集合，会添加到转发到人列表                   |

**响应参数**

`data` 类型为 `Long`，表示回复主键 ID。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": 987654321
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/report/record/reply' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "reportRecordId": "1234567890",
    "contentHtml": "已收到，我会在今天下班前给出方案",
    "isMedia": 0
  }'
```

---

### 5.3 收件箱分页查询

分页查询当前用户收件箱汇报列表。

**基本信息**

| 项目         | 说明                               |
| ------------ | ---------------------------------- |
| 接口地址     | `/work-report/report/record/inbox` |
| 请求方式     | `POST`                             |
| Content-Type | `application/json`                 |

**请求参数**

请求体为 JSON，字段如下（见 `SearchReportRecordParam`，继承 `SearchReportRecordBaseParam`）：

| 参数名                 | 类型        | 必填 | 说明                                                                    |
| ---------------------- | ----------- | ---- | ----------------------------------------------------------------------- |
| `pageSize`             | Integer     | 是   | 每页显示个数                                                            |
| `pageIndex`            | Integer     | 否   | 从 1 开始、页数                                                         |
| `reportRecordType`     | Integer     | 否   | 工作汇报类型：1-工作交流、2-工作指引、3-文件签批、4-AI 汇报、5-工作汇报 |
| `type`                 | String      | 否   | 业务类型                                                                |
| `planId`               | Long        | 否   | 任务 id                                                                 |
| `grade`                | String      | 否   | 优先等级：一般/紧急                                                     |
| `empIdList`            | List\<Long> | 否   | 汇报人 id 列表（多选）                                                  |
| `beginTime`            | Long        | 否   | 汇报时间-开始时间（毫秒）                                               |
| `endTime`              | Long        | 否   | 汇报时间-结束时间（毫秒）                                               |
| `templateId`           | Long        | 否   | 事项 id                                                                 |
| `templateIdList`       | List\<Long> | 否   | 具体签批事项（叶子节点）id 列表，优先级高于 templateId                  |
| `classificationIdList` | List\<Long> | 否   | 汇报分类 id 列表                                                        |
| `labelId`              | Long        | 否   | 标签 id（单选）                                                         |
| `source`               | String      | 否   | 来源：detail-详情、common-通用筛选器                                    |
| `orderColumn`          | String      | 否   | 排序：createTime-汇报时间、lastReplyTime-回复时间、receiveTime-收件时间 |
| `readStatus`           | Integer     | 否   | 是否已读：0-未读、1-已读、null-全部                                     |
| `laterRead`            | Boolean     | 否   | 是否稍后阅读                                                            |
| `mark`                 | Boolean     | 否   | 是否星标                                                                |
| `leadEmpId`            | Long        | 否   | 协办领导 id                                                             |

**响应参数**

`data` 类型为 `PageInfo<ReportRecordPageVO>`，结构如下：

- 分页结构见 **6.3 PageInfo**
- 列表元素结构见 **6.4 ReportRecordPageVO**

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": 1,
    "list": [
      {
        "id": 1234567890,
        "reportRecordType": 5,
        "type": "其他",
        "typeId": 9999,
        "main": "本周工作进展",
        "content": "已完成接口联调",
        "grade": "一般",
        "hasNewReply": false,
        "sendEmpId": 10001,
        "laterRead": false,
        "mark": false,
        "myStatus": 0,
        "replyCount": 0,
        "fileCount": 0,
        "userStatus": null,
        "reportEventVO": null
      }
    ],
    "pageNum": 1,
    "pageSize": 20,
    "size": 1
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/report/record/inbox' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "pageIndex": 1,
    "pageSize": 20,
    "readStatus": 0
  }'
```

---

### 5.4 待处理列表分页查询

分页查询当前用户待办列表（任务/签批/指引/反馈等）。

**基本信息**

| 项目         | 说明                             |
| ------------ | -------------------------------- |
| 接口地址     | `/work-report/todoTask/todoList` |
| 请求方式     | `POST`                           |
| Content-Type | `application/json`               |

**请求参数**

请求体为 JSON，字段如下（见 `TodoTaskListParam`，继承 `PageParam`）：

| 参数名            | 类型    | 必填 | 说明                                                                                       |
| ----------------- | ------- | ---- | ------------------------------------------------------------------------------------------ |
| `pageSize`        | Integer | 否   | 每页显示个数                                                                               |
| `pageIndex`       | Integer | 否   | 页数从 1 开始（默认 1）                                                                    |
| `type`            | String  | 否   | 待办类型：plan-任务、sign-签批、lead-指引、feedback-反馈、file_audit-文件审核、null 查所有 |
| `executionResult` | String  | 否   | 待办事项的执行结果                                                                         |

**响应参数**

`data` 类型为 `PageInfo<TodoTaskDetailVO>`，结构见：

- **6.3 PageInfo**
- **6.5 TodoTaskDetailVO**

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/todoTask/todoList' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "pageIndex": 1,
    "pageSize": 20,
    "type": "feedback"
  }'
```

---

### 5.5 获取汇报内容

获取指定汇报正文及回复列表。

**基本信息**

| 项目         | 说明                       |
| ------------ | -------------------------- |
| 接口地址     | `/work-report/report/info` |
| 请求方式     | `GET`                      |
| Content-Type | -                          |

**请求参数**

| 参数名     | 类型 | 必填 | 说明    |
| ---------- | ---- | ---- | ------- |
| `reportId` | Long | 是   | 汇报 id |

**响应参数**

`data` 类型为 `ReportDTO`，结构见 **6.6 ReportDTO**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "reportId": 1234567890,
    "content": "已完成接口联调",
    "createTime": "2026-03-17 10:00:00",
    "replies": [
      {
        "replyId": 987654321,
        "content": "已收到",
        "replyEmpId": 10002,
        "replyEmpName": "张三",
        "createTime": "2026-03-17 10:10:00"
      }
    ]
  }
}
```

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/work-report/report/info?reportId=1234567890' \
  -H 'appKey: {appKey}'
```

---

### 5.6 获取事项列表

查询最近处理过的事项列表（用于发起汇报时选择事项）。

**基本信息**

| 项目         | 说明                                  |
| ------------ | ------------------------------------- |
| 接口地址     | `/work-report/template/listTemplates` |
| 请求方式     | `POST`                                |
| Content-Type | `application/json`                    |

**请求参数**

请求体为 JSON，字段如下（见 `RecentTemplateParam`）：

| 参数名      | 类型    | 必填 | 说明                           |
| ----------- | ------- | ---- | ------------------------------ |
| `beginTime` | Long    | 否   | 开始时间（默认一个月前，毫秒） |
| `endTime`   | Long    | 否   | 结束时间（默认当前，毫秒）     |
| `limit`     | Integer | 否   | 限制条数（默认 50）            |

**响应参数**

`data` 类型为 `RecentTemplateResultVO`，结构见 **6.7 RecentTemplateResultVO** 与 **6.8 RecentTemplateVO**。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/template/listTemplates' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "limit": 50
  }'
```

---

### 5.7 根据事项 ID 列表获取事项信息

批量查询事项简易信息（事项 ID 与名称）。

**基本信息**

| 项目         | 说明                              |
| ------------ | --------------------------------- |
| 接口地址     | `/work-report/template/listByIds` |
| 请求方式     | `POST`                            |
| Content-Type | `application/json`                |

**请求参数**

请求体为 JSON 数组：

| 参数名        | 类型        | 必填 | 说明                         |
| ------------- | ----------- | ---- | ---------------------------- |
| `templateIds` | List\<Long> | 是   | 事项 ID 列表（请求体为数组） |

**响应参数**

`data` 类型为 `List<TemplateSimpleVO>`，结构见 **6.9 TemplateSimpleVO**。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/template/listByIds' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '[1001,1002]'
```

---

### 5.8 获取待办及未读汇报列表（新的待办和汇报）

插件场景：一次返回最新待办列表与未读汇报列表聚合对象。

**基本信息**

| 项目         | 说明                              |
| ------------ | --------------------------------- |
| 接口地址     | `/work-report/plugin/report/list` |
| 请求方式     | `POST`                            |
| Content-Type | `application/json`                |

**请求参数**

请求体为 JSON，字段如下（见 `PluginReportParam`，继承 `PageParam`）：

| 参数名           | 类型    | 必填 | 说明                           |
| ---------------- | ------- | ---- | ------------------------------ |
| `pageIndex`      | Integer | 否   | 页数从 1 开始（默认 1）        |
| `pageSize`       | Integer | 否   | 每页显示个数                   |
| `lastUpdateTime` | Long    | 是   | 最后更新时间戳（毫秒），默认 0 |

**响应参数**

`data` 类型为 `PluginReportAllVO`，结构见 **6.11 PluginReportAllVO**、**6.12 PluginItemListVO**、**6.13 PluginItemDetailVO**。

---

### 5.9 获取最新待办列表

插件场景：分页获取最新待办列表。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/work-report/plugin/report/latestList` |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

同 **5.8**（`PluginReportParam`）。

**响应参数**

`data` 类型为 `PluginItemListVO`（见 **6.12**）。

---

### 5.10 获取未读汇报列表

插件场景：分页获取未读汇报列表。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/work-report/plugin/report/unreadList` |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

同 **5.8**（`PluginReportParam`）。

**响应参数**

`data` 类型为 `PluginItemListVO`（见 **6.12**）。

---

### 5.11 工作任务列表查询

分页查询工作任务列表，支持按角色/状态/关键词/标签/优先级等筛选。

**基本信息**

| 项目         | 说明                                  |
| ------------ | ------------------------------------- |
| 接口地址     | `/work-report/report/plan/searchPage` |
| 请求方式     | `POST`                                |
| Content-Type | `application/json`                    |

**请求参数**

请求体为 JSON，字段如下（见 `ReportPlanSearchPageParam`）：

| 参数名         | 类型          | 必填 | 说明                                         |
| -------------- | ------------- | ---- | -------------------------------------------- |
| `pageSize`     | Integer       | 否   | 每页显示个数（默认 30）                      |
| `pageIndex`    | Integer       | 否   | 从 1 开始、页数（默认 1）                    |
| `userType`     | String        | 否   | 工作任务列表类型：null-全部、用户类型        |
| `keyWord`      | String        | 否   | 任务名称关键字                               |
| `status`       | Integer       | 否   | 任务状态：0-关闭、1-进行中                   |
| `isRead`       | Integer       | 否   | 任务读取状态：0-未读、1-已读                 |
| `reportStatus` | Integer       | 否   | 汇报状态：0-关闭、1-待汇报、2-已汇报、3-逾期 |
| `roleType`     | String        | 否   | 筛选框-角色类型：null-全部、用户类型         |
| `empIdList`    | List\<Long>   | 否   | 筛选框-人员 ID 列表                          |
| `labelList`    | List\<String> | 否   | 标签名称列表                                 |
| `grades`       | List\<String> | 否   | 优先级列表                                   |

**响应参数**

`data` 类型为 `PageInfo<ReportPlanSearchPageVO>`（见 **6.3** 与 **6.14**）。

---

### 5.12 获取用户创建的反馈类型待办列表

查询用户创建的反馈待办列表；不传 `empId` 默认查询登录用户。

**基本信息**

| 项目         | 说明                                         |
| ------------ | -------------------------------------------- |
| 接口地址     | `/work-report/todoTask/listCreatedFeedbacks` |
| 请求方式     | `GET`                                        |
| Content-Type | -                                            |

**请求参数**

| 参数名  | 类型 | 必填 | 说明                            |
| ------- | ---- | ---- | ------------------------------- |
| `empId` | Long | 否   | 反馈创建人 ID，不传查询登陆用户 |

**响应参数**

`data` 类型为 `List<TodoTaskCreatedFeedbackVO>`（见 **6.15**）。

---

### 5.13 任务简易信息 VO

获取任务简易信息及该任务提交的汇报简易信息列表。

**基本信息**

| 项目         | 说明                                                  |
| ------------ | ----------------------------------------------------- |
| 接口地址     | `/work-report/report/plan/getSimplePlanAndReportInfo` |
| 请求方式     | `GET`                                                 |
| Content-Type | -                                                     |

**请求参数**

| 参数名   | 类型 | 必填 | 说明    |
| -------- | ---- | ---- | ------- |
| `planId` | Long | 是   | 任务 id |

**响应参数**

`data` 类型为 `ReportPlanSimpleInfoVO`（见 **6.16** 与 **6.17 ReportSimpleInfoVO**）。

---

### 5.14 发件箱

分页查询当前用户发件箱汇报列表。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/work-report/report/record/outbox` |
| 请求方式     | `POST`                              |
| Content-Type | `application/json`                  |

**请求参数**

同 **4.3 收件箱分页查询**（`SearchReportRecordParam`）。

**响应参数**

`data` 类型为 `PageInfo<ReportRecordPageVO>`（见 **6.3** 与 **6.4**）。

---

### 5.15 分页获取当前用户的决策/建议/反馈待办列表

分页获取当前用户需要处理的汇报待办列表（决策/建议/反馈）。

**基本信息**

| 项目         | 说明                                        |
| ------------ | ------------------------------------------- |
| 接口地址     | `/work-report/reportInfoOpenQuery/todoList` |
| 请求方式     | `POST`                                      |
| Content-Type | `application/json`                          |

**请求参数**

请求体为 JSON，字段如下（见 `ReportInfoOpenQueryPageParam`）：

| 参数名      | 类型    | 必填 | 说明                    |
| ----------- | ------- | ---- | ----------------------- |
| `pageIndex` | Integer | 否   | 页数从 1 开始（默认 1） |
| `pageSize`  | Integer | 否   | 每页显示个数（默认 20） |

**响应参数**

`data` 类型为 `PageInfo<ReportTodoListItemVO>`，结构见：

- **6.3 PageInfo**
- **6.18 ReportTodoListItemVO**
- **6.10 ReportTodoDetailVO**（列表项 `detail`）

---

### 5.16 分页获取当前用户的未读汇报列表

分页获取当前用户未读汇报列表。

**基本信息**

| 项目         | 说明                                          |
| ------------ | --------------------------------------------- |
| 接口地址     | `/work-report/reportInfoOpenQuery/unreadList` |
| 请求方式     | `POST`                                        |
| Content-Type | `application/json`                            |

**请求参数**

同 **4.15**（`ReportInfoOpenQueryPageParam`）。

**响应参数**

`data` 类型为 `PageInfo<ReportUnreadListItemVO>`，结构见：

- **6.3 PageInfo**
- **6.19 ReportUnreadListItemVO**
- **6.10 ReportTodoDetailVO**（列表项 `detail`）

---

### 5.17 判断员工对指定汇报是否已读

根据汇报 ID 与员工 ID 判断已读状态。

**基本信息**

| 项目         | 说明                                            |
| ------------ | ----------------------------------------------- |
| 接口地址     | `/work-report/reportInfoOpenQuery/isReportRead` |
| 请求方式     | `GET`                                           |
| Content-Type | -                                               |

**请求参数**

| 参数名       | 类型 | 必填 | 说明    |
| ------------ | ---- | ---- | ------- |
| `reportId`   | Long | 是   | 汇报 id |
| `employeeId` | Long | 是   | 员工 id |

**响应参数**

`data` 类型为 `Boolean`：`true`-已读、`false`-未读。

---

### 5.18 完成待办（建议/决策）

提交建议/决策内容，完成指定待办。决策类待办需要传 `operate=agree/disagree`。

**基本信息**

| 项目         | 说明                                           |
| ------------ | ---------------------------------------------- |
| 接口地址     | `/work-report/open-platform/todo/completeTodo` |
| 请求方式     | `POST`                                         |
| Content-Type | `application/json`                             |

**请求参数**

请求体为 JSON，字段如下（见 `OpenPlatformTodoCompleteParam`）：

| 参数名    | 类型   | 必填 | 说明                                                                                                       |
| --------- | ------ | ---- | ---------------------------------------------------------------------------------------------------------- |
| `todoId`  | Long   | 是   | 待办主键 ID（TodoTask.id）                                                                                 |
| `content` | String | 是   | 填写内容（纯文本）；建议时建议必填，决策可为空；写阶段可不传 `contentHtml`，未传时用 `<p>content</p>` 填充 |
| `operate` | String | 否   | 决策时必填：agree-同意、disagree-不同意；建议类型无需传                                                    |

**响应参数**

`data` 类型为 `Boolean`。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/open-platform/todo/completeTodo' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "todoId": 12345,
    "content": "同意该方案，按计划执行",
    "operate": "agree"
  }'
```

---

### 5.19 汇报内容 AI 问答（流式返回）

对指定汇报集合进行 AI SSE 问答/编辑，响应为 `text/event-stream`。

**基本信息**

| 项目         | 说明                                          |
| ------------ | --------------------------------------------- |
| 接口地址     | `/work-report/open-platform/report/aiSseQaV2` |
| 请求方式     | `POST`                                        |
| Content-Type | `application/json`                            |
| 响应类型     | `text/event-stream`                           |

**请求参数**

请求体为 JSON，字段如下（见 `OpenPlatformReportContentAiEditParam`）：

| 参数名         | 类型        | 必填 | 说明                     |
| -------------- | ----------- | ---- | ------------------------ |
| `userContent`  | String      | 是   | 用户问题内容             |
| `aiType`       | Integer     | 否   | AI 类型，不传默认 42     |
| `reportIdList` | List\<Long> | 是   | 汇报 ID 列表（用于 RAG） |

**响应说明**

以 SSE 形式持续推送字符串片段（事件格式由 AI 服务定义）。

**请求示例**

```bash
curl -N -X POST 'https://{域名}/open-api/work-report/open-platform/report/aiSseQaV2' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "userContent": "请总结这几条汇报的关键风险点",
    "aiType": 42,
    "reportIdList": [1234567890, 1234567891]
  }'
```

---

### 5.20 创建工作任务

通过 OpenAPI 创建高级工作任务，并指定汇报人和（可选的）责任人/协办人等任务相关人。

**任务角色与职责**

1. **创建人**：任务创建人，进行创建操作，默认操作人即为创建人。
2. **责任人**：任务最主要负责人，默认汇报人与责任人为同一人，但特殊场景可设置责任人为其他人。
3. **汇报人**：基于任务写汇报的人，负责按周期汇报任务。（执行人：如果提到执行人，执行人即为汇报人，也是责任人。）
4. **协办人**：在任务写的汇报上发表意见，协助任务执行。
5. **监督人**：在任务写的汇报上给出决策意见。
6. **观察员**：一般为管理层，监控任务，检查项目进展。
7. **抄送人**：接收任务写的汇报抄送。

> **分配人员 ID (empId) 说明**：
> 若在配置各项参与人（汇报人、责任人等）时只有对方“姓名”而没有 `empId`（员工 ID），需遵循以下处理流程：
> 1. 先调用 **4.1 按姓名搜索全部员工(带外部联系人)**（`GET /cwork-user/searchEmpByName`）获取员工列表。
     >    - 查询不到：请提示用户“未找到该姓名对应的员工，请确认姓名或直接提供员工 ID”。
>    - 同名返回多条：请提示用户“存在同名员工，请指定唯一员工（例如结合部门、职级等信息协助挑选）后再传”。
> 2. 获取到唯一的员工 ID（该 4.1 接口返回列表数据对象中的 `id` 字段）后，再将其填入本接口的 `reportEmpIdList`、`ownerEmpIdList` 等各项干系人数组参数中。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/work-report/open-platform/report/plan/create` |
| 请求方式     | `POST`                              |
| Content-Type | `application/json`                  |

**请求参数**

请求体为 JSON，字段如下：

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `main` | String | 是 | 任务名称 |
| `needful` | String | 是 | 任务描述/要求 |
| `typeId` | Long | 是 | 业务类型id（如常规业务请填写对应的类型，如 9999 代表其他） |
| `reportEmpIdList` | List\<Long> | 是 | 汇报人员id列表 |
| `target` | String | 是 | 任务目标 |
| `ownerEmpIdList` | List\<Long> | 否 | 责任人id列表(不传系统默认将当前接口调用者设为责任人) |
| `assistEmpIdList` | List\<Long> | 否 | 协办人id列表 |
| `supervisorEmpIdList` | List\<Long> | 否 | 监督人id列表 |
| `copyEmpIdList` | List\<Long> | 否 | 抄送人id列表 |
| `observerEmpIdList` | List\<Long> | 否 | 观察者id列表 |
| `endTime` | Long | 是 | 任务结束时间(时间戳) |
| `pushNow` | Integer | 否 | 任务创建后是否立即发送通知和待办：0-否、1-是(默认1) |

**响应参数**

`data` 类型为 `Long`，表示创建成功的任务主键 ID。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": 1234567890
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/open-platform/report/plan/create' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
  "main": "开放平台测试-创建高级任务",
  "needful": "<p>这是通过OpenAPI创建的高级任务的<span style=\"color: rgb(85, 85, 85); font-size: 14px;\">任务要求</span></p>",
  "target": "<p>这是高级任务的<span style=\"color: rgb(85, 85, 85); background-color: rgb(255, 255, 255); font-size: 14px;\">任务目标</span></p>",
  "typeId": 9999,
  "reportEmpIdList": [
    1512393035869810690
  ],
  "ownerEmpIdList": [
    1512393035869810690
  ],
  "assistEmpIdList": [],
  "supervisorEmpIdList": [],
  "copyEmpIdList": [],
  "observerEmpIdList": [],
  "endTime": 1774972799000,
  "pushNow": 1
}'
```

---

### 5.21 获取我的新消息列表


**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/work-report/open-platform/report/findMyNewMsgList` |
| 请求方式     | `GET`                                  |
| Content-Type | -                                   |

**请求参数**

Query 参数：

| 参数名   | 类型    | 必填 | 说明                                                              |
| -------- | ------- | ---- | ----------------------------------------------------------------- |
| `msgType` | Integer | 否   | 消息类型过滤字典。默认为 1（重要消息）。可以使用您的业务枚举整数值进行查询过滤。 |

**响应参数**

`data` 类型为 `OpenPlatformNewMsgSummaryVO`，结构见：

- **6.22 OpenPlatformNewMsgSummaryVO**
- **6.23 OpenPlatformNewMsgVO**（列表项 `msgList`）

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/work-report/open-platform/report/findMyNewMsgList?msgType=1' \
  -H 'appKey: {appKey}'
```


---

### 5.22 阅读汇报（清除未读/新消息）

标记指定汇报为已读，并清除该汇报在当前用户下的所有新消息/未读提醒。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址     | `/work-report/open-platform/report/readReport` |
| 请求方式     | `GET`                                  |
| Content-Type | -                                   |

**请求参数**

Query 参数：

| 参数名   | 类型    | 必填 | 说明                                                              |
| -------- | ------- | ---- | ----------------------------------------------------------------- |
| `reportId` | Long | 是   | 汇报 ID。 |

**响应参数**

`data` 类型为 `null`。

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/work-report/open-platform/report/readReport?reportId=123456789' \
  -H 'appKey: {appKey}'
```

---

### 5.23 新增或更新汇报草稿

保存或更新当前用户的汇报草稿；请求体模型与正式提交相近。**详细业务逻辑与通用参数配置请阅读 [场景一：发送汇报 或 新增/更新草稿 通用参数说明](#场景一发送汇报-或-新增更新草稿-通用参数说明)**。正式发出汇报请使用 **5.1 发送汇报**（`POST /work-report/report/record/submit`）。

> **更新约定（务必遵守）**  
> - **若是更新草稿，必须在请求体中传入 `id`（汇报 id）**；不传则一律视为**新增**，会生成新的草稿记录。`id` 可与 **5.23** 返回的 `data.id`、**5.24** 列表中 `bizType=report` 时的 `businessId`、或 **5.25** 路径中的 `reportRecordId` 对齐。  
> - **更新语义为全量更新（覆盖写）**：服务端按本次请求体整体落库，**未传入的字段不会保留旧值**。例如原草稿已填写接收人，本次更新若**不带** `acceptEmpIdList`（或等价地传空列表，以实际联调为准），则**接收人会被清空**；`copyEmpIdList`、`reportLevelList`、`fileVOList` 等集合类字段同理。建议更新前先调用 **5.25 草稿汇报详情** 取回完整数据，在完整对象上修改后再调用本接口保存。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/work-report/draftBox/saveOrUpdate`    |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

请求体为 JSON，字段如下（OpenAPI 模型名：`开放平台-提交汇报参数`）。结构与 **5.1 发送汇报** 中 `SubmitReportParam` 一致处可直接复用；下列说明以草稿接口为准。

| 参数名            | 类型                      | 必填 | 说明                                                                                       |
| ----------------- | ------------------------- | ---- | ----------------------------------------------------------------------------------------- |
| `id`              | Long                      | 条件 | **更新时必填**：汇报 id；新增草稿可不传。不传 `id` 视为新增，会产生新草稿。                 |
| `planId`          | Long                      | 否   | 工作任务 id                                                                                |
| `templateId`      | Long                      | 否   | 事项 id                                                                                    |
| `typeId`          | Long                      | 否   | 业务类型 id，默认 `9999`（其他汇报）                                                       |
| `main`            | String                    | 是   | 汇报标题                                                                                   |
| `grade`           | String                    | 否   | 优先级：一般、紧急；默认一般                                                               |
| `privacyLevel`    | String                    | 否   | 密级：非涉密、涉密；默认非涉密                                                             |
| `contentType`     | String                    | 否   | 正文类型：`html`、`markdown`；**默认 `markdown`**（与 **5.1** 默认值表述以本接口为准）     |
| `contentHtml`     | String                    | 是   | 汇报内容（富文本或 Markdown 字符串）                                                       |
| `acceptEmpIdList` | List\<Long>               | 否   | 接收人员 id 列表；新增时可为空。**更新时若省略且按空处理，会清空原接收人**（全量更新，见上文）。 |
| `copyEmpIdList`   | List\<Long>               | 否   | 抄送人员 id 列表；**更新时省略可能导致原抄送被清空**。                                     |
| `reportLevelList` | List\<ReportLevelParam>   | 否   | 多级节点；结构见 **6.1**。**更新时须带齐须保留的节点，省略可能导致原节点被清空**。          |
| `fileVOList`      | List\<OpenPlatformFileVO> | 否   | 关联附件，见 **6.24**。**更新时省略可能导致原附件关联被清空**。                            |

> 说明：服务端对正文的处理与 **5.1** 相同，会将 `contentHtml` 去标签生成纯文本 `content` 落库；调用方无需传 `content`。

**响应参数**

`data` 类型为 `BaseInfo`（主要字段为主键 `id`），与 **5.1** 响应一致。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": 1234567890
  }
}
```

**请求示例**

新增草稿（不传 `id`）：

```bash
curl -X POST 'https://{域名}/open-api/work-report/draftBox/saveOrUpdate' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "main": "草稿标题",
    "contentHtml": "## 尚未填完的正文",
    "contentType": "markdown",
    "typeId": 9999
  }'
```

更新草稿（**必须带 `id`**，且建议带齐需保留的接收人/抄送/节点/附件等，避免被全量清空）：

```bash
curl -X POST 'https://{域名}/open-api/work-report/draftBox/saveOrUpdate' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "id": 2036325013120483330,
    "main": "草稿标题（已改）",
    "contentHtml": "## 已补充正文",
    "contentType": "markdown",
    "typeId": 9999,
    "acceptEmpIdList": [1512393035869810690],
    "reportLevelList": []
  }'
```

**数据流向**

- 返回的 `data.id` 为汇报的id，非草稿id，可用于后续草稿列表、详情或更新、提交草稿等流程（具体以平台提供的草稿相关接口为准）。

---

### 5.24 草稿箱分页查询

分页查询当前登录用户的草稿箱列表。

**基本信息**

| 项目         | 说明                                 |
| ------------ | ------------------------------------ |
| 接口地址     | `/work-report/draftBox/listByPage`   |
| 请求方式     | `POST`                               |
| Content-Type | `application/json`                   |

**请求参数**

请求体为 JSON，字段如下（模型名：`DraftBoxQueryParam`）：

| 参数名      | 类型    | 必填 | 说明              |
| ----------- | ------- | ---- | ----------------- |
| `pageIndex` | Integer | 是   | 页码，从 1 开始   |
| `pageSize`  | Integer | 是   | 每页条数，默认20          |

**响应参数**

`data` 类型为 `PageInfo<DraftBoxListVO>`：

- 分页外层结构见 **6.3 PageInfo\<T>**
- 列表元素结构见 **6.27 DraftBoxListVO**

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": 2,
    "list": [
      {
        "id": 2036325013120483329,
        "bizType": "report",
        "businessId": 2036325013120483330,
        "title": "周报草稿",
        "content": "## 本周进展\n- 接口联调",
        "grade": "一般",
        "existsFiles": 1,
        "status": 1,
        "createTime": "2026-03-28 10:00:00",
        "updateTime": "2026-03-28 11:30:00"
      }
    ],
    "pageNum": 1,
    "pageSize": 20,
    "size": 1
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/draftBox/listByPage' \
  -H 'Content-Type: application/json' \
  -H 'appKey: {appKey}' \
  -d '{
    "pageIndex": 1,
    "pageSize": 20
  }'
```

**数据流向**

- 列表项中的 `id` 为**草稿 ID**（用于后续的删除草稿使用）；`bizType=report` 时 `businessId` 为关联的**汇报 ID**，可与 **5.23** 返回的汇报 id、草稿详情/提交/删除等接口配合使用。

---

### 5.25 草稿汇报详情

根据**汇报 ID**查询草稿态汇报的完整编辑数据（OpenAPI：`draftBoxDetailUsingGET`，摘要「34、草稿汇报详情」）。路径参数与 **5.24** 列表中的 `businessId`（`bizType=report` 时）或 **5.23** 返回的汇报 id 一致。

**基本信息**

| 项目         | 说明                                                       |
| ------------ | ---------------------------------------------------------- |
| 接口地址     | `/work-report/draftBox/detail/{reportRecordId}`            |
| 请求方式     | `GET`                                                      |
| Content-Type | -                                                          |

**请求参数**

路径参数：

| 参数名            | 类型 | 必填 | 说明    |
| ----------------- | ---- | ---- | ------- |
| `reportRecordId`  | Long | 是   | 汇报 id |

**响应参数**

`data` 类型为 `汇报详情VO`（OpenAPI 模型名），结构见 **6.28 汇报详情VO**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": 2036325013120483330,
    "main": "周报草稿",
    "contentHtml": "<p>正文</p>",
    "contentType": "markdown",
    "typeId": 9999,
    "templateId": null,
    "planId": null,
    "grade": "一般",
    "privacyLevel": "非涉密",
    "reportCode": "RPT-20260328-001",
    "reportRecordType": 5,
    "status": 2,
    "acceptEmployeeList": [],
    "copyEmployeeList": [],
    "reportLevelList": [],
    "fileList": []
  }
}
```

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/work-report/draftBox/detail/2036325013120483330' \
  -H 'appKey: {appKey}'
```

**数据流向**

- 用于在编辑页回显草稿：与 **5.23 新增或更新汇报草稿** 组成「保存—列表—详情—再保存」闭环。
- `status=2` 表示暂存（草稿），具体枚举以 **6.28** 为准。

---

### 5.26 删除草稿

按**草稿 ID**删除当前用户在草稿箱中的对应草稿（OpenAPI：`deleteDraftUsingPOST`，摘要「33、删除草稿」）。路径中的 `id` 为 **草稿 ID**，与 **5.24 草稿箱分页查询** 列表项中的 `id` 一致（不是汇报 `businessId`）。

**基本信息**

| 项目         | 说明                                      |
| ------------ | ----------------------------------------- |
| 接口地址     | `/work-report/draftBox/delete/{id}`     |
| 请求方式     | `POST`                                    |
| Content-Type | -（无请求体，仅路径参数）                 |

**请求参数**

路径参数：

| 参数名 | 类型 | 必填 | 说明    |
| ------ | ---- | ---- | ------- |
| `id`   | Long | 是   | 草稿 id |

**响应参数**

`data` 类型为 `Boolean`，表示是否删除成功（OpenAPI：`Result«boolean»`）。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": true
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/draftBox/delete/2036325013120483329' \
  -H 'appKey: {appKey}'
```

**数据流向**

- 删除成功后客户端可刷新 **5.24** 列表或关闭详情页；若需同时清理本地编辑态，请以 `resultCode` 与 `data` 为准。

---

### 5.27 将草稿转为正式汇报发出

将指定草稿箱中的汇报转为正式发布状态。

> **实现状态（务必阅读）**  
> 本接口在 [Swagger / OpenAPI](https://cwork-test-open-api.xgjktech.com.cn/swagger-ui/index.html#/%E5%B7%A5%E4%BD%9C%E5%8D%8F%E5%90%8C%E6%9C%8D%E5%8A%A1/submitDraftBoxUsingPOST) 中**已定义**（摘要「27、将草稿转为正式汇报发出」）。按需先通过 **5.23** 新增或者更新汇报草稿再操作此接口。

**基本信息**

| 项目         | 说明                                   |
| ------------ | -------------------------------------- |
| 接口地址     | `/work-report/draftBox/submit/{id}`    |
| 请求方式     | `POST`                                 |
| Content-Type | -（无请求体，仅路径参数）              |

**请求参数**

路径参数：

| 参数名 | 类型 | 必填 | 说明    |
| ------ | ---- | ---- | ------- |
| `id`   | Long | 是   | 汇报 id |

> 与 **5.24** 的对应关系：`bizType=report` 时列表项的 `businessId` 即为汇报 id，可与本路径 `{id}` 对齐。

**响应参数**

`data` 类型为 `Boolean`，表示是否提交成功。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/work-report/draftBox/submit/2036325013120483330' \
  -H 'appKey: {appKey}'
```

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
| `groupIdList`   | List\<Long>                 | 分组 ID 列表（通过 **4.03** 接口获取）               |

`ReportLevelUserParam`：

| 字段名        | 类型   | 说明    |
| ------------- | ------ | ------- |
| `empId`       | Long   | 员工 id |
| `requirement` | String | AI 要求 |

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
| `content`    | String          | 汇报正文 |
| `createTime` | Timestamp       | 创建时间 |
| `replies`    | List\<ReplyDTO> | 回复列表 |

`ReplyDTO`：

| 字段名         | 类型      | 说明       |
| -------------- | --------- | ---------- |
| `replyId`      | Long      | 回复 ID    |
| `content`      | String    | 回复内容   |
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

---

## 七、错误码说明

> 以下为通用与鉴权相关错误码示例，具体以平台配置与返回为准。

| resultCode | 说明                                                     |
| ---------- | -------------------------------------------------------- |
| 1          | 请求成功                                                 |
| 401        | 鉴权失败/缺少访问凭证（如缺少 appKey、Token 校验失败等） |
| 60001      | 内部接口，禁止外部访问                                   |
| 60002      | 禁止访问                                                 |

---

## 八、注意事项

1. **ID 精度**：所有 ID 建议按 Long/字符串处理，前端请避免用 JS Number 直接承载超大整数。
2. **时间戳单位**：文档中 `beginTime/endTime/lastUpdateTime/timestamp` 均为 **毫秒**。
3. **SSE 接口**：`/work-report/open-platform/report/aiSseQaV2` 为 `text/event-stream`，客户端需使用支持 SSE 的方式持续读取流。
4. **汇报内容字段**：提交汇报时建议只传 `contentHtml`，服务端会生成纯文本 `content`；回复同理。

