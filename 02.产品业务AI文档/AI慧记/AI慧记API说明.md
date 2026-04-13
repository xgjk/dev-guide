# AI慧记 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |
| 1.1 | 2026-03-27 | 新增 4.10 增量查询指定慧记的分片录音转写列表、4.11 按视频会议号查询慧记列表 | - |
| 1.2 | 2026-03-28 | 补充场景六；明确 **4.1**（本人名下）与 **4.11**（参与会议 + 会议号）口径差异 | - |
| 1.3 | 2026-03-31 | 删除已废弃接口，重新编号接口列表；完善公共数据结构 | - |
| 1.4 | 2026-04-10 | 新增 **4.7** 通过文件URL创建慧记接口说明（`startChatByFileUrl`） | - |

> 历史版本（1.1、1.2）变更摘要中的接口编号（如 4.10、4.11）为当时文档版本，与当前「一、概述」及第四章编号不必一致。

## 一、概述

本文档描述了 **AI慧记** 模块对外开放的全部 API 接口。全部接口均为 `POST`，完整 URL 为 `https://{域名}/open-api` 加上下表「接口路径」；域名见 **2.2 环境信息**。

| 序号 | 概述中的能力名 | 文档小节 | 接口路径（相对 `/open-api`） |
|------|----------------|----------|------------------------------|
| 1 | 查询我的AI慧记列表（本人名下） | 4.1 | `/ai-huiji/meetingChat/chatListByPage` |
| 2 | 查询指定慧记的改写的原文 | 4.2 | `/ai-huiji/meetingChat/checkSecondSttV2` |
| 3 | 增量查询指定慧记的分片录音转写列表 | 4.3 | `/ai-huiji/meetingChat/splitRecordListV2` |
| 4 | 按视频会议号查询慧记列表（参与关系，含他人录制本人参会） | 4.4 | `/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumberV2` |
| 5 | 根据慧记Id创建慧记分享信息 | 4.5 | `/ai-huiji/meetingChat/createShareV2` |
| 6 | 根据慧记分享ID查询慧记信息 | 4.6 | `/ai-huiji/meetingChat/getChatFromShareId` |
| 7 | 通过文件URL创建慧记（上传音频V2） | 4.7 | `/ai-huiji/meetingChat/startChatByFileUrl` |

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

1. 调用 **4.1 查询我的AI慧记列表**（`POST /ai-huiji/meetingChat/chatListByPage`），传入分页与筛选条件（如 `chatTypeList` 等），获取 `pageContent` 与 `total`。
2. 对每条列表项，可直接用返回字段做展示与分区，无需再调接口：
   - **标题**：`name`
   - **时间线**：`createTime`、`finishTime` 等
   - **录制状态**：`recordState`，**`0`=录制中，`1`=已结束，`3`=处理出错**（详见 **五、5.1 FindChatVO**）


### 场景二：查询会议原文（会中实时展示、会后完整获取）

> **适用前提与范围**：面向需要获取**会议转写原文**的场景，**会议进行中**和**会议结束后**均可调用。根据使用阶段不同，提供两种查询模式：
> - **会中实时模式**：会议进行中，实时展示当前转写内容
> - **会后完整模式**：会议结束后，获取完整转写记录作为最终交付物

**会中实时模式**

1. 通过 **4.1** 或 **4.4** 获取进行中的 `meetingChatId`（列表项 `_id`；**4.4** 返回的 `FindChatVO` 中 **`recordState = 0`** 表示录制中）。
2. **增量查询（推荐）**：调用 **4.3 增量查询指定慧记的分片录音转写列表**（`POST /ai-huiji/meetingChat/splitRecordListV2`），传入 `meetingChatId` 与 `lastStartTime`（上次已同步的最大 `startTime`），仅获取新增片段，实现实时流式展示。

**会后完整模式**

1. 通过 **4.1** 定位 **`recordState = 1`（录制已结束）** 的慧记，或直接使用已结束会议对应的 `meetingChatId`。
2. **全量查询**：调用 **4.3 不传 `lastStartTime`**（`POST /ai-huiji/meetingChat/splitRecordListV2`）获取全量分片。


### 场景三：已结束会议获取改写原文

> **适用前提**：针对**已结束**的会议纪要（慧记）。本场景关注的是「改写原文状态与终稿可用性判断」，不是是否能查到原文分片。会后会对语音转写结果做**大模型二次改写**，整体可读性通常优于分片原文；主流程通过 **4.2** 查询改写与相关处理**是否完成、是否失败**（`POST /ai-huiji/meetingChat/checkSecondSttV2`）。  
> **时间与失败兜底**：会议结束后，终稿转写与改写仍需要一定时间；可能出现**仍在处理**、**改写失败**或**长时间未完成**等情况。此时应用侧用 **4.3 全量**（不传 `lastStartTime`）做**兜底展示**：拉取分片转写记录，将各分片 `text` 按 `startTime` / `realTime` 排序拼接，作为可阅读的「原文」展示，待 **4.2** 状态成功后再切换为改写后的终稿来源（若有单独落库字段，以产品/详情接口为准）。进行中会议的实时转写仍以**场景二**为主。

1. 确认目标为**已结束**慧记（如 **4.1** 中 **`recordState = 1`**），取得 `meetingChatId`。
2. **主路径**：调用 **4.2 检查指定慧记的改写的原文**（`POST /ai-huiji/meetingChat/checkSecondSttV2`），传入 `meetingChatId`，轮询 **`state` / `totalProgress` 等**（见 **4.2**），直到成功或明确失败/超时策略。
3. **兜底路径**：当 **4.2** 显示处理中过久、失败或暂无可用终稿时，调用 **4.3** 全量（不传 `lastStartTime`）获取全量分片，用分片 `text` 拼接作为临时原文；会中增量拉取继续配合 **4.3** 增量（见**场景二**）。

### 场景四：查询线上视频会议相关纪要并路由转写原文

> **适用范围**：面向**线上视频会议**关联的慧记。围绕某场视频会议，应优先用 **4.4** 按**视频会议号**拉取列表（口径见下方「与 4.1 的差异」）；再按**会议是否结束**选择转写/总结接口。若要做**会中实时总结或实时原文展示**，必须先根据状态分流。

> **4.1 与 4.4 的差异（重要）**：**4.1** 查的是**归属在当前用户名下**的慧记（「我的」创建/归属口径）。**4.4** 查的是**当前用户所参与的**那场**视频会议**下的慧记，按 **视频会议号** 向会议域关联查询；**即使整场会议由他人录制、慧记挂在其他同事名下，只要当前用户参与了该会议，仍可通过 4.4 查到与自己参与关系对应的慧记记录**。因此：视频会议集成、按会议号找人维度下的纪要，用 **4.4**；只浏览「我名下有哪些慧记」用 **4.1**。

**1. 定位视频会议对应的慧记（我参与的会议）**

- **按视频会议 + 我是否参与（推荐，概述表第 4 项）**：调用 **4.4 按视频会议号查询慧记列表**（`POST /ai-huiji/meetingChat/listHuiJiIdsByMeetingNumberV2`），请求体传入 **`meetingNumber`**（视频会议号，与会议域一致），可选 **`lastTs`** 做增量同步。返回的 **`data`** 为 `List<FindChatVO>`；每一项的 **`_id`** 即后续 **4.2 / 4.3** 等接口所需的 **`meetingChatId`**。可结合 **`recordState`**、`createTime`、`finishTime`、`meetingLength` 等做展示与粗判。需 **当前登录用户上下文** + **`appKey`**，详见 **4.4**。


1. **视频会议（含他人录制、本人参会）**：用 **4.4**（`meetingNumber`）→ 列表项 **`_id`** 即 `meetingChatId`；**仅查本人名下**请用 **4.1**，不按会议号从会议域反查时用 **4.1**。


---

## 四、接口详细说明

---

### 4.1 查询我的AI慧记列表

按条件分页查询**归属当前用户名下**的 AI 慧记列表（「我的」慧记），通常作为获取 `meetingChatId` 的入口接口。

**与 4.4 的差异**：本接口以慧记**归属者**为口径，返回的是挂在当前用户下的记录。**不**用于按「我参加了哪场视频会议」从会议域反查——若会议由**他人录制**、慧记归属在对方名下，即使你也参会，这里**可能查不到**，此时应使用 **4.4 按视频会议号查询慧记列表**（按 `meetingNumber` + 参会身份关联）。

**基本信息**

| 项目         | 说明                                    |
| ------------ | --------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/chatListByPage` |
| 请求方式     | `POST`                                  |
| Content-Type | `application/json`                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名         | 类型            | 必填 | 说明                                                                                                                                                                                        |
| -------------- | --------------- | ---- |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pageSize`     | Integer         | 是   | 每页数量                                                                                                                                                                                      |
| `pageNum`      | Integer         | 是   | 页码（从 0 开始）                                                                                                                                                                                |
| `chatTypeList` | List\<Integer\> | 否   | 慧记类型列表，与代码 `ChatListByPageParam` 一致。可传类型：`0` 玄关会议、`1` 用户上传音频、`2` 提交文字、`3` 上传文本文件、`4` 文件列表、`5` 录音实时转写、`6` 上传文件不总结、`7` ai慧记、`8` 上传音频V2、`9` 慧记玄关会议、`10` 外部产生慧记(合规等)、`11` 钉钉闪记。 以上类型均表示生成慧记方式 |
| `nameBlur`     | String          | 否   | 名称模糊搜索                                                                                                                                                                                    |
| `sortKey`      | String          | 否   | 排序字段，默认 `updateTime`                                                                                                                                                                      | 

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/chatListByPage' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "pageSize": 10,
    "pageNum": 0,
    "chatTypeList": [7]
  }'
```

**响应参数**

`data` 类型为 `MeetingChatPageVO`，字段如下：

| 字段名        | 类型                  | 说明               |
| ------------- | --------------------- | ------------------ |
| `total`       | Long                  | 总记录数            |
| `pageContent` | List\<FindChatVO\>    | 分页内容列表，元素结构见 **五、5.1 FindChatVO** |

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
            "name": "产品周会（录制中）",
            "recordState": 0,
            "createTime": 1716345600000,
            "finishTime": null,
            "meetingLength": null,
            "simpleSummary": null
         },
         {
            "_id": "774f1a2b3c4d5e6f7a8b9c0e",
            "name": "上周复盘（已结束）",
            "recordState": 1,
            "createTime": 1715740800000,
            "finishTime": 1715745300000,
            "meetingLength": 2700000,
            "simpleSummary": "示例摘要"
         }
      ]
   }
}
```

**数据流向**

- 列表项中的 `name`、`createTime`、`finishTime`、`recordState` 等可直接用于 UI；其中 **`recordState`**：`0`=录制中，`2`=结束，`3`=处理出错（见 **五、5.1 FindChatVO**）。
- 返回的 `pageContent[*]._id` 可作为需传入 **`meetingChatId`** 的接口（**4.2 / 4.3 / 4.5**）的入参（**4.6** 使用 `shareId`，不适用；调用前注意 **七、注意事项** 中 `_id` 带 `__` 后缀时的处理）。


### 4.2 查询指定慧记的转写状态、进度

查询指定慧记音频转文字的处理状态、进度及改写文字内容。是否已转写完成请以整体 `state` 字段为准。


**基本信息**

| 项目         | 说明                                      |
| ------------ | ----------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/checkSecondSttV2` |
| 请求方式     | `POST`                                    |
| Content-Type | `application/json`                        |

**请求参数**

| 参数名           | 类型   | 必填 | 说明    |
| ---------------- | ------ | ---- |-------|
| `meetingChatId`  | String | 是   | 慧记 ID |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/checkSecondSttV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

**响应参数**

`data` 类型为 `CheckSecondSttV2VO`字段如下：

| 字段名          | 类型                         | 说明 |
| --------------- | ---------------------------- | ---- |
| `totalProgress` | Long                         | 改写进度 |
| `state`         | Integer                      | 改写状态：`1`=进行中，`2`=成功，`3`=失败 |
| `sttPartList`   | List\<SttPartItem\>          | 文字改写分片列表；元素类型为内部类 `SttPartItem`，见下表 |
| `errMsg`        | String                       | 改写错误信息 |

`SttPartItem`（`CheckSecondSttV2VO.SttPartItem`）字段：

| 字段名         | 类型   | 说明            |
| -------------- | ------ |---------------|
| `speakerName`  | String | 发言人           |
| `rewriteText`  | String | 改写后的文本        |
| `startTime`    | Long   | 分片开始对应的慧记录制时间 |
| `rewriteState`    | Integer   | 原文改写状态: `1`=进行中, `2`=成功, `3`=失败      |

**响应示例**

```json
{
   "resultCode": 1,
   "resultMsg": null,
   "data": {
      "totalProgress": 100,
      "state": 2,
      "sttPartList": [
         {
            "speakerName": "张三",
            "rewriteText": "改写后的段落内容……",
            "startTime": 120000
         }
      ],
      "errMsg": null
   }
}
```

> 提示：该接口返回的是**当前时刻**的转写状态快照。若业务侧需要更准确地感知“是否已完成转写”，建议基于 `meetingChatId` 按固定间隔（如 2~5 秒）轮询调用本接口，并以 `state`（整体状态）作为完成判断依据；当状态为成功（`2`）后即可停止轮询。

---

### 4.3 查询指定慧记的分片录音转写列表，包含增量

查询进行中、已完成慧记的录音原文内容，按照录音分片结构返回。
请求体支持可选字段 **`lastStartTime`**：不传或者值小于0，表示查询全量内容； 其它返回所有startTime > lastStartTime 的分片原文内容。

调用方需要根据拉取到的总列表按照startTime顺序排列获得最大的startTime作为下一次调用接口时lastStartTime值，从而实现增量查询。

**基本信息**

| 项目         | 说明                                      |
| ------------ | ----------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/splitRecordListV2` |
| 请求方式     | `POST`                                    |
| Content-Type | `application/json`                        |

**请求参数**

| 参数名           | 类型   | 必填 | 说明 |
| ---------------- | ------ | ---- | ---- |
| `meetingChatId`  | String | 是   | 慧记 ID |
| `lastStartTime`  | Long   | 否   | 上次已同步的最大 `startTime`（与分片上 `startTime` 同语义，相对录音起点的毫秒）。**不传**：返回全量；**传**：仅返回 `startTime` 大于该值的记录（`startTime` 为 `null` 的分片在增量模式下会被过滤掉） |

**请求示例（全量）**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/splitRecordListV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

**请求示例（增量）**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/splitRecordListV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d",
    "lastStartTime": 120000
  }'
```

**响应参数**

`data` 类型为 `List<SplitRecordVO>`，`SplitRecordVO` 元素字段如下：

| 字段名      | 类型   | 说明 |
| ----------- | ------ | ---- |
| `text`      | String | 转写文本（会议原文片段）。 |
| `realTime`  | Long   | 现实时间戳（毫秒），用于排序与时间段筛选。 |
| `startTime` | Long   | 开始时间（相对录音起点的毫秒数），用于排序、增量与时间段筛选。 |

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

---

### 4.4 按视频会议号查询慧记列表

根据 **视频会议号**（业务侧会议编号），查询**当前用户在该场会议参与关系下**可访问的慧记记录列表。

**与 4.1 的差异**：本接口以**视频会议 + 当前用户是否参与该会议**为口径，由会议域侧关联慧记。**即使整场会议由他人发起/录制、慧记归属不在当前用户名下，只要当前用户参与了该会议，仍可能通过本接口查到对应条目**。**4.1** 则只覆盖**归属在你名下**的慧记，二者不可替代。

**基本信息**

| 项目         | 说明                                               |
| ------------ | -------------------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumberV2` |
| 请求方式     | `POST`                                             |
| Content-Type | `application/json`                                 |

**请求参数**

请求体为 JSON，字段如下：

| 参数名           | 类型   | 必填 | 说明                                                                  |
| ---------------- | ------ | ---- |---------------------------------------------------------------------|
| `meetingNumber`  | String | 是   | 视频会议号（业务约定格式，与会议域一致）                                                |
| `lastTs`         | Long   | 否   | 时间戳（增量，**毫秒**）。**未传或 ≤0**：只拉取**最近一个月** ；**>0**：拉取大于lastTs的数据，可约定做增量 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/listHuiJiIdsByMeetingNumberV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingNumber": "MTG-20260327-001",
    "lastTs": 0
  }'
```

**响应参数**

`data` 类型为 `List<FindChatVO>`，元素字段见 **五、5.1 FindChatVO**（本接口由会议插件记录组装的字段可能少于 **4.1** 全量列表，以实际返回为准）。

**响应示例**

```json
{
   "resultCode": 1,
   "resultMsg": null,
   "data": [
      {
         "_id": "37644c5a-5ddd-48f1-b473-75098924d7a0",
         "name": "周例会",
         "recordState": 1,
         "createTime": 0,
         "finishTime": 3600000,
         "meetingLength": 3600000,
         "tidyText": null,
         "simpleSummary": null,
         "keywordList": null,
         "personId": null
      }
   ]
}
```


### 4.5 根据慧记Id创建慧记分享信息

为指定慧记创建分享，返回分享码、分享 ID、链接等信息；下游与 `createShareV2` 一致。创建成功后可将返回的 **`shareId`** 用于 **4.6 根据慧记分享ID查询慧记信息**。

**基本信息**

| 项目         | 说明                                      |
| ------------ | ----------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/createShareV2`     |
| 请求方式     | `POST`                                    |
| Content-Type | `application/json`                        |

**请求参数**

请求体为 JSON，与 `MeetingChatIdParam` 一致：

| 参数名           | 类型   | 必填 | 说明    |
| ---------------- | ------ | ---- | ------- |
| `meetingChatId`  | String | 是   | 慧记 ID |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/createShareV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingChatId": "664f1a2b3c4d5e6f7a8b9c0d"
  }'
```

**响应参数**

`data` 类型为 `CreateShareV2VO`（与代码 `com.xgjktech.openapi.feign.aihuiji.vo.CreateShareV2VO` 一致），字段如下：

| 字段名      | 类型   | 说明     |
| ----------- | ------ | -------- |
| `code`      | String | 分享码   |
| `title`     | String | 标题     |
| `shareId`   | String | 分享 ID  |
| `url`       | String | 分享链接 |
| `shortUrl`  | String | 短链接   |
| `desc`      | String | 描述     |
| `imgUrl`    | String | 图片链接 |

**响应示例**

```json
{
   "resultCode": 1,
   "resultMsg": null,
   "data": {
      "code": "ABC123",
      "title": "产品周会",
      "shareId": "83780c2a-572f-4c3f-a964-d542f2a1372c",
      "url": "https://example.com/share/...",
      "shortUrl": "https://s.example.com/xxxxx",
      "desc": null,
      "imgUrl": null
   }
}
```

---

### 4.6 根据慧记分享ID查询慧记信息

根据慧记分享 ID 查询（或通过分享复制）慧记会议信息，通常用于「他人通过分享链接打开慧记」或业务侧根据分享码查询慧记详情。分享 ID 可由 **4.5** 创建分享接口返回。

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

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/getChatFromShareId' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "shareId": "83780c2a-572f-4c3f-a964-d542f2a1372c"
  }'
```

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
| `srcUser`          | Object                | 分享来源用户信息；常见子字段：`_id`（用户 ID）、`name`（用户名称） |
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

---

### 4.7 通过文件URL创建慧记

通过可访问的音频文件 URL 发起慧记创建。

**基本信息**

| 项目         | 说明                                           |
| ------------ | ---------------------------------------------- |
| 接口地址     | `/ai-huiji/meetingChat/startChatByFileUrl`    |
| 请求方式     | `POST`                                        |
| Content-Type | `application/json`                            |

**请求参数**

请求体为 JSON，字段如下（与 `StartChatByFileUrlParam` 一致）：

| 参数名      | 类型    | 必填 | 说明 |
| ----------- | ------- | ---- | ---- |
| `fileUrl`   | String  | 是   | 音频/视频文件可访问 URL。 |
| `fileExt`   | String  | 是   | 文件扩展名（不含点，内部会规范化）。当前支持：`mp3`、`mp4`、`wav`、`m4a`。 |

> 文件URL建议：推荐先将文件上传到七牛，拿到可公网访问的 URL（例如 `https://...`）后，再将该地址作为 `fileUrl` 传入本接口。获取七牛上传 token 的接口请参考 [《基础服务-> API接口明细-> 文件服务 4.3章节》](https://github.com/xgjk/dev-guide/blob/main/02.%E4%BA%A7%E5%93%81%E4%B8%9A%E5%8A%A1AI%E6%96%87%E6%A1%A3/%E5%9F%BA%E7%A1%80%E6%9C%8D%E5%8A%A1/API%E6%8E%A5%E5%8F%A3%E6%98%8E%E7%BB%86/02-%E6%96%87%E4%BB%B6%E6%9C%8D%E5%8A%A1.md#43-%E8%8E%B7%E5%8F%96%E4%B8%83%E7%89%9B%E4%B8%8A%E4%BC%A0-token)。


**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/ai-huiji/meetingChat/startChatByFileUrl' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "fileUrl": "https://filegpt-hn.file.mediportal.com.cn/21ccb6c1-6500-46f8-a4ff-d26deb73c36c语音035.m4a",
    "fileExt": "m4a"
  }'
```

**响应参数**

`data` 类型为 `StartChatResultVO`，常用字段如下：

| 字段名       | 类型    | 说明 |
| ------------ | ------- | ---- |
| `_id`        | String  | 慧记 ID。 |
| `chatType`   | Integer | 慧记类型。 |
| `recordState`| Integer | 当前处理状态（`0` 录制中，`2` 结束，`3` 处理出错）。 |
| `fileUrl`    | String  | 文件 URL。 |
| `fileExt`    | String  | 文件扩展名。 |
| `name`       | String  | 慧记名称。 |
| `createTime` | Long    | 创建时间（毫秒）。 |
| `updateTime` | Long    | 更新时间（毫秒）。 |
| `personId`   | String  | 人员 ID。 |
| `userId`     | String  | 用户 ID。 |

**响应示例**

```json
{
   "resultCode": 1,
   "resultMsg": null,
   "data": {
      "_id": "e6839164-2491-4fb3-899a-c27fedb82a68",
      "chatType": 8,
      "recordState": 2,
      "fileUrl": "https://filegpt-hn.file.mediportal.com.cn/21ccb6c1-6500-46f8-a4ff-d26deb73c36c语音035.m4a",
      "fileExt": "m4a",
      "name": "2026-04-10 11:17:13 记录",
      "createTime": 1775791033252,
      "updateTime": 1775791033252,
      "personId": "12028",
      "userId": "1742024210481586177"
   }
}
```

## 五、公共数据结构

> 本章列出**在多个接口中复用、且返回结构一致**的数据结构（当前仅 **FindChatVO**）。仅在单接口出现的结构（如 **4.3** 的 `SplitRecordVO`）已在对应 **四、接口详细说明** 中描述。

### 5.1 FindChatVO（4.1 / 4.4）

与代码 `com.xgjktech.openapi.feign.aihuiji.vo.FindChatVO` 一致；**4.1** 列表项与 **4.4** 返回项均为该结构（**4.4** 可能仅填充部分字段）。

| 字段名          | 类型                   | 说明 |
| --------------- | ---------------------- | ---- |
| `_id`           | String                 | 会议 ID（即 `meetingChatId`）。 |
| `name`          | String                 | 会议名称。 |
| `recordState`   | Integer                | 录音状态：`0` 录制中，`2` 结束，`3` 处理出错。 |
| `createTime`    | Long                   | 创建时间（毫秒时间戳）。 |
| `finishTime`    | Long                   | 完成时间（毫秒时间戳）。 |
| `meetingLength` | Long                   | 会议时长（毫秒）。 可能为空，例如：慧记为结束|
| `tidyText`      | String                 | 整理后正文摘要。 可能为空，整理失败或者未生成 |
| `simpleSummary` | String                 | 简单摘要（`tidyText` 为空时兜底）。 可能为空，失败或者未生成|
| `keywordList`   | List\<KeywordItem\>    | 关键词列表。 可能为空，失败或者未生成 |
| `personId`      | String                 | 拥有者标识（内部用）。 可能为空，没有拥有者|

`keywordList` 元素 `KeywordItem`：`keyword`（String）。

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
2. **meetingChatId / 入参约定**：**4.1** 为分页查询，无 `meetingChatId`；**4.4** 入参为 `meetingNumber`（及可选 `lastTs`）；**4.5** 入参为 **`meetingChatId`**（创建分享）；**4.6** 入参为 **`shareId`**（根据分享查询）。其余需定位慧记的接口使用请求体中的 **`meetingChatId`**。`meetingChatId` 通常取自 **4.1** 或 **4.4** 列表项的 **`_id`**（二者口径差异见 **场景四** 与 **4.1 / 4.4**）。
3. **时间戳格式**：所有时间字段均为毫秒级时间戳（13 位），如 `1716345600000`。
4. **分页页码从 0 开始**：**4.1 查询我的AI慧记列表** 的 `pageNum` 参数从 0 开始计数。
5. **ID 精度**：凡后端可能以 Long（雪花）下发的 ID 字段，前端建议以**字符串**接收与传递，避免 JavaScript `Number` 精度丢失。
6. **鉴权方式**：所有接口需在请求头中携带 `appKey`，未携带或无效将返回鉴权失败。
7. **`_id` 字段特殊后缀处理**：部分情况下 `_id` 字段的值会以双下划线加数字结尾（如 `664f1a2b3c4d5e6f7a8b9c0d__12298`），此时不能直接将其作为 `meetingChatId` 使用。可通过以下两种方式获取正确的 `meetingChatId`：
   - 使用该记录的 `originChatId` 字段值作为 `meetingChatId`；
   - 或将 `_id` 中双下划线及其后的数字部分截掉（如 `664f1a2b3c4d5e6f7a8b9c0d__12298` → `664f1a2b3c4d5e6f7a8b9c0d`），截取后的值作为 `meetingChatId` 使用。

---

**文档版本**：v1.4
**更新日期**：2026-04-10
