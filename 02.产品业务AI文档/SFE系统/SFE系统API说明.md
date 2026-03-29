# SFE系统 Open API 接口文档

## 修订记录

| 版本 | 日期       | 修订内容                     | 修订人 |
| ---- | ---------- | ---------------------------- | ------ |
| V1.0 | 2026-03-16 | 初始版本，开放 17 个基础接口 | 王馗      |
| V1.1 | 2026-03-25 | 支持分页查询               | 王馗      |
| V1.2 | 2026-03-28 | 支持租户选择               | 王馗      |

---

## 一、概述

本文档描述了 **SFE系统** 对外开放的全部 API 接口。通过这些接口，可以实现以下业务能力：

1. **查询用户授权的区划** — 获取用户有权限的区划列表，用于确定业务范围
2. **查询用户授权的产品** — 获取用户有权限的产品列表
3. **查询用户授权的客户** — 获取用户有权限的客户列表
4. **查询用户授权客户的画像** — 获取客户的属性标签信息
5. **查询用户授权的覆盖分管关系** — 获取区划与客户画像的关联关系
6. **查询用户参与的数据采集项目摘要** — 获取项目基本信息与周期配置
7. **查询项目的周期列表** — 获取项目下所有可用周期
8. **查询项目的填报模板** — 获取数据字段的 JSON Schema 定义
9. **查询项目的角色权限** — 获取用户在各模板下的操作权限
10. **查询用户的待办任务状态** — 获取待处理/已完成的任务列表
11. **查询用户的计划编制数据** — 获取目标管理类项目的计划数据
12. **查询用户的实际结果数据** — 获取目标管理类项目的执行数据
13. **查询用户的采集填报数据** — 获取普通采集项目的填报数据
14. **查询指定区划的待办任务** — 按区划维度查询任务状态
15. **查询指定区划的计划数据** — 按区划维度查询计划编制
16. **查询指定区划的实际数据** — 按区划维度查询实际结果
17. **查询指定区划的采集数据** — 按区划维度查询采集填报

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/erp-open-api/{接口地址}
```

### 2.2 环境信息

| 环境     | 域名/Base URL                          | 备注 |
| -------- | -------------------------------------- | ---- |
| 生产环境 | `https://erp-web.mediportal.com.cn`    | -    |

### 2.3 公共请求头

| Header         | 说明                                     | 是否必填 |
| -------------- | --------------------------------------- | -------- |
| `appKey`       | 从工作协同/ERP/SFE 系统获取的 API 密钥      | 是       |
| `Content-Type` | 请求体类型，`application/json`            | POST 必填 |
| `tenantId`     | 租户ID，默认无须传入，用户存在多个租户身份时须传入     | 否        | 

注：用户只存在一个租户身份时无须传入`tenantId`，用户存在多个租户身份时须传入查询的具体`tenantId`，如未传入具体`tenantId`，会返回用户可选择的租户列表

### 2.4 通用响应结构

所有接口返回统一的响应结构：

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": null,
  "timestamp": 1774252310993,
  "success": true
}
```

| 字段         | 类型     | 说明                                      |
| ------------ | -------- | ----------------------------------------- |
| `resultCode` | Integer  | 业务状态码，`1` 表示成功，其他值表示失败  |
| `resultMsg`  | String   | 提示信息，成功时可能为 `null`             |
| `data`       | T        | 业务数据，不同接口类型不同，失败时为 `null` |
| `timestamp`  | Long     | 响应时间戳                                |
| `success`    | Boolean  | 是否成功，与 `resultCode=1` 对应          |

### 2.5 分页查询

#### 分页参数

所有接口支持 `page` 参数进行分页查询，不传入时默认查询第 1 页。每页固定返回 1000 条记录。

| 参数   | 类型    | 必填 | 说明                       |
| ------ | ------- | ---- | -------------------------- |
| `page` | Integer | 否   | 请求页数，缺省为第 1 页    |

#### 查询总记录数

所有接口可在 URL 后添加 `/count` 查询总记录数，用于确定总页数。

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-actual/count' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "projectId": "2014631829004370001",
    "periodCode": "2026-Q1"
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": 3,
  "timestamp": 1774252310993,
  "success": true
}
```

---

## 三、关键业务流程说明

### 场景一：获取用户授权的基础数据

> 需求：获取用户在 SFE 系统中有权限访问的区划、产品、客户等基础数据，用于后续业务查询。

1. 调用 **4.1 查询用户授权的区划**（`POST /bia/open/biz-service/sfe-user/zone`），获取用户授权的区划列表，筛选 `status=1` 的启用区划，保存 `id` 作为后续接口的 `zoneId`
2. 调用 **4.2 查询用户授权的产品**（`POST /bia/open/biz-service/sfe-user/product`），获取产品列表，返回的 `id` 可用于查询客户画像
3. 调用 **4.3 查询用户授权的客户**（`POST /bia/open/biz-service/sfe-user/customer`），获取客户列表，返回的 `id` 可用于查询客户画像

### 场景二：查询项目数据采集任务

> 需求：获取用户参与的数据采集项目，了解项目周期、模板结构，并查询填报数据。

1. 调用 **4.6 查询用户参与的数据采集项目摘要**（`POST /bia/open/biz-service/sfe-user/project-summary`），获取项目列表，筛选目标项目保存 `id` 作为 `projectId`
2. 调用 **4.7 查询项目的周期列表**（`POST /bia/open/biz-service/sfe-user/project-period`），传入上一步的 `projectId`，获取周期列表，选择目标周期保存 `code` 作为 `periodCode`
3. 调用 **4.8 查询项目的填报模板**（`POST /bia/open/biz-service/sfe-user/project-schema`），传入 `projectId`，获取模板定义，根据 `field` 字段解析数据结构
4. 根据项目类型，调用对应数据查询接口：
   - 目标管理类项目：调用 **4.11 查询用户的计划编制数据** 或 **4.12 查询用户的实际结果数据**
   - 普通采集项目：调用 **4.13 查询用户的采集填报数据**

### 场景三：查询指定区划的任务完成情况

> 需求：针对特定区划，查询某项目在特定时期的任务完成状态和填报数据。

1. 调用 **4.1 查询用户授权的区划**，获取 `zoneId`
2. 调用 **4.6 查询用户参与的数据采集项目摘要**，获取 `projectId`
3. 调用 **4.7 查询项目的周期列表**，确定 `periodStart` 和 `periodEnd`
4. 调用 **4.14 查询指定区划的待办任务**，传入 `zoneId`、`projectId`、`periodStart`、`periodEnd`，获取任务状态
5. 根据需要调用 **4.15~4.17** 查询该区划的计划、实际或采集数据

---

## 四、接口详细说明

---

### 4.1 查询用户授权的区划

获取用户有权限访问的区划列表，通常作为数据查询的第一步，用于确定业务范围。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/zone`                   |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名   | 类型    | 必填 | 说明                                                         |
| -------- | ------- | ---- | ------------------------------------------------------------ |
| `id`     | String  | 否   | 区划 ID，用于精确查询                                        |
| `name`   | String  | 否   | 区划名称，支持模糊查询                                       |
| `level`  | String  | 否   | 区划层次：`hq`-总部，`region`-大区，`district`-片区，`area`-地区，`territory`-辖区 |
| `status` | Integer | 否   | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据         |
| `page`   | Integer | 否   | 页码，默认第 1 页                                            |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/zone' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": 1
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名        | 类型    | 说明                                                         |
| ------------- | ------- | ------------------------------------------------------------ |
| `id`          | String  | 区划 ID                                                      |
| `name`        | String  | 区划名称                                                     |
| `pathNames`   | String  | 区划名称路径，以 `/` 分隔                                    |
| `pathIds`     | String  | 区划 ID 路径，以 `/` 分隔                                    |
| `level`       | String  | 区划层次：`hq`-总部，`region`-大区，`district`-片区，`area`-地区，`territory`-辖区 |
| `isPrincipal` | Integer | 是否负责人：0-否，1-是                                       |
| `isDelegate`  | Integer | 是否代理人：0-否，1-是                                       |
| `status`      | Integer | 状态：0-禁用，1-启用                                         |
| `createTime`  | String  | 创建时间                                                     |
| `updateTime`  | String  | 更新时间                                                     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": "1940947912592429057",
      "name": "维盛河北眼二区岗位1",
      "pathNames": "",
      "pathIds": "1940947710347284481/1940947718278713346/1940947723160883202",
      "level": "hierarchicalLevel.territory",
      "isPrincipal": 0,
      "isDelegate": 0,
      "status": 1,
      "createTime": "2025-07-04T09:36:58",
      "updateTime": "2026-03-23T02:01:24"
    }
  ],
  "timestamp": 1774252310993,
  "success": true
}
```

**数据流向**

- 返回的 `id` 用于 **4.5** 的 `zoneId` 参数
- 返回的 `id` 用于 **4.14~4.17** 的 `zoneId` 参数

---

### 4.2 查询用户授权的产品

获取用户有权限访问的产品列表。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/product`                |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名   | 类型    | 必填 | 说明                                                 |
| -------- | ------- | ---- | ---------------------------------------------------- |
| `id`     | String  | 否   | 产品 ID，用于精确查询                                |
| `name`   | String  | 否   | 产品名称，支持模糊查询                               |
| `status` | Integer | 否   | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page`   | Integer | 否   | 页码，默认第 1 页                                    |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/product' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名       | 类型    | 说明                 |
| ------------ | ------- | -------------------- |
| `id`         | String  | 产品 ID              |
| `name`       | String  | 产品名称             |
| `status`     | Integer | 状态：0-禁用，1-启用 |
| `createTime` | String  | 创建时间             |
| `updateTime` | String  | 更新时间             |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": "1986131416662327297",
      "name": "诺适得(雷珠单抗)(HNWS)",
      "status": 1,
      "createTime": "2025-12-30T16:31:40",
      "updateTime": "2026-02-03T17:38:56"
    }
  ],
  "timestamp": 1774002961365,
  "success": true
}
```

**数据流向**

- 返回的 `id` 用于 **4.4** 的 `productId` 参数

---

### 4.3 查询用户授权的客户

获取用户有权限访问的客户列表。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/customer`               |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名       | 类型    | 必填 | 说明                                                 |
| ------------ | ------- | ---- | ---------------------------------------------------- |
| `id`         | String  | 否   | 客户 ID，用于精确查询                                |
| `name`       | String  | 否   | 客户名称，支持模糊查询                               |
| `type`       | String  | 否   | 客户类型                                             |
| `sourceType` | String  | 否   | 来源类型                                             |
| `sourceId`   | String  | 否   | 来源 ID                                              |
| `status`     | Integer | 否   | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page`       | Integer | 否   | 页码，默认第 1 页                                    |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/customer' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名       | 类型    | 说明                                                                 |
| ------------ | ------- | -------------------------------------------------------------------- |
| `id`         | String  | 客户 ID                                                              |
| `name`       | String  | 客户名称                                                             |
| `type`       | String  | 客户类型：`hospital`-医院，`pharmacy`-药店，`virtualHospital`-虚拟医院，`professional`-专业人士/医生 |
| `sourceType` | String  | 来源类型：`hco`-HCO，`hcp`-HCP                                       |
| `sourceId`   | String  | 来源 ID：HCO 或 HCP 的 ID                                            |
| `status`     | Integer | 状态：0-禁用，1-启用                                                 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "4014631829004370001",
      "name": "上海市第一人民医院",
      "type": "hospital",
      "sourceType": "hco",
      "sourceId": "HCO001",
      "status": 1
    }
  ],
  "timestamp": 1704067200000,
  "success": true
}
```

**数据流向**

- 返回的 `id` 用于 **4.4** 的 `customerId` 参数

---

### 4.4 查询用户授权客户的画像

获取客户的属性标签信息。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/customer-profile`      |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名         | 类型    | 必填 | 说明                                                 |
| -------------- | ------- | ---- | ---------------------------------------------------- |
| `customerId`   | String  | 否   | 客户 ID，来自 4.3 返回的 `id`                        |
| `productId`    | String  | 否   | 产品 ID，来自 4.2 返回的 `id`                        |
| `drugFormName` | String  | 否   | 剂型名称                                             |
| `status`       | Integer | 否   | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page`         | Integer | 否   | 页码，默认第 1 页                                    |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/customer-profile' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"customerId": "4014631829004370001"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名         | 类型    | 说明                 |
| -------------- | ------- | -------------------- |
| `id`           | String  | 画像 ID              |
| `customerId`   | String  | 客户 ID              |
| `customerName` | String  | 客户名称             |
| `productId`    | String  | 产品 ID              |
| `productName`  | String  | 产品名称             |
| `drugFormName` | String  | 剂型名称             |
| `tags`         | Array   | 客户标签数组         |
| `status`       | Integer | 状态：0-禁用，1-启用 |

`tags` 数组元素字段：

| 字段名 | 类型   | 说明 |
| ------ | ------ | ---- |
| `type` | String | 类型 |
| `name` | String | 名称 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "5014631829004370001",
      "customerId": "4014631829004370001",
      "customerName": "上海市第一人民医院",
      "productId": "3014631829004370001",
      "productName": "产品A",
      "drugFormName": "片剂",
      "tags": [
        { "type": "科室", "name": "心内科" },
        { "type": "级别", "name": "三甲" }
      ],
      "status": 1
    }
  ],
  "timestamp": 1704067200000,
  "success": true
}
```

**数据流向**

- 返回的 `id` 用于 **4.5** 的 `customerProfleId` 参数

---

### 4.5 查询用户授权的覆盖分管关系

获取区划与客户画像的关联关系。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/coverage`               |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名             | 类型    | 必填 | 说明                                                 |
| ------------------ | ------- | ---- | ---------------------------------------------------- |
| `zoneId`           | String  | 否   | 区划 ID，来自 4.1 返回的 `id`                        |
| `customerProfleId` | String  | 否   | 客户画像 ID，来自 4.4 返回的 `id`                    |
| `status`           | Integer | 否   | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page`             | Integer | 否   | 页码，默认第 1 页                                    |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/coverage' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"zoneId": "2014631829004370002"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名             | 类型    | 说明                 |
| ------------------ | ------- | -------------------- |
| `zoneId`           | String  | 区划 ID              |
| `customerProfleId` | String  | 客户画像 ID          |
| `customerName`     | String  | 客户名称             |
| `productName`      | String  | 产品名称             |
| `status`           | Integer | 状态：0-禁用，1-启用 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "zoneId": "2014631829004370002",
      "customerProfleId": "5014631829004370001",
      "customerName": "上海市第一人民医院",
      "productName": "产品A",
      "status": 1
    }
  ],
  "timestamp": 1704067200000,
  "success": true
}
```

---

### 4.6 查询用户参与的数据采集项目摘要

获取用户参与的数据采集项目列表，包含项目基本信息与周期配置。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-summary`        |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名   | 类型    | 必填 | 说明                                                 |
| -------- | ------- | ---- | ---------------------------------------------------- |
| `id`     | String  | 否   | 项目 ID，用于精确查询                                |
| `code`   | String  | 否   | 项目编码                                             |
| `name`   | String  | 否   | 项目名称，支持模糊查询                               |
| `status` | Integer | 否   | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page`   | Integer | 否   | 页码，默认第 1 页                                    |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-summary' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                    | 类型    | 说明                                                                                                  |
| ------------------------- | ------- | ----------------------------------------------------------------------------------------------------- |
| `id`                      | String  | 项目 ID                                                                                               |
| `code`                    | String  | 项目编码                                                                                              |
| `name`                    | String  | 项目名称                                                                                              |
| `type`                    | String  | 类别                                                                                                  |
| `startDate`               | String  | 开始日期                                                                                              |
| `endDate`                 | String  | 结束日期                                                                                              |
| `isRepeatCycle`           | Integer | 是否重复周期：0-否，1-是                                                                              |
| `cycleUnit`               | String  | 周期单位：`daily`-天，`iso_weekly`-ISO年周，`nature_weekly`-自然月周，`monthly`-月，`quarterly`-季度，`yearly`-年 |
| `isExcludeNonWorkingDays` | Integer | 是否排除非工作日：0-不排除，1-排除                                                                    |
| `status`                  | Integer | 状态：0-禁用，1-启用                                                                                  |
| `createTime`              | String  | 创建时间                                                                                              |
| `updateTime`              | String  | 更新时间                                                                                              |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": "1985681736518647809",
      "code": "lzPatientDaily",
      "name": "雷珠患者跟进日填报",
      "type": "businessProjectType.general",
      "startDate": "2025-11-04",
      "endDate": "2026-12-31",
      "isRepeatCycle": true,
      "cycleUnit": "daily",
      "isExcludeNonWorkingDays": false,
      "status": 1,
      "createTime": "2025-11-04T20:13:13",
      "updateTime": "2025-12-02T14:52:23"
    }
  ],
  "timestamp": 1774003121919,
  "success": true
}
```

**数据流向**

- 返回的 `id` 用于 **4.7~4.13** 的 `projectId` 参数

---

### 4.7 查询项目的周期列表

获取项目下所有可用周期。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-period`         |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型   | 必填 | 说明                           |
| ------------- | ------ | ---- | ------------------------------ |
| `projectId`   | String | 否   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodCode`  | String | 否   | 周期编码                       |
| `periodName`  | String | 否   | 周期名称                       |
| `periodStart` | String | 否   | 周期开始时间                   |
| `periodEnd`   | String | 否   | 周期结束时间                   |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-period' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1985681736518647809"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名      | 类型   | 说明     |
| ----------- | ------ | -------- |
| `projectId` | String | 项目 ID  |
| `periods`   | Array  | 周期列表 |

`periods` 数组元素字段：

| 字段名      | 类型   | 说明                                                                                                  |
| ----------- | ------ | ----------------------------------------------------------------------------------------------------- |
| `code`      | String | 周期编码                                                                                              |
| `name`      | String | 周期名称                                                                                              |
| `cycleUnit` | String | 周期单位：`daily`-天，`iso_weekly`-ISO年周，`nature_weekly`-自然月周，`monthly`-月，`quarterly`-季度，`yearly`-年 |
| `startDate` | String | 周期开始时间                                                                                          |
| `endDate`   | String | 周期结束时间                                                                                          |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "periods": [
        {
          "code": "1002.2025.11.10",
          "endDate": "2025-11-10",
          "name": "2025年11月10日",
          "cycleUnit": "daily",
          "startDate": "2025-11-10"
        }
      ],
      "projectId": "1985681736518647809"
    }
  ],
  "timestamp": 1774003359858,
  "success": true
}
```

**数据流向**

- 返回的 `periods[].code` 用于 **4.10~4.17** 的 `periodCode` 参数
- 返回的 `startDate`/`endDate` 用于筛选时间范围

---

### 4.8 查询项目的填报模板

获取项目数据字段的 JSON Schema 定义。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-schema`         |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型   | 必填 | 说明                           |
| --------------- | ------ | ---- | ------------------------------ |
| `projectId`     | String | 否   | 项目 ID，来自 4.6 返回的 `id`  |
| `schemaCode`    | String | 否   | 模板编码                       |
| `schemaName`    | String | 否   | 模板名称                       |
| `schemaVersion` | String | 否   | 模板版本                       |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-schema' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1985681736518647809"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名      | 类型   | 说明     |
| ----------- | ------ | -------- |
| `projectId` | String | 项目 ID  |
| `schemas`   | Array  | 模板列表 |

`schemas` 数组元素字段：

| 字段名    | 类型   | 说明                |
| --------- | ------ | ------------------- |
| `code`    | String | 模板编码            |
| `name`    | String | 模板名称            |
| `version` | String | 模板版本            |
| `field`   | String | 字段的 JSON Schema  |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "schemas": [
        {
          "code": "lucentisPatientDailyCollection",
          "field": "{"type":"object","title":"模型-维盛-概要患者跟进日填报-患者概要","properties":{"medicationDate":{"title":"用药日期","type":"string"}}},
          "name": "诺适得患者跟进日填报-患者概要",
          "version": "1.0"
        }
      ],
      "projectId": "1985681736518647809"
    }
  ],
  "timestamp": 1774003444334,
  "success": true
}
```

**数据流向**

- 返回的 `schemas[].code` 用于 **4.11~4.17** 的 `schemaCode` 参数
- 返回的 `field` 用于解析 `fieldValue` 字段结构

---

### 4.9 查询项目的角色权限

获取用户在各模板下的操作权限。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-role`           |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名      | 类型   | 必填 | 说明                           |
| ----------- | ------ | ---- | ------------------------------ |
| `projectId` | String | 否   | 项目 ID，来自 4.6 返回的 `id`  |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-role' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1985681736518647809"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名      | 类型   | 说明     |
| ----------- | ------ | -------- |
| `projectId` | String | 项目 ID  |
| `roles`     | String | 角色权限 JSON 字符串 |

`roles` JSON 结构说明：
- 外层 key 为模板编码（schemaCode）
- 内层 key 为角色名称（如 `salesRep`、`salesManager` 等）
- 值为权限对象，包含 `read`、`create`、`update`、`delete`、`submit`、`review`、`export`、`lock` 等布尔值

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "projectId": "1985681736518647809",
      "roles": "{"leizhuPatientDailyActual": {"salesRep": {"read": true, "create": true, "delete": true, "export": true, "submit": true, "update": true}}}
    }
  ],
  "timestamp": 1774003509464,
  "success": true
}
```

---

### 4.10 查询用户的待办任务状态

获取用户的待处理/已完成的任务列表。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-task`           |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明                                                                         |
| ------------- | ------- | ---- | ---------------------------------------------------------------------------- |
| `projectId`   | String  | 否   | 项目 ID，来自 4.6 返回的 `id`                                                |
| `periodStart` | String  | 否   | 周期开始时间                                                                 |
| `periodEnd`   | String  | 否   | 周期结束时间                                                                 |
| `status`      | Integer | 否   | 状态：0-待处理，1-已完成，2-已取消，3-过期关闭，4-手工关闭，默认查询全部数据 |
| `page`        | Integer | 否   | 页码，默认第 1 页                                                            |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-task' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1985681736518647809"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名      | 类型   | 说明     |
| ----------- | ------ | -------- |
| `zoneId`    | String | 区划 ID  |
| `projectId` | String | 项目 ID  |
| `tasks`     | Array  | 任务列表 |

`tasks` 数组元素字段：

| 字段名       | 类型    | 说明                                                       |
| ------------ | ------- | ---------------------------------------------------------- |
| `id`         | String  | 任务 ID                                                    |
| `name`       | String  | 任务名称                                                   |
| `startDate`  | String  | 任务开始日期                                               |
| `endDate`    | String  | 任务结束日期                                               |
| `zoneId`     | String  | 区划 ID                                                    |
| `periodCode` | String  | 周期编码                                                   |
| `schemaCode` | String  | 模板编码                                                   |
| `status`     | Integer | 状态：0-待处理，1-已完成，2-已取消，3-过期关闭，4-手工关闭 |
| `createTime` | String  | 创建时间                                                   |
| `updateTime` | String  | 更新时间                                                   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "1940947954631938050",
      "projectId": "1985681736518647809",
      "tasks": [
        {
          "endDate": "2025-11-14",
          "schemaCode": "leizhuPatientDailyActual",
          "createTime": "2025-11-19T04:02:02",
          "name": "2025年11月14日-雷珠患者跟进日填报",
          "zoneId": "1940947954631938050",
          "updateTime": "2025-11-26T14:45:37",
          "id": "1990873150412124161",
          "startDate": "2025-11-14",
          "periodCode": "1002.2025.11.14",
          "status": 0
        }
      ]
    }
  ],
  "timestamp": 1774003605796,
  "success": true
}
```

---

### 4.11 查询用户的计划编制数据

获取用户在目标管理类项目中提交的计划编制数据。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-plan`           |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                           |
| --------------- | ------- | ---- | ------------------------------ |
| `projectId`     | String  | 否   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodStart`   | String  | 否   | 周期开始时间                   |
| `periodEnd`     | String  | 否   | 周期结束时间                   |
| `schemaCode`    | String  | 否   | 模板编码，来自 4.8 返回的 `code` |
| `schemaVersion` | String  | 否   | 模板版本                       |
| `page`          | Integer | 否   | 页码，默认第 1 页              |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-plan' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1996045141549051905", "periodCode": "1002.2025"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型    | 说明                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `id`            | String  | 记录 ID                                                                   |
| `zoneId`        | String  | 区划 ID                                                                   |
| `zoneName`      | String  | 区划名称                                                                   |
| `pathIds`       | String  | 区划父级ID                                                                 |
| `pathNames`     | String  | 区划父级名称                                                               |
| `projectId`     | String  | 项目 ID                                                                   |
| `projectCode`   | String  | 项目编码                                                                  |
| `projectName`   | String  | 项目名称                                                                  |
| `periodCode`    | String  | 周期编码                                                                  |
| `periodName`    | String  | 周期名称                                                                  |
| `periodStart`   | String  | 周期开始时间                                                              |
| `periodEnd`     | String  | 周期结束时间                                                              |
| `schemaCode`    | String  | 模板编码                                                                  |
| `schemaName`    | String  | 模板名称                                                                  |
| `schemaVersion` | String  | 模板版本                                                                  |
| `fieldValue`    | Object  | 字段值，结构由模板定义                                                    |
| `status`        | Integer | 状态：-1-未编辑，0-已编辑，100-已提交，200-已审核，300-已锁定，400-已发布 |
| `createTime`    | String  | 创建时间                                                                  |
| `updateTime`    | String  | 更新时间                                                                  |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "pathIds": "1941049359938527233/1941049361112932353/1941049362991980546",
      "schemaVersion": "1.0",
      "pathNames": null,
      "periodName": "2026年第1季度",
      "updateTime": "2025-12-18T20:20:34",
      "schemaName": "客户管理季度计划",
      "fieldValue": {
        "productId": "1986131416662327297",
        "hcoId": "1945795841394532353",
        "hcoName": "凉山彝族自治州第一人民医院",
        "hcpName": "何继才",
        "hcpId": "1945796288024993794",
        "productName": "诺适得(雷珠单抗)(HNWS)"
      },
      "periodCode": "1002.2026.Q1",
      "projectCode": "qtPlanForCustMgmt2026",
      "schemaCode": "hcpManageQuarterlyPlan",
      "createTime": "2025-12-18T20:20:16",
      "zoneId": "1986131412379516929",
      "id": "2001628576841007106",
      "zoneName": "维盛四川眼二区岗位5",
      "projectName": "2026年客户管理季度目标规划",
      "projectId": "2001569639747887106",
      "periodStart": "2026-01-01",
      "periodEnd": "2026-03-31",
      "status": -1
    }
  ],
  "timestamp": 1774003661740,
  "success": true
}
```

---

### 4.12 查询用户的实际结果数据

获取用户在目标管理类项目中提交的实际结果数据。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-actual`         |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                           |
| --------------- | ------- | ---- | ------------------------------ |
| `projectId`     | String  | 否   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodStart`   | String  | 否   | 周期开始时间                   |
| `periodEnd`     | String  | 否   | 周期结束时间                   |
| `schemaCode`    | String  | 否   | 模板编码，来自 4.8 返回的 `code` |
| `schemaVersion` | String  | 否   | 模板版本                       |
| `page`          | Integer | 否   | 页码，默认第 1 页              |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-actual' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1996047565512830978"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型    | 说明                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `id`            | String  | 记录 ID                                                                   |
| `zoneId`        | String  | 区划 ID                                                                   |
| `zoneName`      | String  | 区划名称                                                                   |
| `pathIds`       | String  | 区划父级ID                                                                 |
| `pathNames`     | String  | 区划父级名称                                                               |
| `projectId`     | String  | 项目 ID                                                                   |
| `projectCode`   | String  | 项目编码                                                                  |
| `projectName`   | String  | 项目名称                                                                  |
| `periodCode`    | String  | 周期编码                                                                  |
| `periodName`    | String  | 周期名称                                                                  |
| `periodStart`   | String  | 周期开始时间                                                              |
| `periodEnd`     | String  | 周期结束时间                                                              |
| `schemaCode`    | String  | 模板编码                                                                  |
| `schemaName`    | String  | 模板名称                                                                  |
| `schemaVersion` | String  | 模板版本                                                                  |
| `fieldValue`    | Object  | 字段值，结构由模板定义                                                    |
| `status`        | Integer | 状态：-1-未编辑，0-已编辑，100-已提交，200-已审核，300-已锁定，400-已发布 |
| `createTime`    | String  | 创建时间                                                                  |
| `updateTime`    | String  | 更新时间                                                                  |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "pathIds": "1941049359938527233/1941049361238761474/1941049363142975489",
      "schemaVersion": "1.0",
      "pathNames": null,
      "periodName": "2026年1月",
      "updateTime": "2026-02-28T10:22:33",
      "schemaName": "客户管理月度执行",
      "fieldValue": {
        "focusType": "focusType.maintenanceDosage",
        "productId": "1938529763362717697",
        "salesVolume": 500,
        "planVersionId": "1978661864328298498",
        "hcoId": "1939661554274316290",
        "hcoName": "东莞东华医院",
        "hcpName": "李春芳",
        "hcpId": "1939673352109105154",
        "territoryId": "1941052027817861121",
        "academicConferenceExpense": 300,
        "productName": "施图伦(HNWS)",
        "academicLinkExpense": 500
      },
      "periodCode": "1002.2026.M1",
      "projectCode": "mtActualForCustMgmt2026",
      "schemaCode": "hcpManageMonthlyActual",
      "createTime": "2026-01-04T16:26:34",
      "zoneId": "1941052027817861121",
      "id": "2007730360189784065",
      "zoneName": "维盛深圳眼一区岗位6",
      "projectName": "2026年客户管理月度结果填报",
      "projectId": "2004564976721121281",
      "periodStart": "2026-01-01",
      "periodEnd": "2026-01-31",
      "status": 100
    }
  ],
  "timestamp": 1774003711368,
  "success": true
}
```

---

### 4.13 查询用户的采集填报数据

获取用户在普通采集项目中提交的采集填报数据。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-user/project-general`        |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                           |
| --------------- | ------- | ---- | ------------------------------ |
| `projectId`     | String  | 否   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodStart`   | String  | 否   | 周期开始时间                   |
| `periodEnd`     | String  | 否   | 周期结束时间                   |
| `schemaCode`    | String  | 否   | 模板编码，来自 4.8 返回的 `code` |
| `schemaVersion` | String  | 否   | 模板版本                       |
| `page`          | Integer | 否   | 页码，默认第 1 页              |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-general' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{"projectId": "1985681736518647809"}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型    | 说明                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `id`            | String  | 记录 ID                                                                   |
| `zoneId`        | String  | 区划 ID                                                                   |
| `zoneName`      | String  | 区划名称                                                                   |
| `pathIds`       | String  | 区划父级ID                                                                 |
| `pathNames`     | String  | 区划父级名称                                                               |
| `projectId`     | String  | 项目 ID                                                                   |
| `projectCode`   | String  | 项目编码                                                                  |
| `projectName`   | String  | 项目名称                                                                  |
| `periodCode`    | String  | 周期编码                                                                  |
| `periodName`    | String  | 周期名称                                                                  |
| `periodStart`   | String  | 周期开始时间                                                              |
| `periodEnd`     | String  | 周期结束时间                                                              |
| `schemaCode`    | String  | 模板编码                                                                  |
| `schemaName`    | String  | 模板名称                                                                  |
| `schemaVersion` | String  | 模板版本                                                                  |
| `fieldValue`    | Object  | 字段值，结构由模板定义                                                    |
| `status`        | Integer | 状态：-1-未编辑，0-已编辑，100-已提交，200-已审核，300-已锁定，400-已发布 |
| `createTime`    | String  | 创建时间                                                                  |
| `updateTime`    | String  | 更新时间                                                                  |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
{
      "pathIds": "1941049359938527233/1941049360743833601/1941049361909850113",
      "schemaVersion": "1.0",
      "pathNames": null,
      "periodName": "2026年1月4日",
      "updateTime": "2026-02-28T10:22:31",
      "schemaName": "倍优适患者跟进日填报-患者概要",
      "fieldValue": {
        "area": "维盛黑龙江眼一区",
        "territoryName": null,
        "productId": "1986131416679104514",
        "positionType": "专岗",
        "aflibercept": 0,
        "hcoId": "1939661534565281794",
        "hcoName": "哈尔滨医科大学附属第一医院",
        "hcpName": "郑轶-201709809597",
        "jobState": "在职",
        "hcoCpId": 201602260012,
        "medicationDate": "2026-01-04",
        "productName": "倍优适(布西珠单抗)(HNWS)",
        "lucentis": 1,
        "androidMin": 0,
        "conbercept": 0,
        "hcpId": "1939673148014272514",
        "territoryId": "1941052029948567553",
        "persistentDmeCount": 1,
        "faricimab": 0,
        "region": "维盛东北大区",
        "otherDmeCount": 0,
        "beovu": 0,
        "territory": "维盛黑龙江眼一区岗位2"
      },
      "periodCode": "1002.2026.1.4",
      "projectCode": "dyCollForBeovuPatientMgmt2026",
      "schemaCode": "beovuPatientDailyCollection",
      "createTime": "2026-01-04T16:33:25",
      "zoneId": "1941052029948567553",
      "id": "2007732080811114497",
      "zoneName": "维盛黑龙江眼一区岗位2",
      "projectName": "2026年倍优适患者管每日结果填报",
      "projectId": "2006184441719885825",
      "periodStart": "2026-01-04",
      "periodEnd": "2026-01-04",
      "status": 100
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

### 4.14 查询指定区划的待办任务

按区划维度查询任务状态。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-zone/project-task`           |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明                                                       |
| ------------- | ------- | ---- | ---------------------------------------------------------- |
| `zoneId`      | String  | 是   | 区划 ID，来自 4.1 返回的 `id`                              |
| `projectId`   | String  | 是   | 项目 ID，来自 4.6 返回的 `id`                              |
| `periodStart` | String  | 是   | 周期开始时间                                               |
| `periodEnd`   | String  | 是   | 周期结束时间                                               |
| `status`      | Integer | 否   | 状态：0-待处理，1-已完成，2-已取消，3-过期关闭，4-手工关闭 |
| `page`        | Integer | 否   | 页码，默认第 1 页                                          |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-zone/project-task' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "zoneId": "1940947954631938050",
    "projectId": "1985681736518647809",
    "periodStart": "2025-11-01",
    "periodEnd": "2025-11-30"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名      | 类型   | 说明     |
| ----------- | ------ | -------- |
| `projectId` | String | 项目 ID  |
| `tasks`     | Array  | 任务列表 |

`tasks` 数组元素字段：

| 字段名       | 类型    | 说明                                                       |
| ------------ | ------- | ---------------------------------------------------------- |
| `id`         | String  | 任务 ID                                                    |
| `name`       | String  | 任务名称                                                   |
| `startDate`  | String  | 任务开始日期                                               |
| `endDate`    | String  | 任务结束日期                                               |
| `zoneId`     | String  | 区划 ID                                                    |
| `periodCode` | String  | 周期编码                                                   |
| `schemaCode` | String  | 模板编码                                                   |
| `status`     | Integer | 状态：0-待处理，1-已完成，2-已取消，3-过期关闭，4-手工关闭 |
| `createTime` | String  | 创建时间                                                   |
| `updateTime` | String  | 更新时间                                                   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "projectId": "1985681736518647809",
      "tasks": [
        {
          "endDate": "2025-11-14",
          "schemaCode": "leizhuPatientDailyActual",
          "createTime": "2025-11-19T04:02:02",
          "name": "2025年11月14日-雷珠患者跟进日填报",
          "zoneId": "1940947954631938050",
          "updateTime": "2025-11-26T14:45:37",
          "id": "1990873150412124161",
          "startDate": "2025-11-14",
          "periodCode": "1002.2025.11.14",
          "status": 0
        }
      ]
    }
  ],
  "timestamp": 1774003854930,
  "success": true
}
```

---

### 4.15 查询指定区划的计划编制数据

按区划维度查询计划编制数据。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-zone/project-plan`           |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                           |
| --------------- | ------- | ---- | ------------------------------ |
| `zoneId`        | String  | 是   | 区划 ID，来自 4.1 返回的 `id`  |
| `projectId`     | String  | 是   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodStart`   | String  | 是   | 周期开始时间                   |
| `periodEnd`     | String  | 是   | 周期结束时间                   |
| `schemaCode`    | String  | 否   | 模板编码                       |
| `schemaVersion` | String  | 否   | 模板版本                       |
| `page`          | Integer | 否   | 页码，默认第 1 页              |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-zone/project-plan' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "zoneId": "1940947913078968322",
    "projectId": "1996045141549051905",
    "periodStart": "2025-01-01",
    "periodEnd": "2025-12-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型    | 说明                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `id`            | String  | 记录 ID                                                                   |
| `zoneId`        | String  | 区划 ID                                                                   |
| `zoneName`      | String  | 区划名称                                                                   |
| `pathIds`       | String  | 区划父级ID                                                                 |
| `pathNames`     | String  | 区划父级名称                                                               |
| `projectId`     | String  | 项目 ID                                                                   |
| `projectCode`   | String  | 项目编码                                                                  |
| `projectName`   | String  | 项目名称                                                                  |
| `periodCode`    | String  | 周期编码                                                                  |
| `periodName`    | String  | 周期名称                                                                  |
| `periodStart`   | String  | 周期开始时间                                                              |
| `periodEnd`     | String  | 周期结束时间                                                              |
| `schemaCode`    | String  | 模板编码                                                                  |
| `schemaName`    | String  | 模板名称                                                                  |
| `schemaVersion` | String  | 模板版本                                                                  |
| `fieldValue`    | Object  | 字段值，结构由模板定义                                                    |
| `status`        | Integer | 状态：-1-未编辑，0-已编辑，100-已提交，200-已审核，300-已锁定，400-已发布 |
| `createTime`    | String  | 创建时间                                                                  |
| `updateTime`    | String  | 更新时间                                                                  |

---

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "pathIds": "1941049359938527233/1941049361112932353/1941049362991980546",
      "schemaVersion": "1.0",
      "pathNames": null,
      "periodName": "2026年第1季度",
      "updateTime": "2025-12-18T20:20:34",
      "schemaName": "客户管理季度计划",
      "fieldValue": {
        "productId": "1986131416662327297",
        "hcoId": "1945795841394532353",
        "hcoName": "凉山彝族自治州第一人民医院",
        "hcpName": "何继才",
        "hcpId": "1945796288024993794",
        "productName": "诺适得(雷珠单抗)(HNWS)"
      },
      "periodCode": "1002.2026.Q1",
      "projectCode": "qtPlanForCustMgmt2026",
      "schemaCode": "hcpManageQuarterlyPlan",
      "createTime": "2025-12-18T20:20:16",
      "zoneId": "1986131412379516929",
      "id": "2001628576841007106",
      "zoneName": "维盛四川眼二区岗位5",
      "projectName": "2026年客户管理季度目标规划",
      "projectId": "2001569639747887106",
      "periodStart": "2026-01-01",
      "periodEnd": "2026-03-31",
      "status": -1
    }
  ],
  "timestamp": 1774003661740,
  "success": true
}
```

### 4.16 查询指定区划的实际结果数据

按区划维度查询实际结果数据。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-zone/project-actual`         |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                           |
| --------------- | ------- | ---- | ------------------------------ |
| `zoneId`        | String  | 是   | 区划 ID，来自 4.1 返回的 `id`  |
| `projectId`     | String  | 是   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodStart`   | String  | 是   | 周期开始时间                   |
| `periodEnd`     | String  | 是   | 周期结束时间                   |
| `schemaCode`    | String  | 否   | 模板编码                       |
| `schemaVersion` | String  | 否   | 模板版本                       |
| `page`          | Integer | 否   | 页码，默认第 1 页              |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-zone/project-actual' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "zoneId": "1991567365303562242",
    "projectId": "1996047565512830978",
    "periodStart": "2025-12-01",
    "periodEnd": "2025-12-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型    | 说明                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `id`            | String  | 记录 ID                                                                   |
| `zoneId`        | String  | 区划 ID                                                                   |
| `zoneName`      | String  | 区划名称                                                                   |
| `pathIds`       | String  | 区划父级ID                                                                 |
| `pathNames`     | String  | 区划父级名称                                                               |
| `projectId`     | String  | 项目 ID                                                                   |
| `projectCode`   | String  | 项目编码                                                                  |
| `projectName`   | String  | 项目名称                                                                  |
| `periodCode`    | String  | 周期编码                                                                  |
| `periodName`    | String  | 周期名称                                                                  |
| `periodStart`   | String  | 周期开始时间                                                              |
| `periodEnd`     | String  | 周期结束时间                                                              |
| `schemaCode`    | String  | 模板编码                                                                  |
| `schemaName`    | String  | 模板名称                                                                  |
| `schemaVersion` | String  | 模板版本                                                                  |
| `fieldValue`    | Object  | 字段值，结构由模板定义                                                    |
| `status`        | Integer | 状态：-1-未编辑，0-已编辑，100-已提交，200-已审核，300-已锁定，400-已发布 |
| `createTime`    | String  | 创建时间                                                                  |
| `updateTime`    | String  | 更新时间                                                                  |

---

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "pathIds": "1941049359938527233/1941049361238761474/1941049363142975489",
      "schemaVersion": "1.0",
      "pathNames": null,
      "periodName": "2026年1月",
      "updateTime": "2026-02-28T10:22:33",
      "schemaName": "客户管理月度执行",
      "fieldValue": {
        "focusType": "focusType.maintenanceDosage",
        "productId": "1938529763362717697",
        "salesVolume": 500,
        "planVersionId": "1978661864328298498",
        "hcoId": "1939661554274316290",
        "hcoName": "东莞东华医院",
        "hcpName": "李春芳",
        "hcpId": "1939673352109105154",
        "territoryId": "1941052027817861121",
        "academicConferenceExpense": 300,
        "productName": "施图伦(HNWS)",
        "academicLinkExpense": 500
      },
      "periodCode": "1002.2026.M1",
      "projectCode": "mtActualForCustMgmt2026",
      "schemaCode": "hcpManageMonthlyActual",
      "createTime": "2026-01-04T16:26:34",
      "zoneId": "1941052027817861121",
      "id": "2007730360189784065",
      "zoneName": "维盛深圳眼一区岗位6",
      "projectName": "2026年客户管理月度结果填报",
      "projectId": "2004564976721121281",
      "periodStart": "2026-01-01",
      "periodEnd": "2026-01-31",
      "status": 100
    }
  ],
  "timestamp": 1774003711368,
  "success": true
}
```

### 4.17 查询指定区划的采集填报数据

按区划维度查询采集填报数据。

**基本信息**

| 项目           | 说明                                                    |
| -------------- | ------------------------------------------------------- |
| 接口地址       | `/bia/open/biz-service/sfe-zone/project-general`        |
| 请求方式       | `POST`                                                  |
| Content-Type   | `application/json`                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                           |
| --------------- | ------- | ---- | ------------------------------ |
| `zoneId`        | String  | 是   | 区划 ID，来自 4.1 返回的 `id`  |
| `projectId`     | String  | 是   | 项目 ID，来自 4.6 返回的 `id`  |
| `periodStart`   | String  | 是   | 周期开始时间                   |
| `periodEnd`     | String  | 是   | 周期结束时间                   |
| `schemaCode`    | String  | 否   | 模板编码                       |
| `schemaVersion` | String  | 否   | 模板版本                       |
| `page`          | Integer | 否   | 页码，默认第 1 页              |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-zone/project-general' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "zoneId": "1940947913078968322",
    "projectId": "1985681736518647809",
    "periodStart": "2025-11-01",
    "periodEnd": "2025-11-30"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型    | 说明                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `id`            | String  | 记录 ID                                                                   |
| `zoneId`        | String  | 区划 ID                                                                   |
| `zoneName`      | String  | 区划名称                                                                   |
| `pathIds`       | String  | 区划父级ID                                                                 |
| `pathNames`     | String  | 区划父级名称                                                               |
| `projectId`     | String  | 项目 ID                                                                   |
| `projectCode`   | String  | 项目编码                                                                  |
| `projectName`   | String  | 项目名称                                                                  |
| `periodCode`    | String  | 周期编码                                                                  |
| `periodName`    | String  | 周期名称                                                                  |
| `periodStart`   | String  | 周期开始时间                                                              |
| `periodEnd`     | String  | 周期结束时间                                                              |
| `schemaCode`    | String  | 模板编码                                                                  |
| `schemaName`    | String  | 模板名称                                                                  |
| `schemaVersion` | String  | 模板版本                                                                  |
| `fieldValue`    | Object  | 字段值，结构由模板定义                                                    |
| `status`        | Integer | 状态：-1-未编辑，0-已编辑，100-已提交，200-已审核，300-已锁定，400-已发布 |
| `createTime`    | String  | 创建时间                                                                  |
| `updateTime`    | String  | 更新时间                                                                  |

---

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
{
      "pathIds": "1941049359938527233/1941049360743833601/1941049361909850113",
      "schemaVersion": "1.0",
      "pathNames": null,
      "periodName": "2026年1月4日",
      "updateTime": "2026-02-28T10:22:31",
      "schemaName": "倍优适患者跟进日填报-患者概要",
      "fieldValue": {
        "area": "维盛黑龙江眼一区",
        "territoryName": null,
        "productId": "1986131416679104514",
        "positionType": "专岗",
        "aflibercept": 0,
        "hcoId": "1939661534565281794",
        "hcoName": "哈尔滨医科大学附属第一医院",
        "hcpName": "郑轶-201709809597",
        "jobState": "在职",
        "hcoCpId": 201602260012,
        "medicationDate": "2026-01-04",
        "productName": "倍优适(布西珠单抗)(HNWS)",
        "lucentis": 1,
        "androidMin": 0,
        "conbercept": 0,
        "hcpId": "1939673148014272514",
        "territoryId": "1941052029948567553",
        "persistentDmeCount": 1,
        "faricimab": 0,
        "region": "维盛东北大区",
        "otherDmeCount": 0,
        "beovu": 0,
        "territory": "维盛黑龙江眼一区岗位2"
      },
      "periodCode": "1002.2026.1.4",
      "projectCode": "dyCollForBeovuPatientMgmt2026",
      "schemaCode": "beovuPatientDailyCollection",
      "createTime": "2026-01-04T16:33:25",
      "zoneId": "1941052029948567553",
      "id": "2007732080811114497",
      "zoneName": "维盛黑龙江眼一区岗位2",
      "projectName": "2026年倍优适患者管每日结果填报",
      "projectId": "2006184441719885825",
      "periodStart": "2026-01-04",
      "periodEnd": "2026-01-04",
      "status": 100
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

## 五、错误码说明

| resultCode | 说明             | 处理建议                   |
| ---------- | ---------------- | -------------------------- |
| 1          | 请求成功         | -                          |
| 0          | 系统异常         | 联系技术支持               |
| 400        | 请求参数错误     | 检查请求参数格式和必填项   |
| 401        | 未授权           | 检查 `appKey` 是否正确     |
| 403        | 无权限访问       | 确认 `appKey` 对应的应用权限 |
| 404        | 资源不存在       | 检查请求的资源 ID 是否正确 |
| 429        | 请求频率超限     | 降低请求频率，稍后重试     |
| 500        | 服务器内部错误   | 联系技术支持               |

---

## 六、注意事项

1. **分页查询**：每页固定返回 1000 条记录。大量数据请使用 `/count` 接口获取总记录数后分页查询。

2. **状态码区分**：
   - `status` 用于通用启用/禁用状态（0-禁用，1-启用）
   - `status` 用于数据项状态时有更多枚举值（-1~400）

3. **fieldValue 结构**：`fieldValue` 为 JSON 对象，字段结构由对应 `schemaCode` 的模板定义，请调用 **4.8** 获取模板定义后了解具体字段。

4. **环境区分**：目前仅提供生产环境，测试请使用生产环境的测试账号。

5. **请求频率**：建议控制请求频率，避免短时间内大量请求导致 429 错误。

---

## 附录

### A. 状态码枚举

#### A.1 通用状态（status）

| 状态码 | 状态名称 | 说明                 |
| ------ | -------- | -------------------- |
| 0      | 禁用     | 数据已禁用，不可使用 |
| 1      | 启用     | 数据正常可用         |

#### A.2 数据项状态（itemStatus）

| 状态码 | 状态名称 | 说明                     |
| ------ | -------- | ------------------------ |
| -1     | 待编辑   | 数据项已创建，待代表填写 |
| 0      | 已编辑   | 代表已填写，待提交审核   |
| 100    | 待审核   | 已提交，等待审核         |
| 200    | 已审核   | 审核通过                 |
| 300    | 已锁定   | 数据已锁定，不可修改     |
| 400    | 已发布   | 数据已发布归档           |

#### A.3 任务状态（taskStatus）

| 状态码 | 状态名称 | 说明       |
| ------ | -------- | ---------- |
| 0      | 待处理   | 任务待完成 |
| 1      | 已完成   | 任务已完成 |
| 2      | 已取消   | 任务已取消 |
| 3      | 过期关闭 | 任务超时   |
| 4      | 手工关闭 | 任务人工关闭 |

### B. 周期单位枚举（cycleUnit）

| 值              | 说明          |
| --------------- | ------------- |
| `daily`         | 天            |
| `iso_weekly`    | ISO 年周      |
| `nature_weekly` | 自然月周      |
| `monthly`       | 月            |
| `quarterly`     | 季度          |
| `yearly`        | 年            |

### C. 区划层次枚举（level）

| 值          | 说明   |
| ----------- | ------ |
| `hq`        | 总部   |
| `region`    | 大区   |
| `district`  | 片区   |
| `area`      | 地区   |
| `territory` | 辖区   |

### D. 术语表

| 术语         | 英文                    | 说明                                               |
| ------------ | ----------------------- | -------------------------------------------------- |
| 区划         | Zone                    | 代表负责的业务区域，对应 API 字段 `zoneId`         |
| 周期         | Period                  | 数据采集的时间周期，对应 API 字段 `periodCode`     |
| 模板         | Schema                  | 定义数据字段结构的模板，对应 API 字段 `schemaCode` |
| 覆盖分管     | Coverage                | 代表对医疗机构或医生的负责关系                     |
| 画像         | Profile                 | 医疗机构或医生的属性标签集合                       |
| 数据采集项目 | Data Collection Project | 按周期组织的数据采集任务集合                       |
| 数据项       | Data Item               | 具体一条采集任务记录                               |
| AppKey       | App Key                 | 应用唯一标识，用于 API 鉴权                        |