# 知识库 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |
| 1.1 | 2026-03-26 | 更新上传切片说明 | 刘艳华 |
| 1.2 | 2026-03-26 | 下线 getRawFileContent 接口，更新 API 规范与 AI 底层穿透能力文档 | 刘艳华 |
| 1.3 | 2026-03-30 | 补充 deleteFile、updateFileProperty、batchGetContent 接口说明及参数更新 | AI |

## 一、概述

本文档描述了 **知识库服务** 对外开放的全部 Open API 接口。通过这些接口，可以实现以下业务能力：

1. **文件与目录检索** — 支持通过父 ID 下钻、项目 ID 获取一级目录，或全局关键词模糊搜索等多维手段，灵活检索出层级的目录及文件列表。
2. **文件获取与在线预览** — 支持获取在线预览凭据、下载 url、及针对解析后的文本提取。
3. **大文件分片上传** — 覆盖预检秒传、多段切片提交、分布式资源后置合并流程。
4. **个人知识库维护** — 获取个人专属空间 `projectId`，支持在云端存取自身文档。

---

## 二、通用说明

### 2.1 访问地址
```
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境   | 域名/Base URL                    | 备注  |
| ---- | ------------------------------ | --- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` | -   |

### 2.3 公共请求头

| Header   | 说明                         | 是否必填  |
| -------- | -------------------------- | ----- |
| `appKey` | 从工作协同系统获取的 API 密钥           | 是     |

### 2.4 通用响应结构

所有接口响应均返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段           | 类型      | 说明                                      |
| ------------ | ------- | ----------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，非 `1` 表示失败 |
| `resultMsg`  | String  | 提示信息，成功时为 `null`，失败时为错误描述 |
| `data`       | T       | 业务数据，根据各接口不同，失败时通常为 `null` |

---

## 三、关键业务流程说明

### 场景一：从个人知识库获取目录或文件 [新增]

> 需求：用户在外部应用中，从零拉取个人知识库面板全盘全景。

1. **获取空间 id**：调用 **4.8 获取个人知识库空间Id**（`GET /document-database/project/personal/getProjectId`），获取到用户的唯一知识库空间 `projectId`。
2. **拉取首层全景**：调用 **4.12 根据项目ID获取一级目录列表**（`GET /document-database/file/getLevel1Folders`），传入 `projectId`，即可完美拉取绝对顶层（根目录）的所有夹/文件列表。
3. **分步下钻**：调用 **4.1 根据父ID获取下级目录及文件列表**（`GET /document-database/file/getChildFiles`），传入：`parentId={文件夹ID}`，向下递归剥洋葱式钻取。
4. **在线预览文件**：参见 **[场景三](#场景三在线视频文档流式预览)**。

---

### 场景二：上传文件到个人知识库指定目录 [新增]

> 需求：将第三方资产或离线文件直存到指定知识库逻辑节点。

1. **底层资源初始化（可选）**：
   - 若上传的是大文件，需按需分段调用 **4.5 预检**、**4.7 分片切片上传** 以及 **4.6 合并生成资源**。
   - 最终从合并接口中拿取底层的统一数据资源锚点：`resourceId`。
2. **一键存盘绑定**：调用 **4.10 将文件资源保存到个人知识库目录**（`POST /document-database/project/personal/saveFile`），载荷传入：
   - `name`: 文件展示名称；
   - `parentId`: 存盘的目标文件夹 ID（若直接存入绝对根目录，传 `0`）；
   - `type`: `2` (文件)；
   - `resourceId`: 前置生成的资源关联 key。

---

### 场景三：在线视频/文档流式预览

> 需求：调用方需要在自有 Web 端内嵌展示或在线打开知识库中的文档。

1. **凭据拉取**：调用 **4.2 获取文件下载与在线预览凭据**（`GET /document-database/file/getDownloadInfo`），传入 `forceDownload=false` 以声明为在线预览。
2. **打开方式决策路由**：
   - 检查响应里的 `DownloadInfoVO.openWith`：
     - 若为 `2` (PDF)：可直接采用 H5 预览套件，若 `lazyLoad=true`，则支持无感知流式分页加载降低带宽。
     - 若为 `4` (HTML 转化版)：直接使用 `<iframe>` 载入 `downloadUrl` 进行快照渲染。

---

### 场景四：全局或指定目录模糊搜索 [新增]

> 需求：根据关键词查询匹配的文件或文件夹（支持时间过滤与路径范围限缩）。

1. **确定搜索维度**：
   - **全局搜索**：调用 **4.11 搜索文件或目录**（`GET /document-database/file/searchFile`），传入 `nameKey="搜索词"`。
   - **限缩目录盘查**：若只需在某个父目录下查找，需额外传入 `rootFileId`（指定根目录）。
2. **按需分类渲染**：
   - 依照返回体 `SearchFileVO` 中的 `folders`（文件夹列表）和 `files`（文件列表）在前端进行分类，渲染列表后可通过 `id` 进行在线预览（详见场景三）。

---

## 四、接口详细说明

### 4.1 【检索】根据父ID获取下级目录及文件列表

根据父文件夹 ID 获取其下级目录及文件列表，支持排序、标签、类型等筛选。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getChildFiles` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `parentId` | Long | 是 | 要展开的父文件夹id(根目录传0或查出的项目级id) |
| `type` | Integer | 否 | 过滤资源类型(空为所有，1只查文件夹，2只查文件) |
| `label` | String | 否 | 标签:空或者[原始]都是全部,初始化,待处理,放行 |
| `order` | Integer | 否 | 排序规则：1倒序更新 2顺序更新 3倒序创建 4顺序创建 5倒序名字 6顺序名字(AI常用1或3) |
| `excludeFileTypes` | String | 否 | 需要排除的文件业务分类，多个用逗号分隔(例如: work_report,work_plan,huiji) |
| `excludeFolderNames` | String | 否 | 需要排除的文件夹名称，多个用逗号分隔(例如: 临时文件,测试文件夹) |
| `returnFileDesc` | Boolean | 否 | 强制带回文件描述摘要(建议AI传true) |

**响应参数**

`data` 类型为 `List<FileVO>`，字段详见 **[5.1 FileVO](#51-filevo)**。

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/getChildFiles?parentId=1000' \
  -H 'appKey: YOUR_API_KEY'
```

---

### 4.2 【获取】获取文件下载与在线预览凭据

根据文件 ID 获取下载 URL 或在线预览所需凭据信息。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getDownloadInfo` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件 id |
| `forceDownload` | Boolean | 否 | 是否强制下载（true 下载，false 在线预览） |
| `bypassRisk` | Boolean | 否 | 是否绕过风险检查 |

**响应参数**

`data` 类型为 `DownloadInfoVO`，字段详见 **[5.2 DownloadInfoVO](#52-downloadinfovo)**。

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/getDownloadInfo?fileId=20001' \
  -H 'appKey: YOUR_API_KEY'
```

---

### 4.3 【获取】UI阅读模式：根据文件ID和页码分页获取内容

主要供 UI 界面提供对文件进行分段、分页的分批流式展示。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getFileContent` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件 id |
| `pageNumber` | Integer | 否 | 页码，从第一页开始 |

**响应参数**

`data` 类型为 `String`，为该页的排版文本。

---

### 4.4 【获取】AI摘要模式：根据业务资源自适应获取全局提纯文本

面向 AI Agent 设计的智能全文提取引擎。会自动根据传入的业务类型路由至对应微服务获取实况，若不传则降级反查内部物理文件的 RAG 知识库脱水版本。返回经过高度清洗和提纯的全局 Markdown 文本。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getFullFileContent` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 否 | 文件id（推荐仅传此参数，后端自动补全其余字段） |
| `relationId` | String | 否 | 业务关联id（可选，后端可根据fileId自动补全） |
| `fileType` | String | 否 | 业务类型（可选，后端可根据fileId自动补全）。枚举：doc(富文本), file(普通文件), work_report(工作汇报), work_plan(工作任务), url(链接), huiji(慧记), ai-report(AI情报) |

**响应参数**

`data` 类型为 `String`，格式为全局提纯的纯文本或 Markdown 面向解析器的文本格式。

---

### 4.5 【上传】预检文件MD5信息（支持秒传）

上传前根据文件 MD5 预检，若服务器已存在该文件可秒传，无需重复上传。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getSliceIdByMd5V2` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `md5` | String | 是 | 文件 MD5 |

**响应参数**

`data` 类型为 `SliceCheckVO`，字段详见 **[5.4 SliceCheckVO](#54-slicecheckvo)**。


---

### 4.6 【上传】合并文件分片生成底层资源

所有分片上传完成后，合并分片并生成底层资源。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/saveResource` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 `SaveResourceParam` (见 5.5)。

---

### 4.7 【上传】注册文件分片数据

当 MD5 预检未命中秒传时，将已物理上传到 MinIO (通过 PUT `uploadUrl`) 的文件分片在服务端进行注册。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/uploadFileSliceV2` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 `UploadFileSliceParam` (见 5.6)。


---
 
### 4.8 【基础】获取个人知识库空间ID

获取当前用户个人知识库的空间 ID（projectId），用于对应知识库目录。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/personal/getProjectId` |
| 请求方式 | `GET` |

---
 
### 4.9 【检索】获取我最新上传的文件

获取当前用户最新上传的文件列表（支持 limit 限制）。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/personal/getRecentFiles` |
| 请求方式 | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `limit` | Integer | 否 | 限制数量 |
| `searchKey` | String | 否 | 搜索关键字 |

---
 
### 4.10 【上传】将文件资源保存到个人知识库目录

将已有资源或新建内容保存到个人知识库目录。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/personal/saveFile` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 `SavePersonalFileParam` (见 5.8)。

---
 
### 4.11 【检索】搜索文件或目录

根据关键词、时间范围等条件，在指定项目/空间或全局范围内搜索文件和文件夹。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/searchFile` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `projectId` | Long | 否 | 项目/空间 id |
| `nameKey` | String | 否 | 名称关键词 |
| `rootFileId` | Long | 否 | 指定根目录 id（在此目录下搜索） |
| `startTime` | Long | 否 | 创建时间-开始时间戳 |
| `endTime` | Long | 否 | 创建时间-结束时间戳 |
| `isFileStorage` | Boolean | 否 | 是否为文件存储范围（默认 false） |
| `permissionQuery` | String | 否 | 权限查询条件 |
| `excludeFileTypes` | String | 否 | 排除的文件类型，逗号分隔 |
| `excludeFolderNames` | String | 否 | 排除的文件夹名称，逗号分隔 |

**响应参数**

`data` 类型为 `SearchFileVO`，字段详见 **[5.9 SearchFileVO](#59-searchfilevo)**。

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/searchFile?nameKey=测试' \
  -H 'appKey: YOUR_API_KEY'
```

---
 
### 4.12 【检索】根据项目ID获取一级目录列表

拉取指定项目空间（如个人知识库空间）的绝对顶层（根目录）下的所有文件夹及文件。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getLevel1Folders` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `projectId` | Long | 是 | 项目/空间 id |
| `order` | Integer | 否 | 排序规则：1(更新倒序), 2(更新顺序), 5(名字倒序), 6(名字顺序) |
| `permissionQuery` | String | 否 | 权限查询条件 |

**响应参数**

`data` 类型为 `List<[FileVO](#51-filevo)>`。

**请求示例**

```bash
curl -X GET 'https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/getLevel1Folders?projectId=2009488364113997826' \
  -H 'appKey: YOUR_API_KEY'
```

---

### 4.13 【写操作】删除文件（逻辑删除或物理彻底删除）

当 `isPhysical` 为 `true` 时，将执行物理彻底删除（逻辑删除后再彻底从回收站抹除）。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/deleteFile` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 `FileDeleteParam`，主要字段如下：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件 ID |
| `isPhysical` | Boolean | 否 | 是否物理彻底删除 (true=彻底销毁, false/null=移入回收站) |

**响应参数**

`data` 类型为 `Boolean`，表示操作成功与否。

---

### 4.14 【写操作】更新文件属性（重命名/移动/覆盖）

【Agent 提示】支持重命名和跨目录移动。同名冲突策略（三选一）：cover=true 静默覆盖 -> autoRename=true 自动追加后缀 -> 二者均不传则抛异常。请 Agent 依据人类用户的意向选择。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/updateFileProperty` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 `FileModifyParam`，主要字段如下：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |
| `newName` | String | 否 | 新文件名（为空即可仅做移动） |
| `targetParentId` | Long | 否 | 目标父目录ID（为空即可仅做重命名） |
| `cover` | Boolean | 否 | 同名冲突时是否覆盖（cover 与 autoRename 互斥，cover 优先级更高） |
| `autoRename` | Boolean | 否 | 同名冲突时是否自动追加数字后缀重命名（cover=true 时本字段被忽略） |

**响应参数**

`data` 类型为 `Boolean`，表示操作成功与否。

---

### 4.15 【获取】批量获取多个文件的 RAG 全文内容

批量获取多个文件的全文本资料，减少交互往返次数，提升数据处理效率。走 Adapter 穿透引擎。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/ai/batchGetContent` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

请求体为 `BatchGetContentParam`：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `files` | List<FileIdentifyDTO> | 是 | 文件解析标识对象列表 |

其中 `FileIdentifyDTO` 结构说明：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |
| `relationId` | String | 否 | 业务关联ID（可选，后端可根据fileId自动补全。仅在需要强制覆盖元数据时传入） |
| `fileType` | String | 否 | 关联的业务类型（可选，后端可根据fileId自动补全）。枚举：doc(富文本), file(普通文件), work_report(工作汇报), work_plan(工作任务), url(链接), huiji(慧记), ai-report(AI情报) |

**响应参数**

`data` 类型为 `List<FileContentVO>`：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `fileId` | Long | 文件ID |
| `content` | String | 文件内容体 |
| `status` | String | 状态 (success/empty/error) |
| `message` | String | 附带消息 |

---

## 五、公共数据结构

### 5.1 FileVO
文件/目录属性卡片模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 主键 id |
| `name` | String | 文件名 |
| `type` | Integer | 资源类型：1 文件夹，2 文件 |
| `parentId` | Long | 所属文件夹 ID |
| `projectId` | Long | 项目 id |
| `resourceId` | Long | 关联资源 id |
| `ancestorNames` | String | 祖先名字，斜杠 / 分隔 |
| `fileDescription` | String | 文件描述 |
| `fileType` | String | 文件类型：doc 富文本 / file 离线文件 |
| `hasChild` | Boolean | 是否有子目录或文件 |
| `size` | Long | 文件大小（字节） |
| `suffix` | String | 后缀名 |

---

### 5.2 DownloadInfoVO
下载/在线预览凭据信息。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `downloadUrl` | String | 下载 url / 临时签名 |
| `fileContent` | String | 文件内载体 |
| `fileId` | Long | 文件 id |
| `openWith` | Integer | 打开方式：1 wps / 2 pdf / 4 html |

---

### 5.3 FileContentTaskVO
文件内容抽取结果。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `fileContent` | String | 原文大文本内容 |
| `resourceId` | Long | 资源 id |
| `status` | Integer | 当前抽取状态 |

---



### 5.4 SliceCheckVO
分片预查结果（秒传必备）。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `sliceId` | Long | 切片 ID（若直接命中说明已秒传成功） |
| `uploadUrl` | String | MinIO 预签名上传链接（未命中秒传时返回，需先使用 PUT 方式物理上传分片） |
| `fullPath` | String | 服务端目标存储路径（未命中秒传时返回，供 `uploadFileSliceV2` 注册使用） |

---

### 5.5 SaveResourceParam
合并分片生成底座资源。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 文件名称 |
| `size` | Long | 是 | 文件总大小 |
| `sliceIds` | array[Long] | 是 | 分片 ID 列表 |
| `suffix` | String | 是 | 后缀。例如 `pdf` |

---



### 5.6 UploadFileSliceParam
切片注册参数。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `filePath` | String | 是 | 服务端存储路径（由预检接口返回的 `fullPath`） |
| `md5` | String | 是 | 文件 MD5 |
| `size` | Long | 是 | 当前上传大小 |
| `storageType` | String | 是 | 填入 `document-database` |

---

### 5.7 PersonalFileVO
个人空间文档结构。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 主键 id |
| `name` | String | 文件名 |
| `type` | Integer | 类型：1 文件夹，2 文件 |
| `parentId` | Long | 父 id |
| `children` | List<PersonalFileVO> | 嵌套下级文件树列表 |

---

### 5.8 SavePersonalFileParam
将资源入挂个人树请求。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 文件名 |
| `parentId` | Long | 是 | 父文件夹 id（主层传 0） |
| `type` | Integer | 是 | 1 文件夹，2 文件 |
| `resourceId` | Long | 否 | 引用底层的资源 ID |
| `fileType` | String | 否 | doc 小作文 / file 普通文件 |

---

### 5.9 SearchFileVO
搜索结果分类模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `folders` | List<[FileVO](#51-filevo)> | 匹配到的文件夹列表 |
| `files` | List<[FileVO](#51-filevo)> | 匹配到的文件列表 |

---

## 六、错误码说明

开放平台接口统一使用 `resultCode` 表示业务处理结果。除通用的成功（1）和失败（0）外，系统还定义了以下标准错误码，便于调用方进行精确的分支处理与异常提示：

| resultCode | 说明 | 参考信息 / 异常原因 |
| ---------- | ---------------------- | ------------------------------------------ |
| **1** | **请求成功** | success |
| **0** | **通用失败** | failure |
| **500** | **系统异常/内部错误** | 系统崩溃、微服务超时或内部异常 |
| 610002 | `appKey` 无效 | 应用密钥不匹配或未分配 |
| 610003 | `appSecret` 无效 | 密钥校验失败 |
| 610005 | 签名 `sign` 无效 | 签名计算错误 |
| 610006 | `access_key` 无效/非最新| 授权令牌过期或已被顶替 |
| 610007 | 授权度达到上限 | 授权额度已耗尽 |
| 610008 | 请求 URL 不在白名单 | 跨域或未白名单授权的 API 访问 |
| 610009 | 不支持的请求方法 | 例如 GET 接口使用了 POST 请求 |
| 610010 | `nonce` 防重放值无效 | nonce 重复使用 |
| 610011 | 时间戳 `timestamp` 无效 | 调用方系统时间相差过大（通常需在 5 分钟内） |
| 610012 | **请求太频繁（触发限流）**| 超过 QPS 限制，请休眠后重试 |
| 610013 | 请求 API 未找到 | 404，路由错误 |
| 610014 | 应用被禁用 | 开发者应用已被管理员冻结 |
| 610015 | 无访问权限 | 未给该 appKey 授权对应接口的调用权限 |
| 610016 | `openUserId` 无效 | 外部用户 ID 映射错误 |
| 610018 | 非当前企业用户 | 跨企业越权访问禁止 |
| 610019 | 用户已被禁用 | 对应的协同系统用户已离职或冻结 |
| 610030 | 重复的请求 | 防重放/幂等拦截 |

---

## 七、注意事项

为了确保对接的安全性与稳定性，调用方应严格遵守以下约束：

1. **大文件落库安全流程**：请勿跳过分片合并动作。单个上传切片不可直接被 `saveFile` 引用，必须先走完分片上传与合并流程，换取合法 `resourceId`。
2. **ID 精度防御**：所有 ID 类型在后端使用 64位 Long 整数（如 `id`, `parentId`, `projectId`），前端展示或外部对接时请务必使用 **String 字符串** 类型接收，避免 JavaScript 等弱类型语言发生精度丢失。
3. **鉴权与防重放**：所有接口均需在 Header 携带合法的 `appKey`；若接口需要计算签名，请确保 `timestamp` 与服务端时间差在 5 分钟内。
4. **频率限制（QPS 控制）**：开放平台配有流控保护，收到 `610012` 错误时推荐使用指数级退避算法进行降频重试。

---

**文档版本**：v1.6  
**更新日期**：2026-03-30  
**维护人/团队**：知识库服务团队
