# AI慧记 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.2 | 2026-03-28 | 补充场景六；明确 **4.1**（本人名下）与 **4.11**（参与会议 + 会议号）口径差异 | - |
| 1.1 | 2026-03-27 | 新增 4.10 增量查询指定慧记的分片录音转写列表、4.11 按视频会议号查询慧记列表 | - |
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |

## 一、概述

本文档描述了 **AI慧记** 模块对外开放的全部 API 接口。全部接口均为 `POST`，完整 URL 为 `https://{域名}/open-api` 加上下表「接口路径」；域名见 **2.2 环境信息**。

| 序号 | 概述中的能力名 | 文档小节 | 接口路径（相对 `/open-api`） |
|------|----------------|----------|------------------------------|
| 1 | 查询我的AI慧记列表（本人名下） | 4.1 | `/ai-huiji/meetingChat/chatListByPage` |
| 2 | 查询指定慧记详情（废弃） | 4.2 | `/ai-huiji/meetingChat/findChat` |
| 3 | 查询指定慧记报告信息 | 4.3 | `/ai-huiji/report/reportInfo` |
| 4 | 查询指定慧记的分片录音转写列表 | 4.4 | `/ai-huiji/meetingChat/splitRecordList` |
| 5 | 创建指定慧记分享地址 V2 | 4.5 | `/ai-huiji/meetingChat/createShareV2` |
| 6 | 查询指定慧记待办事项列表 | 4.6 | `/ai-huiji/report/todoList` |
| 7 | 检查指定慧记的改写的原文（废弃） | 4.7 | `/ai-huiji/meetingChat/checkSecondStt` |
| 8 | 检查指定慧记的改写的原文 | 4.8 | `/ai-huiji/meetingChat/checkSecondSttV2` |
| 9 | 报告内容上传到个人知识库 | 4.9 | `/ai-huiji/uploadContentToPersonalProject` |
| 10 | 增量查询指定慧记的分片录音转写列表 | 4.10 | `/ai-huiji/meetingChat/splitRecordListV2` |
| 11 | 按视频会议号查询慧记列表（参与关系，含他人录制本人参会） | 4.11 | `/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber` |

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

### 场景一：查询我的会议纪要列表并查看详情

> 需求：分页拉取「我的会议纪要」列表；列表中需能区分**进行中的纪要**与**已结束的纪要**，并可点进某条查看完整详情。

1. 调用 **4.1 查询我的AI慧记列表**（`POST /ai-huiji/meetingChat/chatListByPage`），传入分页与筛选条件（如 `chatType` 等），获取 `pageContent` 与 `total`。
2. 对每条列表项，可直接用返回字段做展示与分区，无需再调接口：
   - **标题**：`name`
   - **时间线**：`meetingBegin`（开始）、`updateTime`（最近更新）等
   - **进行中 / 已结束**：`combineState`，**`0`=进行中，`2`=已完成**（详见 **5.1 FindChatVO** 中该字段说明）


### 场景二：获取已结束会议的纪要报告与待办

> **适用前提与范围**：面向**已结束的会议**所对应的慧记。会结束后，慧记系统会**自动生成**会议纪要类报告（文字 / HTML）；本场景用于在**报告已生成（或生成成功）**的前提下，拉取**现成的**纪要报告内容与从纪要中抽取的**待办事项**。进行中的会议、或报告尚未生成 / 仍处理中时，返回内容可能为空或状态非成功，需结合 **4.3** 返回的 `textState`、`htmlState` 判断，或待会议结束且生成完成后再调。

1. 通过 **4.1 查询我的AI慧记列表** 定位 **`combineState = 2`（已完成）** 的慧记，或直接使用已结束会议对应的 `meetingChatId`。
2. 调用 **4.3 查询指定慧记报告信息**（`POST /ai-huiji/report/reportInfo`），传入 `meetingChatId`，读取已落库的文字纪要（`textReport`）与 HTML 纪要（`htmlReport`）；通过 `textState`、`htmlState` 确认是否已生成成功（枚举见 **4.3** 响应说明）。
3. 在报告已就绪的前提下，调用 **4.6 查询指定慧记待办事项列表**（`POST /ai-huiji/report/todoList`），传入同一 `meetingChatId`，获取系统生成的**待办事项列表**。

### 场景三：未结束会议中获取实时转写原文

> **适用前提**：会议**尚未结束**（如列表项 **`combineState = 0`（进行中）**），尚无最终纪要报告或仍以「边录边转」为主。要展示**会议进行过程中的实时转写原文**，应依赖**分片转写列表**：每个分片上的 `text` 即为该时段转写内容，客户端可**定时轮询**以拉取最新分片。**核心接口**为 **4.4**（`ai-huiji/meetingChat/splitRecordList`）；需**增量**同步时使用 **4.10**（`ai-huiji/meetingChat/splitRecordListV2`），通过 **`lastStartTime`** 与上次进度对齐（详见 **4.10**）。

1. 通过 **4.1** 拿到进行中慧记的 `meetingChatId`，或从会中业务侧已持有的会话 ID 直接调用下文接口。
2. **全量**：调用 **4.4 查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入 `meetingChatId`，获取截至当前的所有分片转写记录；按 `startTime` / `realTime` 排序或拼接即可呈现连续转写原文（字段见 **4.4**）。
3. **增量（推荐）**：调用 **4.10 增量查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordListV2`），传入 `meetingChatId` 与 **`lastStartTime`**（上次已同步的最大 `startTime`），网关仅返回 `startTime` 大于该值的片段，减少重复传输；大会议全量后再过滤时注意性能与流量（说明见 **4.10**）。

### 场景四：已结束会议获取改写原文

> **适用前提**：针对**已结束**的会议纪要（慧记）。会后会对语音转写结果做**大模型二次改写**，整体可读性通常优于会中实时分片转写；主流程通过 **4.8** 查询改写与相关处理**是否完成、是否失败**（`POST /ai-huiji/meetingChat/checkSecondSttV2`）。  
> **时间与失败兜底**：会议结束后，终稿转写与改写仍需要一定时间；可能出现**仍在处理**、**改写失败**或**长时间未完成**等情况。此时应用侧应用 **4.4** 做**兜底展示**：调用 **4.4 查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入同一 `meetingChatId`，取**录制过程中**已落库的分片转写记录，将各分片 `text` 按 `startTime` / `realTime` 排序拼接，作为可阅读的「原文」展示，待 **4.8** 状态成功后再切换为改写后的终稿来源（若有单独落库字段，以产品/详情接口为准）。进行中会议的实时转写仍以**场景三**为主。

1. 确认目标为**已结束**慧记（如 **4.1** 中 **`combineState = 2`**），取得 `meetingChatId`。
2. **主路径**：调用 **4.8 检查指定慧记的改写的原文**（`POST /ai-huiji/meetingChat/checkSecondSttV2`），传入 `meetingChatId`，轮询 **`state` / `totalProgress` 等**（见 **4.8**），直到成功或明确失败/超时策略。新对接请勿使用已废弃的 **4.7**。
3. **兜底路径**：当 **4.8** 显示处理中过久、失败或暂无可用终稿时，调用 **4.4 查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入同一 `meetingChatId`，获取全量分片转写记录，用分片 `text` 拼接作为临时原文；会中增量拉取习惯可继续配合 **4.10**（见**场景三**）。

### 场景五：分享纪要给他人并保存到知识库

> **分享**：用户要把某条纪要**分享给他人**时，通过 **4.5** 生成可转发的分享地址（`url` / `shortUrl`）。分享链路要求**对方需要接受/确认**才算生效，因此返回的链接带有**时效性**：**自生成时起 24 小时内有效**，超时后链接不可用，需重新调用 **4.5** 生成新地址（若服务端策略调整，以实际配置为准）。  
> **知识库**：若同时要把报告正文归档到个人知识库，再执行下方第 2、3 步。

1. 调用 **4.5 创建指定慧记分享地址 V2**（`POST /ai-huiji/meetingChat/createShareV2`），传入 `meetingChatId`，获取分享链接；将链接发给对方，并在 **24 小时有效期内** 完成对方侧的接受流程。
2. 调用 **4.3 查询指定慧记报告信息** 获取报告内容（适用前提同**场景二**，一般为已结束且报告已生成）。
3. 调用 **4.9 报告内容上传到个人知识库**（`POST /ai-huiji/uploadContentToPersonalProject`），传入报告内容（`content`）和文件名（`fileName`），保存到个人知识库。


### 场景六：查询线上视频会议相关纪要并路由转写原文

> **适用范围**：面向**线上视频会议**关联的慧记。围绕某场视频会议，应优先用 **4.11** 按**视频会议号**拉取列表（口径见下方「与 4.1 的差异」）；再按**会议是否结束**选择转写/总结接口。若要做**会中实时总结或实时原文展示**，必须先根据状态分流。

> **4.1 与 4.11 的差异（重要）**：**4.1** 查的是**归属在当前用户名下**的慧记（「我的」创建/归属口径）。**4.11** 查的是**当前用户所参与的**那场**视频会议**下的慧记，按 **视频会议号** 向会议域关联查询；**即使整场会议由他人录制、慧记挂在其他同事名下，只要当前用户参与了该会议，仍可通过 4.11 查到与自己参与关系对应的慧记记录**。因此：视频会议集成、按会议号找人维度下的纪要，用 **4.11**；只浏览「我名下有哪些慧记」用 **4.1**。

**1. 定位视频会议对应的慧记（我参与的会议）**

- **按视频会议 + 我是否参与（推荐，概述表第 11 项）**：调用 **4.11 按视频会议号查询慧记列表**（`POST /ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber`），请求体传入 **`meetingNumber`**（视频会议号，与会议域一致），可选 **`lastTs`** 做增量同步。返回的 **`data`** 为该会议下、与**当前登录用户参与关系**相关的慧记条目列表；每一项的 **`chatId`** 即后续 **4.4 / 4.8 / 4.10** 等接口所需的 **`meetingChatId`**。列表侧可结合 **`open`**、**`isDoneRecordingFile`**、**`startTime`** / **`stopTime`** 等做展示与粗判（语义以会议域为准）。需 **当前登录用户上下文** + **`appKey`**，详见 **4.11**。


1. **视频会议（含他人录制、本人参会）**：用 **4.11**（`meetingNumber`）→ **`chatId`** 即 `meetingChatId`；**仅查本人名下**或不传入`meetingNumber`，是查询我的参与过的视频会议相关的会议纪要列表。 


---

## 四、接口详细说明

---

### 4.1 查询我的AI慧记列表

按条件分页查询**归属当前用户名下**的 AI 慧记列表（「我的」慧记），通常作为获取 `meetingChatId` 的入口接口。

**与 4.11 的差异**：本接口以慧记**归属者**为口径，返回的是挂在当前用户下的记录。**不**用于按「我参加了哪场视频会议」从会议域反查——若会议由**他人录制**、慧记归属在对方名下，即使你也参会，这里**可能查不到**，此时应使用 **4.11 按视频会议号查询慧记列表**（按 `meetingNumber` + 参会身份关联）。

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
        "name": "产品周会（进行中）",
        "chatType": 7,
        "meetingBegin": 1716345600000,
        "meetingLength": 3600000,
        "combineState": 0,
        "summaryState": 2,
        "createTime": 1716345600000,
        "updateTime": 1716349200000
      },
      {
        "_id": "774f1a2b3c4d5e6f7a8b9c0e",
        "name": "上周复盘（已结束）",
        "chatType": 7,
        "meetingBegin": 1715740800000,
        "meetingLength": 2700000,
        "combineState": 2,
        "summaryState": 2,
        "createTime": 1715740800000,
        "updateTime": 1715745300000
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

- 列表项中的 `name`、`meetingBegin`、`updateTime`、`combineState` 等可直接用于 UI；其中 **`combineState`：`0`=进行中，`2`=已完成**。
- 返回的 `pageContent[*]._id` 可作为 **4.2~4.8** 等接口的 `meetingChatId` 入参（调用前注意 **七、注意事项** 中 `_id` 带 `__` 后缀时的处理）。

---

### 4.2 查询指定慧记详情（废弃）

> **废弃说明**：该接口已废弃，新集成请避免依赖；存量对接如需保留请联系管理员。

根据慧记 ID（`meetingChatId`）获取单条慧记的完整信息，包括转写文本、摘要、状态等。

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

### 4.3 查询指定慧记报告信息

获取指定慧记的文字报告和 HTML 报告内容及处理状态。

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

- 返回的 `textReport` / `htmlReport` 可作为 **4.9 报告内容上传到个人知识库** 的 `content` 入参

---

### 4.4 查询指定慧记的分片录音转写列表

获取指定慧记的全部分片录音转写记录，包含每片的转写文本、时间等。

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
	  "realTime": 1774613847119,
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

### 4.5 创建指定慧记分享地址 V2

为指定慧记创建分享链接，便于将纪要分享给他人。分享需**接收方接受**后方可生效，因此返回的 `url` / `shortUrl` 具有**时效性**：**生成后 24 小时内有效**，过期需重新调用本接口获取新链接（具体以部署环境配置为准）。

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

### 4.6 查询指定慧记待办事项列表

获取指定慧记关联的待办事项列表，包含待办内容、状态、截止时间及相关人员。

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

### 4.7 检查指定慧记的改写的原文（废弃）

> **废弃说明**：该接口已废弃，新集成请优先使用 **4.8**；存量对接如需保留请联系管理员。

查询指定慧记的改写原文相关处理状态、进度及重写状态（与网关/服务内「二次语音转文字」字段语义一致）。

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

### 4.8 检查指定慧记的改写的原文

查询指定慧记改写原文的处理状态（简化版接口），返回总进度和整体状态（与 **4.7** 相比字段更精简，推荐使用）。

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

### 4.9 报告内容上传到个人知识库

将文本内容（例如报告正文）上传到用户个人知识库的指定文件夹中，生成文件。

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

### 4.10 增量查询指定慧记的分片录音转写列表

在 **4.4 查询指定慧记的分片录音转写列表** 能力基础上，增加可选参数 `lastStartTime`：传入时由 **open-api 网关**在拉取慧记服务全量分片列表后，按 `startTime` **大于** `lastStartTime` 在内存中过滤，用于增量同步；不传时与 4.4 全量行为一致。**下游慧记服务仍只接收 `meetingChatId`**，大会议场景全量拉取后再过滤时请注意性能与流量。

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
| `meetingChatId`  | String | 是   | 慧记 ID（`meetingChatId`），与 4.4 一致 |
| `lastStartTime`  | Long   | 否   | 上次已同步的最大 **startTime**（与分片上的 `startTime` 同语义，相对录音起点的毫秒）。**不传**：返回全量分片列表；**传**：仅返回 `startTime` **大于** 该值的记录（`startTime` 为 `null` 的分片在增量模式下会被过滤掉） |

**响应参数**

`data` 类型为 `List<SplitRecordVO>`，字段说明同 **4.4 查询指定慧记的分片录音转写列表**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {	
	  "realTime": 1774613847119,
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

- 与 **4.4**（查询指定慧记的分片录音转写列表）使用相同的慧记下游接口拉取数据，**增量过滤在 open-api 侧完成**。
- 若慧记服务端后续原生支持时间筛选，可优先使用服务端能力以减少全量传输。

---

### 4.11 按视频会议号查询慧记列表

根据 **视频会议号**（业务侧会议编号），查询**当前用户在该场会议参与关系下**可访问的慧记记录列表。内部将请求转发至 **会议域 AI 摘要插件**（`getLastRecordList`），返回结构与插件一致。调用前需能通过网关解析 **当前登录员工**（如 `access-token` 等开放鉴权方式），并需携带 **`appKey`**。

**与 4.1 的差异**：本接口以**视频会议 + 当前用户是否参与该会议**为口径，由会议域侧关联慧记。**即使整场会议由他人发起/录制、慧记归属不在当前用户名下，只要当前用户参与了该会议，仍可能通过本接口查到对应条目**。**4.1** 则只覆盖**归属在你名下**的慧记，二者不可替代。

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
| `meetingNumber`  | String | 是   | 视频会议号（业务约定格式，与会议域一致） |
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
- 列表范围由**会议域**按「该用户与此 `meetingNumber` 对应会议的参与关系」判定，**与慧记是否归属在当前用户名下无必然一致**（典型场景：**他人录制、本人参会**仍可查询）。
- 需在开放平台的 **访问白名单** 中放行本路径（如 `AccessRule` / `accessUrls`），否则可能返回无权限。
- 会议域域名等由服务端配置（如 Nacos `meetingServiceHost`），与本文档 2.2 域名可能不同，以实际部署为准。

---

## 五、公共数据结构

### 5.1 FindChatVO

慧记详情对象，作为分页列表元素和单条查询的返回结构。

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
| `combineState`     | Integer          | 纪要合并状态；**列表侧常用：`0`=进行中，`2`=已完成**，用于区分进行中的纪要与已结束的纪要。与文件合并流程同源，亦可能出现 `1`（处理中）、`3`（失败）等取值，以实际返回为准。                                                                                 |
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
2. **meetingChatId 与入参约定**：除 **4.1 查询我的AI慧记列表**、**4.9 报告内容上传到个人知识库**（入参为 `content`/`fileName` 等）、**4.11 按视频会议号查询慧记列表**（入参为 `meetingNumber`）外，其余接口均需传入 `meetingChatId`。`meetingChatId` 可来自 **4.1** 列表项的 `_id`（**本人名下**慧记），或 **4.11** 返回项的 **`chatId`**（**按视频会议参与关系**，含他人录制、本人参会）；二者口径差异见 **场景六** 与 **4.1 / 4.11** 章节说明。
3. **时间戳格式**：所有时间字段均为毫秒级时间戳（13 位），如 `1716345600000`。
4. **分页页码从 0 开始**：**4.1 查询我的AI慧记列表** 的 `pageNum` 参数从 0 开始计数。
5. **ID 精度**：`UploadContentToPersonalProjectResult` 中的 `projectId`、`folderId`、`fileId` 为 Long 类型（雪花算法），前端请用字符串接收，避免 JavaScript Number 精度丢失。
6. **鉴权方式**：所有接口需在请求头中携带 `appKey`，未携带或无效将返回鉴权失败。
7. **`_id` 字段特殊后缀处理**：部分情况下 `_id` 字段的值会以双下划线加数字结尾（如 `664f1a2b3c4d5e6f7a8b9c0d__12298`），此时不能直接将其作为 `meetingChatId` 使用。可通过以下两种方式获取正确的 `meetingChatId`：
   - 使用该记录的 `originChatId` 字段值作为 `meetingChatId`；
   - 或将 `_id` 中双下划线及其后的数字部分截掉（如 `664f1a2b3c4d5e6f7a8b9c0d__12298` → `664f1a2b3c4d5e6f7a8b9c0d`），截取后的值作为 `meetingChatId` 使用。

---

**文档版本**：v1.2
**更新日期**：2026-03-28
