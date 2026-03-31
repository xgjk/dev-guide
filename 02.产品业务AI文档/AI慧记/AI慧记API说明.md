# AI慧记 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.3 | 2026-03-31 | 删除已废弃接口，重新编号接口列表；完善公共数据结构 | - |
| 1.2 | 2026-03-28 | 补充场景六；明确 **4.1**（本人名下）与 **4.11**（参与会议 + 会议号）口径差异 | - |
| 1.1 | 2026-03-27 | 新增 4.10 增量查询指定慧记的分片录音转写列表、4.11 按视频会议号查询慧记列表 | - |
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |

## 一、概述

本文档描述了 **AI慧记** 模块对外开放的全部 API 接口。全部接口均为 `POST`，完整 URL 为 `https://{域名}/open-api` 加上下表「接口路径」；域名见 **2.2 环境信息**。

| 序号 | 概述中的能力名 | 文档小节 | 接口路径（相对 `/open-api`） |
|------|----------------|----------|------------------------------|
| 1 | 查询我的AI慧记列表（本人名下） | 4.1 | `/ai-huiji/meetingChat/chatListByPage` |
| 2 | 查询指定慧记的分片录音转写列表 | 4.2 | `/ai-huiji/meetingChat/splitRecordList` |
| 3 | 检查指定慧记的改写的原文（废弃） | 4.3 | `/ai-huiji/meetingChat/checkSecondStt` |
| 4 | 检查指定慧记的改写的原文 | 4.4 | `/ai-huiji/meetingChat/checkSecondSttV2` |
| 5 | 增量查询指定慧记的分片录音转写列表 | 4.5 | `/ai-huiji/meetingChat/splitRecordListV2` |
| 6 | 按视频会议号查询慧记列表（参与关系，含他人录制本人参会） | 4.6 | `/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber` |
| 7 | 根据慧记分享ID查询慧记信息 | 4.7 | `/ai-huiji/meetingChat/getChatFromShareId` |

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境   | 域名/Base URL                    | 备注 |
| ------ | ------------------------------- | ---- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn`      | -    |

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
   - **进行中 / 已结束**：`combineState`，**`0`=进行中，`2`=已完成**（详见 **5.2.2** 中该字段说明）


### 场景二：查询会议原文（会中实时展示、会后完整获取）

> **适用前提与范围**：面向需要获取**会议转写原文**的场景，**会议进行中**和**会议结束后**均可调用。根据使用阶段不同，提供两种查询模式：
> - **会中实时模式**：会议进行中，实时展示当前转写内容
> - **会后完整模式**：会议结束后，获取完整转写记录作为最终交付物

**会中实时模式**

1. 通过 **4.1** 或 **4.6** 获取进行中的 `meetingChatId`（`combineState = 0`）。
2. **增量查询（推荐）**：调用 **4.5 增量查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordListV2`），传入 `meetingChatId` 与 `lastStartTime`（上次已同步的最大 `startTime`），仅获取新增片段，实现实时流式展示。

**会后完整模式**

1. 通过 **4.1** 定位 **`combineState = 2`（已完成）** 的慧记，或直接使用已结束会议对应的 `meetingChatId`。
2. **全量查询**：调用 **4.2 查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入 `meetingChatId`，获取完整的分片转写记录，拼接形成会议原文交付物。


### 场景三：已结束会议获取改写原文

> **适用前提**：针对**已结束**的会议纪要（慧记）。本场景关注的是「改写原文状态与终稿可用性判断」，不是是否能查到原文分片。会后会对语音转写结果做**大模型二次改写**，整体可读性通常优于分片原文；主流程通过 **4.4** 查询改写与相关处理**是否完成、是否失败**（`POST /ai-huiji/meetingChat/checkSecondSttV2`）。  
> **时间与失败兜底**：会议结束后，终稿转写与改写仍需要一定时间；可能出现**仍在处理**、**改写失败**或**长时间未完成**等情况。此时应用侧应用 **4.2** 做**兜底展示**：调用 **4.2 查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入同一 `meetingChatId`，取**录制过程中**已落库的分片转写记录，将各分片 `text` 按 `startTime` / `realTime` 排序拼接，作为可阅读的「原文」展示，待 **4.4** 状态成功后再切换为改写后的终稿来源（若有单独落库字段，以产品/详情接口为准）。进行中会议的实时转写仍以**场景二**为主。

1. 确认目标为**已结束**慧记（如 **4.1** 中 **`combineState = 2`**），取得 `meetingChatId`。
2. **主路径**：调用 **4.4 检查指定慧记的改写的原文**（`POST /ai-huiji/meetingChat/checkSecondSttV2`），传入 `meetingChatId`，轮询 **`state` / `totalProgress` 等**（见 **4.4**），直到成功或明确失败/超时策略。新对接请勿使用已废弃的 **4.3**。
3. **兜底路径**：当 **4.4** 显示处理中过久、失败或暂无可用终稿时，调用 **4.2 查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordList`），传入同一 `meetingChatId`，获取全量分片转写记录，用分片 `text` 拼接作为临时原文；会中增量拉取习惯可继续配合 **4.5**（见**场景二**）。

### 场景四：查询线上视频会议相关纪要并路由转写原文

> **适用范围**：面向**线上视频会议**关联的慧记。围绕某场视频会议，应优先用 **4.6** 按**视频会议号**拉取列表（口径见下方「与 4.1 的差异」）；再按**会议是否结束**选择转写/总结接口。若要做**会中实时总结或实时原文展示**，必须先根据状态分流。

> **4.1 与 4.6 的差异（重要）**：**4.1** 查的是**归属在当前用户名下**的慧记（「我的」创建/归属口径）。**4.6** 查的是**当前用户所参与的**那场**视频会议**下的慧记，按 **视频会议号** 向会议域关联查询；**即使整场会议由他人录制、慧记挂在其他同事名下，只要当前用户参与了该会议，仍可通过 4.6 查到与自己参与关系对应的慧记记录**。因此：视频会议集成、按会议号找人维度下的纪要，用 **4.6**；只浏览「我名下有哪些慧记」用 **4.1**。

**1. 定位视频会议对应的慧记（我参与的会议）**

- **按视频会议 + 我是否参与（推荐，概述表第 7 项）**：调用 **4.6 按视频会议号查询慧记列表**（`POST /ai-huiji/meetingChat/listHuiJiIdsByMeetingNumber`），请求体传入 **`meetingNumber`**（视频会议号，与会议域一致），可选 **`lastTs`** 做增量同步。返回的 **`data`** 为该会议下、与**当前登录用户参与关系**相关的慧记条目列表；每一项的 **`chatId`** 即后续 **4.2 / 4.4 / 4.5** 等接口所需的 **`meetingChatId`**。列表侧可结合 **`open`**、**`isDoneRecordingFile`**、**`startTime`** / **`stopTime`** 等做展示与粗判（语义以会议域为准）。需 **当前登录用户上下文** + **`appKey`**，详见 **4.6**。


1. **视频会议（含他人录制、本人参会）**：用 **4.6**（`meetingNumber`）→ **`chatId`** 即 `meetingChatId`；**仅查本人名下**或不传入`meetingNumber`，是查询我的参与过的视频会议相关的会议纪要列表。 


---

## 四、接口详细说明

---

### 4.1 查询我的AI慧记列表

按条件分页查询**归属当前用户名下**的 AI 慧记列表（「我的」慧记），通常作为获取 `meetingChatId` 的入口接口。

**与 4.6 的差异**：本接口以慧记**归属者**为口径，返回的是挂在当前用户下的记录。**不**用于按「我参加了哪场视频会议」从会议域反查——若会议由**他人录制**、慧记归属在对方名下，即使你也参会，这里**可能查不到**，此时应使用 **4.6 按视频会议号查询慧记列表**（按 `meetingNumber` + 参会身份关联）。

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
| `chatType`     | Integer         | 否   | 支持类型：0:玄关会议 1:用户上传音频文件 2:提交文字 3:上传文本文件 4:文件列表 5:录音实时转写 6:上传文件不总结 7:ai慧记 8:上传音频V2, 9:慧记玄关会议, 10:外部产生慧记(合规等), 11:钉钉闪记 |
| `chatTypeList` | List\<Integer\> | 否   | 类型列表，传入后忽略 `chatType`                                                                                          |
| `nameBlur`     | String          | 否   | 名称模糊搜索                                                                                                            |
| `sortKey`      | String          | 否   | 排序字段，默认 `updateTime`                                                                                              | 

**响应参数**

`data` 类型为 `MeetingChatPageVO`，字段如下：

| 字段名        | 类型                  | 说明               |
| ------------- | --------------------- | ------------------ |
| `total`       | Long                  | 总记录数            |
| `pageContent` | List\<FindChatVO\>    | 分页内容列表，详见 **五、公共数据结构 — 5.2.2 FindChatVO** |

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

**数据流向**

- 列表项中的 `name`、`meetingBegin`、`updateTime`、`combineState` 等可直接用于 UI；其中 **`combineState`：`0`=进行中，`2`=已完成**。
- 返回的 `pageContent[*]._id` 可作为 **4.2~4.7** 等接口的 `meetingChatId` 入参（调用前注意 **七、注意事项** 中 `_id` 带 `__` 后缀时的处理）。


### 4.2 查询指定慧记的分片录音转写列表

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

### 4.3 检查指定慧记的改写的原文（废弃）

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

### 4.4 检查指定慧记的改写的原文

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

### 4.5 增量查询指定慧记的分片录音转写列表

在 **4.2 查询指定慧记的分片录音转写列表** 能力基础上，增加可选参数 `lastStartTime`：传入时由 **open-api 网关**在拉取慧记服务全量分片列表后，按 `startTime` **大于** `lastStartTime` 在内存中过滤，用于增量同步；不传时与 4.2 全量行为一致。**下游慧记服务仍只接收 `meetingChatId`**，大会议场景全量拉取后再过滤时请注意性能与流量。

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

`data` 类型为 `List<SplitRecordVO>`，字段说明同 **4.2 查询指定慧记的分片录音转写列表**。

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

### 4.6 按视频会议号查询慧记列表

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

### 4.7 根据慧记分享ID查询慧记信息

根据慧记分享 ID 查询（或通过分享复制）慧记会议信息，通常用于「他人通过分享链接打开慧记」或业务侧根据分享码查询慧记详情。

**基本信息**

| 项目         | 说明                                           |
| ------------ | ---------------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/getChatFromShareId`    |
| 请求方式     | `POST`                                        |
| Content-Type | `application/json`                            |

**请求参数**

请求体为 JSON，字段如下：

| 参数名      | 类型   | 必填 | 说明         |
| ----------- | ------ | ---- | ------------ |
| `shareId`   | String | 是   | 慧记分享 ID  |

**响应参数**

`data` 类型为 `ChatShareIdVO`，字段如下（多余字段可能由后端扩展，未列出部分可按需忽略）：

| 字段名             | 类型                  | 说明                  |
| ------------------ | --------------------- | --------------------- |
| `_id`              | String                | 慧记 ID               |
| `chatType`         | Integer               | 聊天类型               |
| `createTime`       | Long                  | 创建时间（毫秒）        |
| `meetingLength`    | Long                  | 会议时长（毫秒）        |
| `name`             | String                | 会议名称               |
| `simpleSummary`    | String                | 简要摘要               |
| `srcText`          | String                | 原始文本               |
| `srcUser`          | Object                | 分享来源用户信息，结构见 **5.3 ChatShareIdVO.SrcUser** |
| `updateTime`       | Long                  | 更新时间（毫秒）        |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "_id": "664f1a2b3c4d5e6f7a8b9c0d",
    "chatType": 7,
    "createTime": 1716345600000,
    "meetingLength": 3600000,
    "name": "产品周会（分享副本）",
    "simpleSummary": "本次会议讨论了Q2产品路线图...",
    "srcText": "大家好，今天我们主要讨论...",
    "srcUser": {
      "_id": "user_001",
      "name": "张三"
    },
    "updateTime": 1716349200000
  }
}
```

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/getChatFromShareId' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "shareId": "83780c2a-572f-4c3f-a964-d542f2a1372c"
  }'
```

## 五、公共数据结构

### 5.1 请求参数数据接口

> 本小节对各 Param 的字段做详细说明，字段与代码中的属性一一对应。

#### 5.1.1 ChatListByPageParam（4.1）

| 字段名         | 类型             | 说明 |
| -------------- | ---------------- | ---- |
| `pageSize`     | Integer          | 每页数量，必填。 |
| `pageNum`      | Integer          | 页码（从 0 开始），必填。 |
| `chatTypeList` | List\<Integer\>  | 慧记类型列表，可传类型：0:玄关会议 1:用户上传音频文件 2:提交文字 3:上传文本文件 4:文件列表 5:录音实时转写 6:上传文件不总结 7:ai慧记 8:上传音频V2, 9:慧记玄关会议, 10:外部产生慧记(合规等), 11:钉钉闪记。为空时不过滤类型。 |
| `nameBlur`     | String           | 搜索关键字，名称模糊搜索。 |
| `sortKey`      | String           | 排序字段，可选值：`createTime`、`updateTime`，默认 `updateTime`。 |

#### 5.1.2 MeetingChatIdParam（4.2 / 4.3 / 4.4 等）

| 字段名          | 类型    | 说明 |
| --------------- | ------- | ---- |
| `meetingChatId` | String  | 慧记 ID，必填；来源见「七、注意事项」。 |

#### 5.1.3 SplitRecordListParam（4.5）

继承自 `MeetingChatIdParam`，在其基础上新增如下字段：

| 字段名          | 类型   | 说明 |
| --------------- | ------ | ---- |
| `lastStartTime` | Long   | 上次已同步的最大开始时间（毫秒，相对录音起点）。不传则返回全量；传则仅返回 `startTime` 大于该值的增量分片。 |

#### 5.1.4 MeetingNumberParam（4.6）

| 字段名          | 类型   | 说明 |
| --------------- | ------ | ---- |
| `meetingNumber` | String | 会议编号（业务侧约定格式），必填。 |
| `lastTs`        | Long   | 上次时间戳（毫秒，增量用）。未传或 ≤0 时按最近一个月拉取，由下游约定。 |

#### 5.1.5 ChatShareIdParam（4.7）

| 字段名    | 类型   | 说明 |
| --------- | ------ | ---- |
| `shareId` | String | 慧记分享 ID，必填。 |

### 5.2 响应VO数据接口

#### 5.2.1 MeetingChatPageVO（4.1）

| 字段名        | 类型                | 说明 |
| ------------- | ------------------- | ---- |
| `total`       | Long                | 总记录数。 |
| `pageContent` | List\<FindChatVO\>  | 慧记数据列表，元素结构见 5.2.2 `FindChatVO`。 |

#### 5.2.2 FindChatVO

慧记详情对象（精简版），字段按当前 `FindChatVO` 代码定义整理如下：

| 字段名         | 类型                   | 说明 |
| -------------- | ---------------------- | ---- |
| `_id`          | String                 | 会议 ID（`meetingChatId`）。 |
| `name`         | String                 | 会议名称。 |
| `combineState` | Integer                | 分片文件合并状态：`0`=进行中，`2`=已完成（前提：会议结束后才会进行文件合并）。 |
| `createTime`   | Long                   | 创建时间（毫秒时间戳）。 |
| `finishTime`   | Long                   | 完成时间（毫秒时间戳）。 |
| `meetingLength`| Long                   | 会议时长（毫秒）。 |
| `tidyText`     | String                 | 整理后正文摘要。 |
| `simpleSummary`| String                 | 简单摘要（`tidyText` 为空时兜底）。 |
| `keywordList`  | List\<KeywordItem\>    | 关键词列表。 |
| `personId`     | String                 | 拥有者标识（内部用）。 |

`keywordList` 元素 `KeywordItem` 字段：

| 字段名     | 类型   | 说明 |
| ---------- | ------ | ---- |
| `keyword`  | String | 关键词。 |

---

#### 5.2.3 CheckSecondSttVO / CheckSecondSttV2VO

> 对应 **4.3 / 4.4** 的返回结构，仅列出网关透出的核心字段，具体字段以运行时返回为准。

**CheckSecondSttVO（4.3）**

| 字段名        | 类型                    | 说明                          |
| ------------- | ----------------------- | ----------------------------- |
| `sttPartList` | List\<SttPartItem\>     | 二次转写内容列表                |

其中 `SttPartItem` 字段如下：

| 字段名        | 类型   | 说明                          |
| ------------- | ------ | ----------------------------- |
| `speakerName` | String | 发言人名称                     |
| `rewriteText` | String | 转写/改写后的文字内容           |
| `startTime`   | Long   | 相对会议开始时间（毫秒，用于排序） |

**CheckSecondSttV2VO（4.4）**

| 字段名        | 类型                    | 说明                          |
| ------------- | ----------------------- | ----------------------------- |
| `sttPartList` | List\<SttPartItem\>     | 语音转文字分片列表              |

其中 `SttPartItem` 字段与上表一致。

---

#### 5.2.4 SplitRecordVO（4.2 / 4.5）

| 字段名      | 类型   | 说明                         |
| ----------- | ------ |----------------------------|
| `text`      | String | 会议原文文本。                    |
| `realTime`  | Long   | 现实时间戳（毫秒），用于排序与时间段筛选。      |
| `startTime` | Long   | 开始时间（录音经过的毫秒数），用于排序与时间段筛选。 |

---

#### 5.2.5 AiSummaryLastRecordItemVO（4.6）

| 字段名               | 类型    | 说明 |
| -------------------- | ------- | ---- |
| `chatId`             | String  | 慧记/会话 ID。 |
| `isDoneRecordingFile` | Boolean | 是否已完成录音文件。 |
| `open`               | Boolean | 是否开启。 |
| `startTime`          | Long    | 开始时间（毫秒）。 |
| `stopTime`           | Long    | 结束时间（毫秒）。 |
| `chatName`           | String  | 慧记标题。 |
| `userName`           | String  | 用户名称。 |

---

#### 5.2.6 ChatShareIdVO.SrcUser

> 对应 **4.7 根据慧记分享ID查询慧记信息** 中的 `srcUser` 字段。

| 字段名 | 类型   | 说明   |
| ------ | ------ | ------ |
| `_id`  | String | 用户 ID |
| `name` | String | 用户名称 |

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
2. **meetingChatId 与入参约定**：除 **4.1 查询我的AI慧记列表**、**4.6 按视频会议号查询慧记列表**（入参为 `meetingNumber`）外，其余接口均需传入 `meetingChatId`。`meetingChatId` 可来自 **4.1** 列表项的 `_id`（**本人名下**慧记），或 **4.6** 返回项的 **`chatId`**（**按视频会议参与关系**，含他人录制、本人参会）；二者口径差异见 **场景四** 与 **4.1 / 4.6** 章节说明。
3. **时间戳格式**：所有时间字段均为毫秒级时间戳（13 位），如 `1716345600000`。
4. **分页页码从 0 开始**：**4.1 查询我的AI慧记列表** 的 `pageNum` 参数从 0 开始计数。
5. **ID 精度**：`UploadContentToPersonalProjectResult` 中的 `projectId`、`folderId`、`fileId` 为 Long 类型（雪花算法），前端请用字符串接收，避免 JavaScript Number 精度丢失。
6. **鉴权方式**：所有接口需在请求头中携带 `appKey`，未携带或无效将返回鉴权失败。
7. **`_id` 字段特殊后缀处理**：部分情况下 `_id` 字段的值会以双下划线加数字结尾（如 `664f1a2b3c4d5e6f7a8b9c0d__12298`），此时不能直接将其作为 `meetingChatId` 使用。可通过以下两种方式获取正确的 `meetingChatId`：
   - 使用该记录的 `originChatId` 字段值作为 `meetingChatId`；
   - 或将 `_id` 中双下划线及其后的数字部分截掉（如 `664f1a2b3c4d5e6f7a8b9c0d__12298` → `664f1a2b3c4d5e6f7a8b9c0d`），截取后的值作为 `meetingChatId` 使用。

---

**文档版本**：v1.3
**更新日期**：2026-03-31
