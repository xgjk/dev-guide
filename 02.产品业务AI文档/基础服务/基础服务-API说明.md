# 基础服务 Open API 接口文档

## 修订记录1

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|--------|
| 1.0 | 2026-03-25 | 初版创建 | 成伟 |

## 一、概述

本文档描述了 **文件服务** 与 **用户服务**（统称“基础服务”）对外开放的全部 Open API 接口。通过这些接口，可以实现以下业务能力：

1. **文件服务**：
   - **上传本地文件** — 上传单个文件，获取持久化的资源 ID（resourceId）。
   - **获取文件下载信息** — 根据 resourceId 获取临时的下载 URL（有效期 1 小时）。
2. **用户服务**：
   - **按姓名搜索全部员工** — 支持模糊搜索内部员工与外部联系人。
   - **批量获取员工信息** — 根据企业 ID 和 personId 批量查询。
   - **获取组织架构信息** — 查询员工的直属领导、二三级部门名称等。

---

## 二、通用说明

### 2.1 访问地址
```
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境 | 域名/Base URL | 备注 |
| ---- | ------------------------------ | --- |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn` | - |

### 2.3 公共请求头

| Header | 说明 | 是否必填 |
| -------- | -------------------------- | ----- |
| `appKey` | 从工作协同系统获取的 API 密钥 | 是 |

### 2.4 通用响应结构

所有接口响应均返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```

| 字段 | 类型 | 说明 |
| ------------ | ------- | ----------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，非 `1` 表示失败 |
| `resultMsg`  | String  | 提示信息，成功时为 `null`，失败时为错误描述 |
| `data`       | T       | 业务数据，根据各接口不同，失败时通常为 `null` |

---

## 三、关键业务流程说明

### 场景一：上传文件并获取下载链接 (文件服务)

> 需求：第三方系统期望向文件服务器推送一个本地文件，并快速获取供前端展示或下载的临时 URL。

1. 调用 **4.1 上传本地文件**（`POST /cwork-file/uploadWholeFile`），通过 `multipart/form-data` 传入文件二进制，获取 `Long` 类型的 `resourceId`。
2. 调用 **4.2 获取文件下载信息**（`GET /cwork-file/getDownloadInfo`），传入 `resourceId`，得到 `DownloadFileVO`。
3. 从 `DownloadFileVO` 中提取 `downloadUrl` 供业务展示或进行下载（有效期 1 小时）。

### 场景二：同步企业员工组织架构 (用户服务)

> 需求：第三方系统期望通过员工姓名，拉取其完整的组织树关系进行对齐。

1. 调用 **5.1 按姓名搜索全部员工**（`GET /cwork-user/searchEmpByName`），传入 `searchKey="张三"`，获取 `SearchAddressbookVO`。
2. 从返回的 `SearchAddressbookVO.inside.empList` 中，获取匹配的 `SearchEmployeeVO.id`（员工 id）。
3. 调用 **5.3 根据员工 id 获取组织架构信息**（`GET /cwork-user/employee/getEmployeeOrgInfo`），传入 `empId`，拿到 `EmployeeOrgInfoVO`，内含二级/三级部门名称及直属领导信息。

---

## 四、文件服务接口详细说明

### 4.1 上传本地文件

上传本地文件，返回文件资源 ID，用于后续下载等文件绑定操作。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/cwork-file/uploadWholeFile` |
| 请求方式 | `POST` |
| Content-Type | `multipart/form-data` |

**请求参数**

- **请求体 (Body)**

| 参数名 | 类型 | 必填 | 说明 |
| ----------- | ------------- | ---- | ------------------------------ |
| `file` | binary (File) | 是 | 要上传的文件 |

**响应参数**

`data` 类型为 `Long`，代表**文件资源 ID**。

**数据流向**

- 返回的 `resourceId`（`data`）常用作 **[4.2 获取文件下载信息](#42-获取文件下载信息)** 的请求入参。

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/open-api/cwork-file/uploadWholeFile' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/file.png'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": 123456789012345
}
```

---

### 4.2 获取文件下载信息

根据资源 ID 获取文件下载信息，包含下载 URL。**下载链接有效期为 1 小时**。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/cwork-file/getDownloadInfo` |
| 请求方式 | `GET` |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
| ------------ | ---- | ---- | ----------------- |
| `resourceId` | Long | 是 | 文件资源 ID |

**响应参数**

`data` 类型为 `DownloadFileVO`，详见 **[6.1 DownloadFileVO](#61-downloadfilevo)**。

**请求示例**

```bash
curl -X GET 'https://cwork-api.mediportal.com.cn/open-api/cwork-file/getDownloadInfo?resourceId=123456789012345' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": {
    "downloadUrl": "https://storage.example.com/download/path?token=xxx",
    "fileName": "示例文件.png",
    "resourceId": 123456789012345,
    "suffix": "png",
    "size": 204800
  }
}
```

---

## 五、用户服务接口详细说明

### 5.1 按姓名搜索全部员工(带外部联系人)

按姓名模糊搜索全部员工，包含内部员工与外部联系人。

**基本信息**

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口地址         | `/cwork-user/searchEmpByName`       |
| 请求方式         | `GET`                               |

**请求参数**

| 参数名      | 类型   | 必填 | 说明                           |
| ----------- | ------ | ---- | ------------------------------ |
| `searchKey` | String | 是   | 搜索关键词：支持按姓名模糊搜索 |

**响应参数**

`data` 类型为 `SearchAddressbookVO`，字段详见 **[6.2 SearchAddressbookVO](#62-searchaddressbookvo)**。

**请求示例**

```bash
curl -X GET 'https://cwork-api.mediportal.com.cn/open-api/cwork-user/searchEmpByName?searchKey=%E5%BC%A0%E4%B8%89' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": {
    "inside": {
      "companyVO": {
        "id": 12435,
        "name": "公司A",
        "dingCorpId": "dingxxxx"
      },
      "empList": [
        {
          "id": 10001,
          "personId": 20001,
          "name": "张三",
          "dingUserId": "ding2323",
          "title": "工程师",
          "mainDept": "技术部"
        }
      ]
    },
    "outside": []
  }
}
```

**数据流向**

- 返回的 `inside.empList[].id` 可用于 **[5.3 根据员工 id 获取组织架构信息](#53-根据员工-id-获取组织架构信息)** 的 `empId` 入参。

---

### 5.2 根据 personId+corpId 批量获取员工信息

根据企业 ID 和用户 personId 列表，批量查询员工信息。

**基本信息**

| 项目         | 说明                                                |
| ------------ | --------------------------------------------------- |
| 接口地址         | `/cwork-user/employee/getByPersonIds/{corpId}`     |
| 请求方式         | `POST`                                              |
| Content-Type | `application/json`                                  |

**请求参数**

- **路径参数 (Path)**

| 参数名   | 类型   | 必填 | 说明   |
| -------- | ------ | ---- | ------ |
| `corpId` | Long   | 是   | 企业 ID |

- **请求体 (Body)**
请求体为 `Long[]`（personId 列表，雪花算法或大整型）。

**响应参数**

`data` 类型为 `List<EmployeeVO>`，详见 **[6.6 EmployeeVO](#66-employeevo)**。

**请求示例**

```bash
curl -X POST 'https://cwork-api.mediportal.com.cn/open-api/cwork-user/employee/getByPersonIds/123456' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '[10001, 10002]'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": [
    {
      "id": 10001,
      "personId": 10001,
      "name": "张三",
      "dingUserId": "ding_zhangsan",
      "title": "产品经理"
    }
  ]
}
```

---

### 5.3 根据员工 id 获取组织架构信息

根据员工 ID 获取直属领导、二三级部门、用户名称等组织架构信息。

**基本信息**

| 项目         | 说明                                                |
| ------------ | --------------------------------------------------- |
| 接口地址         | `/cwork-user/employee/getEmployeeOrgInfo`          |
| 请求方式         | `GET`                                              |

**请求参数**

| 参数名  | 类型 | 必填 | 说明   |
| ------- | ---- | ---- | ------ |
| `empId` | Long | 是   | 员工 id |

**响应参数**

`data` 类型为 `EmployeeOrgInfoVO`，详见 **[6.7 EmployeeOrgInfoVO](#67-employeeorginfovo)**。

**请求示例**

```bash
curl -X GET 'https://cwork-api.mediportal.com.cn/open-api/cwork-user/employee/getEmployeeOrgInfo?empId=10001' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "成功",
  "data": {
    "empId": 10001,
    "empName": "张三",
    "managerEmpId": 10002,
    "managerEmpName": "李四",
    "secondLevelDeptId": 200,
    "secondLevelDeptName": "研发中心",
    "thirdLevelDeptId": 300,
    "thirdLevelDeptName": "架构部"
  }
}
```

---

## 六、公共数据结构

### 6.1 DownloadFileVO
文件下载信息对象。

| 字段 | 类型 | 说明 |
| ------------- | ------ | ------------------- |
| `downloadUrl` | String | 下载 URL（有效期 1 小时） |
| `fileName` | String | 文件名 |
| `resourceId` | Long | 资源 ID |
| `suffix` | String | 文件后缀 |
| `size` | Long | 文件大小（单位：字节） |

---

### 6.2 SearchAddressbookVO
企业通讯录搜索结果。

| 字段      | 类型                      | 说明                              |
| --------- | ------------------------- | --------------------------------- |
| `inside`  | `SearchCompanyRelationVO` | 内部员工列表，详见 **[6.3](#63-searchcompanyrelationvo)** |
| `outside` | `SearchCompanyRelationVO[]` | 外部联系人，详见 **[6.3](#63-searchcompanyrelationvo)** |

---

### 6.3 SearchCompanyRelationVO
关联企业信息。

| 字段        | 类型                | 说明               |
| ----------- | ------------------- | ------------------ |
| `companyVO` | `CompanyVO`         | 关联的企业信息，详见 **[6.4](#64-companyvo)** |
| `empList`   | `SearchEmployeeVO[]` | 关联企业下的员工信息，详见 **[6.5](#65-searchemployeevo)** |

---

### 6.4 CompanyVO
企业信息。

| 字段         | 类型   | 说明        |
| ------------ | ------ | ----------- |
| `id`         | Long   | 企业 id     |
| `name`       | String | 企业名称    |
| `dingCorpId` | String | 钉钉 CorpId |

---

### 6.5 SearchEmployeeVO
搜索结果展示的员工信息。

| 字段         | 类型   | 说明                        |
| ------------ | ------ | --------------------------- |
| `id`         | Long   | 员工 id                      |
| `personId`   | Long   | 用户 personId（与企业无关） |
| `name`       | String | 姓名                        |
| `dingUserId` | String | 钉钉 userId                  |
| `title`      | String | 职位                        |
| `mainDept`   | String | 所在部门（只取一条数据）    |

---

### 6.6 EmployeeVO
员工信息。

| 字段         | 类型   | 说明                        |
| ------------ | ------ | --------------------------- |
| `id`         | Long   | 员工 id                      |
| `personId`   | Long   | 用户 personId（与企业无关） |
| `name`       | String | 姓名                        |
| `dingUserId` | String | 钉钉 userId                  |
| `title`      | String | 职位                        |

---

### 6.7 EmployeeOrgInfoVO
员工组织架构信息。

| 字段                  | 类型   | 说明                          |
| --------------------- | ------ | ----------------------------- |
| `empId`               | Long   | 员工 id                        |
| `empName`             | String | 员工名称                      |
| `managerEmpId`        | Long   | 直属领导的员工 id             |
| `managerEmpName`      | String | 直属领导名称                  |
| `secondLevelDeptId`   | Long   | 组织架构第二级部门 id          |
| `secondLevelDeptName` | String | 组织架构第二级部门名称（中心） |
| `thirdLevelDeptId`    | Long   | 组织架构第三级部门 id          |
| `thirdLevelDeptName`  | String | 组织架构第三级部门名称（部门） |

---

## 七、错误码说明

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

## 八、注意事项

为了确保对接的安全性与稳定性，调用方应严格遵守以下约束：

1. **ID 精度防御**：所有 ID 类型在后端使用 64位 Long 整数（如 `resourceId`, `empId`, `corpId`, `personId`），前端展示或外部对接时请务必使用 **String 字符串** 类型接收，避免 JavaScript 等弱类型语言发生精度丢失。
2. **下载有效期 (仅文件服务)**：下载 URL 通常带有临时 Token，**有效期限制为 1 小时**，请避免将其用于持久化的静态资源引用，应当在需要展示时动态二次拉取。
3. **鉴权与防重放**：所有接口均需在 Header 携带合法的 `appKey`；若接口需要计算签名，请确保 `timestamp` 与服务端时间差在 5 分钟内。
4. **频率限制 (QPS 控制)**：开放平台配有流控保护，收到 `610012` 错误时推荐使用指数级退避算法进行降频重试。

---

**文档版本**：v1.3  
**更新日期**：2026-03-17  
**维护人/团队**：基础服务团队
