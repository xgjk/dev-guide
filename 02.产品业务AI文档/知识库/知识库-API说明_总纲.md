# 知识库 Open API 接口文档（总纲）

> 本文档为拆分后的总纲文件。接口详细说明已按能力域拆分至子文档，通用约定独立成文。

## 文档导航

| 文档 | 内容 |
|------|------|
| [_通用约定.md](_通用约定.md) | 访问地址、环境、请求头、响应结构、认证、AI 消费设计 |
| [01-文件检索与浏览.md](01-文件检索与浏览.md) | 4.1, 4.9, 4.11, 4.12 |
| [02-文件获取与内容提取.md](02-文件获取与内容提取.md) | 4.2, 4.3, 4.4, 4.15 |
| [03-文件上传与保存.md](03-文件上传与保存.md) | 4.10, 4.16, 4.17, 4.18 |
| [04-空间与文件管理.md](04-空间与文件管理.md) | 4.8, 4.13, 4.14, 4.19, 4.20 |
| [05-记忆沙盒与版本管理.md](05-记忆沙盒与版本管理.md) | 4.21, 4.22, 4.23, 4.24, 4.25, 4.26, 4.27, 4.28 |

---

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |
| 1.1 | 2026-03-26 | 更新上传切片说明 | 刘艳华 |
| 1.2 | 2026-03-26 | 下线 getRawFileContent 接口，更新 API 规范与 AI 底层穿透能力文档 | 刘艳华 |
| 1.3 | 2026-03-30 | 补充 deleteFile、updateFileProperty、batchGetContent 接口说明及参数更新 | 刘艳华 |
| 1.4 | 2026-04-01 | 新增 saveFileByParentId/saveFileByPath 路径聚合接口、uploadContentToPersonalProject 一键入库；更新 FileVO/DownloadInfoVO/PersonalFileVO/SavePersonalFileParam 数据结构 | 刘艳华 |
| 1.5 | 2026-04-01 | 新增项目/空间发现接口 (list/uploadableList)，支持 Agent 自主识别可写空间 | 刘艳华 |
| 1.6 | 2026-04-01 | 补全 bizCode 业务线过滤参数，新增 ProjectVO.rawEnabled 属性支持 | 刘艳华 |
| 1.7 | 2026-04-01 | 细节打磨：增加全量接口的 JSON 出入参示例样本，校对字段非空约束 | 刘艳华 |
| 1.8 | 2026-04-01 | 补全 4.11-4.20 全量子节（基本信息/行为约定/curl示例/响应示例/数据流向）；统一全文档请求/响应示例格式；修复 4.9 curl 方法错误；补全 5.12 字段 | 刘艳华 |
| 1.9 | 2026-04-02 | SaveFileToProjectParam 新增 suffix 字段；更新 saveFileByParentId/saveFileByPath 请求示例 | 刘艳华 |
| 1.10 | 2026-04-03 | 全量校对上传链路字段准确性：预检接口补充 size/sensitive/suffix 参数；UploadFileSliceParam storageType 修正为 MINIO；SaveResourceParam 修正 suffix/size 为非必填；SaveFileToProjectParam 新增 isSensitive 字段、修正 suffix 描述；全量 curl 示例补全 suffix/size/isSensitive | 刘艳华 |
| 1.11 | 2026-04-13 | 新增“记忆沙盒”模块 (4.21-4.24)；默认存盘逻辑下放至接入层控制 | 刘艳华 |
| 1.12 | 2026-04-16 | 移除 saveFileByParentId/saveFileByPath/saveFile 接口的 doc 富文本上传路径（fileType=doc + fileContent），三个接口统一仅支持 fileType=file + resourceId；纯文本内容统一通过 uploadContent 接口入库；更新相关接口说明、curl 示例及数据结构注释 | 刘艳华 |
| 1.13 | 2026-04-22 | 新增文件版本管理模块（4.25-4.28）：updateFileVersion、getVersionList、getLastVersion、finalizeVersion；扩展 uploadContent（4.18）支持版本更新模式（新增 updateFileId/versionRemark/versionName 字段）；新增 FileVersionVO（5.17）数据结构；更新 5.11 字段说明 | 刘艳华 |
| 1.14 | 2026-04-22 | 拆分 uploadContent 版本更新模式响应结构：新增 UpdateFileVersionResult（5.18），版本更新模式仅返回 fileId 和 fileName；更新 4.18 响应参数说明 | 刘艳华 |
| 1.15 | 2026-04-27 | DownloadInfoVO 新增 previewUrl 字段（forceDownload=false 时填充在线预览短链接）；Agent 应使用 previewUrl 给用户展示预览链接，downloadUrl 仅用于下载 | 刘艳华 |
| 1.14 | 2026-04-22 | 拆分 uploadContent 版本更新模式响应结构：新增 UpdateFileVersionResult（5.18），版本更新模式仅返回 fileId 和 fileName；更新 4.18 响应参数说明 | 刘艳华 |


---

## 一、概述

本文档描述了 **知识库服务** 对外开放的全部 Open API 接口。通过这些接口，可以实现以下业务能力：

1. **文件与目录检索** — 支持通过父 ID 下钻、项目 ID 获取一级目录，或全局关键词模糊搜索等多维手段，灵活检索出层级的目录及文件列表。
2. **文件获取与在线预览** — 支持获取在线预览凭据、下载 url、及针对解析后的文本提取。
3. **大文件分片上传** — 覆盖预检秒传、多段切片提交、分布式资源后置合并流程。
4. **空间发现与个人知识库维护** — 获取用户有权限的空间列表（含可写空间筛选），支持个人专属空间 `projectId` 的获取。
5. **项目知识库文件保存** — 支持按父 ID 或逻辑路径自动解析目录结构，将物理文件资源入库到任意有权限的项目空间。
6. **AI 内容一键入库** — 支持将 AI 生成的文本内容（如对话摘要、Markdown 报告）保存到用户有权限的知识库空间或个人专属文件夹。

---


---

## 三、关键业务流程说明

### 场景一：发现空间并浏览目录文件

> 需求：用户在外部应用中，需要先发现有权限的空间，再从零拉取空间内的目录文件全景。

1. **发现可用空间**：调用 **4.19 获取有权限访问的空间列表**（`GET /document-database/project/list`），获取用户有权访问的所有空间。若仅需个人专属空间，也可调用 **4.8 获取个人知识库空间Id** 直接获取 `projectId`。
2. **拉取首层全景**：调用 **4.12 根据项目ID获取一级目录列表**（`GET /document-database/file/getLevel1Folders`），传入目标 `projectId`，即可拉取绝对顶层（根目录）的所有文件夹/文件列表。
3. **分步下钻**：调用 **4.1 根据父ID获取下级目录及文件列表**（`GET /document-database/file/getChildFiles`），传入 `parentId={文件夹ID}`，向下递归剥洋葱式钻取。
4. **在线预览文件**：参见 **[场景三](#场景三在线视频文档流式预览)**。

---

### 场景二：上传文件到个人知识库指定目录

> 需求：将第三方资产或离线文件直存到个人知识库的指定目录节点。

1. **获取个人空间 ID**：调用 **4.8 获取个人知识库空间Id**（`GET /document-database/project/personal/getProjectId`），拿到 `projectId`。
2. **底层资源初始化（物理文件必需）**：
   - 若保存的是物理文件，需调用 **基础服务-文件服务** 中的大文件分片上传流程（基于 MD5 预检、分片上传与合并），最终拿到 `resourceId`。详见 [02-文件服务.md](../基础服务/API接口明细/02-文件服务.md#场景二大文件分片上传流程-推荐)。
   - 若保存的是纯文本内容，请使用 **4.18 uploadContent** 接口直接入库，无需此步骤。
3. **存盘绑定**：调用 **4.10 将文件资源保存到个人知识库目录**（`POST /document-database/project/personal/saveFile`），载荷传入：
   - `name`: 文件展示名称；
   - `parentId`: 存盘的目标文件夹 ID（若直接存入绝对根目录，传 `0`）；
   - `type`: `2` (文件)；
   - `fileType`: `file`（物理文件）；
   - 传步骤 2 中获取的 `resourceId`。
   
> **纯文本内容**（如 AI 生成的 Markdown/报告）请直接使用 **4.18 uploadContent** 接口，无需走分片上传流程。

---

### 场景三：在线视频/文档流式预览

> 需求：调用方需要在自有 Web 端内嵌展示或在线打开知识库中的文档。

1. **凭据拉取**：调用 **4.2 获取文件下载与在线预览凭据**（`GET /document-database/file/getDownloadInfo`），传入 `forceDownload=false` 以声明为在线预览。
2. **打开方式决策路由**：
   - **优先使用 `previewUrl`**：响应中的 `previewUrl` 是可直接给用户点击的在线预览短链接，Agent 应直接将此链接提供给用户。
   - 若需要更精细的渲染控制，检查 `DownloadInfoVO.openWith`：
     - 若为 `2` (PDF)：可直接采用 H5 预览套件，若 `lazyLoad=true`，则支持无感知流式分页加载降低带宽。
     - 若为 `4` (HTML 转化版)：直接使用 `<iframe>` 载入 `downloadUrl` 进行快照渲染。

---

### 场景四：全局或指定目录模糊搜索

> 需求：根据关键词查询匹配的文件或文件夹（支持时间过滤与路径范围限缩）。

1. **确定搜索维度**：
   - **全局搜索**：调用 **4.11 搜索文件或目录**（`GET /document-database/file/searchFile`），传入 `nameKey="搜索词"`。
   - **限缩目录盘查**：若只需在某个父目录下查找，需额外传入 `rootFileId`（指定根目录）。
2. **按需分类渲染**：
   - 依照返回体 `SearchFileVO` 中的 `folders`（文件夹列表）和 `files`（文件列表）在前端进行分类，渲染列表后可通过 `id` 进行在线预览（详见场景三）。

---

### 场景五：发现可写空间并按路径保存文件 [新增]

> 需求：Agent 需要自主识别用户有权限的空间，并将文件保存到指定逻辑目录路径下（路径不存在时自动递归创建）。

1. **发现可写空间**：调用 **4.20 获取有上传/编辑权限的空间列表**（`GET /document-database/project/uploadableList`），获取用户可写入的空间列表。根据返回的 `ProjectVO.name` 和 `ProjectVO.id` 确定目标空间。
2. **底层资源初始化（物理文件场景必需）**：
   - 若保存的是物理文件，需调用 **基础服务-文件服务** 中的大文件分片上传流程（基于 MD5 预检、分片上传与合并），最终拿到 `resourceId`。详见 [02-文件服务.md](../基础服务/API接口明细/02-文件服务.md#场景二大文件分片上传流程-推荐)。
   - 若保存的是纯文本内容，请使用 **4.18 uploadContent** 接口直接入库，无需此步骤。
3. **按路径存入文件**：调用 **4.17 根据路径保存文件到项目目录**（`POST /document-database/file/saveFileByPath`），传入：
   - `projectId`: 步骤 1 中确定的目标空间 ID；
   - `path`: 逻辑目录路径（如 `"工程档案/设计图纸"`），后端自动解析并创建不存在的文件夹；
   - `name`: 文件名；
   - `fileType`: `file`（物理文件）；
   - 传步骤 2 中获取的 `resourceId`。

> 补充：若已知目标文件夹 ID，也可直接调用 **4.16 根据父ID保存文件到项目目录** 跳过路径解析。纯文本内容请使用 **4.18 uploadContent** 接口。

---

### 场景六：AI 生成内容一键入库到知识库个人空间 [新增]

> 需求：将 AI 对话、摘要或 Markdown 报告等纯文本内容，以最快速度保存到知识库个人空间，无需关心具体空间 ID。

**原生一键入库流程：**
1. 调用 **4.18 一键快速保存纯文本到个人空间** (`POST /document-database/file/uploadContent`)。
2. 构造请求参数：
   - `content`: 文本/Markdown/HTML 源码内容；
   - `fileName`: 文件展示名称（建议带上扩展名，如 `调研结论.md`）；
   - `fileSuffix`: (**建议传**) 显式指定文件后缀（如 `md`, `json`, `html`, `txt`）；
   - `folderName`: (**可选**) 逻辑目录路径。**不传则默认归档至个人空间“和AI的对话”目录下**。
3. **亮点功能 (Smart Logic)**：
   - **后缀兜底**：不传 `fileSuffix` 时，系统兜底为 `md`。**强烈建议显式传入 `fileSuffix`**，避免文件名中已含扩展名（如 `报告.html`）时被错误追加 `.md` 后缀。
   - **零配置归档**：无需前置调用 `getProjectId`，系统自动根据当前 Token 绑定个人专属空间。
4. **结果流转**：接口同步返回 `projectId`、`fileId` 和 `downloadUrl`，可直接通过 `fileId` 进行后续的预览或属性维护。

**响应成功示例**：
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "projectId": 2009488364113997826,
    "projectName": "个人知识库",
    "folderId": 32100,
    "folderName": "和AI的对话",
    "fileId": 32188,
    "fileName": "调研结论.md",
    "downloadUrl": "https://{域名}/..."
  }
}
```

---

---


---

## 四、接口索引表

| 编号 | 接口名称 | 能力域 | 子文档 |
|------|----------|--------|--------|
| 4.1 | 根据父ID获取下级目录及文件列表 | 文件检索与浏览 | [01-文件检索与浏览](01-文件检索与浏览.md) |
| 4.2 | 获取文件下载与在线预览凭据 | 文件获取与内容提取 | [02-文件获取与内容提取](02-文件获取与内容提取.md) |
| 4.3 | UI阅读模式：根据文件ID和页码分页获取内容 | 文件获取与内容提取 | [02-文件获取与内容提取](02-文件获取与内容提取.md) |
| 4.4 | AI摘要模式：根据业务资源自适应获取全局提纯文本 | 文件获取与内容提取 | [02-文件获取与内容提取](02-文件获取与内容提取.md) |
| 4.5-4.7 | 大文件分片上传 (已迁移) | — | 已迁移，保留占位 |
| 4.8 | 获取个人知识库空间ID | 空间与文件管理 | [04-空间与文件管理](04-空间与文件管理.md) |
| 4.9 | 获取我最新上传的文件 | 文件检索与浏览 | [01-文件检索与浏览](01-文件检索与浏览.md) |
| 4.10 | 将文件资源保存到个人知识库目录 | 文件上传与保存 | [03-文件上传与保存](03-文件上传与保存.md) |
| 4.11 | 搜索文件或目录 | 文件检索与浏览 | [01-文件检索与浏览](01-文件检索与浏览.md) |
| 4.12 | 根据项目ID获取一级目录列表 | 文件检索与浏览 | [01-文件检索与浏览](01-文件检索与浏览.md) |
| 4.13 | 删除文件（逻辑删除或物理彻底删除） | 空间与文件管理 | [04-空间与文件管理](04-空间与文件管理.md) |
| 4.14 | 更新文件属性（重命名/移动/覆盖） | 空间与文件管理 | [04-空间与文件管理](04-空间与文件管理.md) |
| 4.15 | 批量获取多个文件的 RAG 全文内容 | 文件获取与内容提取 | [02-文件获取与内容提取](02-文件获取与内容提取.md) |
| 4.16 | 根据父ID保存文件到项目目录 | 文件上传与保存 | [03-文件上传与保存](03-文件上传与保存.md) |
| 4.17 | 根据路径保存文件到项目目录 | 文件上传与保存 | [03-文件上传与保存](03-文件上传与保存.md) |
| 4.18 | 一键快速保存纯文本到个人空间 | 文件上传与保存 | [03-文件上传与保存](03-文件上传与保存.md) |
| 4.19 | 获取该账号有权限访问的空间列表 | 空间与文件管理 | [04-空间与文件管理](04-空间与文件管理.md) |
| 4.20 | 获取该账号有上传/编辑权限的空间列表 | 空间与文件管理 | [04-空间与文件管理](04-空间与文件管理.md) |
| 4.21 | 新建项目长程记忆 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.22 | 获取项目记忆列表 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.23 | 项目记忆检索 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.24 | 获取项目骨架与记忆内容 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.25 | 上传新文件内容以更新文件版本 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.26 | 获取文件的所有历史版本列表 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.27 | 获取文件的最新版本信息 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |
| 4.28 | 将指定版本标记为定稿 | 记忆沙盒与版本管理 | [05-记忆沙盒与版本管理](05-记忆沙盒与版本管理.md) |

---

## 五、公共数据结构

### 5.1 FileVO
文件/目录属性卡片模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 主键 id |
| `name` | String | 文件名 |
| `type` | Integer | 资源类型：1 文件夹，2 文件 |
| `parentId` | Long | 父目录 id |
| `ancestorNames` | String | 祖先名字，斜杠 / 分隔 |
| `fileDescription` | String | 文件描述 |
| `fileType` | String | 关联的业务类型。枚举：doc(富文本), file(普通文件), work_report(工作汇报), work_plan(工作任务), url(链接), huiji(慧记), ai-report(AI情报)。注:如果为文件夹则为 NULL。AI 拉取全文时强依赖此标识 |
| `relationId` | String | 关联的对象 id（拉取全文必需参数） |
| `hasChild` | Boolean | 是否有子目录或文件 |
| `size` | Long | 文件大小（字节） |
| `suffix` | String | 后缀名 |
| `createTime` | Long | 创建时间戳 |
| `createTimeStr` | String | 创建时间（精确到分钟，供 AI 识别语境，格式：yyyy-MM-dd HH:mm） |
| `breadcrumb` | String | 前端决策卡片路径透传导航（与 ancestorNames 一致） |

---

### 5.2 DownloadInfoVO
下载/在线预览凭据信息。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `downloadUrl` | String | 下载直链（OSS 签名 URL），用于文件下载 |
| `previewUrl` | String | **在线预览短链接**（`forceDownload=false` 时填充），可直接给用户点击预览；`forceDownload=true` 时为 `null`。**Agent 应优先使用此字段给用户展示预览链接** |
| `thumbnailUrl` | String | 图片缩略图 url |
| `fileName` | String | 文件名 |
| `versionNumber` | Integer | 版本号 |
| `fileId` | Long | 文件 id |
| `suffix` | String | 文件后缀 |
| `size` | Long | 文件大小（字节） |
| `fileType` | String | 关联的业务类型。枚举：doc(富文本), file(普通文件), work_report(工作汇报), work_plan(工作任务), url(链接), huiji(慧记), ai-report(AI情报) |
| `fileContent` | String | 文件内容 |
| `resourceId` | Long | 资源 id |
| `openWith` | Integer | 打开方式：0 默认或下载 / 1 wps / 2 pdf / 3 畅写 / 4 html / 5 工作协同 / 6 pdf-v5 |
| `lazyLoad` | Boolean | 是否按需加载（目前用于 pdf.js 加载 pdf 文件） |
| `lastVersion` | Boolean | 是否最新版本 |
| `projectId` | Long | 文件空间 Id |

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
| `fullPath` | String | 服务端目标存储路径（未命中秒传时返回，供 `uploadFileSliceV2` 的 `filePath` 使用） |
| `storageType` | String | 存储类型（如 `MINIO`、`MINIO_SZ`），未命中秒传时返回，供 `uploadFileSliceV2` 的 `storageType` 使用 |

---

### 5.5 SaveResourceParam
合并分片生成底座资源。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 文件名称（含后缀） |
| `sliceIds` | array[Long] | 是 | §4.5 秒传和 §4.7 注册分片返回的所有 `sliceId` 列表 |
| `suffix` | String | 否 | 文件后缀（如 `pdf`、`docx`）。建议传入，不传则后端从文件名提取 |
| `size` | Long | 否 | 文件总大小（单位：字节）。建议传入，不传则后端默认 0 |
| `mimeType` | String | 否 | 文件 MIME 类型（如 `application/pdf`） |
| `time` | Long | 否 | 源站总耗时（毫秒） |

---



### 5.6 UploadFileSliceParam
切片注册参数。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `filePath` | String | 是 | 预检接口返回的 `fullPath`（分片物理存储路径） |
| `md5` | String | 是 | 分片的 MD5 值 |
| `size` | Long | 是 | 分片大小（单位：字节），注意是单个分片的大小而非文件总大小 |
| `storageType` | String | 是 | 存储类型：`FTP`、`MINIO`、`MINIO_SZ`、`MINIO_SG`、`QINIU`，默认 `MINIO` |

---

### 5.7 PersonalFileVO
个人空间文档结构。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 主键 id |
| `name` | String | 文件名 |
| `type` | Integer | 类型：1 文件夹，2 文件 |
| `parentId` | Long | 父 id |
| `projectId` | Long | 项目 id |
| `resourceId` | Long | 资源 id |
| `size` | Long | 文件大小（字节） |
| `suffix` | String | 文件后缀 |
| `createTime` | Long | 创建时间 |
| `creator` | String | 创建人 |
| `updateTime` | Long | 修改时间 |
| `updater` | String | 修改人 |
| `ancestorIds` | String | 祖先 id 列表 |
| `sortNumber` | Double | 排序字段 |
| `children` | List<PersonalFileVO> | 嵌套下级文件树列表 |

---

### 5.8 SavePersonalFileParam
将资源入挂个人树请求。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | Long | 否 | 主键 id（为空则新增，有值则更新） |
| `parentId` | Long | 是 | 父文件夹 id（主层传 0） |
| `name` | String | 是 | 文件名 |
| `type` | Integer | 是 | 1 文件夹，2 文件 |
| `suffix` | String | 否 | 文件后缀 |
| `size` | Long | 否 | 文件大小（字节） |
| `resourceId` | Long | 否 | 引用底层的资源 ID |
| `fileType` | String | 否 | file 普通文件（纯文本内容请使用 uploadContent 接口） |
| `fileContent` | String | 否 | 已废弃，请勿传入（纯文本内容请使用 uploadContent 接口） |
| `directory` | List\<String\> | 否 | 文件目录路径列表 |
| `isSensitive` | Integer | 否 | 是否跨境敏感文件（0 非敏感，1 敏感） |

---

### 5.9 SearchFileVO
搜索结果分类模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `folders` | List<[FileVO](#51-filevo)> | 匹配到的文件夹列表 |
| `files` | List<[FileVO](#51-filevo)> | 匹配到的文件列表 |

---

### 5.10 SaveFileToProjectParam [新增]
保存文件到项目空间请求（支持按父 ID 和按路径两种模式）。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `projectId` | Long | 是 | 项目空间 id |
| `parentId` | Long | 否 | 父文件夹 ID（已知目标文件夹时传入；若基于路径则传 `path`） |
| `name` | String | 是 | 保存的文件名 |
| `fileType` | String | 是 | 文件类型：file(普通物理文件)。纯文本内容请使用 uploadContent 接口 |
| `suffix` | String | 否 | 文件后缀（如 `pdf`、`docx`）。建议传入，不传则后端从资源反查 |
| `size` | Long | 否 | 文件大小（字节）。建议传入，不传则后端从资源反查 |
| `resourceId` | Long | 是 | 资源 id，对应已上传的物理文件资源 |
| `fileContent` | String | 否 | 已废弃，请勿传入（纯文本内容请使用 uploadContent 接口） |
| `path` | String | 否 | 逻辑目录路径（不传则存入项目根目录）。示例：`"AI生成/日报总结"`，后端自动递归创建不存在的目录 |
| `isSensitive` | Integer | 否 | 是否跨境敏感文件（0 非敏感，默认；1 敏感） |

---

### 5.11 UploadContentToPersonalProjectParam [新增]
上传内容到个人知识库参数。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `content` | String | 是 | 文件正文内容 (Markdown/Plain Text) |
| `fileName` | String | 是 | 文件展示名称 |
| `fileSuffix` | String | 否 | 文件后缀（按需传入，逻辑层默认为 `md`） |
| `folderName` | String | 否 | 逻辑目录路径。**不传则默认归档至"和AI的对话"目录下**，支持多级路径（如 `"AI生成/调研摘要"`） |
| `updateFileId` | Long | 否 | **版本更新模式专用**：要更新版本的文件 ID（即目标文件的 `fileId`，可通过 `getChildFiles`/`searchFile` 查询获得，或上传文件时的返回值）。传入则更新已有文件的版本，不传则新建文件到个人空间 |
| `versionRemark` | String | 否 | **版本更新模式专用**：版本说明（如“修订了第三章内容”） |
| `versionName` | String | 否 | **版本更新模式专用**：版本名称（如“V2.0”） |

---

### 5.12 UploadContentToPersonalProjectResult [新增]
上传内容到个人知识库返回结果。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `projectId` | Long | 目标个人空间 ID |
| `projectName` | String | 空间名称 |
| `folderId` | Long | 文件夹 ID |
| `folderName` | String | 文件夹名称 |
| `fileId` | Long | 生成的文件 ID |
| `fileName` | String | 最终保存的文件名称 |
| `downloadUrl` | String | 文件的下载/预览地址 |


---

### 5.13 ProjectVO [新增]
空间/项目元数据模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 空间 ID (projectId) |
| `name` | String | 空间名称 |
| `remark` | String | 备注/描述 |
| `type` | String | 空间类型: common(普通), personal(个人) |
| `role` | Integer | 用户在空间的角色: 1(管理员), 0(普通成员) |
| `bizCode` | String | 业务线编码 |
| `canCreateAtRoot` | Boolean | 是否允许在根目录直接创建文件夹/上传 |
| `rawEnabled` | Boolean | 是否开启 Raw 原文展示功能 |
| `hasTopping` | Boolean | 是否已置顶 |
| `creator` | String | 创建人姓名 |
| `createTime` | Long | 创建时间戳 |

---

### 5.14 ProjectItemVO [新增]
记忆项目/目录节点模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 项目(目录)ID |
| `name` | String | 项目名称 |
| `hasChild` | Boolean | 是否有子项 |
| `createTime` | Long | 创建时间戳 |
| `createTimeStr` | String | 格式化时间(yyyy-MM-dd HH:mm) |

---

### 5.15 ProjectFileVO [新增]
记忆项目文件节点模型。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 文件或目录ID |
| `name` | String | 名称 |
| `type` | Integer | 节点类型: 1=文件夹, 2=文件 |
| `suffix` | String | 文件后缀 |
| `size` | Long | 文件大小(字节) |
| `fileType` | String | 业务类型(doc/file/url等) |
| `relationId` | String | 业务关联ID(拉取AI阅读内容必须) |
| `hasChild` | Boolean | 是否有子项 |
| `fileDescription` | String | 文件描述摘要(包含脱水内容骨架) |
| `createTime` | Long | 创建时间戳 |
| `createTimeStr` | String | 格式化创建时间 |

---

### 5.16 CreateProjectParam [新增]
创建记忆项目入参。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 项目名称 |

---

### 5.17 FileVersionVO [新增]
文件版本信息。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | Long | 版本记录ID |
| `fileId` | Long | 文件ID |
| `versionNumber` | Integer | 版本号（从1开始递增） |
| `versionName` | String | 版本名称，如 V2.0 |
| `remark` | String | 版本说明/备注 |
| `status` | Integer | 版本状态：1=未定稿（草稿），2=已定稿 |
| `resourceId` | Long | 底层资源ID |
| `resourceType` | String | 资源来源类型：upload=上传，translation=翻译 |
| `fileType` | String | 文件类型：file=普通文件，doc=富文本 |
| `label` | String | 版本标签：原始、初始化、放行、翻译 |
| `createBy` | Long | 创建人ID |
| `creator` | String | 创建人姓名 |
| `createTime` | Long | 创建时间（毫秒时间戳） |
| `updater` | String | 最后更新人姓名 |
| `updateTime` | Long | 最后更新时间（毫秒时间戳） |
| `lastVersion` | Boolean | true 表示当前最新版本 |
| `fileName` | String | 文件名（含后缀） |

---

### 5.18 UpdateFileVersionResult [新增]
uploadContent 接口**版本更新模式**（传 `updateFileId`）的返回结构。仅含文件标识，不含空间/目录信息。

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `fileId` | Long | 文件 ID |
| `fileName` | String | 文件名（含后缀） |

> 与新建模式返回的 `UploadContentToPersonalProjectResult`（5.12）不同，版本更新模式不返回 `projectId`、`folderId`、`downloadUrl` 等字段，因为文件位置未发生变化。

---


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


---

## 七、注意事项

为了确保对接的安全性与稳定性，调用方应严格遵守以下约束：

1. **大文件落库安全流程**：请勿跳过分片合并动作。单个上传切片不可直接被 `saveFile` 引用，必须先走完分片上传与合并流程，换取合法 `resourceId`。
2. **ID 精度防御**：所有 ID 类型在后端使用 64位 Long 整数（如 `id`, `parentId`, `projectId`），前端展示或外部对接时请务必使用 **String 字符串** 类型接收，避免 JavaScript 等弱类型语言发生精度丢失。
3. **鉴权与防重放**：所有接口均需在 Header 携带合法的 `appKey`；若接口需要计算签名，请确保 `timestamp` 与服务端时间差在 5 分钟内。
4. **频率限制（QPS 控制）**：开放平台配有流控保护，收到 `610012` 错误时推荐使用指数级退避算法进行降频重试。
5. **路径自动解析**：使用 `saveFileByPath` 时，`path` 中的路径分隔符为 `/`，后端会自动递归创建不存在的目录层级。
6. **AI 无关字段过滤**：列表接口仅返回文件元数据（名称/类型/大小/后缀等），不内嵌正文内容；正文需通过 4.3/4.4/4.15 独立获取，避免单次返回 token 过大。
7. **避免父子重复**：`FileVO` 中的 `ancestorNames` 已包含完整路径，不再逐级重复返回父级属性；`breadcrumb` 与 `ancestorNames` 为同义词，优先使用 `ancestorNames`。
8. **层级与长度控制**：文件列表默认 1 层，需下钻时通过 `parentId` 递归调用；大文件全文建议通过 `getFileContent`（4.3）分页读取，避免单次返回超长文本。
9. **富文本原文规则**：在线文档（`fileType=doc`）的原始富文本不在列表接口返回；需通过 `getFileContent` 或 `getFullFileContent` 获取结构化 Markdown 文本。`getFullFileContent` 保留标题/列表/表格等结构语义，不会简单压平为纯文本。
10. **列表裁剪能力**：`getChildFiles` 支持 `type`（仅文件/仅文件夹）、`excludeFileTypes`、`excludeFolderNames`、`returnFileDesc` 等裁剪参数，AI Agent 应善用这些参数减少无关数据。
11. **空值约定**：全文档统一使用 `null` 表示无数据；`null`、空串 `""`、空数组 `[]` 语义相同，调用方无需区分。

---


---

## 八、变更管理

| 项 | 说明 |
| --- | --- |
| 向后兼容要求 | 返回体新增字段不得破坏旧调用方解析；字段类型变更必须经过废弃过渡期 |
| 废弃通知周期 | 废弃接口至少提前 2 周通知，旧版并行保留至下一个发布周期 |
| 字段新增规则 | 新增字段默认为可选（允许 `null`），枚举值允许后端扩展，调用方不应假设枚举值固定 |
| 字段删除规则 | 先标注「已废弃」并保留至少一个发布周期，再在下个大版本中移除 |
| 空值兼容规则 | `null` 与字段缺失等价，调用方应兼容两种情况；空数组与 `null` 均表示无数据 |
| 顺序与分页稳定性 | 文件列表顺序由 `order` 参数控制，默认按更新时间倒序；无游标分页，列表内容可能因并发操作变化 |
| 变更通知人 | 知识库服务团队、对接方技术负责人、开放平台运维群 |

---

**文档版本**：v1.13
**更新日期**：2026-04-22
**维护人/团队**：知识库服务团队

---

> 📎 原始文档：[知识库-API说明.md](../知识库-API说明.md)
