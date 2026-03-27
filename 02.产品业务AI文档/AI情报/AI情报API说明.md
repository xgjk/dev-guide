# AI情报 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-26 | 初版创建，仅覆盖 AI情报助手已定义的报告场景 API | AI协作助手 |

## 一、概述

本文档描述了 **AI情报系统** 在“选模版-生成报告-查看进度与结果-修改章节内容”场景下对外提供的 API 接口。通过这些接口，可以实现以下业务能力：

1. **分页查询模版列表** — 按关键词、目录、是否仅看我的等条件筛选可用模版
2. **获取模版详情** — 查看模版的章节、子章节与提示词结构，判断是否适合当前报告任务
3. **发起报告生成任务** — 基于指定模版和上下文创建异步报告任务
4. **查询任务状态** — 查询报告任务当前状态与进度，用于轮询任务结果
5. **获取报告详情** — 查看报告全文、章节结构及子章节内容
6. **分页查询报告列表** — 按关键词、状态、目录等条件定位历史报告
7. **直接编辑报告章节** — 覆盖指定子章节内容，适用于人工修改不满意章节
8. **查询章节历史版本** — 查看章节直接编辑后的历史版本记录

---

## 二、通用说明

### 2.1 访问地址

业务接口访问地址：

```text
https://{业务域名}/ai-report/{接口地址}
```

鉴权接口访问地址：

```text
https://{鉴权域名}/user/login/appkey?appCode=cms_gpt&appKey={CWork Key}
```

### 2.2 环境信息

| 环境 | 域名/Base URL | 备注 |
|------|---------------|------|
| 生产环境-业务接口 | `https://cwork-api.mediportal.com.cn` | AI情报业务接口 |
| 生产环境-鉴权接口 | `https://cwork-web.mediportal.com.cn` | 通过 `CWork Key` 换取 `access-token` |

### 2.3 公共请求头

| Header | 说明 | 是否必填 |
|--------|------|----------|
| `access-token` | 业务请求凭证，通过鉴权接口返回的 `data.xgToken` 获取 | 是 |
| `Content-Type` | 请求体类型，本文档中的 POST 接口统一为 `application/json` | 按接口要求 |

### 2.4 鉴权说明

所有 AI情报业务接口均使用 `access-token` 鉴权。若当前没有可用 token，可先调用鉴权接口：

```bash
curl -X GET 'https://cwork-web.mediportal.com.cn/user/login/appkey?appCode=cms_gpt&appKey={CWork Key}' \
  -H 'Content-Type: application/json'
```

鉴权成功后，从返回结果中取 `data.xgToken`，并在后续所有业务接口中放入请求头 `access-token`。

鉴权返回示例：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "xgToken": "xxx"
  }
}
```

### 2.5 通用响应结构

所有业务接口返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `resultCode` | Integer | 业务状态码，`1` 表示成功，其他值表示失败 |
| `resultMsg` | String | 提示信息，成功时通常为 `null`，失败时为错误描述 |
| `data` | T | 业务数据，不同接口类型不同，失败时通常为 `null` |

---

## 三、关键业务流程说明

### 场景一：选模版并生成报告

> 需求：用户希望先找到合适模版，再基于模版发起一份新的行业报告任务。

1. 调用 **4.1 分页查询模版列表**（`POST /ai-report/moban/listMobanByPageV2`），按关键词、目录等条件筛选模版，拿到候选模版的 `_id`
2. 调用 **4.2 获取模版详情**（`POST /ai-report/moban/mobanDetail`），传入上一步的 `mobanId`，查看模版章节结构，确认该模版是否适合当前报告任务
3. 调用 **4.3 发起报告生成任务**（`POST /ai-report/task/startTask`），传入 `mobanId`、`taskName`、`dirId` 和 `context`，创建报告任务，拿到 `taskId`
4. 调用 **4.4 查询任务状态**（`POST /ai-report/task/checkTask`），传入 `taskId` 轮询任务状态，直到 `state = 2`
5. 调用 **4.5 获取报告详情**（`POST /ai-report/task/taskDetailV2`），传入同一个 `taskId`，获取报告全文、章节结构和子章节内容

### 场景二：查询历史报告与当前进度

> 需求：用户想查找某份历史报告，或确认某个任务当前是否已经完成。

1. 调用 **4.6 分页查询报告列表**（`POST /ai-report/task/listTaskByPage`），按关键词、状态、目录等条件搜索报告列表，拿到目标报告的 `_id`
2. 若只需判断任务状态，可直接调用 **4.4 查询任务状态**（`POST /ai-report/task/checkTask`），传入 `taskId`
3. 若需查看完整内容，调用 **4.5 获取报告详情**（`POST /ai-report/task/taskDetailV2`），传入 `taskId` 获取全文与章节内容

### 场景三：手动修改某个章节并查看历史版本

> 需求：用户对某个子章节不满意，希望直接覆盖内容，并查看该章节历史修改记录。

1. 先调用 **4.5 获取报告详情**（`POST /ai-report/task/taskDetailV2`），传入 `taskId`，从返回的 `sectionList[].questionList[]._id` 中定位目标子章节的 `questionId`
2. 调用 **4.7 直接编辑报告章节**（`POST /ai-report/task/updateQuestionResult`），传入 `questionId` 和新的 `result` 内容，保存修改
3. 调用 **4.8 查询章节历史版本**（`POST /ai-report/task/listResultVersion`），传入同一个 `questionId`，查看该章节的历史版本记录

---

## 四、接口详细说明

---

### 4.1 分页查询模版列表

按目录、关键词、是否仅看我的等条件分页搜索模版列表。通常作为模版选型的第一步，用于获取候选 `mobanId`。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/moban/listMobanByPageV2` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 JSON，字段如下：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `pageNum` | Number | 是 | 页码，从 `0` 开始 |
| `pageSize` | Number | 是 | 每页条数 |
| `dirId` | String | 否 | 目录 ID，按目录筛选 |
| `searchKey` | String | 否 | 模版名称关键词 |
| `onlyMine` | String | 否 | 是否仅看我的，传 `'true'` 表示只看我的 |
| `mobanTypeId` | String | 否 | 模版类型 ID |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/moban/listMobanByPageV2' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "pageNum": 0,
    "pageSize": 10,
    "searchKey": "竞品分析",
    "onlyMine": "true"
  }'
```

**响应参数**

`data` 类型为 `MobanPageResult`，字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `pageContent` | List\<MobanListItemVO> | 当前页模版列表 |
| `total` | Number | 总记录数 |

`MobanListItemVO` 字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 模版 ID |
| `mobanName` | String | 模版名称 |
| `mobanTypeId` | String | 模版类型 ID |
| `dirId` | String | 目录 ID |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "pageContent": [
      {
        "_id": "moban_1001",
        "mobanName": "医疗行业竞品分析模版",
        "mobanTypeId": "type_01",
        "dirId": "dir_001"
      }
    ],
    "total": 1
  }
}
```

**数据流向**

- 返回的 `pageContent[]._id` 用于 **4.2 获取模版详情** 和 **4.3 发起报告生成任务** 的 `mobanId` 入参

---

### 4.2 获取模版详情

获取指定模版的完整结构，包括章节列表、子章节及提示词配置。通常用于判断模版结构是否适合当前报告任务。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/moban/mobanDetail` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `mobanId` | String | 是 | 模版 ID，来自 **4.1** 返回的 `_id` |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/moban/mobanDetail' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "mobanId": "moban_1001"
  }'
```

**响应参数**

`data` 类型为 `MobanDetailVO`，字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 模版 ID |
| `mobanName` | String | 模版名称 |
| `mobanTypeId` | String | 模版类型 ID |
| `dirId` | String | 目录 ID |
| `sectionList` | List\<MobanSectionVO> | 章节列表 |

`MobanSectionVO` 字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | String | 章节名称 |
| `questionList` | List\<MobanQuestionVO> | 子章节列表 |

`MobanQuestionVO` 字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `title` | String | 子章节标题 |
| `prompt` | String | 该子章节的提示词 |
| `dataSourceType` | String | 数据源类型 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "_id": "moban_1001",
    "mobanName": "医疗行业竞品分析模版",
    "mobanTypeId": "type_01",
    "dirId": "dir_001",
    "sectionList": [
      {
        "name": "市场概览",
        "questionList": [
          {
            "title": "行业现状",
            "prompt": "请总结行业现状与主要趋势",
            "dataSourceType": "rag"
          }
        ]
      }
    ]
  }
}
```

**数据流向**

- 返回的 `_id` 可直接用于 **4.3 发起报告生成任务** 的 `mobanId`
- 返回的 `sectionList` 用于业务侧判断模版是否符合当前生成目标

---

### 4.3 发起报告生成任务

基于指定模版发起异步报告生成任务。接口立即返回 `taskId`，后续需要通过 **4.4** 查询状态，并通过 **4.5** 获取最终内容。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/task/startTask` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 JSON，字段如下：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `mobanId` | String | 是 | 模版 ID |
| `taskName` | String | 是 | 报告名称 |
| `dirId` | String | 是 | 报告所属目录 ID |
| `context` | Object | 否 | 生成上下文，如关键词、目标公司、时间范围等 |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/task/startTask' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "mobanId": "moban_1001",
    "taskName": "特斯拉竞品分析报告",
    "dirId": "dir_001",
    "context": {
      "company": "特斯拉",
      "period": "2026Q1"
    }
  }'
```

**响应参数**

`data` 类型为 `StartTaskResultVO`，字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `taskId` | String | 报告任务 ID |
| `id` | String | 与任务标识等价的兼容字段 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "taskId": "task_9001",
    "id": "task_9001"
  }
}
```

**数据流向**

- 返回的 `taskId` 或 `id` 用于 **4.4 查询任务状态** 和 **4.5 获取报告详情** 的 `taskId`

---

### 4.4 查询任务状态

查询指定报告任务的当前状态与进度。通常在 **4.3** 之后轮询调用，直到任务完成。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/task/checkTask` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `taskId` | String | 是 | 报告任务 ID，来自 **4.3** 返回值 |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/task/checkTask' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "taskId": "task_9001"
  }'
```

**响应参数**

`data` 类型为 `TaskStatusVO`，字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `taskId` | String | 报告任务 ID |
| `taskName` | String | 报告名称 |
| `state` | Number | 状态：`0` 未开始，`1` 进行中，`2` 已完成，`3` 失败 |
| `progress` | Number | 进度百分比，部分部署会返回该字段 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "taskId": "task_9001",
    "taskName": "特斯拉竞品分析报告",
    "state": 1,
    "progress": 60
  }
}
```

**数据流向**

- 当 `state = 2` 时，可继续调用 **4.5 获取报告详情**
- 当 `state = 3` 时，应停止轮询并提示任务失败

---

### 4.5 获取报告详情

获取指定报告的完整详情，包括报告元信息、章节结构及子章节内容。也是定位 `questionId` 的关键接口。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/task/taskDetailV2` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `taskId` | String | 是 | 报告任务 ID |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/task/taskDetailV2' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "taskId": "task_9001"
  }'
```

**响应参数**

`data` 类型为 `TaskDetailVO`，字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 报告任务 ID |
| `taskName` | String | 报告名称 |
| `state` | Number | 报告状态 |
| `mobanId` | String | 所用模版 ID |
| `context` | Object | 报告生成时使用的上下文 |
| `sectionList` | List\<TaskSectionVO> | 章节列表 |

`TaskSectionVO` 字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | String | 章节名称 |
| `questionList` | List\<TaskQuestionVO> | 子章节列表 |

`TaskQuestionVO` 字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 子章节 ID，供 **4.7** 和 **4.8** 使用 |
| `title` | String | 子章节标题 |
| `result` | String | 子章节生成内容，通常为 Markdown |
| `section` | String | 章节标识 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "_id": "task_9001",
    "taskName": "特斯拉竞品分析报告",
    "state": 2,
    "mobanId": "moban_1001",
    "context": {
      "company": "特斯拉",
      "period": "2026Q1"
    },
    "sectionList": [
      {
        "name": "市场概览",
        "questionList": [
          {
            "_id": "question_5001",
            "title": "行业现状",
            "result": "2026年新能源汽车市场继续增长……",
            "section": "section_market_overview"
          }
        ]
      }
    ]
  }
}
```

**数据流向**

- 返回的 `sectionList[].questionList[]._id` 用于 **4.7 直接编辑报告章节** 的 `questionId`
- 返回的 `sectionList[].questionList[]._id` 也用于 **4.8 查询章节历史版本** 的 `questionId`

---

### 4.6 分页查询报告列表

按目录、状态、关键词等条件分页查询历史报告列表，用于定位目标任务和支持报告库浏览。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/task/listTaskByPage` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 JSON，字段如下：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `pageNum` | Number | 是 | 页码，从 `0` 开始 |
| `pageSize` | Number | 是 | 每页条数 |
| `dirId` | String | 否 | 目录 ID |
| `mobanTypeId` | String | 否 | 模版类型 ID |
| `state` | Number | 否 | 状态：`0` 未开始，`1` 进行中，`2` 已完成，`3` 失败 |
| `searchKey` | String | 否 | 报告标题关键词 |
| `reportType` | Number | 否 | 报告来源：`1` 普通，`2` 定时，`3` 系统 |
| `onlyMine` | String | 否 | 是否仅看我的，传 `'true'` |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/task/listTaskByPage' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "pageNum": 0,
    "pageSize": 10,
    "searchKey": "特斯拉",
    "state": 2,
    "onlyMine": "true"
  }'
```

**响应参数**

`data` 类型为 `TaskPageResult`，字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `pageContent` | List\<TaskListItemVO> | 当前页报告列表 |
| `total` | Number | 总记录数 |

`TaskListItemVO` 字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 报告任务 ID |
| `taskName` | String | 报告名称 |
| `state` | Number | 任务状态 |
| `mobanId` | String | 模版 ID |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "pageContent": [
      {
        "_id": "task_9001",
        "taskName": "特斯拉竞品分析报告",
        "state": 2,
        "mobanId": "moban_1001"
      }
    ],
    "total": 1
  }
}
```

**数据流向**

- 返回的 `pageContent[]._id` 用于 **4.4 查询任务状态** 和 **4.5 获取报告详情** 的 `taskId`

---

### 4.7 直接编辑报告章节

将用户自行撰写的内容直接覆盖指定子章节并保存入库。每次成功写入后，系统会保留历史版本。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/task/updateQuestionResult` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `questionId` | String | 是 | 子章节 ID，来自 **4.5** 的 `sectionList[].questionList[]._id` |
| `result` | String | 是 | 新内容，通常为 Markdown 字符串 |

> `questionId` 是子章节对象的 `_id`，不是 `taskId`，也不是章节名称。

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/task/updateQuestionResult' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "questionId": "question_5001",
    "result": "根据最新市场数据，2026年新能源汽车行业增速放缓，但高端细分市场仍保持增长。"
  }'
```

**响应参数**

`data` 类型为 `Boolean`。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `data` | Boolean | `true` 表示写入成功 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": true
}
```

**数据流向**

- 成功写入后，可调用 **4.8 查询章节历史版本** 查看该章节的版本留痕

---

### 4.8 查询章节历史版本

查询指定子章节的历史修改版本列表。通常用于在章节被人工修改后回看历史内容。

**基本信息**

| 项目 | 说明 |
|------|------|
| 接口地址 | `/ai-report/task/listResultVersion` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `questionId` | String | 是 | 子章节 ID，来自 **4.5** 的 `sectionList[].questionList[]._id` |

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/ai-report/task/listResultVersion' \
  -H 'access-token: {access-token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "questionId": "question_5001"
  }'
```

**响应参数**

`data` 类型为 `List<ResultVersionVO>`，每条记录字段如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 版本记录 ID |
| `questionId` | String | 子章节 ID |
| `result` | String | 该版本的章节内容 |
| `createTime` | String | 版本创建时间 |
| `personId` | String | 创建该版本的人员标识 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "_id": "version_7001",
      "questionId": "question_5001",
      "result": "2026年新能源汽车市场继续增长……",
      "createTime": "2026-03-26 10:20:00",
      "personId": "person_1001"
    },
    {
      "_id": "version_7002",
      "questionId": "question_5001",
      "result": "根据最新市场数据，2026年新能源汽车行业增速放缓，但高端细分市场仍保持增长。",
      "createTime": "2026-03-26 11:05:00",
      "personId": "person_1001"
    }
  ]
}
```

---

## 五、公共数据结构

### 5.1 MobanPageResult

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `pageContent` | List\<MobanListItemVO> | 模版分页结果列表 |
| `total` | Number | 总记录数 |

### 5.2 MobanListItemVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 模版 ID |
| `mobanName` | String | 模版名称 |
| `mobanTypeId` | String | 模版类型 ID |
| `dirId` | String | 目录 ID |

### 5.3 MobanDetailVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 模版 ID |
| `mobanName` | String | 模版名称 |
| `mobanTypeId` | String | 模版类型 ID |
| `dirId` | String | 目录 ID |
| `sectionList` | List\<MobanSectionVO> | 章节列表 |

### 5.4 MobanSectionVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | String | 章节名称 |
| `questionList` | List\<MobanQuestionVO> | 子章节列表 |

### 5.5 MobanQuestionVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `title` | String | 子章节标题 |
| `prompt` | String | 子章节提示词 |
| `dataSourceType` | String | 数据源类型 |

### 5.6 StartTaskResultVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `taskId` | String | 报告任务 ID |
| `id` | String | 与 `taskId` 等价的兼容字段 |

### 5.7 TaskStatusVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `taskId` | String | 报告任务 ID |
| `taskName` | String | 报告名称 |
| `state` | Number | `0` 未开始，`1` 进行中，`2` 已完成，`3` 失败 |
| `progress` | Number | 进度百分比，部分部署返回 |

### 5.8 TaskPageResult

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `pageContent` | List\<TaskListItemVO> | 报告分页结果列表 |
| `total` | Number | 总记录数 |

### 5.9 TaskListItemVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 报告任务 ID |
| `taskName` | String | 报告名称 |
| `state` | Number | 任务状态 |
| `mobanId` | String | 模版 ID |

### 5.10 TaskDetailVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 报告任务 ID |
| `taskName` | String | 报告名称 |
| `state` | Number | 报告状态 |
| `mobanId` | String | 模版 ID |
| `context` | Object | 报告生成上下文 |
| `sectionList` | List\<TaskSectionVO> | 章节列表 |

### 5.11 TaskSectionVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | String | 章节名称 |
| `questionList` | List\<TaskQuestionVO> | 子章节列表 |

### 5.12 TaskQuestionVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 子章节 ID |
| `title` | String | 子章节标题 |
| `result` | String | 子章节内容 |
| `section` | String | 章节标识 |

### 5.13 ResultVersionVO

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `_id` | String | 版本记录 ID |
| `questionId` | String | 子章节 ID |
| `result` | String | 该版本内容 |
| `createTime` | String | 创建时间 |
| `personId` | String | 操作人标识 |

---

## 六、错误码说明

| resultCode | 说明 |
|------------|------|
| 1 | 请求成功 |
| 0 | 通用失败 |
| 401 | 鉴权失败或 `access-token` 无效 |
| 500 | 系统异常，请稍后重试 |

> 说明：AI情报业务接口文档当前未提供完整业务错误码表。除以上通用码外，其余错误码请以实际接口返回为准。

---

## 七、注意事项

1. **鉴权前置**：所有业务接口都依赖 `access-token`，而不是直接传 `appKey`。只有鉴权接口才使用 `CWork Key`。
2. **页码起始值**：模版列表和报告列表接口中的 `pageNum` 从 `0` 开始，不是从 `1` 开始。
3. **任务为异步流程**：调用 `startTask` 后不要立即假设报告已生成完成，应通过 `checkTask` 轮询状态，再调用 `taskDetailV2` 获取内容。
4. **章节修改粒度**：章节直接编辑接口操作的是子章节 `questionId`，不是 `taskId`，也不是章节名称。
5. **版本查询前置条件**：只有定位到具体子章节后，才能通过 `listResultVersion` 查看历史版本。
6. **AI 使用场景提示**：`taskDetailV2` 返回的章节内容已经是结构化文本结果，适合直接提供给 AI 做总结、抽取或重写，不需要再额外拼装为其他中间接口结果。
