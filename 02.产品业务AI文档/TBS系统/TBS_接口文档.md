# TBS-Admin API 契约设计

---

## 0. 环境信息与快速联调

### 0.1 Base URL

- **测试环境**: `https://cwork-web-test.xgjktech.com.cn/tbs-admin`
- **生产环境**: `https://sg-al-cwork-web.mediportal.com.cn/tbs-admin`
- **服务名前缀**: `/tbs-admin`
- **说明**: 请求经网关后，会按 `/tbs-admin` 前缀分发到 `tbs-admin` 后台接口路径。
- **完整示例**: `https://cwork-web-test.xgjktech.com.cn/tbs-admin/scene/listScenes`

### 0.2 通用请求头

> 除少量公开接口外，建议统一携带以下请求头。

```http
access-token: <ACCESS_TOKEN>
Content-Type: application/json
```

### 0.3 通用 cURL 模板

```bash
curl -X POST "https://cwork-web-test.xgjktech.com.cn/tbs-admin/<path>" \
  -H "access-token: <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "value"
  }'
```

### 0.4 环境变量模板（推荐）

```bash
export TBS_BASE_URL="https://cwork-web-test.xgjktech.com.cn/tbs-admin"
export TBS_ACCESS_TOKEN="<ACCESS_TOKEN>"
```

使用示例：

```bash
curl -X GET "$TBS_BASE_URL/rolePersona/forResourceSelect" \
  -H "access-token: $TBS_ACCESS_TOKEN"
```

### 0.5 鉴权说明

- `access-token` 使用登录后颁发的登录态 token。
- 大多数管理接口要求登录鉴权。

### 0.6 命名约定（camelCase）

- **JSON 请求体**、**Query 参数**中的业务字段统一为 **camelCase**（如 `departmentId`、`businessDomainId`）。
- **统一响应体**字段为 `resultCode`、`resultMsg`、`data`，结构见文末「公共约定」中的「响应结构」。业务成功时 `resultCode` 一般为 **`1`**（或 **`200`**，与网关及前端 `apiService` 判断一致）。
- **HTTP 请求头** `access-token` 为网关/客户端约定名称（kebab-case），不属于 JSON 字段命名规则。
- **ID 与整型主键**：若数值可能超过 JavaScript 安全整数范围（`Number.MAX_SAFE_INTEGER`，即 2^53−1），在 JSON 中建议使用 **字符串** 表示（如 ID 数组、单字段 ID、响应中的 `data`），避免浏览器端精度丢失；后端通常仍按 `Long` 解析。

---

## 1. 公共资源 API (Resources API)

> **用途**: 前端下拉列表、选择器等只读数据获取

- **医生画像列表**: `GET /rolePersona/forResourceSelect`
- **产品知识列表**: `GET /knowledge/forResourceSelect`
  - 参数: `drugId`, `category`
- **场景标签列表**: `GET /tag/forResourceSelect`
  - 参数: `category`
- **疾病列表**: `GET /disease/forResourceSelect`
  - 参数: `departmentId`

---

## 2. 配置管理 API (Admin API)

> **注意**: 管理端接口按业务模块划分，常用模块包括 **场景**、**提示词**、**基础数据**。

### 2.1 场景管理 (`/scene`)

- **搜索**: `POST /scene/searchScenes`
- **列表**: `POST /scene/listScenes`
- **创建**: `POST /scene/createScene`
- **详情**: `POST /scene/getSceneDetail`
- **更新**: `POST /scene/updateScene`
- **删除**: `POST /scene/deleteScene`

#### 特殊操作

- **复制场景**: `POST /scene/duplicateScene`
- **恢复场景**: `POST /scene/recoverScene`
- **获取 YAML**: `POST /scene/getSceneYaml`
- **生成简报语音**: `POST /scene/generateBriefingAudio`
- **生成背景图任务**: `POST /scene/generateBackgroundImages`
- **查询背景图任务状态**: `POST /scene/getImageTaskStatus`
- **读取最佳实践**: `POST /scene/getBestPractice`
- **保存最佳实践**: `POST /scene/saveBestPractice`
- **获取产品知识聚合文本**: `POST /scene/getProductKnowledge`
- **保存产品知识聚合文本**: `POST /scene/saveProductKnowledge`

#### PPT 演讲场景 (`/pptscene`)

- **列表**: `POST /pptscene/listPptScenes`
- **详情**: `POST /pptscene/getPptSceneDetail`（参数: `id`）
- **创建**: `POST /pptscene/createPptScene`
- **更新**: `POST /pptscene/updatePptScene`
- **删除**: `POST /pptscene/deletePptScene`
- **其他**: `GET /pptscene/proxyNotexPptList`；`POST /pptscene/getPptReviewPromptTemplate`；`POST /pptscene/extractPptKeywords`

### 2.2 提示词配置 (`/prompt`)

- **获取配置**: `GET /prompt/getPrompt`
  - Query: `promptType`（必填）, `scope`（可选）, `sceneDbId`（`scope=scene` 时必填）
- **保存配置**: `POST /prompt/savePrompt`
  - Query: `promptType`（必填）；Body: `SavePromptDTO`（模板等字段）
- **历史记录**: `GET /prompt/listPromptHistory`
  - Query: `promptType`、`scope` **均为必填**；`sceneDbId` 在 `scope=scene` 时必填
- **回滚**: `POST /prompt/rollbackPrompt`
  - Query: `promptType`（必填）；Body: `{"historyId": <Long>}`（必填）
- **清除场景定制**: `POST /prompt/clearScenePrompt`
  - Query: `promptType`（必填）；Body: `{"sceneDbId": <Long>}`（必填，可选兼容字段 `role`）
- **预览**: `POST /prompt/previewPrompt`
  - Body: `PreviewPromptDTO`

### 2.3 基础数据管理

#### 角色画像 (Role Persona)

- `POST /rolePersona/listRolePersonas`
- `POST /rolePersona/createRolePersona`
- `POST /rolePersona/updateRolePersona`
- `POST /rolePersona/deleteRolePersona`

#### 产品知识 (Knowledge)

- `POST /knowledge/listProductKnowledge`
- `POST /knowledge/createProductKnowledge`
- `POST /knowledge/updateProductKnowledge`
- `POST /knowledge/deleteProductKnowledge`
  - 当前按企业维度返回列表；写操作仅企业管理员可执行

#### 品种 (Drugs)

- `POST /drug/listDrugs`
- `POST /drug/createDrug`
- `POST /drug/updateDrug`
- `POST /drug/deleteDrug`
  - 当前仅保留后台主数据 CRUD，不再提供负责人或旧品种权限相关接口

#### 其他基础数据

- **科室**: `/department`
  - `POST /department/listDepartments`
  - `POST /department/createDepartment`
  - `POST /department/updateDepartment`
  - `POST /department/deleteDepartment`
- **疾病**: `/disease`
  - `POST /disease/listDiseases`
  - `POST /disease/createDisease`
  - `POST /disease/updateDisease`
  - `POST /disease/deleteDisease`
- **标签**: `/tag`
  - `POST /tag/listTags`
  - `POST /tag/createTag`
  - `POST /tag/updateTag`
  - `POST /tag/deleteTag`
- **业务领域**: `/businessDomain`
  - `POST /businessDomain/listBusinessDomains`
  - `POST /businessDomain/createBusinessDomain`
  - `POST /businessDomain/updateBusinessDomain`
  - `POST /businessDomain/deleteBusinessDomain`
- **厂家**: `/company`
  - `POST /company/listCompanies`
  - `POST /company/createCompany`
  - `POST /company/updateCompany`
  - `POST /company/deleteCompany`

### 2.4 创建类接口详细文档（标准格式）

> 本节补充常用“创建”接口的标准调用说明，便于联调与测试。
> 除特别说明外，均需登录态，且请求头带 `access-token`。

---

#### 2.4.1 创建自由对话模式场景

- **接口名称**: 创建场景（对话模式）
- **Method**: `POST`
- **URL**: `/scene/createScene`
- **Content-Type**: `application/json`
- **鉴权**: 需要
- **说明**: 普通对话场景使用本接口。PPT 场景请使用 `/pptscene/createPptScene`。

**请求体参数**

| 字段              | 类型             | 必填 | 说明                                                              |
| ----------------- | ---------------- | ---- | ----------------------------------------------------------------- |
| title             | string           | 是   | 场景标题                                                          |
| departmentId      | string \| number | 否   | 科室 ID                                                           |
| drugId            | string \| number | 否   | 品种 ID                                                           |
| businessDomainId  | string \| number | 否   | 业务领域 ID                                                       |
| diseaseId         | string \| number | 否   | 疾病 ID                                                           |
| location          | string           | 否   | 场景地点                                                          |
| doctorOnlyContext | string           | 否   | 医生侧上下文                                                      |
| coachOnlyContext  | string           | 否   | 教练侧上下文                                                      |
| repBriefing       | string           | 否   | 代表简报                                                          |
| personaIds        | array            | 否   | 场景关联画像                                                      |
| knowledgeIds      | array            | 否   | 场景关联知识 ID 列表（元素建议 string，见「命名约定」中 ID 说明） |
| tagIds            | array            | 否   | 场景关联标签 ID 列表（元素建议 string，同上）                     |
| status            | number           | 否   | 状态，默认 1                                                      |

`personaIds` 元素结构：

| 字段       | 类型             | 必填 | 说明                        |
| ---------- | ---------------- | ---- | --------------------------- |
| personaId  | string \| number | 是   | 医生画像 ID（建议 string）  |
| difficulty | string           | 是   | 难度（如 easy/medium/hard） |
| isDefault  | boolean          | 否   | 是否默认画像，默认 false    |
| rounds     | number           | 否   | 最大轮次，默认 5            |

**请求示例**

```json
{
  "title": "高血压门诊首诊沟通",
  "departmentId": "101",
  "drugId": "2001",
  "businessDomainId": "11",
  "diseaseId": "66",
  "location": "门诊诊室",
  "doctorOnlyContext": "医生时间紧张，对疗效与依从性关注高",
  "coachOnlyContext": "观察开场提问质量与需求挖掘深度",
  "repBriefing": "先确认患者分层，再自然引出方案价值",
  "personaIds": [
    {
      "personaId": "3001",
      "difficulty": "medium",
      "isDefault": true,
      "rounds": 6
    }
  ],
  "knowledgeIds": ["5001", "5002"],
  "tagIds": ["7001"],
  "status": 1
}
```

**成功响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": "1968452012345678900"
}
```

**常见错误**

- `400`: 参数格式错误或校验失败
- `403`: 无权限操作

---

#### 2.4.2 创建产品知识

- **接口名称**: 创建产品知识
- **Method**: `POST`
- **URL**: `/knowledge/createProductKnowledge`
- **Content-Type**: `application/json`
- **鉴权**: 需要

**请求体参数**

| 字段      | 类型   | 必填 | 说明         |
| --------- | ------ | ---- | ------------ |
| drugId    | number | 是   | 品种 ID      |
| category  | string | 是   | 分类         |
| title     | string | 是   | 知识标题     |
| content   | string | 是   | 知识正文     |
| sortOrder | number | 否   | 排序，默认 0 |

**请求示例**

```json
{
  "drugId": 2001,
  "category": "核心卖点",
  "title": "首剂起效速度",
  "content": "在目标人群中 2 周即可观察到关键指标改善趋势。",
  "sortOrder": 10
}
```

**成功响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": 5012
}
```

---

#### 2.4.3 创建角色画像（医生画像）

- **接口名称**: 创建角色画像
- **Method**: `POST`
- **URL**: `/rolePersona/createRolePersona`
- **Content-Type**: `application/json`
- **鉴权**: 需要

**请求体参数**

| 字段            | 类型    | 必填 | 说明                     |
| --------------- | ------- | ---- | ------------------------ |
| name            | string  | 是   | 画像名称/医生名          |
| surname         | string  | 否   | 姓氏或补充称呼           |
| title           | string  | 否   | 职称                     |
| description     | string  | 否   | 简介                     |
| personaConfig   | string  | 否   | 人设配置                 |
| trustInitial    | number  | 否   | 初始信任值，默认 50      |
| patienceInitial | number  | 否   | 初始耐心值，默认 60      |
| isPreset        | boolean | 否   | 是否预置画像，默认 false |

**请求示例**

```json
{
  "name": "王主任",
  "surname": "王",
  "title": "心内科主任医师",
  "description": "注重循证，沟通节奏快",
  "personaConfig": "### 性格特征\n- 权威\n- 务实\n### 沟通风格\n- 先结论后细节",
  "trustInitial": 45,
  "patienceInitial": 55,
  "isPreset": false
}
```

**成功响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": 3008
}
```

---

#### 2.4.4 创建业务领域

- **接口名称**: 创建业务领域
- **Method**: `POST`
- **URL**: `/businessDomain/createBusinessDomain`
- **Content-Type**: `application/json`
- **鉴权**: 需要

**请求体参数**

| 字段        | 类型   | 必填 | 说明         |
| ----------- | ------ | ---- | ------------ |
| name        | string | 是   | 领域名称     |
| description | string | 否   | 描述         |
| sortOrder   | number | 否   | 排序，默认 0 |

**请求示例**

```json
{
  "name": "心血管",
  "description": "心脑血管相关业务线",
  "sortOrder": 1
}
```

**成功响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": 18
}
```

---

#### 2.4.5 创建科室/组织

- **接口名称**: 创建科室
- **Method**: `POST`
- **URL**: `/department/createDepartment`
- **Content-Type**: `application/json`
- **鉴权**: 需要

**请求体参数**

| 字段               | 类型   | 必填 | 说明                     |
| ------------------ | ------ | ---- | ------------------------ |
| name               | string | 是   | 科室名称                 |
| code               | string | 否   | 科室编码                 |
| sortOrder          | number | 否   | 排序，默认 0             |
| businessDomainId   | number | 是   | 业务领域 ID              |
| businessDomainName | string | 否   | 业务领域名称（冗余展示） |

**请求示例**

```json
{
  "name": "心内科",
  "code": "CARD",
  "sortOrder": 10,
  "businessDomainId": 18,
  "businessDomainName": "心血管"
}
```

**成功响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": 102
}
```

---

#### 2.4.6 创建产品/品种

- **接口名称**: 创建品种
- **Method**: `POST`
- **URL**: `/drug/createDrug`
- **Content-Type**: `application/json`
- **鉴权**: 需要
- **说明**: `businessDomainId` 为**必填**（后端校验「请选择业务领域」）。
  **请求体参数**

| 字段               | 类型   | 必填 | 说明                     |
| ------------------ | ------ | ---- | ------------------------ |
| name               | string | 是   | 品种名称                 |
| externalId         | string | 否   | 外部系统 ID              |
| genericName        | string | 否   | 通用名                   |
| companyId          | number | 否   | 厂家 ID                  |
| companyName        | string | 否   | 厂家名称（冗余展示）     |
| code               | string | 否   | 品种编码                 |
| description        | string | 否   | 描述                     |
| businessDomainId   | number | 是   | 业务领域 ID              |
| businessDomainName | string | 否   | 业务领域名称（冗余展示） |
| sortOrder          | number | 否   | 排序，默认 0             |

**请求示例**

```json
{
  "name": "XX缓释片",
  "externalId": "DRUG-EXT-001",
  "genericName": "某某通用名",
  "companyId": 8,
  "companyName": "示例药企",
  "code": "DRUG-001",
  "description": "用于慢病长期管理",
  "businessDomainId": 18,
  "businessDomainName": "心血管"
}
```

**成功响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": 2009
}
```

**常见错误**

- `400`: 参数格式错误或校验失败

---

## 3. 公共约定

### 3.1 请求头

```http
access-token: xxx
```

### 3.2 响应结构

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": {}
}
```
