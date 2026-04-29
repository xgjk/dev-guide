# OpenClaw 文件服务 API 说明文档

> **本文档的读者是 AI，不是开发者。** 所有接口文档用于 AI 编写 Skill，规则围绕"AI 能否高效准确地理解和使用接口"设计。

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|-----|
| 1.0 | 2026-04-29 | 初版创建，基于 XG-File 独立文件管理中台 API | AI助手 |
| 1.1 | 2026-04-29 | 按照《开放平台 API 编写规范》重构文档结构，增加详细响应参数说明与 AI 决策列 | AI助手 |

---

## 一、概述

OpenClaw 文件服务（XG-File）是为 OpenClaw 生态设计的独立文件管理中台，提供以下核心能力：

1.  **业务隔离（Bucket）**：为不同 Agent 或项目提供独立的存储命名空间。
2.  **高性能存储**：支持物理秒传（MD5 去重）与逻辑树形目录管理。
3.  **跨 Agent 共享**：通过统一的 `nodeId` 实现跨服务器、跨 Agent 的文件交换。
4.  **版本溯源**：保留文件覆盖上传的历史版本，支持回溯下载。

### 1.1 名词解释

| 名词 | 英文名/Key | 定义与作用 | 典型示例 |
|---|---|---|---|
| **业务桶** | `bucketCode` | 顶层隔离容器。不同桶之间的文件完全隔离，必须先注册桶才能上传。 | `OPENCLAW_PROD`, `PROJECT_ALPHA` |
| **节点 ID** | `nodeId` | 文件的**逻辑唯一标识**。无论物理存储在哪里（七牛/本地），均通过该 ID 进行下载或操作。 | `50012345` |
| **逻辑路径** | `path` | 文件在桶内的虚拟目录结构。支持多层嵌套，与物理存储路径无关。 | `/ai/reports/2026/04/` |
| **冲突策略** | `strategy` | 当上传路径已存在同名文件时的处理规则。 | `2` (自动重命名) |
| **物理秒传** | - | 基于文件 MD5 校验，若系统已存在相同文件，则直接建立逻辑关联，无需重复传输物理字节。 | - |

---

## 二、通用说明

### 2.1 访问地址
所有接口均通过 HTTPS 协议访问：
```
https://xg-file.mediportal.com.cn{接口地址}
```

### 2.2 环境信息
| 环境 | Base URL | 备注 |
|---|---|---|
| 生产 | `https://xg-file.mediportal.com.cn` | 默认环境 |

### 2.3 公共请求头
| Header | 必填 | 说明 |
|---|---|---|
| `appKey` | 是 | 玄关开放平台统一授权密钥 |
| `Content-Type` | POST 必填 | `application/json` 或 `multipart/form-data` (上传时) |

### 2.4 通用响应结构
```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": null
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `resultCode` | Integer | `1` = 成功，其他 = 失败 |
| `resultMsg` | String | 错误描述文案 |
| `data` | T | 业务数据，具体结构见各接口定义 |

### 2.5 错误码
| resultCode | 说明 | AI 处理动作 |
|---|---|---|
| 1 | 成功 | 读取 data |
| 0 | 业务/参数错误 | 读取 resultMsg 展示给用户 |
| 500 | 系统异常 | 稍后重试 |

---

## 三、业务流程

### 3.1 跨 Agent 文件交换流程
1.  **初始化**：调用 `3.1.1 注册业务桶` 为项目创建存储空间。
2.  **产出数据**：Agent A 调用 `3.2.1 单文件直传` 上传文件，获得 `nodeId`。
3.  **传递引用**：Agent A 将 `nodeId` 发送给 Agent B。
4.  **消费数据**：Agent B 调用 `3.2.7 获取真实下载链接` 获取 302 重定向并下载。

---

## 四、接口详细说明

### 3.1 业务桶管理

#### 3.1.1 注册业务桶
用于初始化一个新的逻辑存储空间，默认使用系统全局七牛云配置。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/bucket/register` |
| 请求方式 | POST |
| 数据量级别 | 小 |
| 预估响应体积 | 约 0.5KB |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `bucketCode` | Query | String | 是 | 桶编码 (如: `OPENCLAW_001`) |
| `bucketName` | Query | String | 否 | 桶名称 (用于展示) |

**请求示例**
```bash
curl -X POST 'https://xg-file.mediportal.com.cn/v1/bucket/register?bucketCode=MY_BUCKET&bucketName=测试桶' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应参数**
`data` 类型为 `5.3 Bucket`:

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 否 | 记录 ID |
| `bucketCode` | String | 是 | 桶编码 |
| `bucketName` | String | 否 | 桶名称 |

**响应示例**
```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": {
    "id": 1001,
    "bucketCode": "MY_BUCKET",
    "bucketName": "测试桶"
  }
}
```

---

### 3.2 文件与目录管理

#### 3.2.1 单文件直传
上传物理文件至指定的逻辑路径，支持自动秒传。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/upload` |
| 请求方式 | POST |
| Content-Type | multipart/form-data |
| 数据量级别 | 小 (响应体积) |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 | 典型示例 |
|---|---|---|---|---|---|
| `bucketCode` | Query | String | 是 | **业务桶编码**。必须是已通过 `/register` 注册成功的编码。若包含特殊字符，需进行 **URL Encode**。 | `OPENCLAW_COMMON` |
| `path` | Query | String | 否 | **逻辑上传路径**。以 `/` 开头，不含文件名。目录不存在时会自动创建。若包含特殊字符或中文，需进行 **URL Encode**。 | `/reports/daily` |
| `strategy` | Query | Integer | 否 | **同名冲突策略**：<br>1: **报错** (若存在同名则返回失败);<br>2: **重命名** (默认，自动在名后加 `(1)`);<br>3: **覆盖** (建立新版本，保留旧版本在历史中) | `3` |
| `file` | Body | Binary | 是 | **物理文件**。Multipart 表单中的文件流。 | - |

**请求示例**
```bash
# 注意：path 参数值已进行 URL Encode 处理
curl -X POST 'https://xg-file.mediportal.com.cn/v1/file/upload?bucketCode=MY_BUCKET&path=%2Fopenclaw%2Ftask-results%2F2026-04-29' \
  -H 'appKey: YOUR_APP_KEY' \
  -F 'file=@/path/to/test.pdf'
```

**响应参数**
`data` 类型为 `5.1 FileNodeVO`:

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | **文件节点 ID**，用于后续下载 |
| `nodeName` | String | 是 | 文件名 |
| `fullPath` | String | 否 | 逻辑全路径 |
| `versionNum` | Integer | 是 | 当前版本号 |

**响应示例**
```json
{
  "resultCode": 1,
  "data": {
    "id": 5001,
    "nodeName": "test.pdf",
    "fullPath": "/openclaw/task-results/2026-04-29/test.pdf",
    "versionNum": 1
  }
}
```

#### 3.2.2 全路径模糊搜索
在整个业务桶内模糊匹配节点名称或路径。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/search` |
| 请求方式 | GET |
| 数据量级别 | 中 |

**请求参数**
| 参数名 | 类型 | 必选 | 说明 |
|---|---|---|---|
| `bucketCode` | String | 是 | 业务桶编码 |
| `keyword` | String | 是 | 搜索关键词。若包含中文或特殊符号，需进行 **URL Encode**。 |

**请求示例**
```bash
curl -X GET 'https://xg-file.mediportal.com.cn/v1/file/search?bucketCode=MY_BUCKET&keyword=test' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应参数**
`data` 类型为 `List<5.1 FileNodeVO>`:
（字段结构同 3.2.3）

#### 3.2.3 查询目录列表
获取指定层级下的文件和子目录列表。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/list` |
| 请求方式 | GET |
| 数据量级别 | 中 |
| 默认返回条数 | 不分页 |

**请求参数**
| 参数名 | 类型 | 必选 | 说明 |
|---|---|---|---|
| `bucketCode` | String | 是 | 业务桶编码 |
| `parentId` | Long | 否 | 父级节点ID (传0表示查询根目录) |

**请求示例**
```bash
curl -X GET 'https://xg-file.mediportal.com.cn/v1/file/list?bucketCode=MY_BUCKET&parentId=0' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应参数**
`data` 类型为 `List<5.1 FileNodeVO>`:

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 节点 ID |
| `nodeName` | String | 是 | 名称 |
| `isDir` | Integer | 是 | 是否目录 (1:是, 0:否) |
| `updateTime` | String | 是 | ISO 8601 UTC 毫秒精度 |

#### 3.2.4 查询历史版本列表
获取某文件的所有历史版本记录（按版本号倒序）。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/history/{nodeId}` |
| 请求方式 | GET |
| 数据量级别 | 中 |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `nodeId` | Path | Long | 是 | 文件节点 ID |

**请求示例**
```bash
curl -X GET 'https://xg-file.mediportal.com.cn/v1/file/history/5001' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应参数**
`data` 类型为 `List<5.2 FileHistoryVO>`:

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 历史记录 ID |
| `versionNum` | Integer | 是 | 版本号 |
| `createTime` | String | 是 | 该版本上传时间 |

#### 3.2.5 下载历史版本
通过历史记录 ID 重定向下载对应版本的文件。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/history/download/{historyId}` |
| 请求方式 | GET |
| 数据量级别 | 小 |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `historyId` | Path | Long | 是 | 历史记录 ID |

**请求示例**
```bash
curl -i -X GET 'https://xg-file.mediportal.com.cn/v1/file/history/download/9001' \
  -H 'appKey: YOUR_APP_KEY'
```

#### 3.2.6 获取文件外链链接
返回该文件在物理存储中的直接访问地址。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/getDownloadUrl/{nodeId}` |
| 请求方式 | GET |
| 数据量级别 | 小 |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `nodeId` | Path | Long | 是 | 文件节点 ID |

**请求示例**
```bash
curl -X GET 'https://xg-file.mediportal.com.cn/v1/file/getDownloadUrl/5001' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应参数**
`data` 类型为 `String`: 原始下载 URL。

#### 3.2.7 获取真实下载链接 (302)
自动解析底层存储，并返回 302 重定向至实际物理下载地址。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/download/{nodeId}` |
| 请求方式 | GET |
| 数据量级别 | 小 |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `nodeId` | Path | Long | 是 | 文件节点 ID |

**请求示例**
```bash
curl -i -X GET 'https://xg-file.mediportal.com.cn/v1/file/download/5001' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应说明**
该接口返回 `302 Found` 状态码，`Location` 响应头即为真实下载链接。

---

## 五、公共数据结构

### 5.1 FileNodeVO
文件或目录节点展示对象。

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 节点唯一 ID (即 **nodeId**) |
| `parentId` | Long | 否 | 父节点 ID |
| `nodeName` | String | 是 | 节点名称 |
| `fullPath` | String | 否 | 全路径 |
| `isDir` | Integer | 是 | 1:目录; 0:文件 |
| `versionNum` | Integer | 是 | 当前版本号 |
| `creatorName`| String | 否 | 上传人姓名 |
| `createTime` | String | 是 | ISO 8601 UTC 毫秒精度 |
| `updateTime` | String | 否 | ISO 8601 UTC 毫秒精度 |

### 5.2 FileHistoryVO
文件历史版本记录。

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 历史记录 ID (用于下载旧版本) |
| `nodeId` | Long | 是 | 关联的文件节点 ID |
| `versionNum` | Integer | 是 | 版本号 |
| `creatorName`| String | 否 | 上传人 |
| `createTime` | String | 是 | 上传时间 |

### 5.3 Bucket
业务桶配置对象。

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 桶记录 ID |
| `bucketCode` | String | 是 | 桶编码 |
| `bucketName` | String | 否 | 桶名称 |
| `storageType` | String | 否 | 存储类型 |
| `createTime` | String | 否 | 创建时间 |

---

## 六、变更管理

| 项 | 约定 |
|---|---|
| 时间口径 | 所有接口统一使用 UTC 时区，ISO 8601 毫秒精度字符串。 |
| ID 精度 | `Long` 类型 ID 在 JSON 中应以数字返回，但 AI/前端解析时务必转为字符串防止精度丢失。 |
| 冲突处理 | 默认 `strategy=2`，即自动在文件名后追加数字防止覆盖。 |
