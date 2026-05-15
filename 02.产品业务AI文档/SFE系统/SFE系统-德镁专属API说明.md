# SFE系统德镁专属 Open API 接口文档

## 修订记录

| 版本 | 日期       | 修订内容                                              | 修订人 |
| ---- | ---------- | ----------------------------------------------------- | ------ |
| V1.0 | 2026-03-27 | 初始版本，开放德镁专属接口                            | 王馗   |
| V1.1 | 2026-03-27 | 新增百卢妥日采集按大区统计接口 | 王馗   |
| V1.2 | 2026-04-01 | "百卢妥日采集"更名为"益路取&芦可替尼地区经理日报"，所有采集字段重命名 | 王馗   |
| V1.3 | 2026-05-13 | 新增客户管理相关接口5个，新增益路取&芦可替尼日报执行日统计接口 | 王馗   |

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

### 场景：查询益路取&芦可替尼地区经理日报数据

> 需求：获取益路取&芦可替尼地区经理日报数据。

1. 调用 **4.2.1 益路取&芦可替尼地区经理日报**，传入 `periodStart` 和 `periodEnd` 等筛选条件，获取反馈数据列表
2. 根据返回的 `regionName`（大区）和 `areaName`（地区）进行数据分析

---

## 四、接口详细说明

---

### 4.1 客户管理相关接口

---

#### 4.1.1 客户管理年度跟踪表

查询客户管理年度跟踪数据。

**基本信息**

| 项目         | 说明                                                       |
| ------------ | ---------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/customerManageReport` |
| 请求方式     | `POST`                                                     |
| Content-Type | `application/json`                                         |

**请求参数**

请求体为 JSON，字段如下：

| 参数名         | 类型    | 必填 | 说明                   |
| -------------- | ------- | ---- | ---------------------- |
| `zoneId`       | String  | 否   | 区划 ID                |
| `regionName`   | String  | 否   | 大区名称，支持模糊查询 |
| `areaName`     | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName`| String  | 否   | 辖区名称，支持模糊查询 |
| `monthNo`      | String  | 否   | 月份，格式如202604    |
| `page`         | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/customerManageReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "monthNo": "202604"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                         | 类型   | 说明                              |
| ------------------------------ | ------ | --------------------------------- |
| `regionName`                   | String | 大区名称                          |
| `areaName`                     | String | 地区名称                          |
| `territoryName`                | String | 辖区名称                          |
| `managerName`                  | String | 分管代表名称                      |
| `positionType`                 | String | 岗位类型（区域类型=岗位才有）     |
| `productName`                  | String | 产品名称                          |
| `hcoId`                        | String | 医院 ID                           |
| `hcoName`                      | String | 医院名称                          |
| `deptName`                     | String | 客户科室                          |
| `hcpId`                        | String | 客户 ID                           |
| `hcpName`                      | String | 客户名称                          |
| `isBenchmarkHospital`          | String | 是否标杆医院                      |
| `productAwareness`             | String | 产品认知度                        |
| `medicationPotentialLevel`     | String | 用药潜力等级                      |
| `academicLevel`                | String | 学术级别                          |
| `cyFocusType`                  | String | 年度聚焦客户类型                  |
| `monthNo`                      | String | 月度编号                          |
| `cqFocusType`                  | String | 季度聚焦客户类型                  |
| `cmFocusType`                  | String | 月度聚焦客户类型                  |
| `lastMonthCompletion`          | Number | 上月完成量                        |
| `lastMonthNpCount`             | Number | 上月 NP 数量                      |
| `currentMonthTarget`           | Number | 本月目标量                        |
| `currentMonthTargetNpCount`    | Number | 本月目标 NP 数量                  |
| `academicVisitCount`           | Number | 学术拜访次数（次）                |
| `academicVisitAmount`          | Number | 学术拜访金额（元）                |
| `academicLinkCount`            | Number | 学术链接次数（次）                |
| `academicLinkAmount`           | Number | 学术链接金额（元）                |
| `academicMeetingCount`         | Number | 学术会议次数（次）                |
| `academicMeetingAmount`        | Number | 学术会议金额（元）                |
| `meetingSupportCount`          | Number | 会议支持次数（次）                |
| `meetingSupportAmount`         | Number | 会议支持金额（元）                |
| `resourcePlanTotal`            | Number | 资源规划合计（元）                |
| `w1PlanContent`                | String | w1 周计划                         |
| `w2PlanContent`                | String | w2 周计划                         |
| `w3PlanContent`                | String | w3 周计划                         |
| `w4PlanContent`                | String | w4 周计划                         |
| `w5PlanContent`                | String | w5 周计划                         |
| `w1VisitCnt`                   | Number | w1 学术拜访次数                   |
| `w2VisitCnt`                   | Number | w2 学术拜访次数                   |
| `w3VisitCnt`                   | Number | w3 学术拜访次数                   |
| `w4VisitCnt`                   | Number | w4 学术拜访次数                   |
| `w5VisitCnt`                   | Number | w5 学术拜访次数                   |
| `w1LinkCnt`                    | Number | w1 学术链接次数                   |
| `w2LinkCnt`                    | Number | w2 学术链接次数                   |
| `w3LinkCnt`                    | Number | w3 学术链接次数                   |
| `w4LinkCnt`                    | Number | w4 学术链接次数                   |
| `w5LinkCnt`                    | Number | w5 学术链接次数                   |
| `w1MeetingCnt`                 | Number | w1 学术会议次数                   |
| `w2MeetingCnt`                 | Number | w2 学术会议次数                   |
| `w3MeetingCnt`                 | Number | w3 学术会议次数                   |
| `w4MeetingCnt`                 | Number | w4 学术会议次数                   |
| `w5MeetingCnt`                 | Number | w5 学术会议次数                   |
| `w1SupportCnt`                 | Number | w1 会议支持次数                   |
| `w2SupportCnt`                 | Number | w2 会议支持次数                   |
| `w3SupportCnt`                 | Number | w3 会议支持次数                   |
| `w4SupportCnt`                 | Number | w4 会议支持次数                   |
| `w5SupportCnt`                 | Number | w5 会议支持次数                   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "territoryName": "上海辖区A",
      "managerName": "张三",
      "positionType": "专岗",
      "productName": "益路取",
      "hcoId": "HCO001",
      "hcoName": "上海第一人民医院",
      "deptName": "肿瘤科",
      "hcpId": "HCP001",
      "hcpName": "李医生",
      "isBenchmarkHospital": "是",
      "productAwareness": "高",
      "medicationPotentialLevel": "A级",
      "academicLevel": "主任医师",
      "cyFocusType": "核心客户",
      "monthNo": "202604",
      "cqFocusType": "Q1核心",
      "cmFocusType": "月度重点",
      "lastMonthCompletion": 100,
      "lastMonthNpCount": 15,
      "currentMonthTarget": 120,
      "currentMonthTargetNpCount": 18,
      "academicVisitCount": 4,
      "academicVisitAmount": 500,
      "academicLinkCount": 2,
      "academicLinkAmount": 300,
      "academicMeetingCount": 1,
      "academicMeetingAmount": 1000,
      "meetingSupportCount": 1,
      "meetingSupportAmount": 200,
      "resourcePlanTotal": 2000,
      "w1PlanContent": "完成拜访计划",
      "w2PlanContent": "跟进学术活动",
      "w3PlanContent": "协助会议组织",
      "w4PlanContent": "客户关系维护",
      "w5PlanContent": "",
      "w1VisitCnt": 3,
      "w2VisitCnt": 2,
      "w3VisitCnt": 1,
      "w4VisitCnt": 2,
      "w5VisitCnt": 0,
      "w1LinkCnt": 1,
      "w2LinkCnt": 1,
      "w3LinkCnt": 0,
      "w4LinkCnt": 0,
      "w5LinkCnt": 0,
      "w1MeetingCnt": 0,
      "w2MeetingCnt": 0,
      "w3MeetingCnt": 1,
      "w4MeetingCnt": 0,
      "w5MeetingCnt": 0,
      "w1SupportCnt": 0,
      "w2SupportCnt": 0,
      "w3SupportCnt": 0,
      "w4SupportCnt": 1,
      "w5SupportCnt": 0
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.2 客户规划年度跟踪表

查询客户规划年度跟踪数据。

**基本信息**

| 项目         | 说明                                                       |
| ------------ | ---------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/customerPlanReport`   |
| 请求方式     | `POST`                                                     |
| Content-Type | `application/json`                                         |

**请求参数**

请求体为 JSON，字段如下：

| 参数名       | 类型    | 必填 | 说明                   |
| ------------ | ------- | ---- | ---------------------- |
| `zoneId`     | String  | 否   | 区划 ID                |
| `regionName` | String  | 否   | 大区名称，支持模糊查询 |
| `areaName`   | String  | 否   | 地区名称，支持模糊查询 |
| `page`       | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/customerPlanReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "regionName": "华东"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名             | 类型   | 说明               |
| ------------------ | ------ | ------------------ |
| `regionName`       | String | 大区名称           |
| `areaName`         | String | 地区名称           |
| `productName`      | String | 品种名称           |
| `focusType`        | String | 聚焦类型           |
| `territoryCnt`     | Number | 辖区数             |
| `cyCustomerCnt`    | Number | 年度目标客户总数   |
| `cyAvgCustomerCnt` | Number | 年度岗位均客户数   |
| `q1CustomerCnt`    | Number | Q1目标客户总数     |
| `q1AvgCustomerCnt` | Number | Q1岗位均客户数     |
| `m1CustomerCnt`    | Number | 1月目标客户总数    |
| `m1AvgCustomerCnt` | Number | 1月岗位均客户数    |
| `m2CustomerCnt`    | Number | 2月目标客户总数    |
| `m2AvgCustomerCnt` | Number | 2月岗位均客户数    |
| `m3CustomerCnt`    | Number | 3月目标客户总数    |
| `m3AvgCustomerCnt` | Number | 3月岗位均客户数    |
| `q2CustomerCnt`    | Number | Q2目标客户总数     |
| `q2AvgCustomerCnt` | Number | Q2岗位均客户数     |
| `m4CustomerCnt`    | Number | 4月目标客户总数    |
| `m4AvgCustomerCnt` | Number | 4月岗位均客户数    |
| `m5CustomerCnt`    | Number | 5月目标客户总数    |
| `m5AvgCustomerCnt` | Number | 5月岗位均客户数    |
| `m6CustomerCnt`    | Number | 6月目标客户总数    |
| `m6AvgCustomerCnt` | Number | 6月岗位均客户数    |
| `q3CustomerCnt`    | Number | Q3目标客户总数     |
| `q3AvgCustomerCnt` | Number | Q3岗位均客户数     |
| `m7CustomerCnt`    | Number | 7月目标客户总数    |
| `m7AvgCustomerCnt` | Number | 7月岗位均客户数    |
| `m8CustomerCnt`    | Number | 8月目标客户总数    |
| `m8AvgCustomerCnt` | Number | 8月岗位均客户数    |
| `m9CustomerCnt`    | Number | 9月目标客户总数    |
| `m9AvgCustomerCnt` | Number | 9月岗位均客户数    |
| `q4CustomerCnt`    | Number | Q4目标客户总数     |
| `q4AvgCustomerCnt` | Number | Q4岗位均客户数     |
| `m10CustomerCnt`   | Number | 10月目标客户总数   |
| `m10AvgCustomerCnt`| Number | 10月岗位均客户数   |
| `m11CustomerCnt`   | Number | 11月目标客户总数   |
| `m11AvgCustomerCnt`| Number | 11月岗位均客户数   |
| `m12CustomerCnt`   | Number | 12月目标客户总数   |
| `m12AvgCustomerCnt`| Number | 12月岗位均客户数   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "productName": "益路取",
      "focusType": "核心",
      "territoryCnt": 10,
      "cyCustomerCnt": 500,
      "cyAvgCustomerCnt": 50,
      "q1CustomerCnt": 150,
      "q1AvgCustomerCnt": 15,
      "m1CustomerCnt": 50,
      "m1AvgCustomerCnt": 5,
      "m2CustomerCnt": 50,
      "m2AvgCustomerCnt": 5,
      "m3CustomerCnt": 50,
      "m3AvgCustomerCnt": 5,
      "q2CustomerCnt": 150,
      "q2AvgCustomerCnt": 15,
      "m4CustomerCnt": 50,
      "m4AvgCustomerCnt": 5,
      "m5CustomerCnt": 50,
      "m5AvgCustomerCnt": 5,
      "m6CustomerCnt": 50,
      "m6AvgCustomerCnt": 5,
      "q3CustomerCnt": 100,
      "q3AvgCustomerCnt": 10,
      "m7CustomerCnt": 33,
      "m7AvgCustomerCnt": 3.3,
      "m8CustomerCnt": 33,
      "m8AvgCustomerCnt": 3.3,
      "m9CustomerCnt": 34,
      "m9AvgCustomerCnt": 3.4,
      "q4CustomerCnt": 100,
      "q4AvgCustomerCnt": 10,
      "m10CustomerCnt": 33,
      "m10AvgCustomerCnt": 3.3,
      "m11CustomerCnt": 33,
      "m11AvgCustomerCnt": 3.3,
      "m12CustomerCnt": 34,
      "m12AvgCustomerCnt": 3.4
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.3 客户资源投入分析表

查询客户资源投入分析数据。

**基本信息**

| 项目         | 说明                                                              |
| ------------ | ----------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/customerResInvAnalReport`    |
| 请求方式     | `POST`                                                            |
| Content-Type | `application/json`                                                |

**请求参数**

请求体为 JSON，字段如下：

| 参数名       | 类型    | 必填 | 说明                   |
| ------------ | ------- | ---- | ---------------------- |
| `zoneId`     | String  | 否   | 区划 ID                |
| `regionName` | String  | 否   | 大区名称，支持模糊查询 |
| `areaName`   | String  | 否   | 地区名称，支持模糊查询 |
| `monthNo`    | String  | 否   | 月份，格式如202604    |
| `page`       | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/customerResInvAnalReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "monthNo": "202604"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                        | 类型   | 说明                   |
| ----------------------------- | ------ | ---------------------- |
| `regionName`                  | String | 大区名称               |
| `areaName`                    | String | 地区名称               |
| `productName`                 | String | 品种名称               |
| `cmFocusType`                 | String | 月度聚焦客户类型       |
| `monthNo`                     | Number | 月份                   |
| `academicVisitCount`          | Number | 规划学术拜访次数       |
| `academicVisitUserCount`      | Number | 规划学术拜访人数       |
| `academicVisitFreq`           | Number | 规划学术拜访频率       |
| `actualVisitCnt`              | Number | 执行学术拜访次数       |
| `actualVisitUserCnt`          | Number | 执行学术拜访人数       |
| `actualVisitFreq`             | Number | 执行学术拜访频率       |
| `academicVisitAmount`         | Number | 规划学术拜访金额       |
| `academicVisitAmountRate`     | String | 规划学术拜访金额占比   |
| `academicVisitActualAmount`   | Number | 实际学术拜访金额       |
| `academicVisitActualAmountRate`| String | 实际学术拜访金额占比   |
| `academicLinkCount`           | Number | 规划学术链接次数       |
| `academicLinkUserCount`       | Number | 规划学术链接人数       |
| `academicLinkFreq`            | Number | 规划学术链接频率       |
| `actualLinkCnt`               | Number | 执行学术链接次数       |
| `actualLinkUserCnt`           | Number | 执行学术链接人数       |
| `actualLinkFreq`              | Number | 执行学术链接频率       |
| `academicLinkAmount`          | Number | 规划学术链接金额       |
| `academicLinkAmountRate`      | String | 规划学术链接金额占比   |
| `academicLinkActualAmount`    | Number | 实际学术链接金额       |
| `academicLinkActualAmountRate`| String | 实际学术链接金额占比   |
| `academicMeetingCount`        | Number | 规划学术会议次数       |
| `academicMeetingUserCount`    | Number | 规划学术会议人数       |
| `academicMeetingFreq`         | Number | 规划学术会议频率       |
| `actualMeetingCnt`            | Number | 执行学术会议次数       |
| `actualMeetingUserCnt`        | Number | 执行学术会议人数       |
| `actualMeetingFreq`           | Number | 执行学术会议频率       |
| `academicMeetingAmount`       | Number | 规划学术会议金额       |
| `academicMeetingAmountRate`   | String | 规划学术会议金额占比   |
| `academicMeetingActualAmount` | Number | 实际学术会议金额       |
| `academicMeetingActualAmountRate`| String | 实际学术会议金额占比   |
| `meetingSupportCount`         | Number | 规划会议支持次数       |
| `meetingSupportUserCount`     | Number | 规划会议支持人数       |
| `meetingSupportFreq`          | Number | 规划会议支持频率       |
| `actualSupportCnt`            | Number | 执行会议支持次数       |
| `actualSupportUserCnt`        | Number | 执行会议支持人数       |
| `actualSupportFreq`           | Number | 执行会议支持频率       |
| `meetingSupportAmount`        | Number | 规划会议支持金额       |
| `meetingSupportAmountRate`    | Number | 规划会议支持金额占比   |
| `meetingSupportActualAmount`  | Number | 实际会议支持金额       |
| `meetingSupportActualAmountRate`| String | 实际会议支持金额占比   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "productName": "益路取",
      "cmFocusType": "核心客户",
      "monthNo": "202604",
      "academicVisitCount": 100,
      "academicVisitUserCount": 50,
      "academicVisitFreq": 2.0,
      "actualVisitCnt": 80,
      "actualVisitUserCnt": 40,
      "actualVisitFreq": 2.0,
      "academicVisitAmount": 5000,
      "academicVisitAmountRate": "25.0%",
      "academicVisitActualAmount": 4000,
      "academicVisitActualAmountRate": "20.0%",
      "academicLinkCount": 50,
      "academicLinkUserCount": 30,
      "academicLinkFreq": 1.67,
      "actualLinkCnt": 40,
      "actualLinkUserCnt": 25,
      "actualLinkFreq": 1.6,
      "academicLinkAmount": 3000,
      "academicLinkAmountRate": "15.0%",
      "academicLinkActualAmount": 2500,
      "academicLinkActualAmountRate": "12.5%",
      "academicMeetingCount": 10,
      "academicMeetingUserCount": 100,
      "academicMeetingFreq": 0.1,
      "actualMeetingCnt": 8,
      "actualMeetingUserCnt": 80,
      "actualMeetingFreq": 0.1,
      "academicMeetingAmount": 10000,
      "academicMeetingAmountRate": "50.0%",
      "academicMeetingActualAmount": 8000,
      "academicMeetingActualAmountRate": "40.0%",
      "meetingSupportCount": 5,
      "meetingSupportUserCount": 50,
      "meetingSupportFreq": 0.1,
      "actualSupportCnt": 4,
      "actualSupportUserCnt": 40,
      "actualSupportFreq": 0.1,
      "meetingSupportAmount": 2000,
      "meetingSupportAmountRate": 10,
      "meetingSupportActualAmount": 1600,
      "meetingSupportActualAmountRate": "8.0%"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.4 客户已规划未触碰明细表

查询客户已规划但未触碰的明细数据。

**基本信息**

| 项目         | 说明                                                                |
| ------------ | ------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/customerIsPlannedNotVisited`   |
| 请求方式     | `POST`                                                              |
| Content-Type | `application/json`                                                  |

**请求参数**

请求体为 JSON，字段如下：

| 参数名         | 类型    | 必填 | 说明                   |
| -------------- | ------- | ---- | ---------------------- |
| `zoneId`       | String  | 否   | 区划 ID                |
| `regionName`   | String  | 否   | 大区名称，支持模糊查询 |
| `areaName`     | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName`| String  | 否   | 辖区名称，支持模糊查询 |
| `monthNo`      | String  | 否   | 月份，格式如202604    |
| `page`         | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/customerIsPlannedNotVisited' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "monthNo": "202604"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名           | 类型   | 说明                           |
| ---------------- | ------ | ------------------------------ |
| `regionName`     | String | 大区名称                       |
| `areaName`       | String | 地区名称                       |
| `territoryName`  | String | 辖区名称                       |
| `productName`    | String | 产品名称                       |
| `monthNo`        | Number | 月份                           |
| `cmFocusType`    | String | 月度聚焦客户类型               |
| `hcoName`        | String | 医院名称                       |
| `hcpName`        | String | 客户名称                       |
| `academicVisit`  | String | 学术拜访是否已规划但未触碰     |
| `academicLink`   | String | 学术链接是否已规划但未触碰     |
| `academicMeeting`| String | 学术会议是否已规划但未触碰     |
| `academicSupport`| String | 会议支持是否已规划但未触碰     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "territoryName": "上海辖区A",
      "productName": "益路取",
      "monthNo": "202604",
      "cmFocusType": "核心客户",
      "hcoName": "上海第一人民医院",
      "hcpName": "李医生",
      "academicVisit": "是",
      "academicLink": "否",
      "academicMeeting": "是",
      "academicSupport": "否"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.5 客户管理区划执行分析表

查询客户管理区划执行分析数据。

> **注意**：此接口为大数据报表接口（isBigData=1），数据来源于大数据平台。

**基本信息**

| 项目         | 说明                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/customerZonePerformanceExecAnalysisReport` |
| 请求方式     | `POST`                                                                       |
| Content-Type | `application/json`                                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名         | 类型    | 必填 | 说明                   |
| -------------- | ------- | ---- | ---------------------- |
| `zoneId`       | String  | 否   | 区划 ID                |
| `regionName`   | String  | 否   | 大区名称，支持模糊查询 |
| `areaName`     | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName`| String  | 否   | 辖区名称，支持模糊查询 |
| `monthNo`      | String  | 否   | 月份，格式如202604    |
| `page`         | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/customerZonePerformanceExecAnalysisReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "monthNo": "202604"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名       | 类型   | 说明               |
| ------------ | ------ | ------------------ |
| `regionName` | String | 大区名称           |
| `areaName`   | String | 地区名称           |
| `territoryName`| String | 辖区名称         |
| `managerName`| String | 负责人             |
| `monthNo`    | Number | 月份               |
| `shouldReport`| Number | 代表应汇报数     |
| `hasReported` | Number | 代表已汇报数     |
| `reportedRate`| String | 代表汇报率       |
| `receiveCnt` | Number | 地区经理接收数     |
| `lookCnt`    | Number | 地区经理查看数     |
| `lookRate`   | String | 地区经理查看率     |
| `replyCnt`   | Number | 地区经理回复数     |
| `replyRate`  | String | 地区经理回复率     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "territoryName": "上海辖区A",
      "managerName": "张三",
      "monthNo": "202604",
      "shouldReport": 100,
      "hasReported": 85,
      "reportedRate": "85.0%",
      "receiveCnt": 85,
      "lookCnt": 80,
      "lookRate": "94.1%",
      "replyCnt": 70,
      "replyRate": "82.4%"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

### 4.2 益路取&芦可替尼日报相关接口

---

#### 4.2.1 益路取&芦可替尼地区经理日报

查询益路取&芦可替尼地区经理日报数据。

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

| 字段名                                    | 类型   | 说明                     |
| ----------------------------------------- | ------ | ------------------------ |
| `regionName`                              | String | 大区                     |
| `areaName`                                | String | 地区                     |
| `date`                                    | String | 日期                     |
| `ilumertiNPCount`                         | Number | 益路取NP人数             |
| `ilumertiPrescriptionCount`               | Number | 益路取处方支数           |
| `ruxolitinibNewPatientReservesProCount`   | Number | 芦可替尼PRO拉新人数      |
| `ruxolitinibNewPatientReservesWeComCount` | Number | 芦可替尼企微拉新人数     |
| `ruxolitinibNewPatientReservesTotal`      | Number | 芦可替尼新增患者储备总数 |
| `ruxolitinibNPCount`                      | Number | 芦可替尼NP人数           |
| `ruxolitinibOnlinePrescriptionCount`      | Number | 芦可替尼线上处方支数     |
| `ruxolitinibOfflinePrescriptionCount`     | Number | 芦可替尼线下处方支数     |
| `ruxolitinibPrescriptionTotal`            | Number | 芦可替尼处方总数         |

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
      "ilumertiNPCount": 15,
      "ilumertiPrescriptionCount": 30,
      "ruxolitinibNewPatientReservesProCount": 10,
      "ruxolitinibNewPatientReservesWeComCount": 8,
      "ruxolitinibNewPatientReservesTotal": 18,
      "ruxolitinibNPCount": 12,
      "ruxolitinibOnlinePrescriptionCount": 20,
      "ruxolitinibOfflinePrescriptionCount": 12,
      "ruxolitinibPrescriptionTotal": 32
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.2.2 益路取&芦可替尼日报按大区统计

查询益路取&芦可替尼日报按大区统计数据。

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

| 字段名                                    | 类型   | 说明                     |
| ----------------------------------------- | ------ | ------------------------ |
| `regionName`                              | String | 大区                     |
| `date`                                    | String | 日期                     |
| `ilumertiNPCount`                         | Number | 益路取NP人数             |
| `ilumertiPrescriptionCount`               | Number | 益路取处方支数           |
| `ruxolitinibNewPatientReservesProCount`   | Number | 芦可替尼PRO拉新人数      |
| `ruxolitinibNewPatientReservesWeComCount` | Number | 芦可替尼企微拉新人数     |
| `ruxolitinibNewPatientReservesTotal`      | Number | 芦可替尼新增患者储备总数 |
| `ruxolitinibNPCount`                      | Number | 芦可替尼NP人数           |
| `ruxolitinibOnlinePrescriptionCount`      | Number | 芦可替尼线上处方支数     |
| `ruxolitinibOfflinePrescriptionCount`     | Number | 芦可替尼线下处方支数     |
| `ruxolitinibPrescriptionTotal`            | Number | 芦可替尼处方总数         |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "date": "2025-01-15",
      "ilumertiNPCount": 15,
      "ilumertiPrescriptionCount": 30,
      "ruxolitinibNewPatientReservesProCount": 10,
      "ruxolitinibNewPatientReservesWeComCount": 8,
      "ruxolitinibNewPatientReservesTotal": 18,
      "ruxolitinibNPCount": 12,
      "ruxolitinibOnlinePrescriptionCount": 20,
      "ruxolitinibOfflinePrescriptionCount": 12,
      "ruxolitinibPrescriptionTotal": 32
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.2.3 益路取&芦可替尼日报执行日统计

查询益路取&芦可替尼日报按执行日的统计数据，包含全国及各大区的任务提交情况。

> **注意**：此接口无请求参数，直接返回所有执行日的统计数据。

**基本信息**

| 项目         | 说明                                                                           |
| ------------ | ------------------------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionDailyStats`      |
| 请求方式     | `POST`                                                                         |
| Content-Type | `application/json`                                                             |

**请求参数**

此接口无请求参数，请求体为空 JSON 对象 `{}`。

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionDailyStats' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                  | 类型   | 说明               |
| ----------------------- | ------ | ------------------ |
| `date`                  | String | 日期               |
| `nationalTotal`         | Number | 全国任务总数       |
| `nationalPending`       | Number | 全国待处理         |
| `nationalSubmitted`     | Number | 全国已提交         |
| `nationalSubmissionRate`| String | 全国任务提交率     |
| `northeastTotal`        | Number | 东北大区任务总数   |
| `northeastPending`      | Number | 东北大区待处理     |
| `northeastSubmitted`    | Number | 东北大区已提交     |
| `northeastSubmissionRate`| String | 东北大区任务提交率 |
| `eastChinaTotal`        | Number | 华东大区任务总数   |
| `eastChinaPending`      | Number | 华东大区待处理     |
| `eastChinaSubmitted`    | Number | 华东大区已提交     |
| `eastChinaSubmissionRate`| String | 华东大区任务提交率 |
| `shanghaiTotal`         | Number | 上海大区任务总数   |
| `shanghaiPending`       | Number | 上海大区待处理     |
| `shanghaiSubmitted`     | Number | 上海大区已提交     |
| `shanghaiSubmissionRate`| String | 上海大区任务提交率 |
| `southeastTotal`        | Number | 东南大区任务总数   |
| `southeastPending`      | Number | 东南大区待处理     |
| `southeastSubmitted`    | Number | 东南大区已提交     |
| `southeastSubmissionRate`| String | 东南大区任务提交率 |
| `centralChinaTotal`     | Number | 华中大区任务总数   |
| `centralChinaPending`   | Number | 华中大区待处理     |
| `centralChinaSubmitted` | Number | 华中大区已提交     |
| `centralChinaSubmissionRate`| String | 华中大区任务提交率 |
| `southwestTotal`        | Number | 西南大区任务总数   |
| `southwestPending`      | Number | 西南大区待处理     |
| `southwestSubmitted`    | Number | 西南大区已提交     |
| `southwestSubmissionRate`| String | 西南大区任务提交率 |
| `northwestTotal`        | Number | 西北地区任务总数   |
| `northwestPending`      | Number | 西北地区待处理     |
| `northwestSubmitted`    | Number | 西北地区已提交     |
| `northwestSubmissionRate`| String | 西北地区任务提交率 |
| `beijingTotal`          | Number | 北京大区任务总数   |
| `beijingPending`        | Number | 北京大区待处理     |
| `beijingSubmitted`      | Number | 北京大区已提交     |
| `beijingSubmissionRate` | String | 北京大区任务提交率 |
| `southChinaTotal`       | Number | 华南大区任务总数   |
| `southChinaPending`     | Number | 华南大区待处理     |
| `southChinaSubmitted`   | Number | 华南大区已提交     |
| `southChinaSubmissionRate`| String | 华南大区任务提交率 |
| `hebeiTotal`            | Number | 河北区域任务总数   |
| `hebeiPending`          | Number | 河北区域待处理     |
| `hebeiSubmitted`        | Number | 河北区域已提交     |
| `hebeiSubmissionRate`   | String | 河北区域任务提交率 |
| `hunanTotal`            | Number | 湖南大区任务总数   |
| `hunanPending`          | Number | 湖南大区待处理     |
| `hunanSubmitted`        | Number | 湖南大区已提交     |
| `hunanSubmissionRate`   | String | 湖南大区任务提交率 |
| `hubeiTotal`            | Number | 湖北大区任务总数   |
| `hubeiPending`          | Number | 湖北大区待处理     |
| `hubeiSubmitted`        | Number | 湖北大区已提交     |
| `hubeiSubmissionRate`   | String | 湖北大区任务提交率 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "date": "2026-05-10",
      "nationalTotal": 150,
      "nationalPending": 20,
      "nationalSubmitted": 130,
      "nationalSubmissionRate": "86.7%",
      "northeastTotal": 15,
      "northeastPending": 2,
      "northeastSubmitted": 13,
      "northeastSubmissionRate": "86.7%",
      "eastChinaTotal": 30,
      "eastChinaPending": 5,
      "eastChinaSubmitted": 25,
      "eastChinaSubmissionRate": "83.3%",
      "shanghaiTotal": 20,
      "shanghaiPending": 3,
      "shanghaiSubmitted": 17,
      "shanghaiSubmissionRate": "85.0%",
      "southeastTotal": 25,
      "southeastPending": 2,
      "southeastSubmitted": 23,
      "southeastSubmissionRate": "92.0%",
      "centralChinaTotal": 20,
      "centralChinaPending": 3,
      "centralChinaSubmitted": 17,
      "centralChinaSubmissionRate": "85.0%",
      "southwestTotal": 15,
      "southwestPending": 2,
      "southwestSubmitted": 13,
      "southwestSubmissionRate": "86.7%",
      "northwestTotal": 10,
      "northwestPending": 1,
      "northwestSubmitted": 9,
      "northwestSubmissionRate": "90.0%",
      "beijingTotal": 15,
      "beijingPending": 2,
      "beijingSubmitted": 13,
      "beijingSubmissionRate": "86.7%",
      "southChinaTotal": 15,
      "southChinaPending": 1,
      "southChinaSubmitted": 14,
      "southChinaSubmissionRate": "93.3%",
      "hebeiTotal": 5,
      "hebeiPending": 0,
      "hebeiSubmitted": 5,
      "hebeiSubmissionRate": "100.0%",
      "hunanTotal": 8,
      "hunanPending": 1,
      "hunanSubmitted": 7,
      "hunanSubmissionRate": "87.5%",
      "hubeiTotal": 7,
      "hubeiPending": 1,
      "hubeiSubmitted": 6,
      "hubeiSubmissionRate": "85.7%"
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

4. **大数据报表**：标识为大数据报表的接口（如 `customerZonePerformanceExecAnalysisReport`），数据来源于大数据平台，可能存在数据延迟。

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