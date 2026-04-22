# 知识库 Open API 接口文档

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

## 一、概述

本文档描述了 **知识库服务** 对外开放的全部 Open API 接口。通过这些接口，可以实现以下业务能力：

1. **文件与目录检索** — 支持通过父 ID 下钻、项目 ID 获取一级目录，或全局关键词模糊搜索等多维手段，灵活检索出层级的目录及文件列表。
2. **文件获取与在线预览** — 支持获取在线预览凭据、下载 url、及针对解析后的文本提取。
3. **大文件分片上传** — 覆盖预检秒传、多段切片提交、分布式资源后置合并流程。
4. **空间发现与个人知识库维护** — 获取用户有权限的空间列表（含可写空间筛选），支持个人专属空间 `projectId` 的获取。
5. **项目知识库文件保存** — 支持按父 ID 或逻辑路径自动解析目录结构，将物理文件资源入库到任意有权限的项目空间。
6. **AI 内容一键入库** — 支持将 AI 生成的文本内容（如对话摘要、Markdown 报告）保存到用户有权限的知识库空间或个人专属文件夹。

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

### 2.5 认证与安全（文档级约定）

| 项 | 说明 |
| --- | --- |
| 认证方式 | 所有接口统一在请求头中携带 `appKey` |
| Header 约定 | Header 名称固定为 `appKey`，是否必填、示例值格式与特殊说明见 **2.3 公共请求头** |
| 获取方式 | `appKey` 的申请、开通、分发、轮换流程不在本文档范围内 |
| 鉴权机制 | 默认按应用级鉴权；所有接口均需携带合法 `appKey`，网关层统一校验 |
| 审计日志 | 所有写操作（POST 接口）均记录操作者、时间、资源 ID、动作类型 |
| 行级 / 字段级权限（原则） | 默认按当前 appKey 映射的用户身份过滤数据范围；各接口特例见 4.x |
| 敏感数据（原则） | 文件下载 URL 为临时签名链接，有时效性；文件内容不做脱敏处理，由调用方按业务需要自行控制 |

### 2.6 面向 AI 消费的数据设计

| 项 | 说明 |
| --- | --- |
| 最小必要返回 | `FileVO` 仅返回文件元数据（名称/类型/大小/后缀等），不返回正文内容；正文需通过 4.3/4.4/4.15 独立获取 |
| 去重原则 | `FileVO` 中的 `ancestorNames` 已包含完整路径信息，不再逐级重复返回父级属性 |
| 层级控制 | 文件列表（`getChildFiles`/`getLevel1Folders`）默认 1 层，需下钻时通过 `parentId` 递归调用；`PersonalFileVO.children` 为嵌套树但仅在 `getRecentFiles` 中使用 |
| 文本控制 | `getFullFileContent` 返回全局提纯文本（Markdown），大文件建议通过 `getFileContent` 分页读取；单页文本量由后端控制 |
| 富文本规则 | 在线文档（`fileType=doc`）的原始富文本不直接返回列表接口；需通过 `getFileContent` 或 `getFullFileContent` 获取结构化文本 |
| 格式保留原则 | `getFullFileContent` 返回 Markdown 格式，保留标题/列表/表格等结构语义 |
| 列表控制 | 文件列表接口无分页（单次返回全部子项）；若目录文件过多，建议通过 `searchFile` 按关键词检索 |
| 裁剪能力 | `getChildFiles` 支持 `type`（仅文件/仅文件夹）、`excludeFileTypes`、`excludeFolderNames`、`returnFileDesc` 等裁剪参数 |
| token 控制 | 建议 AI Agent 优先使用 `batchGetContent` 批量获取全文（单次建议不超过 10 个文件）；单个大文件使用 `getFileContent` 分页读取 |

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
   - 检查响应里的 `DownloadInfoVO.openWith`：
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

## 四、接口详细说明

### 4.1 【检索】根据父ID获取下级目录及文件列表

根据父文件夹 ID 获取其下级目录及文件列表，支持排序、标签、类型等筛选。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getChildFiles` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | Agent 遍历目录树、文件浏览 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `parentId` | Long | 是 | 要展开的父文件夹id(根目录传0或查出的项目级id) |
| `type` | Integer | 否 | 过滤资源类型(空为所有，1只查文件夹，2只查文件) |
| `label` | String | 否 | 标签:空或者[原始]都是全部,初始化,待处理,放行 |
| `order` | Integer | 否 | 排序规则：1倒序更新 2顺序更新 3倒序创建 4顺序创建 5倒序名字 6顺序名字(AI常用1或3) |
| `excludeFileTypes` | String | 否 | 需要排除的文件业务分类，多个用逗号分隔(例如: work_report,work_plan,huiji,ai-report) |
| `excludeFolderNames` | String | 否 | 需要排除的文件夹名称，多个用逗号分隔(例如: 临时文件,测试文件夹) |
| `returnFileDesc` | Boolean | 否 | 强制带回文件描述摘要(建议AI传true) |

**响应参数**

`data` 类型为 `List<FileVO>`，字段详见 **[5.1 FileVO](#51-filevo)**。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 支持 `type`/`excludeFileTypes`/`excludeFolderNames`/`returnFileDesc` 过滤 |

**请求示例（新建文件，Agent 归档首选）**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getChildFiles?parentId=1000' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例（新建文件）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {"id": 1001, "name": "技术方案", "type": 1, "parentId": 0, "hasChild": true},
    {"id": 1002, "name": "需求文档.pdf", "type": 2, "parentId": 0, "suffix": "pdf", "size": 204800, "hasChild": false}
  ]
}
```

**响应示例（更新版本）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "fileId": 12345,
    "fileName": "2026Q1调研报告.md"
  }
}
```

**数据流向**

- 返回的 `id`（文件夹类型）可作为本接口 `parentId` 继续下钻；`id`（文件类型）用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** 的入参。

---

### 4.2 【获取】获取文件下载与在线预览凭据

根据文件 ID 获取下载 URL 或在线预览所需凭据信息。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getDownloadInfo` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 文件下载与在线预览 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件 id |
| `path` | String | 否 | 基于文件id的相对路径 |
| `fileName` | String | 否 | 文件名 |
| `forceDownload` | Boolean | 否 | 是否强制下载（true 下载，false 在线预览） |
| `seeOriginal` | Boolean | 否 | 预览是否查看原文 |
| `source` | String | 否 | 来源 |
| `versionNumber` | Integer | 否 | 版本号 |
| `bypassRisk` | Boolean | 否 | 是否绕过风险检查 |

**响应参数**

`data` 类型为 `DownloadInfoVO`，字段详见 **[5.2 DownloadInfoVO](#52-downloadinfovo)**。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回全部字段 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getDownloadInfo?fileId=20001' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "downloadUrl": "https://oss.example.com/signed-urlxxx",
    "fileId": 20001,
    "openWith": 2,
    "lazyLoad": true,
    "fileName": "需求文档.pdf",
    "suffix": "pdf",
    "size": 204800
  }
}
```

**数据流向**

- 返回的 `downloadUrl` 直接用于前端下载/预览；`openWith` 用于决策渲染方式。

---

### 4.3 【获取】UI阅读模式：根据文件ID和页码分页获取内容

主要供 UI 界面提供对文件进行分段、分页的分批流式展示。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getFileContent` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | UI 分页展示文件内容 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件 id |
| `pageNumber` | Integer | 否 | 页码，从第一页开始 |

**响应参数**

`data` 类型为 `String`，为该页的排版文本。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 是（通过 `pageNumber` 参数） |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 按页码返回单页内容 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getFileContent?fileId=30001&pageNumber=1' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "# 第一章 概述\n\n本文档描述了..."
}
```

**数据流向**

- 无下游接口依赖。

---

### 4.4 【获取】AI摘要模式：根据业务资源自适应获取全局提纯文本

面向 AI Agent 设计的智能全文提取引擎。会自动根据传入的业务类型路由至对应微服务获取实况，若不传则降级反查内部物理文件的 RAG 知识库脱水版本。返回经过高度清洗和提纯的全局 Markdown 文本。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getFullFileContent` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | AI Agent 提取文件全文（RAG 入口） |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 否 | 文件id（推荐仅传此参数，后端自动补全其余字段） |
| `relationId` | String | 否 | 业务关联id（可选，后端可根据fileId自动补全） |
| `fileType` | String | 否 | 业务类型（可选，后端可根据fileId自动补全）。枚举：doc(富文本), file(普通文件), work_report(工作汇报), work_plan(工作任务), url(链接), huiji(慧记), ai-report(AI情报) |

**响应参数**

`data` 类型为 `String`，格式为全局提纯的纯文本或 Markdown 面向解析器的文本格式。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回提纯全文，建议大文件使用 4.3 分页 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getFullFileContent?fileId=30001' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": "# 全文提纯内容\n\n## 摘要\n\n本文档主要..."
}
```

**数据流向**

- 无下游接口依赖。

---

### 4.5 - 4.7 大文件分片上传 (已迁移)

为了统一文件处理能力，分片上传相关接口已迁移至 **基础服务 — 文件服务**：

- **4.5 预检文件MD5信息（支持秒传）**
- **4.6 合并文件分片生成底层资源**
- **4.7 注册文件分片数据**

请参阅：**[02-文件服务.md](../基础服务/API接口明细/02-文件服务.md#场景二大文件分片上传流程-推荐)** 获取最新接口详述与调用流程。

---
 
### 4.8 【基础】获取个人知识库空间ID

获取当前用户个人知识库的空间 ID（projectId），用于对应知识库目录。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/personal/getProjectId` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 获取个人知识库空间标识 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `appCode` | String | 否 | 应用编码 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回单个 Long 值 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/project/personal/getProjectId' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": 2009488364113997826
}
```

**数据流向**

- 返回的 `projectId` 用于 **4.12 getLevel1Folders** / **4.11 searchFile** / **4.17 saveFileByPath** 的 `projectId` 入参。

---

### 4.9 【检索】获取我最新上传的文件

获取当前用户最新上传的文件列表（支持 limit 限制）。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/personal/getRecentFiles` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 获取最近上传文件列表 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `limit` | Integer | 否 | 限制数量 |
| `searchKey` | String | 否 | 搜索关键字 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否（通过 `limit` 控制数量） |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 支持 `limit` 限制返回数量 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/project/personal/getRecentFiles' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"limit":10,"searchKey":"报告"}'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {"id": 3001, "name": "周报.pdf", "type": 2, "parentId": 1001, "resourceId": 987654321, "size": 102400, "suffix": "pdf"}
  ]
}
```

**数据流向**

- 返回的 `id` 用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** 的入参。

---
 
### 4.10 【上传】将文件资源保存到个人知识库目录

将已有资源或新建内容保存到个人知识库目录。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/personal/saveFile` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | 将资源绑定到个人知识库目录 |

**请求参数**

请求体为 `SavePersonalFileParam` (见 5.8)。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 否 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回单个 Long 值 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/project/personal/saveFile' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"parentId":0,"name":"测试文件.pdf","type":2,"resourceId":987654321,"fileType":"file","suffix":"pdf","size":102400,"isSensitive":0}'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": 30001
}
```

**数据流向**

- 返回的 `fileId` 可用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** / **4.13 deleteFile** / **4.14 updateFileProperty** 的入参。

---
 
### 4.11 【检索】搜索文件或目录

根据关键词、时间范围等条件，在指定项目/空间或全局范围内搜索文件和文件夹。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/searchFile` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | Agent 按关键词检索文件或目录 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `projectId` | Long | 否 | 项目/空间 id |
| `nameKey` | String | 否 | 名称关键词。**⚠️ 中文必须 URL 编码（UTF-8）** |
| `rootFileId` | Long | 否 | 指定根目录 id（在此目录下搜索） |
| `startTime` | Long | 否 | 创建时间-开始时间戳（毫秒） |
| `endTime` | Long | 否 | 创建时间-结束时间戳（毫秒） |
| `isFileStorage` | Boolean | 否 | 是否为文件存储范围（默认 false） |
| `permissionQuery` | String | 否 | 权限查询条件 |
| `excludeFileTypes` | String | 否 | 排除的文件类型，逗号分隔（如 `work_report,huiji,ai-report`） |
| `excludeFolderNames` | String | 否 | 排除的文件夹名称，逗号分隔（如 `临时文件,测试文件夹`） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 支持 `excludeFileTypes`/`excludeFolderNames` 过滤 |

**请求示例**

```bash
# 示例：搜索名称包含"测试"的文件
# 原始参数：nameKey=测试
# URL 编码后（UTF-8）：nameKey=%E6%B5%8B%E8%AF%95
curl -X GET 'https://{域名}/open-api/document-database/file/searchFile?nameKey=%E6%B5%8B%E8%AF%95' \
  -H 'appKey: YOUR_API_KEY'
```

**响应参数**

`data` 类型为 `SearchFileVO`，字段详见 **[5.9 SearchFileVO](#59-searchfilevo)**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "folders": [
      {"id": 1001, "name": "测试文件夹", "type": 1, "parentId": 0, "hasChild": true}
    ],
    "files": [
      {"id": 2001, "name": "测试报告.pdf", "type": 2, "parentId": 1001, "suffix": "pdf", "size": 102400, "hasChild": false}
    ]
  }
}
```

**数据流向**

- 返回的 `id`（文件类型）用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** 的入参；`id`（文件夹类型）用于 **4.1 getChildFiles** 的 `parentId` 入参。

---
 
### 4.12 【检索】根据项目ID获取一级目录列表

拉取指定项目空间的绝对顶层（根目录）下的所有文件夹及文件。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getLevel1Folders` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | Agent 浏览空间根目录全景 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `projectId` | Long | 是 | 项目/空间 id（来自 4.8 或 4.19 返回的 id） |
| `order` | Integer | 否 | 排序规则：1(更新倒序), 2(更新顺序), 5(名字倒序), 6(名字顺序) |
| `permissionQuery` | String | 否 | 权限查询条件 |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回全部一级子项 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getLevel1Folders?projectId=2009488364113997826' \
  -H 'appKey: YOUR_API_KEY'
```

**响应参数**

`data` 类型为 `List<FileVO>`，字段详见 **[5.1 FileVO](#51-filevo)**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {"id": 1001, "name": "技术方案", "type": 1, "parentId": 0, "hasChild": true},
    {"id": 1002, "name": "需求文档.pdf", "type": 2, "parentId": 0, "suffix": "pdf", "size": 204800, "hasChild": false}
  ]
}
```

**数据流向**

- 返回的 `id`（文件夹类型）用于 **4.1 getChildFiles** 的 `parentId` 入参继续下钻；`id`（文件类型）用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** 的入参。

---

### 4.13 【写操作】删除文件（逻辑删除或物理彻底删除）

当 `isPhysical` 为 `true` 时，将执行物理彻底删除（逻辑删除后再彻底从回收站抹除）。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/deleteFile` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | Agent 删除指定文件 |

**请求参数**

请求体为 `FileDeleteParam`，主要字段如下：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件 ID |
| `isPhysical` | Boolean | 否 | 是否物理彻底删除 (true=彻底销毁, false/null=移入回收站) |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-重复删除已删除文件不会报错 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 不适用 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/deleteFile' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"fileId":30001}'
```

**响应参数**

`data` 类型为 `Boolean`，表示操作成功与否。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": true
}
```

**数据流向**

- 无下游接口依赖。删除后的 `fileId` 不可再用于 **4.2** / **4.3** / **4.4** 等查询接口。

---

### 4.14 【写操作】更新文件属性（重命名/移动/覆盖）

【Agent 提示】支持重命名和跨目录移动。

**冲突处理策略（重要）**:
同名冲突时，系统支持三选一策略：
1. **静默覆盖**：传 `cover=true`。
2. **自动追加后缀**：传 `autoRename=true`（如 `文件名(1).pdf`）。
3. **严格报错**：二者均不传，冲突时后端抛出异常。

请 Agent 依据人类用户的意向选择合适的策略参数。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/updateFileProperty` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | Agent 重命名或移动文件 |

**请求参数**

请求体为 `FileModifyParam`，主要字段如下：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |
| `newName` | String | 否 | 新文件名（为空即可仅做移动） |
| `targetParentId` | Long | 否 | 目标父目录ID（为空即可仅做重命名） |
| `cover` | Boolean | 否 | 同名冲突时是否覆盖（cover 与 autoRename 互斥，cover 优先级更高） |
| `autoRename` | Boolean | 否 | 同名冲突时是否自动追加数字后缀重命名（cover=true 时本字段被忽略） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 否-重复移动可能因覆盖策略产生不同结果 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 不适用 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/updateFileProperty' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"fileId":30001,"newName":"新版报告.pdf","autoRename":true}'
```

**响应参数**

`data` 类型为 `Boolean`，表示操作成功与否。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": true
}
```

**数据流向**

- 无下游接口依赖。操作后文件 `id` 不变，可通过 **4.1 getChildFiles** 重新浏览变更后的目录结构。

---

### 4.15 【获取】批量获取多个文件的 RAG 全文内容

批量获取多个文件的全文本资料，减少交互往返次数，提升数据处理效率。走 Adapter 穿透引擎。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/ai/batchGetContent` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | AI Agent 批量提取文件全文（建议单次不超过 10 个文件） |

**请求参数**

请求体为 `BatchGetContentParam`：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `files` | List\<FileIdentifyDTO\> | 是 | 文件解析标识对象列表 |

其中 `FileIdentifyDTO` 结构说明：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |
| `relationId` | String | 否 | 业务关联ID（可选，后端可根据fileId自动补全。仅在需要强制覆盖元数据时传入） |
| `fileType` | String | 否 | 关联的业务类型（可选，后端可根据fileId自动补全）。枚举：doc(富文本), file(普通文件), work_report(工作汇报), work_plan(工作任务), url(链接), huiji(慧记), ai-report(AI情报) |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 是（建议单次不超过 10 个文件；部分文件失败不影响其他文件返回） |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 每个文件独立返回 status 字段标识成功/空/错误 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/ai/batchGetContent' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"files":[{"fileId":30001},{"fileId":30002,"fileType":"doc"}]}'
```

**响应参数**

`data` 类型为 `List<FileContentVO>`：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `fileId` | Long | 文件ID |
| `content` | String | 文件内容体 |
| `status` | String | 状态 (success/empty/error) |
| `message` | String | 附带消息 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {"fileId": 30001, "content": "# 全文提纯内容\n\n本文档主要...", "status": "success", "message": null},
    {"fileId": 30002, "content": null, "status": "empty", "message": "文件内容为空"}
  ]
}
```

**数据流向**

- 无下游接口依赖。返回的 `content` 可直接供 AI 模型消费。

---

### 4.16 【上传】根据父ID保存文件到项目目录 [新增]

已知目标文件夹 ID 时，通过 `parentId` 直接将物理文件资源保存到项目知识库的指定目录。此接口仅支持绑定已上传的物理文件（传 `resourceId`，建议同时传 `suffix`、`size`）。

> **纯文本内容**（如 AI 生成的 Markdown/报告）请使用 **4.18 uploadContent** 接口，无需走分片上传流程。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/saveFileByParentId` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | Agent 将文件保存到已知目录下 |

**请求参数**

请求体为 `SaveFileToProjectParam`，字段详见 **[5.10 SaveFileToProjectParam](#510-savefiletoprojectparam)**。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 否-重复调用会创建多个文件 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 不适用 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/saveFileByParentId' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"projectId":2025001,"parentId":10086,"name":"技术方案.pdf","fileType":"file","suffix":"pdf","size":204800,"resourceId":987654321,"isSensitive":0}'
```

**响应参数**

`data` 类型为 `Long`，返回新建/更新的文件 ID。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": 12345678
}
```

**数据流向**

- 返回的 `fileId` 可用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** / **4.13 deleteFile** / **4.14 updateFileProperty** 的入参。

---

### 4.17 【上传】根据路径保存文件到项目目录 [新增]

通过 `path` 参数指定逻辑目录路径（如 `FolderA/FolderB`），后端将自动递归解析并创建不存在的文件夹，将物理文件资源保存到最终目录下。此接口仅支持绑定已上传的物理文件（传 `resourceId`，建议同时传 `suffix`、`size`）。

> **纯文本内容**（如 AI 生成的 Markdown/报告）请使用 **4.18 uploadContent** 接口，无需走分片上传流程。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/saveFileByPath` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | Agent 按逻辑路径自动归档文件 |

**请求参数**

请求体为 `SaveFileToProjectParam`，字段详见 **[5.10 SaveFileToProjectParam](#510-savefiletoprojectparam)**。其中 `path` 字段为逻辑目录路径（如 `"工程档案/设计图纸"`），不传则存入项目根目录。

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 否-重复调用会创建多个文件 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 不适用 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/saveFileByPath' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"projectId":2025001,"path":"工程档案/设计图纸","name":"方案.pdf","fileType":"file","suffix":"pdf","size":204800,"resourceId":987654321,"isSensitive":0}'
```

**响应参数**

`data` 类型为 `Long`，返回新建/更新的文件 ID。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": 12345678
}
```

**数据流向**

- 返回的 `fileId` 可用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** / **4.13 deleteFile** / **4.14 updateFileProperty** 的入参。

---

### 4.18 【上传】一键快速保存纯文本到个人空间 [新增]

**Agent 极速存盘首选方案**。专门用于保存 AI 生成的文本内容（摘要、报告、Markdown）。该接口会自动解析当前用户的个人空间，无需外部传入 `projectId`。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/uploadContent` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | AI 生成内容一键持久化到个人空间 |

**请求参数**

请求体为 `UploadContentToPersonalProjectParam`：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `content` | String | 是 | 文本/Markdown/HTML 内容字节流 |
| `fileName` | String | 是 | 保存的文件名 |
| `fileSuffix` | String | 否 | 文件后缀（如 `md`, `json`, `html`, `txt`）。**强烈建议显式传入**。不传则直接兜底为 `md`，若文件名已含扩展名（如 `报告.html`）会被错误追加 `.md` 后缀 |
| `folderName` | String | 否 | 逻辑目录名。**默认：'和AI的对话'**。支持多级路径。仅在新建模式下有效 |
| `updateFileId` | Long | 否 | **版本更新模式专用**：要更新版本的文件 ID（即目标文件的 `fileId`，可通过 `getChildFiles`/`searchFile` 查询获得，或上传文件时的返回值）。传入则更新已有文件的版本，不传则新建文件到个人空间 |
| `versionRemark` | String | 否 | **版本更新模式专用**：版本说明（如"修订了第三章内容"） |
| `versionName` | String | 否 | **版本更新模式专用**：版本名称（如"V2.0"） |

**请求行为约定**

1. **纯文本限制**：该接口仅支持保存纯文本性质的数据，不支持物理二进制流。
2. **后缀兜底**：不传 `fileSuffix` 时，系统兜底为 `md`。建议显式传入 `fileSuffix` 以确保文件格式正确。
3. **默认归档**：如果不传 `folderName`，文件将归档至个人空间默认目录 **"和AI的对话"** 下（仅新建模式）。
4. **版本更新模式**：传入 `updateFileId` 时，接口自动切换为版本更新模式，`folderName` 参数无效，文件内容将作为新版本绑定到目标文件。

**请求示例（新建文件，Agent 归档首选）**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/uploadContent' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "content": "# 调研结论\n\n## 1. 核心观点\n- 方案可行\n- 成本可控\n\n> 提示：这是自动生成的报告",
    "fileName": "2026Q1调研报告",
    "fileSuffix": "md"
  }'
```

**请求示例（更新已有文件版本）**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/uploadContent' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "updateFileId": 12345,
    "content": "# 调研结论 V2\n\n## 1. 核心观点（修订版）\n- 方案可行，成本已优化",
    "fileName": "2026Q1调研报告",
    "fileSuffix": "md",
    "versionRemark": "修订了第三章内容",
    "versionName": "V2.0"
  }'
```

**响应参数**

| 属性名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| `data` | Object | `UploadContentToPersonalProjectResult` 结构（详见 **[5.12](#512-uploadcontenttopersonalprojectresult-新增)**） |

**响应示例（新建文件）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "projectId": 2009488364113997826,
    "projectName": "个人知识库",
    "folderId": 10086,
    "folderName": "和AI的对话",
    "fileId": 30005,
    "fileName": "2026Q1调研报告.md",
    "downloadUrl": "https://oss.../signed-url"
  }
}
```

**响应示例（更新版本）**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "fileId": 12345,
    "fileName": "2026Q1调研报告.md"
  }
}
```

**数据流向**

- 生成的 `fileId` 可直接用于 **4.2 getDownloadInfo** / **4.3 getFileContent** / **4.4 getFullFileContent** 的入参，实现从"写入"到"阅读/索引"的闭环。

---

### 4.19 【基础】获取该账号有权限访问的空间列表 [新增]

拉取当前账号有权访问（含只读）的所有空间列表，用于 Agent 进行前置的空间发现与导航。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/list` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | Agent 发现可用空间、浏览空间列表 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `appCode` | String | 否 | 应用编码（默认 `kz_doc`） |
| `nameKey` | String | 否 | 空间名称模糊搜索关键词。**⚠️ 中文必须 URL 编码（UTF-8）** |
| `bizCode` | String | 否 | 业务线编码过滤（如 `pmo`） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 支持 `nameKey`/`bizCode` 过滤 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/project/list' \
  -H 'appKey: YOUR_API_KEY'
```

**响应参数**

`data` 类型为 `List<ProjectVO>`，字段详见 **[5.13 ProjectVO](#513-projectvo)**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": 2025001,
      "name": "AI 研发中心",
      "remark": "存放 AI 相关的技术蓝图",
      "type": "common",
      "role": 1,
      "canCreateAtRoot": true,
      "rawEnabled": true
    },
    {
      "id": 2025002,
      "name": "产品周报空间",
      "type": "common",
      "role": 0,
      "canCreateAtRoot": false,
      "rawEnabled": false
    }
  ]
}
```

**数据流向**

- 返回的 `id`（即 `projectId`）用于 **4.12 getLevel1Folders** / **4.1 getChildFiles** / **4.11 searchFile** / **4.16 saveFileByParentId** / **4.17 saveFileByPath** 的 `projectId` 入参。

---

### 4.20 【基础】获取该账号有上传/编辑权限的空间列表 [新增]

**存盘必备接口**。仅返回当前账号拥有写入权限的空间。Agent 在执行”保存”、”归档”等动作前，应调用此接口展示目标空间。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/project/uploadableList` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | Agent 保存文件前确定目标空间 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `appCode` | String | 否 | 应用编码（默认 `kz_doc`） |
| `nameKey` | String | 否 | 空间名称模糊搜索关键词。**⚠️ 中文必须 URL 编码（UTF-8）** |
| `bizCode` | String | 否 | 业务线编码过滤（如 `pmo`） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 支持 `nameKey`/`bizCode` 过滤；仅返回有写入权限的空间 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/project/uploadableList?bizCode=pmo' \
  -H 'appKey: YOUR_API_KEY'
```

**响应参数**

`data` 类型为 `List<ProjectVO>`，字段详见 **[5.13 ProjectVO](#513-projectvo)**。

**响应示例**

```json
{
  “resultCode”: 1,
  “resultMsg”: null,
  “data”: [
    {
      “id”: 2025001,
      “name”: “AI 研发中心”,
      “remark”: “存放 AI 相关的技术蓝图”,
      “type”: “common”,
      “role”: 1,
      “canCreateAtRoot”: true,
      “rawEnabled”: true
    }
  ]
}
```

**数据流向**

- 返回的 `id`（即 `projectId`）用于 **4.16 saveFileByParentId** / **4.17 saveFileByPath** 的 `projectId` 入参。

---

### 4.21 【记忆沙盒】新建项目长程记忆

新建项目长程记忆空间。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/memory/createProject` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 版本号 | v1 |
| 推荐调用场景 | 为 AI 任务创建独立的长程记忆容器 |

**请求参数**

请求体为 `CreateProjectParam`：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 项目名称 |

**响应参数**

`data` 类型为 `Long`，返回新创建的项目 ID。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/memory/createProject' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"name": "大模型调研方案"}'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": 10086
}
```

---

### 4.22 【记忆沙盒】获取项目记忆列表

获取当前用户可见的所有项目记忆空间列表。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/memory/getProjectList` |
| 请求方式 | `GET` |
| 推荐调用场景 | 概览所有已存在的记忆空间 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `order` | Integer | 否 | 排序规则：1(更新倒序), 3(创建倒序) |

**响应参数**

`data` 类型为 `List<ProjectItemVO>`，字段详见 **[5.14 ProjectItemVO](#514-projectitemvo)**。

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/memory/getProjectList?order=1' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": 10086,
      "name": "大模型知识空间",
      "hasChild": true,
      "createTime": 1712620800000,
      "createTimeStr": "2026-04-09 10:00"
    }
  ]
}
```

---

### 4.23 【记忆沙盒】项目记忆检索

按名称关键词快速检索记忆空间。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/memory/searchProject` |
| 请求方式 | `GET` |
| 推荐调用场景 | 快速定位特定的记忆项目 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `nameKey` | String | 是 | 搜索关键词 |

**响应参数**

`data` 类型为 `List<ProjectItemVO>`，字段详见 **[5.14 ProjectItemVO](#514-projectitemvo)**。

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/memory/searchProject?nameKey=%E5%A4%A7%E6%A8%A1%E5%9E%8B' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": 10086,
      "name": "大模型安全机制",
      "hasChild": true,
      "createTime": 1712620800000,
      "createTimeStr": "2026-04-09 10:00"
    }
  ]
}
```

---

### 4.24 【记忆沙盒】获取项目骨架与记忆内容

提取指定记忆项目下的逻辑骨架（目录）及文件脱水内容摘要。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/memory/getProjectContents` |
| 请求方式 | `GET` |
| 推荐调用场景 | 获取项目记忆的具体内容大纲 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 记忆空间的根 ID 或子目录 ID |

**响应参数**

`data` 类型为 `List<ProjectFileVO>`，字段详见 **[5.15 ProjectFileVO](#515-projectfilevo)**。

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/memory/getProjectContents?fileId=10086' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": 2001,
      "name": "技术方案.pdf",
      "type": 2,
      "suffix": "pdf",
      "size": 204800,
      "fileType": "file",
      "relationId": "98765",
      "hasChild": false,
      "fileDescription": "本方案描述了架构总体设计...",
      "createTime": 1712620800000,
      "createTimeStr": "2026-04-09 10:00"
    }
  ]
}
```

---


### 4.25 【版本】上传新文件内容以更新文件版本

将已上传的物理文件资源绑定到已有文件，产生新版本记录。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/updateFileVersion` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | 物理文件版本更新 |

**请求参数**

请求体为 `UpdateFileVersionParam`：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | Long | 是 | 要更新的文件ID |
| `projectId` | Long | 是 | 文件所在空间ID |
| `resourceId` | Long | 是 | 新上传的物理资源ID（通过 saveResource 接口获取） |
| `name` | String | 否 | 文件名（可选，不传则保持原文件名） |
| `versionStatus` | Integer | 否 | 版本行为控制：1=覆盖当前草稿（默认）；2=强制新建版本；3=新建版本并立即定稿 |
| `versionName` | String | 否 | 版本名称，如 V2.0 |
| `versionRemark` | String | 否 | 版本说明 |
| `suffix` | String | 否 | 文件后缀 |
| `size` | Long | 否 | 文件大小（字节） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 否-重复调用会创建多个版本 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 不适用 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/updateFileVersion' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"id":12345,"projectId":2025001,"resourceId":987654321,"versionStatus":3,"versionName":"V2.0","versionRemark":"修正了第三章内容"}'
```

**响应参数**

`data` 类型为 `Long`，返回文件 ID。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": 12345
}
```

**数据流向**

- 返回的 `fileId` 可用于 **4.2 getDownloadInfo** / **4.26 getVersionList** 的入参。

---

### 4.26 【版本】获取文件的所有历史版本列表

获取指定文件的完整版本历史，包括版本号、定稿状态、创建人、备注等信息。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getVersionList` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 查看文件版本历史 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回全部版本记录 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getVersionList?fileId=12345' \
  -H 'appKey: YOUR_API_KEY'
```

**响应参数**

`data` 类型为 `List<FileVersionVO>`，字段详见 **[5.17 FileVersionVO](#517-fileversionvo)**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": 1003, "fileId": 12345, "versionNumber": 3, "versionName": "V3.0",
      "status": 1, "remark": "修正了第三章内容", "label": "初始化",
      "creator": "张三", "createTime": 1712707200000,
      "lastVersion": true
    },
    {
      "id": 1002, "fileId": 12345, "versionNumber": 2, "versionName": "V2.0",
      "status": 2, "remark": "增加附录", "label": "放行",
      "creator": "李四", "createTime": 1712620800000,
      "lastVersion": false
    }
  ]
}
```

**数据流向**

- 返回的版本记录可用于 **4.28 finalizeVersion** 的 `versionNumber` 入参。

---

### 4.27 【版本】获取文件的最新版本信息

快速获取文件当前最新版本的详细信息。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/getLastVersion` |
| 请求方式 | `GET` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 查询 |
| 推荐调用场景 | 判断当前版本状态 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-天然幂等（只读查询） |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 返回单个版本记录 |

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/document-database/file/getLastVersion?fileId=12345' \
  -H 'appKey: YOUR_API_KEY'
```

**响应参数**

`data` 类型为 `FileVersionVO`，字段详见 **[5.17 FileVersionVO](#517-fileversionvo)**。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "id": 1003, "fileId": 12345, "versionNumber": 3, "versionName": "V3.0",
    "status": 2, "remark": "最终定稿版本", "label": "放行",
    "creator": "张三", "createTime": 1712707200000,
    "lastVersion": true
  }
}
```

**数据流向**

- 返回的 `status` 字段可用于判断是否需要调用 **4.28 finalizeVersion**。

---

### 4.28 【版本】将指定版本标记为定稿

将文件的某个版本标记为正式定稿状态（status 从 1 变为 2）。

**基本信息**

| 项目 | 说明 |
| :--- | :--- |
| 接口地址 | `/document-database/file/finalizeVersion` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |
| 接口负责人 | 知识库服务团队 |
| 所属模块 | 知识库服务 |
| 版本号 | v1 |
| 接口类型 | 写入 |
| 推荐调用场景 | 版本定稿 |

**请求参数**

请求体为 `FinalizeVersionParam`：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `fileId` | Long | 是 | 文件ID |
| `versionNumber` | Integer | 否 | 要定稿的版本号（不传或传0则定稿最新版本） |

**请求与行为约定**

| 项 | 说明 |
| --- | --- |
| 是否支持分页 | 否 |
| 是否支持批量 | 否 |
| 幂等性要求 | 是-重复定稿已定稿版本不会报错 |
| 额外字段策略 | 忽略未定义字段 |
| 返回裁剪策略 | 不适用 |

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/document-database/file/finalizeVersion' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"fileId":12345,"versionNumber":3}'
```

**响应参数**

`data` 类型为 `Boolean`，表示操作成功与否。

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": true
}
```

**数据流向**

- 定稿后，下次调用 **4.25 updateFileVersion** 或 **4.18 uploadContent（版本更新模式）** 将自动创建新版本。

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
| `downloadUrl` | String | 下载 url / 临时签名 |
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
5. **路径自动解析**：使用 `saveFileByPath` 时，`path` 中的路径分隔符为 `/`，后端会自动递归创建不存在的目录层级。
6. **AI 无关字段过滤**：列表接口仅返回文件元数据（名称/类型/大小/后缀等），不内嵌正文内容；正文需通过 4.3/4.4/4.15 独立获取，避免单次返回 token 过大。
7. **避免父子重复**：`FileVO` 中的 `ancestorNames` 已包含完整路径，不再逐级重复返回父级属性；`breadcrumb` 与 `ancestorNames` 为同义词，优先使用 `ancestorNames`。
8. **层级与长度控制**：文件列表默认 1 层，需下钻时通过 `parentId` 递归调用；大文件全文建议通过 `getFileContent`（4.3）分页读取，避免单次返回超长文本。
9. **富文本原文规则**：在线文档（`fileType=doc`）的原始富文本不在列表接口返回；需通过 `getFileContent` 或 `getFullFileContent` 获取结构化 Markdown 文本。`getFullFileContent` 保留标题/列表/表格等结构语义，不会简单压平为纯文本。
10. **列表裁剪能力**：`getChildFiles` 支持 `type`（仅文件/仅文件夹）、`excludeFileTypes`、`excludeFolderNames`、`returnFileDesc` 等裁剪参数，AI Agent 应善用这些参数减少无关数据。
11. **空值约定**：全文档统一使用 `null` 表示无数据；`null`、空串 `""`、空数组 `[]` 语义相同，调用方无需区分。

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
