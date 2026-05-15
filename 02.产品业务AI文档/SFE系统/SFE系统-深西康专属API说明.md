# SFE系统深西康专属 Open API 接口文档

## 修订记录

| 版本 | 日期       | 修订内容                     | 修订人 |
| ---- | ---------- | ---------------------------- | ------ |
| V1.0 | 2026-03-29 | 初始版本，开放深西康专属接口 | 王馗   |
| V1.1 | 2026-05-11 | 重组文档结构，新增新活素、美泰彤、益盖宁查房、新活素调研相关11个接口 | 王馗   |

---

## 一、概述

本文档描述了 **SFE系统深西康专属接口**，主要针对特定客户的定制化业务场景提供专用API接口。涵盖三大产品线的查房业务：新活素、美泰彤、益盖宁。

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
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsReportV2/count' \
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

### 场景一：查询新活素查房日采集反馈数据
> 需求：获取新活素查房日采集反馈数据。

1. 调用 **4.1.1 新活素查房日采集反馈V2**，传入 `periodStart` 和 `periodEnd` 等筛选条件，获取反馈数据列表
2. 根据返回的 `areaName`（大区）、`districtName`（地区）和 `regionName`（子区域）进行数据分析
3. 可结合 **4.1.3 新活素查房区划应汇报已汇报** 接口确认各辖区汇报完成情况


### 场景二：查询美泰彤查房日反馈数据

> 需求：获取美泰彤查房日反馈数据，分析患者用药和出院带药情况。

1. 调用 **4.2.1 美泰彤查房日反馈明细表**，传入 `periodStart` 和 `periodEnd` 等筛选条件，获取反馈数据列表
2. 根据返回的 `medicatedPatientsCount`（已用药患者数）、`estimatedDischargeMedicationPatientsCount`（预估出院可带药患者数）等字段分析用药情况
3. 可结合 **4.2.2 美泰彤查房区划应汇报已汇报** 接口确认各辖区汇报完成情况

### 场景三：查询益盖宁查房日反馈数据

> 需求：获取益盖宁查房日反馈数据，分析骨质疏松患者用药和诊断情况。

1. 调用 **4.3.1 益盖宁查房日反馈明细表**，传入 `periodStart` 和 `periodEnd` 等筛选条件，获取反馈数据列表
2. 根据返回的 `medicatedPatientsCount`（已用药患者数）、`patientsNotMeetingMinimumWeeklyDosageCount`（未满足一周2支及以上用药患者数）等字段分析用药达标情况
3. 可结合 **4.3.2 益盖宁查房区划应汇报已汇报** 接口确认各辖区汇报完成情况

---

## 四、接口详细说明

---

### 4.1 新活素查房相关接口

本节包含新活素查房业务相关的6个API接口。

---

#### 4.1.1 新活素查房日采集反馈V2

查询新活素查房日采集反馈数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsReportV2` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districName`   | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsReportV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                                   | 类型   | 说明                        |
| ---------------------------------------- | ------ | --------------------------- |
| `zoneId`                                 | String | 区划 ID                     |
| `regionName`                             | String | 大区名称               |
| `districtName`                           | String | 区域名称               |
| `areaName`                               | String | 地区名称               |
| `territoryName`                          | String | 辖区名称                    |
| `submitName`                             | String | 提交人                  |
| `hcoName`                                | String | 医院                |
| `hcoDepartment`                          | String | 科室                |
| `cycle`                                  | String | 周期                        |
| `medicatedPatientCount`                  | Number | 已用药患者数量                |
| `acuteHeartFailureLowDoseCount`          | Number | 急性心衰剂量低于0.01的患者数      |
| `acuteHeartFailureShortCourseCount`      | Number | 急性心衰疗程低于3天患者数      |
| `selfPayAfterThreeDaysCount`             | Number | 3天后应自费用药患者数          |
| `acuteHeartFailureCourseBelow3DaysCount` | Number | 急性心衰疗程低于3天患者数 |
| `selfPayAfter3DaysCount`                 | Number | 3天后自费患者数           |
| `medicalInsuranceRiskCaseCount`          | Number | 医保风险病例数            |
| `nonMedicatedPatientCount`               | Number | 非用药患者数              |
| `undiagnosedWithCommonSymptomsCount`     | Number | 无诊断有心衰常见症状患者数  |
| `potentialProductCandidatesCount1`       | Number | 无诊断但有心衰常见症状有机会使用新活素患者数       |
| `undiagnosedWithMedicationHistoryCount`  | Number | 无诊断无常见症状有常用药用药记录的患者    |
| `potentialProductCandidatesCount2`       | Number | 无诊断无常见心衰症状但有常用药用药记录有机会使用新活素患者数       |
| `currentDayFollowUpStatus`               | String | 当日机会点跟进情况                |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "submitName": "张三",
      "hcoName": "广州市第一人民医院",
      "hcoDepartment": "心内科",
      "cycle": "2025-W01",
      "medicatedPatientCount": 50,
      "acuteHeartFailureLowDoseCount": 10,
      "acuteHeartFailureShortCourseCount": 8,
      "selfPayAfterThreeDaysCount": 5,
      "acuteHeartFailureCourseBelow3DaysCount": 3,
      "selfPayAfter3DaysCount": 5,
      "medicalInsuranceRiskCaseCount": 2,
      "nonMedicatedPatientCount": 15,
      "undiagnosedWithCommonSymptomsCount": 8,
      "potentialProductCandidatesCount1": 12,
      "undiagnosedWithMedicationHistoryCount": 6,
      "potentialProductCandidatesCount2": 10,
      "currentDayFollowUpStatus": "成功修正病历数: 0, 成功提升剂量数: 1, 成功提升疗程数: 0, 3天后转自费数: 0, 机会患者成功数: 2, 有诊断未用药成功用药数: 0"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.2 新活素查房周跟进复盘V2

查询新活素查房周跟进复盘数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsWeekReviewReportV2` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsWeekReviewReportV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                                       | 类型   | 说明                                 |
| -------------------------------------------- | ------ | ------------------------------------ |
| `zoneId`                                     | String | 区划 ID                              |
| `regionName`                                 | String | 大区名称                             |
| `districtName`                               | String | 区域名称                             |
| `areaName`                                   | String | 地区名称                             |
| `submitName`                                 | String | 提交人                               |
| `cycle`                                      | String | 周期                                 |
| `lastWeekOpportunityCount`                   | String | 团队上周发现了多少机会点             |
| `followedUpSuccessCount`                     | String | 跟进成功了多少机会点                 |
| `frequentOpportunityPatientCategoryInRounds` | String | 在查房过程中哪类机会患者出现频率较高 |
| `subsequentRegionalPromotionActions`         | String | 后续地区将安排对应的哪些推广动作     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "submitName": "张三",
      "cycle": "2025-W01",
      "lastWeekOpportunityCount": "剂量低于0.01的患者数: 2, 疗程不达标患者数: 4, 3天后应自费患者数: 2, 风险病历数: 3, 未用药患者数: 2, 根据症状、用药筛查机会患者用药数: 2",
      "followedUpSuccessCount": "成功修正病历数: 3, 成功提升剂量数: 2, 成功提升疗程数: 2, 成功3天后转自费数: 1, 有诊断未用药成功用药数: 2, 根据症状、用药筛查机会患者成功用药数: 2",
      "frequentOpportunityPatientCategoryInRounds": "急性心衰低剂量患者",
      "subsequentRegionalPromotionActions": "加强剂量提升培训，优化随访流程"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.3 新活素查房区划应汇报已汇报

查询新活素查房区划应汇报已汇报数据（当前只支持辖区级数据，即岗位的应汇报已汇报）。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsZoneShouldHasReport` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsZoneShouldHasReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型   | 说明           |
| --------------- | ------ | -------------- |
| `zoneId`        | String | 区划 ID        |
| `regionName`    | String | 大区名称       |
| `districtName`  | String | 区域名称       |
| `areaName`      | String | 地区名称       |
| `territoryName` | String | 辖区名称       |
| `reportDate`    | String | 日期           |
| `shouldReport`  | String | 是否应汇报     |
| `hasReported`   | String | 是否已汇报     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "reportDate": "2025-01-15",
      "shouldReport": "是",
      "hasReported": "是"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.4 新活素查房执行日统计

查询新活素查房执行日统计数据，按各大区汇总任务执行情况。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsExecutionDailyStatsV2` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明         |
| ------------- | ------- | ---- | ------------ |
| `periodStart` | String  | 否   | 期间开始日期 |
| `periodEnd`   | String  | 否   | 期间结束日期 |
| `page`        | Integer | 否   | 页码，默认第 1 页 |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsExecutionDailyStatsV2' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                      | 类型   | 说明               |
| --------------------------- | ------ | ------------------ |
| `date`                       | String | 日期               |
| `nationalTotal`              | Number | 全国任务总数       |
| `nationalPending`            | Number | 全国待处理         |
| `nationalSubmitted`          | Number | 全国已提交         |
| `nationalSubmissionRate`     | String | 全国任务提交率     |
| `beijingTotal`               | Number | 北京大区任务总数   |
| `beijingPending`             | Number | 北京大区待处理     |
| `beijingSubmitted`           | Number | 北京大区已提交     |
| `beijingSubmissionRate`      | String | 北京大区任务提交率 |
| `northeastTotal`             | Number | 东北大区任务总数   |
| `northeastPending`           | Number | 东北大区待处理     |
| `northeastSubmitted`         | Number | 东北大区已提交     |
| `northeastSubmissionRate`    | String | 东北大区任务提交率 |
| `southeastTotal`             | Number | 东南大区任务总数   |
| `southeastPending`           | Number | 东南大区待处理     |
| `southeastSubmitted`         | Number | 东南大区已提交     |
| `southeastSubmissionRate`    | String | 东南大区任务提交率 |
| `northChinaTotal`            | Number | 华北大区任务总数   |
| `northChinaPending`          | Number | 华北大区待处理     |
| `northChinaSubmitted`        | Number | 华北大区已提交     |
| `northChinaSubmissionRate`   | String | 华北大区任务提交率 |
| `eastChinaTotal`             | Number | 华东大区任务总数   |
| `eastChinaPending`           | Number | 华东大区待处理     |
| `eastChinaSubmitted`         | Number | 华东大区已提交     |
| `eastChinaSubmissionRate`    | String | 华东大区任务提交率 |
| `southChinaTotal`            | Number | 华南大区任务总数   |
| `southChinaPending`          | Number | 华南大区待处理     |
| `southChinaSubmitted`        | Number | 华南大区已提交     |
| `southChinaSubmissionRate`   | String | 华南大区任务提交率 |
| `centralChinaTotal`          | Number | 华中大区任务总数   |
| `centralChinaPending`        | Number | 华中大区待处理     |
| `centralChinaSubmitted`      | Number | 华中大区已提交     |
| `centralChinaSubmissionRate` | String | 华中大区任务提交率 |
| `northwestTotal`             | Number | 西北大区任务总数   |
| `northwestPending`           | Number | 西北大区待处理     |
| `northwestSubmitted`         | Number | 西北大区已提交     |
| `northwestSubmissionRate`    | String | 西北大区任务提交率 |
| `southwestTotal`             | Number | 西南大区任务总数   |
| `southwestPending`           | Number | 西南大区待处理     |
| `southwestSubmitted`         | Number | 西南大区已提交     |
| `southwestSubmissionRate`    | String | 西南大区任务提交率 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "date": "2025-01-15",
      "nationalTotal": 1500,
      "nationalPending": 200,
      "nationalSubmitted": 1300,
      "nationalSubmissionRate": "86.67%",
      "beijingTotal": 150,
      "beijingPending": 20,
      "beijingSubmitted": 130,
      "beijingSubmissionRate": "86.67%",
      "northeastTotal": 120,
      "northeastPending": 15,
      "northeastSubmitted": 105,
      "northeastSubmissionRate": "87.50%",
      "southeastTotal": 180,
      "southeastPending": 25,
      "southeastSubmitted": 155,
      "southeastSubmissionRate": "86.11%",
      "northChinaTotal": 140,
      "northChinaPending": 18,
      "northChinaSubmitted": 122,
      "northChinaSubmissionRate": "87.14%",
      "eastChinaTotal": 200,
      "eastChinaPending": 30,
      "eastChinaSubmitted": 170,
      "eastChinaSubmissionRate": "85.00%",
      "southChinaTotal": 220,
      "southChinaPending": 28,
      "southChinaSubmitted": 192,
      "southChinaSubmissionRate": "87.27%",
      "centralChinaTotal": 160,
      "centralChinaPending": 22,
      "centralChinaSubmitted": 138,
      "centralChinaSubmissionRate": "86.25%",
      "northwestTotal": 100,
      "northwestPending": 12,
      "northwestSubmitted": 88,
      "northwestSubmissionRate": "88.00%",
      "southwestTotal": 130,
      "southwestPending": 20,
      "southwestSubmitted": 110,
      "southwestSubmissionRate": "84.62%"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.5 新活素查房日反馈区划患者数与机会点对比

查询新活素查房日反馈区划患者数与机会点对比数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsDailyFeedbackPatientOpportunityComparison` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsWardRoundsDailyFeedbackPatientOpportunityComparison' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                                | 类型   | 说明                       |
| ------------------------------------- | ------ | -------------------------- |
| `zoneId`                              | String | 区划 ID                    |
| `regionName`                          | String | 大区名称                   |
| `districtName`                        | String | 区域名称                   |
| `areaName`                            | String | 地区名称                   |
| `territoryName`                       | String | 辖区名称                   |
| `managerName`                         | String | 负责人                     |
| `startDate`                           | String | 周期开始日期               |
| `endDate`                             | String | 周期结束日期               |
| `medicalInsuranceRiskCaseCount`       | Number | 医保风险病历数             |
| `successCaseCount`                    | Number | 成功修正病历               |
| `acuteHeartFailureLowDoseCount`       | Number | 急性心衰低剂量患者数       |
| `dosageIncreaseCount`                 | Number | 剂量提升患者数             |
| `acuteHeartFailureShortCourseCount`   | Number | 急性心衰短疗程患者数       |
| `treatmentExtendCount`                | Number | 疗程延长患者数             |
| `selfPayAfterThreeDaysCount`          | Number | 3天后应自费患者数          |
| `selfPayAfter3Days`                   | Number | 3天后自费患者数            |
| `potentialProductCandidatesCount`    | Number | 潜在产品候选患者数         |
| `opportunitySuccessCount`             | Number | 机会点成功数               |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "managerName": "张三",
      "startDate": "2025-01-01",
      "endDate": "2025-01-31",
      "medicalInsuranceRiskCaseCount": 10,
      "successCaseCount": 8,
      "acuteHeartFailureLowDoseCount": 15,
      "dosageIncreaseCount": 12,
      "acuteHeartFailureShortCourseCount": 20,
      "treatmentExtendCount": 18,
      "selfPayAfterThreeDaysCount": 5,
      "selfPayAfter3Days": 4,
      "potentialProductCandidatesCount": 25,
      "opportunitySuccessCount": 20
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.1.6 新活素竞品推广行为调研报表

查询新活素竞品推广行为调研数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/xhsCompetitorPromotionReport` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明                   |
| ------------- | ------- | ---- | ---------------------- |
| `zoneId`      | String  | 否   | 区划 ID                |
| `regionName`  | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`| String  | 否   | 区域名称，支持模糊查询 |
| `areaName`    | String  | 否   | 地区名称，支持模糊查询 |
| `periodStart` | String  | 否   | 期间开始日期           |
| `periodEnd`   | String  | 否   | 期间结束日期           |
| `page`        | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/xhsCompetitorPromotionReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                              | 类型   | 说明                   |
| ----------------------------------- | ------ | ---------------------- |
| `zoneId`                            | String | 区划 ID                |
| `regionName`                        | String | 大区名称               |
| `districtName`                      | String | 区域名称               |
| `areaName`                          | String | 地区名称               |
| `submitName`                        | String | 提交人                 |
| `cycle`                             | String | 周期                   |
| `competitorPromotionModel`          | String | 竞品推广模式           |
| `teamBuildingStatus`                | String | 组建团队情况           |
| `distributionPartnerRecordStatus`   | String | 配送商业建档情况       |
| `hospitalContactStatus`             | String | 接触医院情况           |
| `competitorProductAdvantagePoints`   | String | 竞品宣传产品优势点     |
| `competitorXhsAttackPoints`         | String | 竞品针对新活素攻击点   |
| `competitorDevCostInvestment`       | String | 竞品开发费用投入       |
| `competitorClinicalCostInvestment`  | String | 竞品临床费用投入       |
| `otherRemarks`                      | String | 其他补充               |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "submitName": "张三",
      "cycle": "2025-W01",
      "competitorPromotionModel": "学术推广+代理模式",
      "teamBuildingStatus": "已完成15人团队组建",
      "distributionPartnerRecordStatus": "已与3家配送商业建立合作",
      "hospitalContactStatus": "已接触10家目标医院",
      "competitorProductAdvantagePoints": "价格优势、医保覆盖范围广",
      "competitorXhsAttackPoints": "强调价格劣势、质疑疗效差异",
      "competitorDevCostInvestment": "投入约50万元",
      "competitorClinicalCostInvestment": "投入约30万元",
      "otherRemarks": "竞品活动频繁，需加强学术推广"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

### 4.2 美泰彤查房相关接口

本节包含美泰彤查房业务相关的3个API接口。

---

#### 4.2.1 美泰彤查房日反馈明细表

查询美泰彤查房日反馈明细数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/mttWardRoundsReport` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/mttWardRoundsReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                                          | 类型   | 说明                         |
| ----------------------------------------------- | ------ | ---------------------------- |
| `zoneId`                                        | String | 区划 ID                      |
| `hcoName`                                       | String | 医院名称                     |
| `hcoDepartment`                                 | String | 科室名称                     |
| `regionName`                                    | String | 大区名称                     |
| `districtName`                                  | String | 区域名称                     |
| `areaName`                                      | String | 地区名称                     |
| `territoryName`                                 | String | 辖区名称                     |
| `submitName`                                    | String | 提交人                       |
| `cycle`                                         | String | 周期                         |
| `medicatedPatientsCount`                        | Number | 已用药患者数                 |
| `estimatedDischargeMedicationPatientsCount`     | Number | 预估出院可带药患者数         |
| `patientsWithFourOrMoreDosesCount`              | Number | 带药4支及以上患者数          |
| `patientsWithoutDischargeMedicationCount`      | Number | 未出院带药患者数             |
| `unmedicatedPatientsCount`                     | Number | 未用药患者数                 |
| `oralMtxPatientsCount`                         | Number | 口服MTX患者数                |
| `biologicsPatientsCount`                       | Number | 应用生物制剂患者数           |
| `communicatedDischargeMedicationCount`         | Number | 沟通出院带药患者数           |
| `replacedWithMethotrexateCount`                | Number | 片剂替换为美泰彤患者数       |
| `biologicsCombinedWithMethotrexateCount`       | Number | 生物制剂联用美泰彤患者数     |
| `remark`                                        | String | 备注说明                     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "hcoName": "广州市第一人民医院",
      "hcoDepartment": "风湿免疫科",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "submitName": "张三",
      "cycle": "2025-W01",
      "medicatedPatientsCount": 50,
      "estimatedDischargeMedicationPatientsCount": 35,
      "patientsWithFourOrMoreDosesCount": 28,
      "patientsWithoutDischargeMedicationCount": 5,
      "unmedicatedPatientsCount": 10,
      "oralMtxPatientsCount": 20,
      "biologicsPatientsCount": 15,
      "communicatedDischargeMedicationCount": 30,
      "replacedWithMethotrexateCount": 8,
      "biologicsCombinedWithMethotrexateCount": 12,
      "remark": "本周患者依从性良好"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.2.2 美泰彤查房区划应汇报已汇报

查询美泰彤查房区划应汇报已汇报数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/mttZoneShouldHasReport` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/mttZoneShouldHasReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型   | 说明           |
| --------------- | ------ | -------------- |
| `zoneId`        | String | 区划 ID        |
| `regionName`    | String | 大区名称       |
| `districtName`  | String | 区域名称       |
| `areaName`      | String | 地区名称       |
| `territoryName` | String | 辖区名称       |
| `reportDate`    | String | 日期           |
| `shouldReport`  | String | 是否应汇报     |
| `hasReported`   | String | 是否已汇报     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "reportDate": "2025-01-15",
      "shouldReport": "是",
      "hasReported": "是"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.2.3 美泰彤查房执行日统计

查询美泰彤查房执行日统计数据，按各大区汇总任务执行情况。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/mttWardRoundsExecutionDailyStats` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明         |
| ------------- | ------- | ---- | ------------ |
| `periodStart` | String  | 否   | 期间开始日期 |
| `periodEnd`   | String  | 否   | 期间结束日期 |
| `page`        | Integer | 否   | 页码，默认第 1 页 |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/mttWardRoundsExecutionDailyStats' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                      | 类型   | 说明               |
| --------------------------- | ------ | ------------------ |
| `date`                       | String | 日期               |
| `nationalTotal`              | Number | 全国任务总数       |
| `nationalPending`            | Number | 全国待处理         |
| `nationalSubmitted`          | Number | 全国已提交         |
| `nationalSubmissionRate`     | String | 全国任务提交率     |
| `beijingTotal`               | Number | 北京大区任务总数   |
| `beijingPending`             | Number | 北京大区待处理     |
| `beijingSubmitted`           | Number | 北京大区已提交     |
| `beijingSubmissionRate`      | String | 北京大区任务提交率 |
| `northeastTotal`             | Number | 东北大区任务总数   |
| `northeastPending`           | Number | 东北大区待处理     |
| `northeastSubmitted`         | Number | 东北大区已提交     |
| `northeastSubmissionRate`    | String | 东北大区任务提交率 |
| `southeastTotal`             | Number | 东南大区任务总数   |
| `southeastPending`           | Number | 东南大区待处理     |
| `southeastSubmitted`         | Number | 东南大区已提交     |
| `southeastSubmissionRate`    | String | 东南大区任务提交率 |
| `northChinaTotal`            | Number | 华北大区任务总数   |
| `northChinaPending`          | Number | 华北大区待处理     |
| `northChinaSubmitted`        | Number | 华北大区已提交     |
| `northChinaSubmissionRate`   | String | 华北大区任务提交率 |
| `eastChinaTotal`             | Number | 华东大区任务总数   |
| `eastChinaPending`           | Number | 华东大区待处理     |
| `eastChinaSubmitted`         | Number | 华东大区已提交     |
| `eastChinaSubmissionRate`    | String | 华东大区任务提交率 |
| `southChinaTotal`            | Number | 华南大区任务总数   |
| `southChinaPending`          | Number | 华南大区待处理     |
| `southChinaSubmitted`        | Number | 华南大区已提交     |
| `southChinaSubmissionRate`   | String | 华南大区任务提交率 |
| `centralChinaTotal`          | Number | 华中大区任务总数   |
| `centralChinaPending`        | Number | 华中大区待处理     |
| `centralChinaSubmitted`      | Number | 华中大区已提交     |
| `centralChinaSubmissionRate` | String | 华中大区任务提交率 |
| `northwestTotal`             | Number | 西北大区任务总数   |
| `northwestPending`           | Number | 西北大区待处理     |
| `northwestSubmitted`         | Number | 西北大区已提交     |
| `northwestSubmissionRate`    | String | 西北大区任务提交率 |
| `southwestTotal`             | Number | 西南大区任务总数   |
| `southwestPending`           | Number | 西南大区待处理     |
| `southwestSubmitted`         | Number | 西南大区已提交     |
| `southwestSubmissionRate`    | String | 西南大区任务提交率 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "date": "2025-01-15",
      "nationalTotal": 1200,
      "nationalPending": 180,
      "nationalSubmitted": 1020,
      "nationalSubmissionRate": "85.00%",
      "beijingTotal": 120,
      "beijingPending": 15,
      "beijingSubmitted": 105,
      "beijingSubmissionRate": "87.50%",
      "northeastTotal": 100,
      "northeastPending": 12,
      "northeastSubmitted": 88,
      "northeastSubmissionRate": "88.00%",
      "southeastTotal": 150,
      "southeastPending": 20,
      "southeastSubmitted": 130,
      "southeastSubmissionRate": "86.67%",
      "northChinaTotal": 110,
      "northChinaPending": 14,
      "northChinaSubmitted": 96,
      "northChinaSubmissionRate": "87.27%",
      "eastChinaTotal": 180,
      "eastChinaPending": 25,
      "eastChinaSubmitted": 155,
      "eastChinaSubmissionRate": "86.11%",
      "southChinaTotal": 200,
      "southChinaPending": 30,
      "southChinaSubmitted": 170,
      "southChinaSubmissionRate": "85.00%",
      "centralChinaTotal": 130,
      "centralChinaPending": 18,
      "centralChinaSubmitted": 112,
      "centralChinaSubmissionRate": "86.15%",
      "northwestTotal": 80,
      "northwestPending": 10,
      "northwestSubmitted": 70,
      "northwestSubmissionRate": "87.50%",
      "southwestTotal": 100,
      "southwestPending": 16,
      "southwestSubmitted": 84,
      "southwestSubmissionRate": "84.00%"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

### 4.3 益盖宁查房相关接口

本节包含益盖宁查房业务相关的3个API接口。

---

#### 4.3.1 益盖宁查房日反馈明细表

查询益盖宁查房日反馈明细数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/ygnWardRoundsReport` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/ygnWardRoundsReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                                                 | 类型   | 说明                                       |
| ------------------------------------------------------ | ------ | ------------------------------------------ |
| `zoneId`                                               | String | 区划 ID                                    |
| `hcoName`                                              | String | 医院名称                                   |
| `hcoDepartment`                                        | String | 科室名称                                   |
| `regionName`                                           | String | 大区名称                                   |
| `districtName`                                         | String | 区域名称                                   |
| `areaName`                                             | String | 地区名称                                   |
| `territoryName`                                        | String | 辖区名称                                   |
| `submitName`                                           | String | 提交人                                     |
| `cycle`                                                | String | 周期                                       |
| `medicatedPatientsCount`                               | Number | 已用药患者数                               |
| `patientsNotMeetingMinimumWeeklyDosageCount`          | Number | 未满足一周2支及以上用药患者数              |
| `patientsWithoutDischargeMedicationCount`             | Number | 未出院带药患者                             |
| `unmedicatedPatientsCount`                            | Number | 未用药患者数                               |
| `patientsWithRelatedConditionsButNoOsteoporosisDiagnosisCount` | Number | 未诊断骨松但有骨松相关诊断的患者数         |
| `patientsWithHighRiskSymptomsWithoutDiagnosisCount`   | Number | 无上述诊断但有骨松高发症状的患者数          |
| `osteoporosisDiagnosisWithoutPrescriptionSameDayResolutionCount` | Number | 骨松诊断未处方当日解决数                   |
| `suboptimalTreatmentRegimenSameDayResolutionCount`    | Number | 未足量足疗程用药当日解决数                 |
| `dischargeMedicationOmissionSameDayResolutionCount`   | Number | 未出院带药当日解决数                       |
| `undiagnosedWithRelatedFindingsSameDayResolutionCount` | Number | 未诊断但有相关诊断/症状当日解决数          |
| `remark`                                               | String | 备注说明                                   |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "hcoName": "广州市第一人民医院",
      "hcoDepartment": "骨科",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "submitName": "张三",
      "cycle": "2025-W01",
      "medicatedPatientsCount": 60,
      "patientsNotMeetingMinimumWeeklyDosageCount": 12,
      "patientsWithoutDischargeMedicationCount": 8,
      "unmedicatedPatientsCount": 15,
      "patientsWithRelatedConditionsButNoOsteoporosisDiagnosisCount": 10,
      "patientsWithHighRiskSymptomsWithoutDiagnosisCount": 6,
      "osteoporosisDiagnosisWithoutPrescriptionSameDayResolutionCount": 5,
      "suboptimalTreatmentRegimenSameDayResolutionCount": 8,
      "dischargeMedicationOmissionSameDayResolutionCount": 4,
      "undiagnosedWithRelatedFindingsSameDayResolutionCount": 6,
      "remark": "本周骨松筛查工作推进顺利"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.3.2 益盖宁查房区划应汇报已汇报

查询益盖宁查房区划应汇报已汇报数据。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/ygnZoneShouldHasReport` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名          | 类型    | 必填 | 说明                   |
| --------------- | ------- | ---- | ---------------------- |
| `zoneId`        | String  | 否   | 区划 ID                |
| `regionName`    | String  | 否   | 大区名称，支持模糊查询 |
| `districtName`  | String  | 否   | 区域名称，支持模糊查询 |
| `areaName`      | String  | 否   | 地区名称，支持模糊查询 |
| `territoryName` | String  | 否   | 辖区名称，支持模糊查询 |
| `periodStart`   | String  | 否   | 期间开始日期           |
| `periodEnd`     | String  | 否   | 期间结束日期           |
| `page`          | Integer | 否   | 页码，默认第 1 页      |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/ygnZoneShouldHasReport' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名          | 类型   | 说明           |
| --------------- | ------ | -------------- |
| `zoneId`        | String | 区划 ID        |
| `regionName`    | String | 大区名称       |
| `districtName`  | String | 区域名称       |
| `areaName`      | String | 地区名称       |
| `territoryName` | String | 辖区名称       |
| `reportDate`    | String | 日期           |
| `shouldReport`  | String | 是否应汇报     |
| `hasReported`   | String | 是否已汇报     |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "zoneId": "zone123",
      "regionName": "华南大区",
      "districtName": "广东区域",
      "areaName": "广州地区",
      "territoryName": "黄埔辖区",
      "reportDate": "2025-01-15",
      "shouldReport": "是",
      "hasReported": "是"
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

---

#### 4.3.3 益盖宁查房执行日统计

查询益盖宁查房执行日统计数据，按各大区汇总任务执行情况。

**基本信息**

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | `/bia/open/biz-service/sfe-sxk-report/ygnWardRoundsExecutionDailyStats` |
| 请求方式     | `POST`                                                       |
| Content-Type | `application/json`                                           |

**请求参数**

请求体为 JSON，字段如下：

| 参数名        | 类型    | 必填 | 说明         |
| ------------- | ------- | ---- | ------------ |
| `periodStart` | String  | 否   | 期间开始日期 |
| `periodEnd`   | String  | 否   | 期间结束日期 |
| `page`        | Integer | 否   | 页码，默认第 1 页 |

**请求示例**

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-sxk-report/ygnWardRoundsExecutionDailyStats' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

**响应参数**

`data` 为数组，数组元素字段如下：

| 字段名                      | 类型   | 说明               |
| --------------------------- | ------ | ------------------ |
| `date`                       | String | 日期               |
| `nationalTotal`              | Number | 全国任务总数       |
| `nationalPending`            | Number | 全国待处理         |
| `nationalSubmitted`          | Number | 全国已提交         |
| `nationalSubmissionRate`     | String | 全国任务提交率     |
| `beijingTotal`               | Number | 北京大区任务总数   |
| `beijingPending`             | Number | 北京大区待处理     |
| `beijingSubmitted`           | Number | 北京大区已提交     |
| `beijingSubmissionRate`      | String | 北京大区任务提交率 |
| `northeastTotal`             | Number | 东北大区任务总数   |
| `northeastPending`           | Number | 东北大区待处理     |
| `northeastSubmitted`         | Number | 东北大区已提交     |
| `northeastSubmissionRate`    | String | 东北大区任务提交率 |
| `southeastTotal`             | Number | 东南大区任务总数   |
| `southeastPending`           | Number | 东南大区待处理     |
| `southeastSubmitted`         | Number | 东南大区已提交     |
| `southeastSubmissionRate`    | String | 东南大区任务提交率 |
| `northChinaTotal`            | Number | 华北大区任务总数   |
| `northChinaPending`          | Number | 华北大区待处理     |
| `northChinaSubmitted`        | Number | 华北大区已提交     |
| `northChinaSubmissionRate`   | String | 华北大区任务提交率 |
| `eastChinaTotal`             | Number | 华东大区任务总数   |
| `eastChinaPending`           | Number | 华东大区待处理     |
| `eastChinaSubmitted`         | Number | 华东大区已提交     |
| `eastChinaSubmissionRate`    | String | 华东大区任务提交率 |
| `southChinaTotal`            | Number | 华南大区任务总数   |
| `southChinaPending`          | Number | 华南大区待处理     |
| `southChinaSubmitted`        | Number | 华南大区已提交     |
| `southChinaSubmissionRate`   | String | 华南大区任务提交率 |
| `centralChinaTotal`          | Number | 华中大区任务总数   |
| `centralChinaPending`        | Number | 华中大区待处理     |
| `centralChinaSubmitted`      | Number | 华中大区已提交     |
| `centralChinaSubmissionRate` | String | 华中大区任务提交率 |
| `northwestTotal`             | Number | 西北大区任务总数   |
| `northwestPending`           | Number | 西北大区待处理     |
| `northwestSubmitted`         | Number | 西北大区已提交     |
| `northwestSubmissionRate`    | String | 西北大区任务提交率 |
| `southwestTotal`             | Number | 西南大区任务总数   |
| `southwestPending`           | Number | 西南大区待处理     |
| `southwestSubmitted`         | Number | 西南大区已提交     |
| `southwestSubmissionRate`    | String | 西南大区任务提交率 |

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "date": "2025-01-15",
      "nationalTotal": 1000,
      "nationalPending": 150,
      "nationalSubmitted": 850,
      "nationalSubmissionRate": "85.00%",
      "beijingTotal": 100,
      "beijingPending": 12,
      "beijingSubmitted": 88,
      "beijingSubmissionRate": "88.00%",
      "northeastTotal": 80,
      "northeastPending": 10,
      "northeastSubmitted": 70,
      "northeastSubmissionRate": "87.50%",
      "southeastTotal": 120,
      "southeastPending": 18,
      "southeastSubmitted": 102,
      "southeastSubmissionRate": "85.00%",
      "northChinaTotal": 90,
      "northChinaPending": 12,
      "northChinaSubmitted": 78,
      "northChinaSubmissionRate": "86.67%",
      "eastChinaTotal": 150,
      "eastChinaPending": 22,
      "eastChinaSubmitted": 128,
      "eastChinaSubmissionRate": "85.33%",
      "southChinaTotal": 180,
      "southChinaPending": 25,
      "southChinaSubmitted": 155,
      "southChinaSubmissionRate": "86.11%",
      "centralChinaTotal": 100,
      "centralChinaPending": 15,
      "centralChinaSubmitted": 85,
      "centralChinaSubmissionRate": "85.00%",
      "northwestTotal": 70,
      "northwestPending": 8,
      "northwestSubmitted": 62,
      "northwestSubmissionRate": "88.57%",
      "southwestTotal": 80,
      "southwestPending": 12,
      "southwestSubmitted": 68,
      "southwestSubmissionRate": "85.00%"
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