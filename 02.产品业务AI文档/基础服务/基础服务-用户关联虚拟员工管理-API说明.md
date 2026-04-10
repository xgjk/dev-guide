# 基础服务-用户关联虚拟员工管理 Open API 接口文档

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|------|------|----------|-----|
| 1.0 | 2026-04-10 | 初版创建：新增虚拟员工管理基础接口 | 付光伟 |

## 一、概述

本文档描述了 **用户关联虚拟员工管理** 对外开放的 Open API 接口。该功能允许真实用户（Owner）在系统中绑定一个或多个虚拟员工（NPC），用于 AI 助理等业务场景。通过这些接口，可以实现以下业务能力：

1. **虚拟员工管理**：
   - **我的虚拟助理列表** — 获取当前账号下关联的所有虚拟员工。
   - **添加虚拟员工** — 为指定用户或当前用户创建一个虚拟员工角色。
   - **修改虚拟员工信息** — 更新虚拟员工的姓名、备注等。
   - **删除虚拟员工** — 解除绑定并逻辑删除该虚拟实体。

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
| `token` | 用户登录令牌（RequireToken） | 是 |

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

### 场景一：创建并管理我的 AI 助理

> 需求：用户希望通过 API 快速创建一个属于自己的虚拟助手。

1. 调用 **4.2 添加虚拟员工**（`POST /cwork-user/virtual-employee/add`），传入 `name="项目小助手"`。
2. 接口返回新增生成的 `virtualEmpId`。
3. 调用 **4.1 我的虚拟助理列表**（`GET /cwork-user/virtual-employee/list`），确认列表中出现了该助手。
4. 如需修改备注，调用 **4.3 修改虚拟员工信息**（`POST /cwork-user/virtual-employee/update`），传入 `virtualEmpId` 和新的 `remark`。
5. 若助理不再需要，调用 **4.4 删除虚拟员工**（`POST /cwork-user/virtual-employee/delete`）进行物理清理。

---

## 四、虚拟员工管理接口详细说明

### 4.1 我的虚拟助理列表

获取指定用户或当前登录用户关联的所有虚拟员工列表。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/cwork-user/virtual-employee/list` |
| 请求方式 | `GET` |

**请求参数**

无。

**响应参数**

`data` 类型为 `List<VirtualEmployeeVO>`，详见 **[5.1 VirtualEmployeeVO](#51-virtualemployeevo)**。

**请求示例**

```bash
curl -X GET 'https://{域名}/open-api/cwork-user/virtual-employee/list' \
  -H 'appKey: YOUR_API_KEY'
```

---

### 4.2 添加虚拟员工

为当前用户或指定用户创建一个虚拟员工。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/cwork-user/virtual-employee/add` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

`AddVirtualEmployeeParam`：

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | String | 是 | 虚拟员工姓名 |
| `remark` | String | 否 | 备注信息 |

**响应参数**

`data` 类型为 `Long`，返回新增成功的虚拟员工 ID。

**请求示例**

```bash
curl -X POST 'https://{域名}/open-api/cwork-user/virtual-employee/add' \
  -H 'appKey: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "AI 助手",
    "remark": "用于自动化处理"
  }'
```

---

### 4.3 修改虚拟员工信息

更新已有虚拟员工的基本信息。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/cwork-user/virtual-employee/update` |
| 请求方式 | `POST` |
| Content-Type | `application/json` |

**请求参数**

`UpdateVirtualEmployeeParam`：

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `virtualEmpId` | Long | 是 | 虚拟员工 ID |
| `name` | String | 否 | 新的姓名 |
| `remark` | String | 否 | 新的备注 |

**响应参数**

`data` 类型为 `Boolean`，成功返回 `true`。

---

### 4.4 删除虚拟员工

逻辑删除指定的虚拟员工并解除绑定关系。

**基本信息**

| 项目 | 说明 |
| ------------ | ----------------------------------- |
| 接口地址 | `/cwork-user/virtual-employee/delete` |
| 请求方式 | `POST` |

**请求参数**

| 参数名 | 类型 | 必填 |说明 |
| --- | --- | --- | --- |
| `virtualEmpId` | Long | 是 | 虚拟员工 ID |

**响应参数**

`data` 类型为 `Boolean`，成功返回 `true`。

---

## 五、公共数据结构

### 5.1 VirtualEmployeeVO

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `virtualEmpId` | Long | 虚拟员工 ID |
| `name` | String | 虚拟员工姓名 |
| `ownerName` | String | 所属真实员工姓名 |
| `remark` | String | 备注 |

---

**文档版本**：v1.0  
**更新日期**：2026-04-10  
**维护人/团队**：基础服务团队
