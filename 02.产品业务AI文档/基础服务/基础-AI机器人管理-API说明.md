# 基础服务 - AI机器人管理 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|-----|
| 1.0 | 2026-03-31 | 初版创建，新增 AI 机器人管理 3 个接口说明 | AI助手 |

## 一、概述

本文档描述基础服务中的 **AI机器人管理服务** 对外开放的 Open API。通过这些接口可以实现以下业务能力：

1. **注册 AI 机器人**：创建并接入一个新的机器人，返回可用于接入的机器人通道配置。
2. **查询我的机器人**：获取当前应用下可见的机器人列表。
3. **删除我的机器人**：根据 `agentId` 删除指定机器人。

---

## 二、通用说明

### 2.1 访问地址
```text
https://{域名}/open-api/{接口地址}
```

### 2.2 环境信息

| 环境 | 域名/Base URL | 备注 |
| ---- | ------------------------------ | --- |
| 测试环境 | `https://cwork-test-open-api.xgjktech.com.cn` | Swagger 验证地址 |

### 2.3 公共请求头

| Header | 说明 | 是否必填 |
| -------- | -------------------------- | ----- |
| `appKey` | 从工作协同系统获取的 API 密钥 | 是 |

### 2.4 通用响应结构

所有接口响应均返回统一的 `Result<T>` 结构：

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": null
}
```

| 字段 | 类型 | 说明 |
| ------------ | ------- | ----------------------------------------- |
| `resultCode` | Integer | 业务状态码，`1` 表示成功，非 `1` 表示失败 |
| `resultMsg`  | String  | 提示信息，成功时通常为 `success` 或 `null`，失败时为错误描述 |
| `data`       | T       | 业务数据，类型由具体接口定义 |

---

## 三、关键业务流程说明

### 场景一：创建并发布一个私人助理机器人

1. 调用 **4.1 注册 AI 机器人**（`POST /im/robot/register`），提交 `agentId`、`name` 等信息。
2. 接口返回 `RobotPluginVO`，其中包含 `appKey`、`baseUrl`、`wsBaseUrl` 等对接信息。
3. 调用 **4.2 获取我的私人助理**（`GET /im/robot/getMyRobot`）确认机器人已注册并可查询。

### 场景二：下线不再使用的机器人

1. 先通过 **4.2 获取我的私人助理** 查询现有机器人列表，确认目标 `agentId`。
2. 调用 **4.3 根据Agentid删除我的机器人**（`POST /im/robot/deleteMyRobot`）删除该机器人。
3. 若返回 `data=true` 则表示删除成功。

---

## 四、AI机器人管理接口详细说明

### 4.1 注册 AI 机器人

注册一个 AI 机器人，并返回机器人通道配置与认证信息。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/im/robot/register` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

- **请求体 (Body)：`RobotRegisterRequest`**

| 参数名 | 类型 | 必填 | 说明 |
| ----------- | ------------- | ---- | ------------------------------ |
| `agentId` | String | 是 | 绑定的外部(openclaw)AgentID，例如：`main` |
| `name` | String | 是 | 机器人名称 |
| `avatar` | String | 否 | 机器人头像 URL |
| `groupLabel` | String | 否 | 分组标签 |
| `remark` | String | 否 | 备注信息 |
| `visibleType` | Integer | 否 | 可见性类型：`0`-私有(默认)，`1`-公开，`2`-指定范围 |
| `visibleRange` | List\<VisibleRangeItem\> | 否 | 可见范围列表；当 `visibleType=2` 时必传 |

`visibleRange` 子项 `VisibleRangeItem` 字段如下：

| 字段 | 类型 | 说明 |
| ----------- | ------------- | ------------------------------ |
| `targetId` | String | 目标 ID |
| `targetType` | String | 目标类型：`USER`-人员，`DEPT`-部门 |

**响应参数**

`data` 类型为 `RobotPluginVO`，字段详见 **[5.2 RobotPluginVO](#52-robotpluginvo)**。

**请求示例**

```bash
curl -X POST 'https://cwork-test-open-api.xgjktech.com.cn/open-api/im/robot/register' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "agentId": "main",
    "name": "销售助手",
    "avatar": "https://img.example.com/robot.png",
    "groupLabel": "销售支持",
    "remark": "用于销售问答",
    "visibleType": 2,
    "visibleRange": [
      { "targetId": "10001", "targetType": "USER" },
      { "targetId": "20001", "targetType": "DEPT" }
    ]
  }'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": {
    "agentId": "main",
    "appKey": "robot_app_key_xxx",
    "avatar": "https://img.example.com/robot.png",
    "baseUrl": "https://cwork-open-api.example.com",
    "groupLabel": "销售支持",
    "name": "销售助手",
    "remark": "用于销售问答",
    "userId": "734612345678901234",
    "wsBaseUrl": "wss://cwork-open-api.example.com"
  }
}
```

---

### 4.2 获取我的私人助理

获取当前应用下可见的机器人列表。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/im/robot/getMyRobot` |
| 请求方式 | `GET` |

**请求参数**

无业务参数。

**响应参数**

`data` 类型为 `List<AiRobotVO>`，字段详见 **[5.1 AiRobotVO](#51-airobotvo)**。

**请求示例**

```bash
curl -X GET 'https://cwork-test-open-api.xgjktech.com.cn/open-api/im/robot/getMyRobot' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": [
    {
      "agentId": "main",
      "appKey": "robot_app_key_xxx",
      "avatar": "https://img.example.com/robot.png",
      "groupLabel": "销售支持",
      "name": "销售助手",
      "remark": "用于销售问答",
      "userId": "734612345678901234"
    }
  ]
}
```

---

### 4.3 根据Agentid删除我的机器人

根据机器人 `agentId` 删除我的机器人。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/im/robot/deleteMyRobot` |
| 请求方式 | `POST` |

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 说明 |
| ----------- | ------ | ---- | ---- | ------------------------------ |
| `agentId` | Query | String | 是 | 机器人 AgentID |

**响应参数**

`data` 类型为 `Boolean`，`true` 表示删除成功，`false` 表示删除失败。

**请求示例**

```bash
curl -X POST 'https://cwork-test-open-api.xgjktech.com.cn/open-api/im/robot/deleteMyRobot?agentId=main' \
  -H 'appKey: YOUR_API_KEY'
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": true
}
```

---

## 五、公共数据结构

### 5.1 AiRobotVO
AI 机器人详情。

| 字段 | 类型 | 说明 |
| ------------- | ------ | ------------------- |
| `agentId` | String | Agent ID |
| `appKey` | String | 机器人的认证 AppKey |
| `avatar` | String | 头像 URL |
| `groupLabel` | String | 分组标签 |
| `name` | String | 机器人名称 |
| `remark` | String | 备注信息 |
| `userId` | String | 机器人虚拟用户 ID（employeeId） |

---

### 5.2 RobotPluginVO
AI 机器人 channel 配置。

| 字段 | 类型 | 说明 |
| ------------- | ------ | ------------------- |
| `agentId` | String | Agent ID |
| `appKey` | String | 机器人的认证 AppKey |
| `avatar` | String | 头像 URL |
| `baseUrl` | String | 后台服务域名 |
| `groupLabel` | String | 分组标签 |
| `name` | String | 机器人名称 |
| `remark` | String | 备注信息 |
| `userId` | String | 机器人的虚拟用户 ID（employeeId） |
| `wsBaseUrl` | String | 后台服务 WSS 域名 |

---

### 5.3 RobotRegisterRequest
注册机器人请求体。

| 字段 | 类型 | 必填 | 说明 |
| ------------- | ------ | ---- | ------------------- |
| `agentId` | String | 是 | 绑定的外部(openclaw)AgentID，例如：`main` |
| `name` | String | 是 | 机器人名称 |
| `avatar` | String | 否 | 机器人头像 URL |
| `groupLabel` | String | 否 | 分组标签 |
| `remark` | String | 否 | 备注信息 |
| `visibleType` | Integer | 否 | 可见性类型：`0`-私有，`1`-公开，`2`-指定范围 |
| `visibleRange` | List\<VisibleRangeItem\> | 否 | 可见范围，`visibleType=2` 时必传 |

---

### 5.4 VisibleRangeItem
可见范围条目。

| 字段 | 类型 | 说明 |
| ------------- | ------ | ------------------- |
| `targetId` | String | 目标 ID |
| `targetType` | String | 目标类型：`USER`-人员，`DEPT`-部门 |

---

## 六、错误码说明

开放平台接口统一使用 `resultCode` 表示业务处理结果。常见返回码如下：

| resultCode | 说明 | 参考信息 / 异常原因 |
| ---------- | ---------------------- | ------------------------------------------ |
| **1** | **请求成功** | success |
| **0** | **通用失败** | failure |
| **500** | **系统异常/内部错误** | 系统崩溃、微服务超时或内部异常 |
| 610002 | `appKey` 无效 | 应用密钥不匹配或未分配 |
| 610012 | 请求太频繁（触发限流） | 超过 QPS 限制，建议降频重试 |
| 610015 | 无访问权限 | 未给该 appKey 授权对应接口调用权限 |

---

## 七、注意事项

1. **接口幂等性建议**：注册接口为业务写操作，请在调用侧做好重试幂等控制，避免重复创建同名机器人。
2. **ID 与字符串处理**：`userId`、`agentId` 等建议按字符串处理与存储，避免跨语言解析差异。
3. **可见范围约束**：当 `visibleType=2` 时，必须传 `visibleRange`，并明确 `targetType` 为 `USER` 或 `DEPT`。
4. **安全性要求**：请妥善保管机器人返回的 `appKey`，避免泄露到前端公开环境。

---

**文档版本**：v1.0  
**更新日期**：2026-03-31  
**维护人/团队**：基础服务团队
