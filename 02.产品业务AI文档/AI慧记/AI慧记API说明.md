# AI慧记 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.1 | 2026-03-27 | 新增 4.10 分片录音列表 V2、4.11 按会议编号查询慧记列表 | - |
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |

## 一、概述

本文档描述了 **AI慧记** 模块对外开放的全部 API 接口。通过这些接口，可以实现以下业务能力：

1. **分页查询聊天列表** — 按条件分页获取会议聊天记录，支持类型筛选、名称搜索、时间范围等
2. **查询会议聊天详情** — 根据会议聊天 ID 获取单条聊天的完整信息
3. **查询 AI 慧记报告信息** — 获取指定会议聊天的文字报告和 HTML 报告内容及状态
4. **查询分片录音列表** — 获取指定会议聊天的所有分片录音记录
5. **创建分享 V2** — 为指定会议聊天创建分享链接
6. **查询待办列表** — 获取指定会议聊天关联的待办事项列表
7. **检查二次语音转文字** — 查询指定会议聊天的二次语音转文字处理状态与进度
8. **检查二次语音转文字 V2** — 查询二次语音转文字处理状态（简化版）
9. **上传内容到个人知识库** — 将文本内容上传到用户个人知识库的指定文件夹
10. **查询分片录音列表 V2** — 在分片录音列表基础上，支持按 `lastStartTime` 在网关侧增量过滤（可选）
11. **按会议编号查询慧记列表** — 按会议编号拉取慧记记录列表（委托会议域 AI 摘要插件，需 `appKey` 与登录用户上下文）

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境   | 域名/Base URL                    | 备注 |
| ------ | ------------------------------- | ---- |
| 生产环境 | `https://sg-al-ai-voice-assistant.mediportal.com.cn/api`      | -    |

### 2.3 公共请求头

| Header         | 说明                                    | 是否必填 |
| -------------- | --------------------------------------- | -------- |
| `appKey`       | 应用密钥，请联系管理员获取                  | 是       |
| `Content-Type` | 固定为 `application/json`（所有接口均为 POST） | 是       |

### 2.4 通用响应结构

所有接口返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段         | 类型    | 说明                                  |
| ------------ | ------- | ------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，其他值表示失败 |
| `resultMsg`  | String  | 提示信息，成功时为 `null`，失败时为错误描述 |
| `data`       | T       | 业务数据，不同接口类型不同，失败时为 `null` |

---

## 三、关键业务流程说明

### 场景一：获取会议聊天列表并查看详情

> 需求：分页浏览会议聊天记录，选择某条记录查看完整详情

1. 调用 **4.1 分页查询聊天列表**（`POST /ai-huiji/meetingChat/chatListByPage`），传入分页参数和筛选条件，获取 `pageContent` 列表及 `total` 总数
2. 从返回的 `pageContent` 列表中取出目标记录的 `_id`
3. 调用 **4.2 查询会议聊天详情**（`POST /ai-huiji/meetingChat/findChat`），传入 `meetingChatId = _id`，获取该条聊天的完整信息

### 场景二：查看会议报告与待办

> 需求：获取某次会议的 AI 报告和待办事项

1. 调用 **4.1 分页查询聊天列表** 或已知 `meetingChatId`
2. 调用 **4.3 查询 AI 慧记报告信息**（`POST /ai-huiji/report/reportInfo`），传入 `meetingChatId`，获取文字报告（`textReport`）和 HTML 报告（`htmlReport`）内容
3. 调用 **4.6 查询待办列表**（`POST /ai-huiji/report/todoList`），传入 `meetingChatId`，获取会议产生的待办事项

### 场景三：获取录音分片并检查转写状态

> 需求：查看某次会议的录音分片，并确认二次转写是否完成

1. 调用 **4.4 查询分片录音列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入 `meetingChatId`，获取所有分片录音
2. 调用 **4.7 检查二次语音转文字**（`POST /ai-huiji/meetingChat/checkSecondStt`）或 **4.8 检查二次语音转文字 V2**（`POST /ai-huiji/meetingChat/checkSecondSttV2`），传入 `meetingChatId`，查看转写进度与状态

### 场景四：分享会议并保存到知识库

> 需求：将某次会议分享给他人，并将报告内容保存到个人知识库

1. 调用 **4.5 创建分享 V2**（`POST /ai-huiji/meetingChat/createShareV2`），传入 `meetingChatId`，获取分享链接（`url`/`shortUrl`）
2. 调用 **4.3 查询 AI 慧记报告信息** 获取报告内容
3. 调用 **4.9 上传内容到个人知识库**（`POST /ai-huiji/uploadContentToPersonalProject`），传入报告内容（`content`）和文件名（`fileName`），保存到个人知识库

---

## 四、接口详细说明

---

### 4.1 分页查询聊天列表

按条件分页查询会议聊天列表，通常作为获取 `meetingChatId` 的入口接口。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/chatListByPage` |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名         | 类型            | 必填 | 说明                                                                                                                  |
| -------------- | --------------- | ---- | --------------------------------------------------------------------------------------------------------------------- |
| `pageSize`     | Integer         | 是   | 每页数量                                                                                                               |
| `pageNum`      | Integer         | 是   | 页码（从 0 开始）                                                                                                       |
| `chatType`     | Integer         | 否   | 类型筛选：0=玄关会议, 1=上传音频, 2=提交文字, 3=上传文本文件, 4=文件列表, 5=录音, 7=AI慧记, 8=上传音频V2                           |
| `chatTypeList` | List\<Integer\> | 否   | 类型列表，传入后忽略 `chatType`                                                                                          |
| `nameBlur`     | String          | 否   | 名称模糊搜索                                                                                                            |
| `sortKey`      | String          | 否   | 排序字段，默认 `updateTime`                                                                                              |
| `clean`        | Boolean         | 否   | 是否精简返回，默认 `false`                                                                                                |
| `sttOkOnly`    | Boolean         | 否   | 只返回转写成功的记录                                                                                                      |
| `minTs`        | Long            | 否   | 最小时间戳（毫秒）                                                                                                       |
| `maxTs`        | Long            | 否   | 最大时间戳（毫秒）                                                                                                       |

**响应参数**

`data` 类型为 `MeetingChatPageVO`，字段如下：

| 字段名        | 类型                  | 说明               |
| ------------- | --------------------- | ------------------ |
| `total`       | Long                  | 总记录数            |
| `pageContent` | List\<FindChatVO\>    | 分页内容列表，详见 **五、公共数据结构 — 5.1 FindChatVO** |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "total": 50,
    "pageContent": [
      {
        "_id": "664f1a2b3c4d5e6f7a8b9c0d",
        "name": "产品周会",
        "chatType": 7,
        "meetingBegin": 1716345600000,
        "meetingLength": 3600000,
        "summaryState": 2,
        "createTime": 1716345600000,
        "updateTime": 1716349200000
      }
    ]
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/chatListByPage' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "pageSize": 10,
    "pageNum": 0,
    "chatType": 7
  }'
```

**数据流向**

- 返回的 `pageContent[*]._id` 用于 **4.2~4.8** 各接口的 `meetingChatId` 入参

---

### 4.2 查询会议聊天详情

根据会议聊天 ID 获取单条聊天的完整信息，包括转写文本、摘要、状态等。

**基本信息**

| 项目         | 说明                              |
| ------------ | --------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/findChat` |
| 请求方式     | `POST`                            |
| Content-Type | `application/json`                |

**请求参数**

请求体为 JSON，字段如下：

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `FindChatVO`，详见 **五、公共数据结构 — 5.1 FindChatVO**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "_id": "664f1a2b3c4d5e6f7a8b9c0d",
    "name": "产品周会",
    "chatType": 7,
    "meetingTopic": "Q2产品规划讨论",
    "meetingBegin": 1716345600000,
    "meetingLength": 3600000,
    "simpleSummary": "本次会议讨论了Q2产品路线图...",
    "sttText": "大家好，今天我们主要讨论...",
    "summaryState": 2,
    "recordState": 2,
    "createTime": 1716345600000,
    "updateTime": 1716349200000,
    "delFlag": 0
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/findChat' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

---

### 4.3 查询 AI 慧记报告信息

获取指定会议聊天的文字报告和 HTML 报告内容及处理状态。

**基本信息**

| 项目         | 说明                           |
| ------------ | ------------------------------ |
| 接口地址     | `/ai-huiji/report/reportInfo` |
| 请求方式     | `POST`                         |
| Content-Type | `application/json`             |

**请求参数**

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `ReportInfoVO`，字段如下：

| 字段名       | 类型    | 说明                                        |
| ------------ | ------- | ------------------------------------------- |
| `_id`        | String  | 汇报 ID（即 meetingChatId）                   |
| `textReport` | String  | 文字报告内容                                  |
| `textState`  | Integer | 文字报告状态：0=未开始, 1=处理中, 2=成功, 3=失败 |
| `htmlReport` | String  | HTML 报告内容                                 |
| `htmlState`  | Integer | HTML 报告状态：0=未开始, 1=处理中, 2=成功, 3=失败 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "_id": "664f1a2b3c4d5e6f7a8b9c0d",
    "textReport": "## 会议纪要\n\n### 一、会议概要\n...",
    "textState": 2,
    "htmlReport": "<h2>会议纪要</h2><h3>一、会议概要</h3>...",
    "htmlState": 2
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/report/reportInfo' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

**数据流向**

- 返回的 `textReport` / `htmlReport` 可作为 **4.9 上传内容到个人知识库** 的 `content` 入参

---

### 4.4 查询分片录音列表

获取指定会议聊天的所有分片录音记录，包含每片的转写文本、状态、文件地址等。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/splitRecordList` |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `List<SplitRecordVO>`，元素字段如下：

| 字段名           | 类型                     | 说明                                     |
| ---------------- | ------------------------ | ---------------------------------------- |
| `startTime`      | Long                     | 开始时间（录音经过的毫秒数）                  |
| `text`           | String                   | 转写文本                                    |
| `realTime`       | Long                     | 现实时间戳                                   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {	
	  "realTime": 1774613847119
      "startTime": 120000,
      "text": "片段会议原文..."
    }
  ]
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/splitRecordList' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

---

### 4.5 创建分享 V2

为指定会议聊天创建分享链接，可将会议内容分享给他人。

**基本信息**

| 项目         | 说明                                   |
| ------------ | -------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/createShareV2` |
| 请求方式     | `POST`                                 |
| Content-Type | `application/json`                     |

**请求参数**

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `CreateShareV2VO`，字段如下：

| 字段名     | 类型   | 说明     |
| ---------- | ------ | -------- |
| `code`     | String | 分享码    |
| `title`    | String | 标题      |
| `shareId`  | String | 分享 ID   |
| `url`      | String | 分享链接   |
| `shortUrl` | String | 短链接    |
| `desc`     | String | 描述      |
| `imgUrl`   | String | 图片链接   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "code": "abc123",
    "title": "产品周会",
    "shareId": "share_001",
    "url": "https://example.com/share/abc123",
    "shortUrl": "https://s.example.com/abc123",
    "desc": "产品周会会议纪要",
    "imgUrl": "https://example.com/img/cover.png"
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/createShareV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

---

### 4.6 查询待办列表

获取指定会议聊天关联的待办事项列表，包含待办内容、状态、截止时间及相关人员。

**基本信息**

| 项目         | 说明                         |
| ------------ | ---------------------------- |
| 接口地址     | `/ai-huiji/report/todoList` |
| 请求方式     | `POST`                       |
| Content-Type | `application/json`           |

**请求参数**

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `List<TodoListVO>`，元素字段如下：

| 字段名             | 类型             | 说明                        |
| ------------------ | ---------------- | --------------------------- |
| `_id`              | String           | 待办 ID                      |
| `meetingChatId`    | String           | 会议聊天 ID                   |
| `text`             | String           | 待办内容                      |
| `state`            | Integer          | 状态：0=未完成, 1=已完成        |
| `deadline`         | Long             | 截止时间（毫秒时间戳）          |
| `reportEmpIdList`  | List\<String\>   | 汇报人 ID 列表                |
| `acceptEmpIdList`  | List\<String\>   | 接收人 ID 列表                |
| `cworkPlanId`      | String           | 工作协同任务 ID                |
| `reportUserList`   | List\<Object\>   | 汇报人列表                    |
| `acceptUserList`   | List\<Object\>   | 接收人列表                    |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "_id": "todo_001",
      "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d",
      "text": "完成Q2产品方案初稿",
      "state": 0,
      "deadline": 1717036800000,
      "reportEmpIdList": ["emp001"],
      "acceptEmpIdList": ["emp002", "emp003"],
      "cworkPlanId": null
    }
  ]
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/report/todoList' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

---

### 4.7 检查二次语音转文字

查询指定会议聊天的二次语音转文字处理状态、进度及重写状态。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/checkSecondStt` |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `CheckSecondSttVO`，字段如下：

| 字段名            | 类型             | 说明                                              |
| ----------------- | ---------------- | ------------------------------------------------- |
| `secondSttState`  | Integer          | 语音转文字状态：-1=未开始, 0=进行中, 1=成功, 2=失败    |
| `rewriteState`    | Integer          | 重写状态：0=未开始, 1=进行中, 2=成功                  |
| `sttProgress`     | Integer          | 语音转文字进度                                       |
| `retryTimes`      | Integer          | 重试次数                                            |
| `errMsg`          | String           | 错误信息                                            |
| `sttPartList`     | List\<Object\>   | 语音转文字分片列表                                    |
| `rewriteProgress` | Integer          | 重写进度                                            |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "secondSttState": 1,
    "rewriteState": 2,
    "sttProgress": 100,
    "retryTimes": 0,
    "errMsg": null,
    "sttPartList": [],
    "rewriteProgress": 100
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/checkSecondStt' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

---

### 4.8 检查二次语音转文字 V2

查询二次语音转文字处理状态的简化版接口，返回总进度和整体状态。

**基本信息**

| 项目         | 说明                                      |
| ------------ | ----------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/checkSecondSttV2` |
| 请求方式     | `POST`                                    |
| Content-Type | `application/json`                        |

**请求参数**

| 参数名           | 类型   | 必填 | 说明       |
| ---------------- | ------ | ---- | ---------- |
| `meetingChatId`  | String | 是   | 会议聊天 ID |

**响应参数**

`data` 类型为 `CheckSecondSttV2VO`，字段如下：

| 字段名          | 类型             | 说明                              |
| --------------- | ---------------- | --------------------------------- |
| `totalProgress` | Integer          | 总进度                             |
| `state`         | Integer          | 状态：1=进行中, 2=成功, 3=失败       |
| `sttPartList`   | List\<Object\>   | 语音转文字分片列表                    |
| `errMsg`        | String           | 错误信息                            |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "totalProgress": 100,
    "state": 2,
    "sttPartList": [],
    "errMsg": null
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/checkSecondSttV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

---

### 4.9 上传内容到个人知识库

将文本内容上传到用户个人知识库的指定文件夹中，生成文件。

**基本信息**

| 项目         | 说明                                         |
| ------------ | -------------------------------------------- |
| 接口地址     | `/ai-huiji/uploadContentToPersonalProject`  |
| 请求方式     | `POST`                                       |
| Content-Type | `application/json`                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名       | 类型   | 必填 | 说明                                      |
| ------------ | ------ | ---- | ----------------------------------------- |
| `content`    | String | 是   | 文件内容                                    |
| `fileName`   | String | 是   | 文件名称，最大长度 500 字符，超出将自动截取     |
| `fileSuffix` | String | 否   | 文件后缀，默认为 `md`                        |
| `folderName` | String | 否   | 文件夹名称，默认为 `和cms智汇的对话`           |

**响应参数**

`data` 类型为 `UploadContentToPersonalProjectResult`，字段如下：

| 字段名        | 类型   | 说明                    |
| ------------- | ------ | ----------------------- |
| `projectId`   | Long   | 空间 ID（项目 ID）        |
| `projectName` | String | 空间名称（项目名称）       |
| `folderId`    | Long   | 文件夹 ID                |
| `folderName`  | String | 文件夹名称               |
| `fileId`      | Long   | 文件 ID                  |
| `fileName`    | String | 文件名称                  |
| `downloadUrl` | String | 文件下载地址              |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "projectId": 100001,
    "projectName": "个人知识库",
    "folderId": 200001,
    "folderName": "和cms智汇的对话",
    "fileId": 300001,
    "fileName": "产品周会纪要",
    "downloadUrl": "https://example.com/download/300001"
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/uploadContentToPersonalProject' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "## 会议纪要\n\n...",
    "fileName": "产品周会纪要",
    "fileSuffix": "md",
    "folderName": "会议记录"
  }'
```

---

### 4.10 查询分片录音列表 V2

在 **4.4 查询分片录音列表** 能力基础上，增加可选参数 `lastStartTime`：传入时由 **open-api 网关**在拉取慧记服务全量分片列表后，按 `startTime` **大于** `lastStartTime` 在内存中过滤，用于增量同步；不传时与 4.4 全量行为一致。**下游慧记服务仍只接收 `meetingChatId`**，大会议场景全量拉取后再过滤时请注意性能与流量。

**基本信息**

| 项目         | 说明                                      |
| ------------ | ----------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/splitRecordListV2` |
| 请求方式     | `POST`                                    |
| Content-Type | `application/json`                        |

**请求参数**

请求体为 JSON，字段如下：

| 参数名           | 类型   | 必填 | 说明 |
| ---------------- | ------ | ---- | ---- |
| `meetingChatId`  | String | 是   | 会议聊天 ID，与 4.4 一致 |
| `lastStartTime`  | Long   | 否   | 上次已同步的最大 **startTime**（与分片上的 `startTime` 同语义，相对录音起点的毫秒）。**不传**：返回全量分片列表；**传**：仅返回 `startTime` **大于** 该值的记录（`startTime` 为 `null` 的分片在增量模式下会被过滤掉） |

**响应参数**

`data` 类型为 `List<SplitRecordVO>`，字段说明同 **4.4 查询分片录音列表**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {	
	  "realTime": 1774613847119
      "startTime": 120000,
      "text": "片段会议原文..."
    }
  ]
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/splitRecordListV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d",
    "lastStartTime": 120034
  }'
```

**说明**

- 与 **4.4** 使用相同的慧记下游接口拉取数据，**增量过滤在 open-api 侧完成**。
- 若慧记服务端后续原生支持时间筛选，可优先使用服务端能力以减少全量传输。

---

### 4.11 按会议编号查询慧记列表

根据 **会议编号** 查询当前用户相关的慧记记录列表。内部将请求转发至 **会议域 AI 摘要插件**（`getLastRecordList`），返回结构与插件一致。调用前需能通过网关解析 **当前登录员工**（如 `access-token` 等开放鉴权方式），并需携带 **`appKey`**。

**基本信息**

| 项目         | 说明                                               |
| ------------ | -------------------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber` |
| 请求方式     | `POST`                                             |
| Content-Type | `application/json`                                 |

**请求头（除 2.3 公共头外）**

| Header    | 说明 |
| --------- | ---- |
| `appKey`  | 应用密钥，与 2.3 一致，**必填**（亦支持 `app_key`） |
| （鉴权）  | 需具备员工上下文（如 `access-token` 等），由网关注入 `employeeId` 等，用于查询用户手机号并调用会议插件 |

**请求参数**

请求体为 JSON，字段如下：

| 参数名           | 类型   | 必填 | 说明 |
| ---------------- | ------ | ---- | ---- |
| `meetingNumber`  | String | 是   | 会议编号（业务约定格式） |
| `lastTs`         | Long   | 否   | 上次时间戳（增量，**毫秒**）。**未传或 ≤0**：在会议插件侧按 **最近一个月** 起点拉取；**>0**：按插件与会议域约定做增量 |

**响应参数**

`data` 类型为 `List<AiSummaryLastRecordItemVO>`，元素字段如下：

| 字段名                 | 类型    | 说明 |
| ---------------------- | ------- | ---- |
| `chatId`               | String  | 慧记/会话 ID |
| `isDoneRecordingFile`  | Boolean | 是否已完成录音文件 |
| `open`                 | Boolean | 是否开启 |
| `startTime`            | Long    | 开始时间（毫秒，语义以会议域为准） |
| `stopTime`             | Long    | 结束时间（毫秒） |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "chatId": "37644c5a-5ddd-48f1-b473-75098924d7a0",
      "isDoneRecordingFile": true,
      "open": false,
      "startTime": 0,
      "stopTime": 3600000
    }
  ]
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingNumber": "MTG-20260327-001",
    "lastTs": 0
  }'
```

**说明**

- 接口名含 “Ids” 为历史命名；当前返回为 **慧记记录项列表**（含 `chatId` 等），而非仅 ID 字符串数组。
- 需在开放平台的 **访问白名单** 中放行本路径（如 `AccessRule` / `accessUrls`），否则可能返回无权限。
- 会议域域名等由服务端配置（如 Nacos `meetingServiceHost`），与本文档 2.2 域名可能不同，以实际部署为准。

---

## 五、公共数据结构

### 5.1 FindChatVO

会议聊天详情对象，作为分页列表元素和单条查询的返回结构。

| 字段名             | 类型             | 说明                                                                                                                       |
| ------------------ | ---------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `_id`              | String           | 聊天 ID                                                                                                                    |
| `userId`           | String           | 用户 ID                                                                                                                    |
| `personId`         | String           | 人员 ID                                                                                                                    |
| `meetingId`        | String           | 会议 ID                                                                                                                    |
| `name`             | String           | 聊天名称                                                                                                                    |
| `chatType`         | Integer          | 类型：0=玄关会议, 1=上传音频, 2=提交文字, 3=上传文本文件, 4=文件列表, 5=录音, 7=AI慧记, 8=上传音频V2, 9=慧记玄关会议, 10=外部产生慧记, 101=demo |
| `qaType`           | Integer          | 问答类型：0=普通问答, 1=会议问答                                                                                               |
| `meetingTopic`     | String           | 会议主题/背景信息                                                                                                             |
| `meetingBegin`     | Long             | 会议开始时间（毫秒时间戳）                                                                                                     |
| `meetingMember`    | String           | 会议成员                                                                                                                    |
| `fileName`         | String           | 文件名                                                                                                                      |
| `fileSize`         | Long             | 文件大小                                                                                                                    |
| `fileExt`          | String           | 文件扩展名                                                                                                                   |
| `fileUrl`          | String           | 文件 URL                                                                                                                    |
| `fileHash`         | String           | 文件 Hash                                                                                                                   |
| `fileList`         | List\<Map\>      | 文件列表                                                                                                                    |
| `customWords`      | List\<String\>   | 自定义热词列表                                                                                                                |
| `simpleSummary`    | String           | 摘要                                                                                                                        |
| `tidyText`         | String           | 整理后文本                                                                                                                   |
| `srcText`          | String           | 原文                                                                                                                        |
| `sttText`          | String           | 语音转文字文本（不带发言人）                                                                                                    |
| `sttRaw`           | List\<Object\>   | 语音转文字原始数据                                                                                                             |
| `summaryState`     | Integer          | 总结状态：0=未开始, 1=进行中, 2=成功, 3=失败                                                                                    |
| `recordState`      | Integer          | 录音会议状态：0=未完成, 1=结束, 2=处理成功, 3=处理出错                                                                            |
| `combineState`     | Integer          | 文件合并状态：0=未开始, 1=处理中, 2=成功, 3=失败                                                                                 |
| `combineTs`        | Long             | 合并时间（毫秒时间戳）                                                                                                        |
| `vdbState`         | Integer          | 向量库状态：1=处理中, 2=成功, 3=失败                                                                                           |
| `vdbHash`          | String           | 向量库 Hash                                                                                                                 |
| `systemMsg`        | String           | 系统提示语                                                                                                                   |
| `keywordList`      | List\<Object\>   | 关键词列表                                                                                                                   |
| `deviceInfo`       | Map              | 设备信息                                                                                                                    |
| `encodeInfo`       | Map              | 编码信息                                                                                                                    |
| `encodedUrl`       | String           | 编码后 URL                                                                                                                  |
| `meetingLength`    | Long             | 会议时长（毫秒）                                                                                                              |
| `estimateDoneTime` | Long             | 预计完成时间（毫秒时间戳）                                                                                                     |
| `rushState`        | Integer          | 提前结束状态：空=不提前, 0=提前结束, 1=补全中, 2=补全完毕, 3=补全失败, 10=rush等待中, 11=等待中收到补全切片                              |
| `retryTimes`       | Integer          | 重试次数                                                                                                                    |
| `combineInfo`      | Map              | 合并信息                                                                                                                    |
| `lang`             | Map              | 语言设置                                                                                                                    |
| `videoUrl`         | String           | 视频地址                                                                                                                    |
| `bgInfo`           | String           | 背景信息                                                                                                                    |
| `shared`           | Boolean          | 是否已分享                                                                                                                   |
| `srcChatId`        | String           | 来源聊天 ID（复制功能）                                                                                                       |
| `originChatId`     | String           | 源头聊天 ID（复制功能）                                                                                                       |
| `srcUserId`        | String           | 来源用户 ID（复制功能）                                                                                                       |
| `createTime`       | Long             | 创建时间（毫秒时间戳）                                                                                                        |
| `updateTime`       | Long             | 更新时间（毫秒时间戳）                                                                                                        |
| `finishTime`       | Long             | 完成时间（毫秒时间戳）                                                                                                        |
| `delFlag`          | Integer          | 删除标记：0=未删除, 1=删除, 2=彻底删除                                                                                         |
| `sttInfo`          | Map              | 语音转文字信息                                                                                                                |
| `extra`            | Map              | 扩展信息                                                                                                                    |
| `meeting`          | Map              | 关联会议信息                                                                                                                 |
| `srcUser`          | Map              | 来源用户信息                                                                                                                 |

---

## 六、错误码说明

| resultCode | 说明     |
| ---------- | -------- |
| 1          | 请求成功  |
| 0          | 通用失败  |
| 500        | 系统异常  |

---

## 七、注意事项

1. **所有接口均为 POST 请求**：即使是查询类接口也使用 POST 方式，请求体为 JSON 格式。
2. **meetingChatId 为必传参数**：除分页查询接口外，其余接口均需传入 `meetingChatId`，该值来源于分页查询返回的 `_id` 字段。
3. **时间戳格式**：所有时间字段均为毫秒级时间戳（13 位），如 `1716345600000`。
4. **分页页码从 0 开始**：分页查询接口的 `pageNum` 参数从 0 开始计数。
5. **ID 精度**：`UploadContentToPersonalProjectResult` 中的 `projectId`、`folderId`、`fileId` 为 Long 类型（雪花算法），前端请用字符串接收，避免 JavaScript Number 精度丢失。
6. **鉴权方式**：所有接口需在请求头中携带 `appKey`，未携带或无效将返回鉴权失败。
7. **`_id` 字段特殊后缀处理**：部分情况下 `_id` 字段的值会以双下划线加数字结尾（如 `664f1a2b3c4d5e6f7a8b9c0d__12298`），此时不能直接将其作为 `meetingChatId` 使用。可通过以下两种方式获取正确的 `meetingChatId`：
   - 使用该记录的 `originChatId` 字段值作为 `meetingChatId`；
   - 或将 `_id` 中双下划线及其后的数字部分截掉（如 `664f1a2b3c4d5e6f7a8b9c0d__12298` → `664f1a2b3c4d5e6f7a8b9c0d`），截取后的值作为 `meetingChatId` 使用。

---

**文档版本**：v1.1
**更新日期**：2026-03-27
