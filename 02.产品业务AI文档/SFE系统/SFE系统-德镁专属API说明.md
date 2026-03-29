# SFE系统德镁专属 Open API 接口文档

## 修订记录

| 版本 | 日期       | 修订内容                       | 修订人 |
| ---- | ---------- | ------------------------------ | ------ |
| V1.0 | 2026-03-27 | 初始版本，开放德镁专属接口     | 王馗   |
| V1.1 | 2026-03-27 | 新增百卢妥日采集按大区统计接口 | 王馗   |

---

## 一、概述

本文档描述了 **SFE系统德镁专属接口**，主要针对特定客户的定制化业务场景提供专用API接口。

---

## 二、通用说明

### 2.1 访问地址

```
https://{域名}/erp-open-api/{接口地址}
```

### 2.2 环境信息

| 环境     | 域名/Base URL                       | 备注 |
| -------- | ----------------------------------- | ---- |
| 生产环境 | `https://erp-web.mediportal.com.cn` | -    |

### 2.3 公共请求头

| Header         | 说明                                   | 是否必填  |
| -------------- | -------------------------------------- | --------- |
| `appKey`       | 从工作协同/ERP/SFE 系统获取的 API 密钥 | 是        |
| `Content-Type` | 请求体类型，`application/json`         | POST 必填 |

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

| 字段         | 类型    | 说明                                        |
| ------------ | ------- | ------------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，其他值表示失败    |
| `resultMsg`  | String  | 提示信息，成功时可能为 `null`               |
| `data`       | T       | 业务数据，不同接口类型不同，失败时为 `null` |
| `timestamp`  | Long    | 响应时间戳                                  |
| `success`    | Boolean | 是否成功，与 `resultCode=1` 对应            |

### 2.5 分页查询

#### 分页参数

所有接口支持 `page` 参数进行分页查询，不传入时默认查询第 1 页。每页固定返回 1000 条记录。

| 参数   | 类型    | 必填 | 说明                    |
| ------ | ------- | ---- | ----------------------- |
| `page` | Integer | 否   | 请求页数，缺省为第 1 页 |

#### 查询总记录数

所有接口可在 URL 后添加 `/count` 查询总记录数，用于确定总页数。

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionFeedback/count' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
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

### 场景：查询百卢妥日采集反馈数据

> 需求：获取百卢妥日采集反馈数据。

1. 调用 **4.1 百卢妥日采集反馈**，传入 `periodStart` 和 `periodEnd` 等筛选条件，获取反馈数据列表
2. 根据返回的 `regionName`（大区）和 `areaName`（地区）进行数据分析

---

## 四、接口详细说明

---

### 4.1 百卢妥日采集反馈

查询百卢妥日采集反馈数据。

**基本信息**

| 项目         | 说明                                                                    |
| ------------ | ----------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionFeedback` |
| 请求方式     | `POST`                                                                  |
| Content-Type | `application/json`                                                      |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明                   |
| ------------- | ------- | ---- | ---------------------- |
| `zoneId`      | String  | 否   | 区划 ID                |
| `regionName`  | String  | 否   | 大区名称，支持模糊查询 |
| `areaName`    | String  | 否   | 地区名称，支持模糊查询 |
| `periodStart` | String  | 否   | 期间开始日期           |
| `periodEnd`   | String  | 否   | 期间结束日期           |
| `page`        | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionFeedback' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                         | 类型   | 说明                     |
| ------------------------------ | ------ | ------------------------ |
| `regionName`                   | String | 大区                     |
| `areaName`                     | String | 地区                     |
| `date`                         | Date   | 日期                     |
| `newPatientReservesProCount`   | Number | 新增患者储备PRO拉新人数  |
| `newPatientReservesWeComCount` | Number | 新增患者储备企微拉新人数 |
| `newPatientReservesTotal`      | Number | 新增患者储备总数         |
| `onlinePrescriptionCount`      | Number | 线上处方支数             |
| `offlinePrescriptionCount`     | Number | 线下处方支数             |
| `prescriptionTotal`            | Number | 处方支数总数             |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "date": "2025-01-15",
      "newPatientReservesProCount": 10,
      "newPatientReservesWeComCount": 8,
      "newPatientReservesTotal": 18,
      "onlinePrescriptionCount": 20,
      "offlinePrescriptionCount": 12,
      "prescriptionTotal": 32
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

### 4.2 百卢妥日采集按大区统计

查询百卢妥日采集按大区统计数据。

**基本信息**

| 项目         | 说明                                                                              |
| ------------ | --------------------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionStatisticsByRegion` |
| 请求方式     | `POST`                                                                            |
| Content-Type | `application/json`                                                                |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明                   |
| ------------- | ------- | ---- | ---------------------- |
| `regionName`  | String  | 否   | 大区名称，支持模糊查询 |
| `periodStart` | String  | 否   | 期间开始日期           |
| `periodEnd`   | String  | 否   | 期间结束日期           |
| `page`        | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionStatisticsByRegion' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                         | 类型   | 说明                     |
| ------------------------------ | ------ | ------------------------ |
| `regionName`                   | String | 大区                     |
| `date`                         | Date   | 日期                     |
| `newPatientReservesProCount`   | Number | 新增患者储备PRO拉新人数  |
| `newPatientReservesWeComCount` | Number | 新增患者储备企微拉新人数 |
| `newPatientReservesTotal`      | Number | 新增患者储备总数         |
| `onlinePrescriptionCount`      | Number | 线上处方支数             |
| `offlinePrescriptionCount`     | Number | 线下处方支数             |
| `prescriptionTotal`            | Number | 处方支数总数             |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "date": "2025-01-15",
      "newPatientReservesProCount": 10,
      "newPatientReservesWeComCount": 8,
      "newPatientReservesTotal": 18,
      "onlinePrescriptionCount": 20,
      "offlinePrescriptionCount": 12,
      "prescriptionTotal": 32
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

## 五、错误码说明

| resultCode | 说明           | 处理建议                     |
| ---------- | -------------- | ---------------------------- |
| 1          | 请求成功       | -                            |
| 0          | 系统异常       | 联系技术支持                 |
| 400        | 请求参数错误   | 检查请求参数格式和必填项     |
| 401        | 未授权         | 检查 `appKey` 是否正确       |
| 403        | 无权限访问     | 确认 `appKey` 对应的应用权限 |
| 404        | 资源不存在     | 检查请求的资源 ID 是否正确   |
| 429        | 请求频率超限   | 降低请求频率，稍后重试       |
| 500        | 服务器内部错误 | 联系技术支持                 |

---

## 六、注意事项

1. **分页查询**：每页固定返回 1000 条记录。大量数据请使用 `/count` 接口获取总记录数后分页查询。

2. **环境区分**：目前仅提供生产环境，测试请使用生产环境的测试账号。

3. **请求频率**：建议控制请求频率，避免短时间内大量请求导致 429 错误。

---

## 附录

### A. 状态码枚举

#### A.1 通用状态（status）

| 状态码 | 状态名称 | 说明                 |
| ------ | -------- | -------------------- |
| 0      | 禁用     | 数据已禁用，不可使用 |
| 1      | 启用     | 数据正常可用         |

### B. 术语表

| 术语   | 英文   | 说明                                       |
| ------ | ------ | ------------------------------------------ |
| 区划   | Zone   | 代表负责的业务区域，对应 API 字段 `zoneId` |
| AppKey | AppKey | 应用唯一标识，用于 API 鉴权                |
