# SFE系统维盛专属 Open API 接口文档

## 修订记录

| 版本 | 日期       | 修订内容                   | 修订人 |
| ---- | ---------- | -------------------------- | ------ |
| V1.0 | 2026-03-29 | 初始版本，开放维盛专属接口 | 王馗   |
| V1.1 | 2026-03-31 | 查询参数增加品种名称、医院名称、医生姓名 | 王馗   |

---

## 一、概述

本文档描述了 **SFE系统维盛专属接口**，主要针对特定客户的定制化业务场景提供专用API接口。

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
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-ws-report/{接口地址}/count' \
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

（待补充，根据维盛专属接口的业务场景填写）

---

## 四、接口详细说明

### 4.1 客户管理年度跟踪表

查询客户管理年度跟踪数据，包括年度目标、季度规划、周计划、周执行、月销量等信息。

**基本信息**

| 项目         | 说明                                                                |
| ------------ | ------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-ws-report/hcpManageYearlyTrackingReport` |
| 请求方式     | POST                                                                |
| Content-Type | application/json                                                    |

**请求参数**

| 参数名          | 类型   | 必填 | 说明                   |
| --------------- | ------ | ---- | ---------------------- |
| `zoneId`        | String | 否   | 区划ID                 |
| `regionName`    | String | 否   | 大区名称，支持模糊查询 |
| `areaName`      | String | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String | 否   | 辖区名称，支持模糊查询 |
| `productName`   | String | 否   | 品种名称，支持模糊查询 |
| `hcoName`       | String | 否   | 医院名称，支持模糊查询 |
| `hcpName`       | String | 否   | 医生姓名，支持模糊查询 |
| `year`          | Number | 否   | 年度                   |
| `quarter`       | Number | 否   | 季度                   |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-ws-report/hcpManageYearlyTrackingReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "zoneId": "zone123",
    "year": 2026,
    "quarter": 1
  }'
```

**响应参数**

`data` 为数组，数组元素包含以下字段：

| 参数名                                       | 类型   | 说明                   |
| -------------------------------------------- | ------ | ---------------------- |
| `id`                                         | String | ID                     |
| `year`                                       | Number | 年度                   |
| `sourceType`                                 | String | 来源标签               |
| `regionName`                                 | String | 大区名称               |
| `areaName`                                   | String | 地区名称               |
| `territoryName`                              | String | 岗位名称               |
| `positionType`                               | String | 岗位类型               |
| `managerName`                                | String | 管理人                 |
| `productName`                                | String | 品种名称               |
| `hcoId`                                      | String | 医院ID                 |
| `hcoName`                                    | String | 医院名称               |
| `hcoCpId`                                    | String | 医院云平台ID           |
| `hcpId`                                      | String | 医生ID                 |
| `hcpName`                                    | String | 医生名称               |
| `hcpCpId`                                    | String | 医生云平台ID           |
| `deptName`                                   | String | 医生科室               |
| `subspecialityName`                          | String | 亚专科标签名称         |
| `isAdministrativeCustomer`                   | String | 是否是行政客户         |
| `lyRoleCount`                                | Number | 去年角色次数           |
| `lyTargetLectureCount`                       | Number | 去年讲课次数           |
| `cyKeyHospitalFlag`                          | String | 重点医院标记           |
| `lyMonthlyAverage`                           | Number | 去年月均量             |
| `lyProductAwareness`                         | String | 去年产品认知度         |
| `cyMonthlyPotential`                         | Number | 今年月潜力量           |
| `cyPotentialProductAwareness`                | String | 今年潜力产品认知度     |
| `cyTargetMonthlyAverage`                     | Number | 今年目标月均量         |
| `cyTargetProductAwareness`                   | String | 今年目标产品认知度     |
| `cyRoleCount`                                | Number | 今年角色次数           |
| `cyTargetLectureCount`                       | Number | 今年目标讲课次数       |
| `cyFocusType`                                | String | 年度聚焦类型           |
| `cyQ1MonthlyAverageTarget`                   | Number | 今年Q1季度月均量       |
| `cyQ2MonthlyAverageTarget`                   | Number | 今年Q2季度月均量       |
| `cyQ3MonthlyAverageTarget`                   | Number | 今年Q3季度月均量       |
| `cyQ4MonthlyAverageTarget`                   | Number | 今年Q4季度月均量       |
| `cyAnnualTotalTarget`                        | Number | 年度总目标量           |
| `cyQ1ExpenseInvestment`                      | Number | 今年Q1季度费用投入     |
| `cyQ2ExpenseInvestment`                      | Number | 今年Q2季度费用投入     |
| `cyQ3ExpenseInvestment`                      | Number | 今年Q3季度费用投入     |
| `cyQ4ExpenseInvestment`                      | Number | 今年Q4季度费用投入     |
| `cyEstimatedAnnualExpensePerBox`             | Number | 年度预计单盒费用       |
| `cyEstimatedAnnualTotalExpense`              | Number | 预估年度总费用         |
| `cyEstimatedAnnualAcademicConferenceExpense` | Number | 预估年度学术会议费用   |
| `cyEstimatedAnnualAcademicLinkExpense`       | Number | 预估年度学术链接费用   |
| `quarter`                                    | String | 季度                   |
| `lqMonthlyAverage`                           | Number | 上季度月均完成量       |
| `lqProductAwareness`                         | String | 上季度产品认知度       |
| `cqTargetMonthlyAverage`                     | Number | 本季度月均目标量       |
| `cqTargetProductAwareness`                   | String | 本季度目标产品认知度   |
| `cqHcoWorkTarget`                            | String | 本季度医院工作目标     |
| `cqFocusType`                                | String | 本季度聚焦类型         |
| `cqRoleCount`                                | Number | 本季度规划学术会议次数 |
| `cqTargetLectureCount`                       | Number | 本季度规划讲课次数     |
| `cqAcademicLinkCount`                        | String | 本季度规划关系营销次数 |
| `cqAcademicLinkExpense`                      | Number | 本季度关系营销费用     |
| `cqAcademicConferenceExpense`                | Number | 本季度学术营销费用     |
| `cqActualRoleCount`                          | Number | 本季度已覆盖角色次数   |
| `cqActualLectureCount`                       | Number | 本季度已覆盖讲课次数   |
| `w1PlanContent`                              | String | W1周计划               |
| `w2PlanContent`                              | String | W2周计划               |
| `w3PlanContent`                              | String | W3周计划               |
| `w4PlanContent`                              | String | W4周计划               |
| `w5PlanContent`                              | String | W5周计划               |
| `w6PlanContent`                              | String | W6周计划               |
| `w7PlanContent`                              | String | W7周计划               |
| `w8PlanContent`                              | String | W8周计划               |
| `w9PlanContent`                              | String | W9周计划               |
| `w10PlanContent`                             | String | W10周计划              |
| `w11PlanContent`                             | String | W11周计划              |
| `w12PlanContent`                             | String | W12周计划              |
| `w13PlanContent`                             | String | W13周计划              |
| `w14PlanContent`                             | String | W14周计划              |
| `w1VisitCnt`                                 | Number | W1执行拜访次数         |
| `w2VisitCnt`                                 | Number | W2执行拜访次数         |
| `w3VisitCnt`                                 | Number | W3执行拜访次数         |
| `w4VisitCnt`                                 | Number | W4执行拜访次数         |
| `w5VisitCnt`                                 | Number | W5执行拜访次数         |
| `w6VisitCnt`                                 | Number | W6执行拜访次数         |
| `w7VisitCnt`                                 | Number | W7执行拜访次数         |
| `w8VisitCnt`                                 | Number | W8执行拜访次数         |
| `w9VisitCnt`                                 | Number | W9执行拜访次数         |
| `w10VisitCnt`                                | Number | W10执行拜访次数        |
| `w11VisitCnt`                                | Number | W11执行拜访次数        |
| `w12VisitCnt`                                | Number | W12执行拜访次数        |
| `w13VisitCnt`                                | Number | W13执行拜访次数        |
| `w14VisitCnt`                                | Number | W14执行拜访次数        |
| `w1LinkCnt`                                  | Number | W1执行学术连接次数     |
| `w2LinkCnt`                                  | Number | W2执行学术连接次数     |
| `w3LinkCnt`                                  | Number | W3执行学术连接次数     |
| `w4LinkCnt`                                  | Number | W4执行学术连接次数     |
| `w5LinkCnt`                                  | Number | W5执行学术连接次数     |
| `w6LinkCnt`                                  | Number | W6执行学术连接次数     |
| `w7LinkCnt`                                  | Number | W7执行学术连接次数     |
| `w8LinkCnt`                                  | Number | W8执行学术连接次数     |
| `w9LinkCnt`                                  | Number | W9执行学术连接次数     |
| `w10LinkCnt`                                 | Number | W10执行学术连接次数    |
| `w11LinkCnt`                                 | Number | W11执行学术连接次数    |
| `w12LinkCnt`                                 | Number | W12执行学术连接次数    |
| `w13LinkCnt`                                 | Number | W13执行学术连接次数    |
| `w14LinkCnt`                                 | Number | W14执行学术连接次数    |
| `w1MeetingCnt`                               | Number | W1执行学术会议次数     |
| `w2MeetingCnt`                               | Number | W2执行学术会议次数     |
| `w3MeetingCnt`                               | Number | W3执行学术会议次数     |
| `w4MeetingCnt`                               | Number | W4执行学术会议次数     |
| `w5MeetingCnt`                               | Number | W5执行学术会议次数     |
| `w6MeetingCnt`                               | Number | W6执行学术会议次数     |
| `w7MeetingCnt`                               | Number | W7执行学术会议次数     |
| `w8MeetingCnt`                               | Number | W8执行学术会议次数     |
| `w9MeetingCnt`                               | Number | W9执行学术会议次数     |
| `w10MeetingCnt`                              | Number | W10执行学术会议次数    |
| `w11MeetingCnt`                              | Number | W11执行学术会议次数    |
| `w12MeetingCnt`                              | Number | W12执行学术会议次数    |
| `w13MeetingCnt`                              | Number | W13执行学术会议次数    |
| `w14MeetingCnt`                              | Number | W14执行学术会议次数    |
| `m1SalesVolume`                              | Number | 当季度第1月销量        |
| `m2SalesVolume`                              | Number | 当季度第2月销量        |
| `m3SalesVolume`                              | Number | 当季度第3月销量        |
| `avgSalesVolume`                             | Number | 季度月均量             |
| `isCultivationSuccessful`                    | String | 是否培养成功           |
| `cqExpense`                                  | Number | 季度花费               |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": "12345",
      "year": 2026,
      "sourceType": "系统导入",
      "regionName": "华东大区",
      "areaName": "上海地区",
      "territoryName": "上海代表岗位",
      "positionType": "专岗",
      "managerName": "张三",
      "productName": "产品A",
      "hcoId": "hco001",
      "hcoName": "上海市第一人民医院",
      "hcoCpId": "cp_hco001",
      "hcpId": "hcp001",
      "hcpName": "李医生",
      "hcpCpId": "cp_hcp001",
      "deptName": "内科",
      "subspecialityName": "心血管",
      "isAdministrativeCustomer": "是",
      "lyRoleCount": 10,
      "lyTargetLectureCount": 5,
      "cyKeyHospitalFlag": "重点",
      "lyMonthlyAverage": 100,
      "lyProductAwareness": "高",
      "cyMonthlyPotential": 150,
      "cyPotentialProductAwareness": "中",
      "cyTargetMonthlyAverage": 120,
      "cyTargetProductAwareness": "高",
      "cyRoleCount": 12,
      "cyTargetLectureCount": 6,
      "cyFocusType": "核心客户",
      "cyQ1MonthlyAverageTarget": 30,
      "cyQ2MonthlyAverageTarget": 35,
      "cyQ3MonthlyAverageTarget": 40,
      "cyQ4MonthlyAverageTarget": 45,
      "cyAnnualTotalTarget": 1500,
      "cyQ1ExpenseInvestment": 5000,
      "cyQ2ExpenseInvestment": 6000,
      "cyQ3ExpenseInvestment": 7000,
      "cyQ4ExpenseInvestment": 8000,
      "cyEstimatedAnnualExpensePerBox": 10,
      "cyEstimatedAnnualTotalExpense": 15000,
      "cyEstimatedAnnualAcademicConferenceExpense": 10000,
      "cyEstimatedAnnualAcademicLinkExpense": 5000,
      "quarter": "Q1",
      "lqMonthlyAverage": 90,
      "lqProductAwareness": "中",
      "cqTargetMonthlyAverage": 30,
      "cqTargetProductAwareness": "高",
      "cqHcoWorkTarget": "提升学术影响力",
      "cqFocusType": "核心客户",
      "cqRoleCount": 3,
      "cqTargetLectureCount": 2,
      "cqAcademicLinkCount": "5",
      "cqAcademicLinkExpense": 2000,
      "cqAcademicConferenceExpense": 3000,
      "cqActualRoleCount": 1,
      "cqActualLectureCount": 1,
      "w1PlanContent": "拜访计划",
      "w2PlanContent": "学术会议",
      "w3PlanContent": null,
      "w4PlanContent": null,
      "w5PlanContent": null,
      "w6PlanContent": null,
      "w7PlanContent": null,
      "w8PlanContent": null,
      "w9PlanContent": null,
      "w10PlanContent": null,
      "w11PlanContent": null,
      "w12PlanContent": null,
      "w13PlanContent": null,
      "w14PlanContent": null,
      "w1VisitCnt": 5,
      "w2VisitCnt": 3,
      "w3VisitCnt": 0,
      "w4VisitCnt": 0,
      "w5VisitCnt": 0,
      "w6VisitCnt": 0,
      "w7VisitCnt": 0,
      "w8VisitCnt": 0,
      "w9VisitCnt": 0,
      "w10VisitCnt": 0,
      "w11VisitCnt": 0,
      "w12VisitCnt": 0,
      "w13VisitCnt": 0,
      "w14VisitCnt": 0,
      "w1LinkCnt": 1,
      "w2LinkCnt": 0,
      "w3LinkCnt": 0,
      "w4LinkCnt": 0,
      "w5LinkCnt": 0,
      "w6LinkCnt": 0,
      "w7LinkCnt": 0,
      "w8LinkCnt": 0,
      "w9LinkCnt": 0,
      "w10LinkCnt": 0,
      "w11LinkCnt": 0,
      "w12LinkCnt": 0,
      "w13LinkCnt": 0,
      "w14LinkCnt": 0,
      "w1MeetingCnt": 0,
      "w2MeetingCnt": 1,
      "w3MeetingCnt": 0,
      "w4MeetingCnt": 0,
      "w5MeetingCnt": 0,
      "w6MeetingCnt": 0,
      "w7MeetingCnt": 0,
      "w8MeetingCnt": 0,
      "w9MeetingCnt": 0,
      "w10MeetingCnt": 0,
      "w11MeetingCnt": 0,
      "w12MeetingCnt": 0,
      "w13MeetingCnt": 0,
      "w14MeetingCnt": 0,
      "m1SalesVolume": 100,
      "m2SalesVolume": 120,
      "m3SalesVolume": 150,
      "avgSalesVolume": 123.33,
      "isCultivationSuccessful": "是",
      "cqExpense": 5000
    }
  ],
  "timestamp": 1774252310993,
  "success": true
}
```

### 4.2 医院管理年度跟踪表

查询医院管理年度跟踪数据，包括年度目标、季度流向、月流向、周流向、执行情况等信息。

**基本信息**

| 项目         | 说明                                                                |
| ------------ | ------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-ws-report/hcoManageYearlyTrackingReport` |
| 请求方式     | POST                                                                |
| Content-Type | application/json                                                    |

**请求参数**

| 参数名          | 类型   | 必填 | 说明                   |
| --------------- | ------ | ---- | ---------------------- |
| `zoneId`        | String | 否   | 区划ID                 |
| `regionName`    | String | 否   | 大区名称，支持模糊查询 |
| `areaName`      | String | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String | 否   | 辖区名称，支持模糊查询 |
| `productName`   | String | 否   | 品种名称，支持模糊查询 |
| `hcoName`       | String | 否   | 医院名称，支持模糊查询 |
| `year`          | String | 否   | 年度                   |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-ws-report/hcoManageYearlyTrackingReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "zoneId": "zone123",
    "year": "2026"
  }'
```

**响应参数**

`data` 为数组，数组元素包含以下字段：

| 参数名                     | 类型   | 说明                                       |
| -------------------------- | ------ | ------------------------------------------ |
| `id`                       | String | ID                                         |
| `year`                     | Number | 年                                         |
| `region`                   | String | 大区名称                                   |
| `area`                     | String | 地区名称                                   |
| `territory`                | String | 岗位名称                                   |
| `positionType`             | String | 岗位类型                                   |
| `jobState`                 | String | 在职状态                                   |
| `managerName`              | String | 负责人名称                                 |
| `hcoCpId`                  | String | 医院云平台ID                               |
| `productName`              | String | 产品名称                                   |
| `hcoName`                  | String | 医院名称                                   |
| `hcoCollectionType`        | String | 集合类别                                   |
| `hcoNatureType`            | String | 医院性质                                   |
| `hcoGradeType`             | String | 医院级别                                   |
| `hqName`                   | String | 集团归属                                   |
| `hcoManageType`            | String | 医院类别                                   |
| `cyHcoWorkTarget`          | String | 年度医院工作目标                           |
| `cyYearlyM3Amount`         | String | 年度M3目标量                               |
| `blyCompleted`             | Number | 前年完成                                   |
| `lyCompleted`              | Number | 去年完成                                   |
| `lyYoy`                    | Number | 去年同比                                   |
| `lyQ1Flow`                 | Number | 去年Q1流向                                 |
| `lyQ2Flow`                 | Number | 去年Q2流向                                 |
| `lyQ3Flow`                 | Number | 去年Q3流向                                 |
| `lyQ4Flow`                 | Number | 去年Q4流向                                 |
| `cyM2Task`                 | Number | 今年M2任务                                 |
| `cyFlow`                   | Number | 今年流向                                   |
| `m01Flow`                  | Number | 今年1月流向                                |
| `m02Flow`                  | Number | 今年2月流向                                |
| `m03Flow`                  | Number | 今年3月流向                                |
| `q1Flow`                   | Number | 今年1季度流向                              |
| `q1Yoy`                    | Number | 今年1季度流向同比                          |
| `q1Mom`                    | Number | 今年1季度流向环比                          |
| `q1M2Progress`             | Number | 今年1季度M2进度                            |
| `m04Flow`                  | Number | 今年4月流向                                |
| `m05Flow`                  | Number | 今年5月流向                                |
| `m06Flow`                  | Number | 今年6月流向                                |
| `q2Flow`                   | Number | 今年2季度流向                              |
| `q2Yoy`                    | Number | 今年2季度流向同比                          |
| `q2Mom`                    | Number | 今年2季度流向环比                          |
| `q2M2Progress`             | Number | 今年2季度M2进度                            |
| `h1Flow`                   | Number | 今年上半年流向                             |
| `h1Yoy`                    | Number | 今年上半年流向同比                         |
| `h1M2Progress`             | Number | 今年上半年M2进度                           |
| `m07Flow`                  | Number | 今年7月流向                                |
| `m08Flow`                  | Number | 今年8月流向                                |
| `m09Flow`                  | Number | 今年9月流向                                |
| `q3Flow`                   | Number | 今年3季度流向                              |
| `q3Yoy`                    | Number | 今年3季度流向同比                          |
| `q3Mom`                    | Number | 今年3季度流向环比                          |
| `q3M2Progress`             | Number | 今年3季度M2进度                            |
| `m10Flow`                  | Number | 今年10月流向                               |
| `m11Flow`                  | Number | 今年11月流向                               |
| `m12Flow`                  | Number | 今年12月流向                               |
| `q4Flow`                   | Number | 今年4季度流向                              |
| `q4Yoy`                    | Number | 今年4季度流向同比                          |
| `q4Mom`                    | Number | 今年4季度流向环比                          |
| `q4M2Progress`             | Number | 今年4季度M2进度                            |
| `h2Flow`                   | Number | 今年下半年流向                             |
| `h2Yoy`                    | Number | 今年下半年流向同比                         |
| `h2M2Progress`             | Number | 今年下半年M2进度                           |
| `cyYtdCompleted`           | Number | 今年YTD完成                                |
| `cyYtdM2Progress`          | Number | 今年YTD完成进度                            |
| `cqTask`                   | Number | 当前季度M2任务                             |
| `cqHcoWorkTarget`          | String | 当前季度医院工作目标                       |
| `cqLockedCustCnt`          | String | 当前季度锁定客户数                         |
| `cqLockedKeyUpgIncCustCnt` | String | 当前季度锁定提级+增量客户数                |
| `cqLockedMntDosageCustCnt` | String | 当前季度锁定维持用量客户数                 |
| `hcoLockedMeetingCnt`      | Number | 当前季度医院锁定客户的季度规划学术会议次数 |
| `hcoLockedMeetingAmt`      | Number | 当前季度医院锁定客户的季度规划学术会议金额 |
| `hcoLockedLinkCnt`         | Number | 当前季度医院锁定客户的季度规划学术链接次数 |
| `hcoLockedLinkAmt`         | Number | 当前季度医院锁定客户的季度规划学术链接金额 |
| `cmW1Flow`                 | Number | 当月第1周流向                              |
| `cmW2Flow`                 | Number | 当月第2周流向                              |
| `cmW3Flow`                 | Number | 当月第3周流向                              |
| `cmW4Flow`                 | Number | 当月第4周流向                              |
| `cmW5Flow`                 | Number | 当月第5周流向                              |
| `cmW6Flow`                 | Number | 当月第6周流向                              |
| `cmFlow`                   | Number | 当月流向代表填报                           |
| `cmFlowSync`               | Number | 当月流向系统带入                           |
| `cmActVisitCnt`            | Number | 当月实际执行学术拜访次数                   |
| `cmActLinkCnt`             | Number | 当月实际执行学术链接次数                   |
| `cmActMeetingCnt`          | Number | 当月实际执行学术会议次数                   |
| `cqActVisitCnt`            | Number | 当前季度实际执行学术拜访次数               |
| `cqActLinkCnt`             | Number | 当前季度实际执行学术链接次数               |
| `cqActMeetingCnt`          | Number | 当前季度实际执行学术会议次数               |
| `monthlyAverageRate`       | Number | 季度锁定客户上季度用量占比                 |
| `cqCost`                   | Number | 当季度费用使用                             |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "id": "12345",
      "year": 2026,
      "region": "华东大区",
      "area": "上海地区",
      "territory": "上海代表岗位",
      "positionType": "专岗",
      "jobState": "在职",
      "managerName": "张三",
      "hcoCpId": "cp_hco001",
      "productName": "产品A",
      "hcoName": "上海市第一人民医院",
      "hcoCollectionType": "核心",
      "hcoNatureType": "公立",
      "hcoGradeType": "三级甲等",
      "hqName": "华东医疗集团",
      "hcoManageType": "综合医院",
      "cyHcoWorkTarget": "提升市场份额",
      "cyYearlyM3Amount": "10000",
      "blyCompleted": 8000,
      "lyCompleted": 9000,
      "lyYoy": 12.5,
      "lyQ1Flow": 2000,
      "lyQ2Flow": 2500,
      "lyQ3Flow": 2200,
      "lyQ4Flow": 2300,
      "cyM2Task": 12000,
      "cyFlow": 5000,
      "m01Flow": 1000,
      "m02Flow": 1200,
      "m03Flow": 1300,
      "q1Flow": 3500,
      "q1Yoy": 15.0,
      "q1Mom": null,
      "q1M2Progress": 29.17,
      "m04Flow": 1100,
      "m05Flow": 1400,
      "m06Flow": 1500,
      "q2Flow": 4000,
      "q2Yoy": 16.0,
      "q2Mom": 14.29,
      "q2M2Progress": 33.33,
      "h1Flow": 7500,
      "h1Yoy": 15.5,
      "h1M2Progress": 62.5,
      "m07Flow": 1200,
      "m08Flow": 1300,
      "m09Flow": 1400,
      "q3Flow": 3900,
      "q3Yoy": 14.0,
      "q3Mom": null,
      "q3M2Progress": 32.5,
      "m10Flow": 1100,
      "m11Flow": 1200,
      "m12Flow": 1300,
      "q4Flow": 3600,
      "q4Yoy": 13.0,
      "q4Mom": null,
      "q4M2Progress": 30.0,
      "h2Flow": 7500,
      "h2Yoy": 13.5,
      "h2M2Progress": 62.5,
      "cyYtdCompleted": 15000,
      "cyYtdM2Progress": 125.0,
      "cqTask": 3000,
      "cqHcoWorkTarget": "稳定用量",
      "cqLockedCustCnt": "5",
      "cqLockedKeyUpgIncCustCnt": "2",
      "cqLockedMntDosageCustCnt": "3",
      "hcoLockedMeetingCnt": 10,
      "hcoLockedMeetingAmt": 50000,
      "hcoLockedLinkCnt": 20,
      "hcoLockedLinkAmt": 30000,
      "cmW1Flow": 300,
      "cmW2Flow": 350,
      "cmW3Flow": 400,
      "cmW4Flow": 450,
      "cmW5Flow": 0,
      "cmW6Flow": 0,
      "cmFlow": 1500,
      "cmFlowSync": 1500,
      "cmActVisitCnt": 50,
      "cmActLinkCnt": 10,
      "cmActMeetingCnt": 5,
      "cqActVisitCnt": 150,
      "cqActLinkCnt": 30,
      "cqActMeetingCnt": 15,
      "monthlyAverageRate": 85.5,
      "cqCost": 80000
    }
  ],
  "timestamp": 1774252310993,
  "success": true
}
```

---

### 4.3 开发管理年度跟踪表

获取开发管理年度跟踪数据，包含医院开发状态、关键客户跟进、周计划执行等信息。

**基本信息**

| 项目         | 说明                                                                |
| ------------ | ------------------------------------------------------------------- |
| 接口地址     | `/bia/open/biz-service/sfe-ws-report/devManageYearlyTrackingReport` |
| 请求方式     | POST                                                                |
| Content-Type | application/json                                                    |

**请求参数**

| 参数名          | 类型   | 必填 | 说明                   |
| --------------- | ------ | ---- | ---------------------- |
| `zoneId`        | String | 否   | 区划ID                 |
| `regionName`    | String | 否   | 大区名称，支持模糊查询 |
| `areaName`      | String | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String | 否   | 辖区名称，支持模糊查询 |
| `productName`   | String | 否   | 品种名称，支持模糊查询 |
| `hcoName`       | String | 否   | 医院名称，支持模糊查询 |
| `year`          | Number | 否   | 年度                   |
| `quarter`       | Number | 否   | 季度                   |

**请求示例**

```bash
curl -X POST "https://api.example.com/bia/open/biz-service/sfe-ws-report/devManageYearlyTrackingReport" \
  -H "Content-Type: application/json" \
  -H "appKey: YOUR_APP_KEY" \
  -d '{
    "zoneId": "zone123",
    "year": 2024,
    "quarter": 1
  }'
```

**响应参数**

`data` 为数组，数组元素包含以下字段：

| 字段名                                      | 类型   | 说明                         |
| ------------------------------------------- | ------ | ---------------------------- |
| `id`                                        | String | ID                           |
| `year`                                      | Number | 年度                         |
| `regionName`                                | String | 大区名称                     |
| `areaName`                                  | String | 地区名称                     |
| `territoryName`                             | String | 岗位名称                     |
| `positionType`                              | String | 岗位类型                     |
| `managerName`                               | String | 负责人                       |
| `productName`                               | String | 品种名称                     |
| `hcoId`                                     | String | 医院ID                       |
| `hcoName`                                   | String | 医院名称                     |
| `hcoCpId`                                   | String | 医院云平台ID                 |
| `outpatientAmount`                          | Number | 门诊量/年                    |
| `operationAmount`                           | Number | 抗VEGF眼底针数/月            |
| `monthlyHcoPotentialAmount`                 | Number | 医院月潜力                   |
| `sourceType`                                | String | 今年开发标记                 |
| `hcoNatureType`                             | String | 医院性质                     |
| `hqName`                                    | String | 集团归属                     |
| `hcoGradeType`                              | String | 医院级别                     |
| `hcoManageType`                             | String | 医院类别                     |
| `cyStartDevelopStatus`                      | String | 年初开发状态                 |
| `cyDevelopStatus`                           | String | 当前开发状态                 |
| `cyIsDualChannelEnabled`                    | String | 双通道是否已打通             |
| `cyDevelopmentSelect`                       | String | 院内/双通道开发选择          |
| `currentYearDevelopmentPercentage`          | Number | 今年开发几率                 |
| `currentYearTargetAmount`                   | Number | 今年目标量M2                 |
| `currentYearProductunitPrice`               | Number | 今年品种单价                 |
| `plannedDevelopmentQuarter`                 | String | 计划开发季度                 |
| `plannedDevelopmentCost`                    | Number | 计划开发费用/元              |
| `cyClinicalClient`                          | String | 锁定临床关键客户             |
| `cyClinicalClientViewpoint`                 | String | 临床关键客户观点             |
| `cyPharmacyClient`                          | String | 锁定药学关键客户             |
| `cyPharmacyClientViewpoint`                 | String | 药学关键客户关系             |
| `cyAdministrationClient`                    | String | 锁定行政关键客户             |
| `cyAdministrationClientRelationship`        | String | 锁定行政关键客户关系         |
| `hcoDevelopmentModelsDescription`           | String | 医院既往开发模式简述         |
| `quarter`                                   | Number | 季度                         |
| `cqPlannedDevelopmentQuarter`               | String | 预计成功开发季度             |
| `cqPlannedDevelopmentCost`                  | Number | 计划开发费用/元              |
| `cqStartDevelopStatus`                      | String | 季度初开发状态               |
| `cqDevelopStatus`                           | String | 当前开发状态                 |
| `cqIsDualChannelEnabled`                    | String | 双通道是否已打通             |
| `cqDevelopmentSelect`                       | String | 院内/双通道开发选择          |
| `cqFollowQuarter`                           | String | 跟进季度                     |
| `cqClinicalClient`                          | String | 锁定临床关键客户             |
| `cqClinicalClientViewpoint`                 | String | 临床关键客户观点             |
| `cqPharmacyClient`                          | String | 锁定药学关键客户             |
| `cqPharmacyClientViewpoint`                 | String | 药学关键客户关系             |
| `cqAdministrationClient`                    | String | 锁定行政关键客户             |
| `cqAdministrationClientRelationship`        | String | 锁定行政关键客户关系         |
| `cqClinicalClientPlanningResources`         | String | 临床客户规划资源             |
| `cqPharmacyClientPlanningResources`         | String | 药学客户规划资源             |
| `cqAdministrationClientPlanningResources`   | String | 行政客户规划资源             |
| `cqClinicalRoleCount`                       | Number | 临床关键客户规划学术会议次数 |
| `cqClinicalAcademicConferenceExpense`       | Number | 临床关键客户规划学术会议费用 |
| `cqClinicalAcademicLinkCount`               | Number | 临床关键客户学术规划链接次数 |
| `cqClinicalAcademicLinkExpense`             | Number | 临床关键客户学术规划链接费用 |
| `cqAdministrationRoleCount`                 | Number | 行政关键客户学术规划会议次数 |
| `cqAdministrationAcademicConferenceExpense` | Number | 行政关键客户规划学术会议费用 |
| `cqAdministrationAcademicLinkCount`         | Number | 行政关键客户规划学术链接次数 |
| `cqAdministrationAcademicLinkExpense`       | Number | 行政关键客户规划学术链接费用 |
| `cqPharmacyRoleCount`                       | Number | 药学关键客户规划学术会议次数 |
| `cqPharmacyAcademicConferenceExpense`       | Number | 药学关键客户规划学术会议费用 |
| `cqPharmacyAcademicLinkCount`               | Number | 药学关键客户规划学术链接次数 |
| `cqPharmacyAcademicLinkExpense`             | Number | 药学关键客户规划学术链接费用 |
| `cqClinicalVisitCount`                      | Number | 临床关键客户学术拜访次数     |
| `cqClinicalLinkCount`                       | Number | 临床关键客户学术链接次数     |
| `cqClinicalMeetingCount`                    | Number | 临床关键客户学术会议次数     |
| `cqAdministrationVisitCount`                | Number | 行政关键客户学术拜访次数     |
| `cqAdministrationLinkCount`                 | Number | 行政关键客户学术链接次数     |
| `cqAdministrationMeetingCount`              | Number | 行政关键客户学术会议次数     |
| `cqPharmacyVisitCount`                      | Number | 药学关键客户学术拜访次数     |
| `cqPharmacyLinkCount`                       | Number | 药学关键客户学术链接次数     |
| `cqPharmacyMeetingCount`                    | Number | 药学关键客户学术会议次数     |
| `w1PlanContent`                             | String | W1周计划                     |
| `w2PlanContent`                             | String | W2周计划                     |
| `w3PlanContent`                             | String | W3周计划                     |
| `w4PlanContent`                             | String | W4周计划                     |
| `w5PlanContent`                             | String | W5周计划                     |
| `w6PlanContent`                             | String | W6周计划                     |
| `w7PlanContent`                             | String | W7周计划                     |
| `w8PlanContent`                             | String | W8周计划                     |
| `w9PlanContent`                             | String | W9周计划                     |
| `w10PlanContent`                            | String | W10周计划                    |
| `w11PlanContent`                            | String | W11周计划                    |
| `w12PlanContent`                            | String | W12周计划                    |
| `w13PlanContent`                            | String | W13周计划                    |
| `w14PlanContent`                            | String | W14周计划                    |
| `w1IsPlanningExecute`                       | String | W1是否完全执行               |
| `w2IsPlanningExecute`                       | String | W2是否完全执行               |
| `w3IsPlanningExecute`                       | String | W3是否完全执行               |
| `w4IsPlanningExecute`                       | String | W4是否完全执行               |
| `w5IsPlanningExecute`                       | String | W5是否完全执行               |
| `w6IsPlanningExecute`                       | String | W6是否完全执行               |
| `w7IsPlanningExecute`                       | String | W7是否完全执行               |
| `w8IsPlanningExecute`                       | String | W8是否完全执行               |
| `w9IsPlanningExecute`                       | String | W9是否完全执行               |
| `w10IsPlanningExecute`                      | String | W10是否完全执行              |
| `w11IsPlanningExecute`                      | String | W11是否完全执行              |
| `w12IsPlanningExecute`                      | String | W12是否完全执行              |
| `w13IsPlanningExecute`                      | String | W13是否完全执行              |
| `w14IsPlanningExecute`                      | String | W14是否完全执行              |
| `w1DevelopmentStatus`                       | String | W1周开发状态                 |
| `w2DevelopmentStatus`                       | String | W2周开发状态                 |
| `w3DevelopmentStatus`                       | String | W3周开发状态                 |
| `w4DevelopmentStatus`                       | String | W4周开发状态                 |
| `w5DevelopmentStatus`                       | String | W5周开发状态                 |
| `w6DevelopmentStatus`                       | String | W6周开发状态                 |
| `w7DevelopmentStatus`                       | String | W7周开发状态                 |
| `w8DevelopmentStatus`                       | String | W8周开发状态                 |
| `w9DevelopmentStatus`                       | String | W9周开发状态                 |
| `w10DevelopmentStatus`                      | String | W10周开发状态                |
| `w11DevelopmentStatus`                      | String | W11周开发状态                |
| `w12DevelopmentStatus`                      | String | W12周开发状态                |
| `w13DevelopmentStatus`                      | String | W13周开发状态                |
| `w14DevelopmentStatus`                      | String | W14周开发状态                |
| `cqActualDevelopmentQuarter`                | String | 实际开发季度                 |
| `cqActualDevelopmentCost`                   | Number | 实际开发费用/元              |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": [
    {
      "id": "dev001",
      "year": 2024,
      "regionName": "华东大区",
      "areaName": "上海地区",
      "territoryName": "上海代表处",
      "positionType": "专岗",
      "managerName": "张经理",
      "productName": "产品A",
      "hcoId": "hco123",
      "hcoName": "上海第一人民医院",
      "hcoCpId": "cp123",
      "outpatientAmount": 5000,
      "operationAmount": 200,
      "monthlyHcoPotentialAmount": 100,
      "sourceType": "新开发",
      "hcoNatureType": "公立",
      "hqName": "医疗集团A",
      "hcoGradeType": "三级甲等",
      "hcoManageType": "综合医院",
      "cyStartDevelopStatus": "未开发",
      "cyDevelopStatus": "开发中",
      "cyIsDualChannelEnabled": "是",
      "cyDevelopmentSelect": "院内开发",
      "currentYearDevelopmentPercentage": 80,
      "currentYearTargetAmount": 500,
      "currentYearProductunitPrice": 100,
      "plannedDevelopmentQuarter": "Q2",
      "plannedDevelopmentCost": 50000,
      "cyClinicalClient": "李医生",
      "cyClinicalClientViewpoint": "认可产品",
      "cyPharmacyClient": "王药师",
      "cyPharmacyClientViewpoint": "支持引进",
      "cyAdministrationClient": "陈院长",
      "cyAdministrationClientRelationship": "良好",
      "hcoDevelopmentModelsDescription": "既往学术推广模式",
      "quarter": 1,
      "cqPlannedDevelopmentQuarter": "Q2",
      "cqPlannedDevelopmentCost": 50000,
      "cqStartDevelopStatus": "未开发",
      "cqDevelopStatus": "开发中",
      "cqIsDualChannelEnabled": "是",
      "cqDevelopmentSelect": "院内开发",
      "cqFollowQuarter": "Q1",
      "cqClinicalClient": "李医生",
      "cqClinicalClientViewpoint": "认可产品",
      "cqPharmacyClient": "王药师",
      "cqPharmacyClientViewpoint": "支持引进",
      "cqAdministrationClient": "陈院长",
      "cqAdministrationClientRelationship": "良好",
      "cqClinicalClientPlanningResources": "学术会议资源",
      "cqPharmacyClientPlanningResources": "药学会议资源",
      "cqAdministrationClientPlanningResources": "行政支持资源",
      "cqClinicalRoleCount": 5,
      "cqClinicalAcademicConferenceExpense": 20000,
      "cqClinicalAcademicLinkCount": 3,
      "cqClinicalAcademicLinkExpense": 10000,
      "cqAdministrationRoleCount": 2,
      "cqAdministrationAcademicConferenceExpense": 15000,
      "cqAdministrationAcademicLinkCount": 2,
      "cqAdministrationAcademicLinkExpense": 8000,
      "cqPharmacyRoleCount": 3,
      "cqPharmacyAcademicConferenceExpense": 10000,
      "cqPharmacyAcademicLinkCount": 2,
      "cqPharmacyAcademicLinkExpense": 5000,
      "cqClinicalVisitCount": 10,
      "cqClinicalLinkCount": 5,
      "cqClinicalMeetingCount": 3,
      "cqAdministrationVisitCount": 5,
      "cqAdministrationLinkCount": 2,
      "cqAdministrationMeetingCount": 2,
      "cqPharmacyVisitCount": 8,
      "cqPharmacyLinkCount": 3,
      "cqPharmacyMeetingCount": 2,
      "w1PlanContent": "拜访李医生",
      "w2PlanContent": "安排学术会议",
      "w3PlanContent": "",
      "w4PlanContent": "",
      "w5PlanContent": "",
      "w6PlanContent": "",
      "w7PlanContent": "",
      "w8PlanContent": "",
      "w9PlanContent": "",
      "w10PlanContent": "",
      "w11PlanContent": "",
      "w12PlanContent": "",
      "w13PlanContent": "",
      "w14PlanContent": "",
      "w1IsPlanningExecute": "是",
      "w2IsPlanningExecute": "否",
      "w3IsPlanningExecute": "",
      "w4IsPlanningExecute": "",
      "w5IsPlanningExecute": "",
      "w6IsPlanningExecute": "",
      "w7IsPlanningExecute": "",
      "w8IsPlanningExecute": "",
      "w9IsPlanningExecute": "",
      "w10IsPlanningExecute": "",
      "w11IsPlanningExecute": "",
      "w12IsPlanningExecute": "",
      "w13IsPlanningExecute": "",
      "w14IsPlanningExecute": "",
      "w1DevelopmentStatus": "跟进中",
      "w2DevelopmentStatus": "跟进中",
      "w3DevelopmentStatus": "",
      "w4DevelopmentStatus": "",
      "w5DevelopmentStatus": "",
      "w6DevelopmentStatus": "",
      "w7DevelopmentStatus": "",
      "w8DevelopmentStatus": "",
      "w9DevelopmentStatus": "",
      "w10DevelopmentStatus": "",
      "w11DevelopmentStatus": "",
      "w12DevelopmentStatus": "",
      "w13DevelopmentStatus": "",
      "w14DevelopmentStatus": "",
      "cqActualDevelopmentQuarter": "",
      "cqActualDevelopmentCost": 0
    }
  ],
  "timestamp": 1715668800000,
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
