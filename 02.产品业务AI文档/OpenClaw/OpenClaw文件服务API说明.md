# OpenClaw 文件服务 API 说明文档

> **本文档的读者是 AI，不是开发者。** 所有接口文档用于 AI 编写 Skill，规则围绕"AI 能否高效准确地理解和使用接口"设计。

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|-----|
| 1.0 | 2026-04-29 | 初版创建，基于 XG-File 独立文件管理中台 API | AI助手 |
| 1.1 | 2026-04-29 | 按照《开放平台 API 编写规范》重构文档结构，增加详细响应参数说明与 AI 决策列 | AI助手 |
| 1.2 | 2026-05-02 | 1. 新增/修改/删除部分API接口<br>2. 新增 WebDAV 协议支持及使用章节 | AI助手 |

---

## 一、概述

OpenClaw 文件服务（XG-File）是为 OpenClaw 生态设计的独立文件管理中台，提供以下核心能力：

1.  **业务隔离（Bucket）**：为不同 Agent 或项目提供独立的存储命名空间。
2.  **高性能存储**：支持存储层物理去重（基于 MD5）与逻辑树形目录管理。
3.  **跨 Agent 共享**：通过统一的 `nodeId` 实现跨服务器、跨 Agent 的文件交换。
4.  **版本溯源**：保留文件覆盖上传的历史版本，支持回溯下载。
5.  **WebDAV 支持**：提供标准的 WebDAV 挂载能力，兼容主流操作系统与客户端。

### 1.1 名词解释

| 名词 | 英文名/Key | 定义与作用 | 典型示例 |
|---|---|---|---|
| **业务桶** | `bucketCode` | 顶层隔离容器。不同桶之间的文件完全隔离，必须先注册桶才能上传。 | `OPENCLAW_PROD`, `PROJECT_ALPHA` |
| **节点 ID** | `nodeId` | 文件的**逻辑唯一标识**。无论物理存储在哪里（七牛/本地），均通过该 ID 进行下载或操作。 | `50012345` |
| **逻辑路径** | `path` | 文件在桶内的虚拟目录结构。支持多层嵌套，与物理存储路径无关。 | `/ai/reports/2026/04/` |
| **冲突策略** | `strategy` | 当上传路径已存在同名文件时的处理规则。 | `2` (自动重命名) |
| **物理去重** | - | 无论重复上传多少次相同内容的文件（尽管网络仍然会传输文件数据到服务端），底层存储只会保留一份物理文件副本，仅建立多个逻辑关联，大幅节省存储空间。 | - |

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

跨 Agent 进行文件协同共享时，支持两种引用传递模式：

**模式一：基于 nodeId 传递（推荐用于精确版本控制）**
1.  **初始化**：调用 `5.1.1 注册业务桶` 为项目创建存储空间（如已创建则跳过）。
2.  **产出数据**：Agent A 调用 `5.2.1 单文件直传` 上传文件，解析响应获得 `nodeId`。
3.  **传递引用**：Agent A 将 `nodeId` 发送给 Agent B。
4.  **消费数据**：Agent B 调用 `5.2.4 获取单文件外链` 获取带有鉴权码的 URL。
5.  **安全下载**：Agent B 使用鉴权码调用 `5.2.6 安全核销下载` 获取真实的物理文件流。

**模式二：基于 业务桶(bucketCode) + 逻辑路径(path) 传递（推荐用于目录结构协同）**
1.  **产出数据**：Agent A 将文件上传至指定的 `bucketCode` 和逻辑 `path`（例如 `/reports/2026/summary.pdf`）。
2.  **传递引用**：Agent A 将 `bucketCode` 和 `path` 发送给 Agent B。
3.  **消费数据**：Agent B 收到后，有两种获取方式：一是直接拼接 WebDAV 链接（`https://xg-file.mediportal.com.cn/dav/{bucketCode}{path}`），使用 `appKey` 作为密码进行基础认证（Basic Auth）后直接下载文件或挂载目录；二是通过调用 `5.2.7 获取全量层级树` 或 `5.2.8 获取全量打平列表` 接口，传入 `bucketCode` 和所在目录的 `path`，精确查询出该文件或目录下的所有子文件并提取对应的 `nodeId`，然后再走模式一进行下载。

---

## 四、WebDAV 协议支持（新增）

XG-File 提供了标准的 WebDAV 协议支持，允许客户端（如 Windows 资源管理器、macOS Finder、Obsidian 等）像操作本地文件系统一样直接读写云端逻辑文件树，所有操作均实时与后端 API 保持同步。

### 4.1 访问地址与鉴权

- **WebDAV 挂载根路径**: `https://xg-file.mediportal.com.cn/dav/{bucketCode}/`
- **认证方式**: Basic Auth (基本认证)
- **账号**: 任意不为空的字符串（系统忽略账号字段校验）
- **密码**: 填入开放平台分配的 `appKey`

> **提示：** 必须使用已通过 API 注册过的 `bucketCode` 才能成功挂载，否则会返回 404/未授权。

### 4.2 核心特性

- **无缝映射**: WebDAV 视图直接映射对应 `bucketCode` 桶内的逻辑目录（`/`）。
- **完全兼容**: 支持多级目录创建（MKCOL）、文件上传（PUT）、修改、删除（DELETE）、移动重命名（MOVE/COPY）及属性读取（PROPFIND）。
- **分布式并发锁**: 内置基于 Redis 的 WebDAV 标准锁机制（支持 Exclusive 写锁），防止多端并发编辑或上传导致的数据不一致问题。
- **一致性**: 走 WebDAV 协议上传的文件会自动触发系统物理文件去重与版本管理策略。

### 4.3 常用客户端挂载指引

1. **Windows 资源管理器**: 
   - 映射网络驱动器 -> 选择文件夹路径 -> 输入 `https://xg-file.mediportal.com.cn/dav/{bucketCode}/`。
   - 勾选“使用其他凭据连接”，输入账号和 `appKey` 作为密码。
2. **macOS Finder**:
   - 前往 -> 连接服务器 -> 输入网址同上 -> 连接身份使用“注册用户”，密码输入 `appKey`。
3. **Obsidian (Remotely Save 插件)**:
   - 选择 WebDAV 协议，输入上述服务端地址、任意账号以及 `appKey` 作为密码，即可实现知识库与 XG-File 桶实时双向同步。

---

## 五、接口详细说明

### 5.1 业务桶管理

#### 5.1.1 注册业务桶
用于初始化一个新的逻辑存储空间，支持动态指定存储引擎与配置。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/bucket/register` |
| 请求方式 | POST |
| 数据量级别 | 小 |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `bucketCode` | Query | String | 是 | 桶编码 (如: `OPENCLAW_001`) |
| `bucketName` | Query | String | 否 | 桶名称 (用于展示) |
| `storageType` | Query | String | 否 | 存储类型，可选值：`QINIU`（七牛云存储）、`LOCAL`（本地存储）。**推荐默认使用 `LOCAL`**。如果不传则系统底层默认为 `QINIU`。 |
| `storageConfig` | Query | String | 否 | 个性化配置 (JSON 字符串格式)，为空则使用系统全局配置 |

**请求示例**
```bash
curl -X POST 'https://xg-file.mediportal.com.cn/v1/bucket/register?bucketCode=MY_BUCKET&bucketName=测试桶' \
  -H 'appKey: YOUR_APP_KEY'
```

**响应参数**
`data` 类型为 `6.3 Bucket`:

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 否 | 记录 ID |
| `bucketCode` | String | 是 | 桶编码 |
| `bucketName` | String | 否 | 桶名称 |

---

### 5.2 文件与目录管理

#### 5.2.1 单文件直传
上传物理文件至指定的逻辑路径，服务端会自动进行文件级物理去重，避免重复占用存储。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/upload` |
| 请求方式 | POST |
| Content-Type | multipart/form-data |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 | 典型示例 |
|---|---|---|---|---|---|
| `bucketCode` | Query | String | 是 | **业务桶编码**。必须是已注册的编码。若包含特殊字符需 URL Encode。 | `OPENCLAW_COMMON` |
| `path` | Query | String | 否 | **逻辑上传路径**。默认为根目录 `/`。 | `/reports/daily` |
| `strategy` | Query | Integer | 否 | **冲突策略**: 1-报错, 2-自动重命名(默认), 3-覆盖。 | `2` |
| `file` | Body | Binary | 是 | **物理文件**。Multipart 表单中的文件流。 | - |

#### 5.2.2 查询目录列表
获取指定层级下的直接子文件和子目录列表。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/list` |
| 请求方式 | GET |

**请求参数**
| 参数名 | 类型 | 必选 | 说明 |
|---|---|---|---|
| `bucketCode` | String | 是 | 业务桶编码 |
| `parentId` | Long | 否 | 父级节点ID (传0或不传表示查询根目录) |

**响应参数**
`data` 类型为 `List<6.1 FileNodeVO>`。

#### 5.2.3 全路径模糊搜索
在整个业务桶内模糊匹配节点名称或路径。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/search` |
| 请求方式 | GET |

**请求参数**
| 参数名 | 类型 | 必选 | 说明 |
|---|---|---|---|
| `bucketCode` | String | 是 | 业务桶编码 |
| `keyword` | String | 是 | 搜索关键词 |

#### 5.2.4 获取单文件外链 (含临时授权码)
返回文件在系统中的安全下载外链地址，该地址携带短期鉴权信息。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/getDownloadUrl/{nodeId}` |
| 请求方式 | GET |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `nodeId` | Path | Long | 是 | 文件节点 ID |

**响应参数**
`data` 类型为 `String`: 原始安全下载 URL。

#### 5.2.5 批量获取文件外链
批量换取多个文件的安全下载外链。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/getBatchDownloadUrls` |
| 请求方式 | POST |
| Content-Type | application/json |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `nodeIds` | Body | `List<Long>` | 是 | 需要下载的节点 ID 数组 |

**响应参数**
`data` 类型为 `Map<Long, String>`，Key 为 nodeId，Value 为安全下载链接。

#### 5.2.6 安全核销下载
由 `getDownloadUrl` 颁发的外链或 code 触发，真实输出物理文件字节流。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/downloadByCode` |
| 请求方式 | GET |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `code` | Query | String | 是 | 下载临时授权码 |

**响应说明**
该接口直接返回文件字节流数据（二进制），不会包装标准的 JSON 响应对象。

#### 5.2.7 获取全量层级树
递归获取指定目录下所有子目录和文件，并按树形结构返回。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/listTree` |
| 请求方式 | GET |

**请求参数**
| 参数名 | 类型 | 必选 | 说明 |
|---|---|---|---|
| `bucketCode` | String | 是 | 业务桶编码 |
| `path` | String | 否 | 起始路径 (默认为根目录 `/`) |

**响应参数**
`data` 类型为 `List<6.4 FileTreeVO>`。

#### 5.2.8 获取全量打平列表
递归获取指定目录下所有文件（不包含文件夹），以扁平列表形式返回。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/listFlat` |
| 请求方式 | GET |

**请求参数**
同 `5.2.7`。
**响应参数**
`data` 类型为 `List<6.1 FileNodeVO>`。

#### 5.2.9 查询历史版本列表
获取某文件的所有历史版本记录(按版本号倒序)。注意: 当前主版本不在此列表中，请直接查看节点信息。

**基本信息**
| 项目 | 说明 |
|---|---|
| 接口地址 | `/v1/file/history/{nodeId}` |
| 请求方式 | GET |

**请求参数**
| 参数名 | 位置 | 类型 | 必选 | 说明 |
|---|---|---|---|---|
| `nodeId` | Path | Long | 是 | 文件节点 ID |

**响应参数**
`data` 类型为 `List<6.2 FileHistoryVO>`。

---

## 六、公共数据结构

### 6.1 FileNodeVO
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

### 6.2 FileHistoryVO
文件历史版本记录。

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 历史记录 ID |
| `nodeId` | Long | 是 | 关联的文件节点 ID |
| `versionNum` | Integer | 是 | 版本号 |
| `creatorName`| String | 否 | 上传人 |
| `createTime` | String | 是 | 上传时间 |

### 6.3 Bucket
业务桶配置对象。

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| `id` | Long | 是 | 桶记录 ID |
| `bucketCode` | String | 是 | 桶编码 |
| `bucketName` | String | 否 | 桶名称 |
| `storageType` | String | 否 | 存储类型 |
| `createTime` | String | 否 | 创建时间 |

### 6.4 FileTreeVO
文件层级树展示对象，继承自 `FileNodeVO`。

| 字段名 | 类型 | AI决策 | 说明 |
|---|---|---|---|
| (继承字段) | - | - | 包含 `6.1 FileNodeVO` 所有字段 |
| `children` | `List<FileTreeVO>` | 是 | 子节点列表 |

---

## 七、变更管理

| 项 | 约定 |
|---|---|
| 时间口径 | 所有接口统一使用 UTC 时区，ISO 8601 毫秒精度字符串。 |
| ID 精度 | `Long` 类型 ID 在 JSON 中应以数字返回，但 AI/前端解析时务必转为字符串防止精度丢失。 |
| 冲突处理 | 默认 `strategy=2`，即自动在文件名后追加数字防止覆盖。 |
