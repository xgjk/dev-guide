import re

def format_doc():
    filepath = 'd:/doc/dev-guide/dev-guide/02.产品业务AI文档/TBS系统/TBS_接口文档.md'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Base URLs and add open-api
    content = content.replace('/tbs-admin', '/open-api/tbs-admin')
    # Use exact replaces to avoid double replacements
    content = content.replace('https://cwork-web-test.xgjktech.com.cn/open-api/tbs-admin/open-api/tbs-admin', 'https://cwork-web-test.xgjktech.com.cn/open-api/tbs-admin')
    
    content = content.replace('access-token', 'appKey')
    content = content.replace('TBS_ACCESS_TOKEN', 'TBS_APP_KEY')
    content = content.replace('<ACCESS_TOKEN>', '<APP_KEY>')

    new_header = """# TBS-Admin API 接口文档

> **本文档的读者是 AI，不是开发者。** 所有接口文档用于 AI 编写 Skill，规则围绕"AI 能否高效准确地理解和使用接口"设计。

## 修订记录

| 版本 | 日期 | 变更摘要 | 变更人 |
|---|---|---|---|
| 1.0 | 2026-04-30 | 规范化接口文档，更新鉴权方式为 appKey 及基址包含 open-api | AI助手 |

---

## 一、概述

本系统主要提供 TBS 配置管理能力，涵盖**场景**、**提示词**、**基础数据**等核心模块的管理与操作。

---

## 二、通用说明

### 2.1 访问地址
```
https://{域名}/open-api/tbs-admin{接口地址}
```

### 2.2 环境信息

| 环境 | Base URL | 备注 |
|---|---|---|
| 测试环境 | `https://cwork-web-test.xgjktech.com.cn/open-api/tbs-admin` | - |
| 生产环境 | `https://sg-al-cwork-web.mediportal.com.cn/open-api/tbs-admin` | - |

### 2.3 公共请求头

| Header | 必填 | 说明 |
|---|---|---|
| `appKey` | 是 | 应用级鉴权密钥 |
| `Content-Type` | POST/PUT 必填 | `application/json` |

### 2.4 通用响应结构

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": null
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `resultCode` | Integer | `1` = 成功，其他 = 失败 |
| `resultMsg` | String | 成功时 `null`，失败时错误描述 |
| `data` | T | 业务数据，失败时 `null` |

### 2.5 错误码

| resultCode | 说明 | AI 处理动作 |
|---|---|---|
| 1 | 成功 | 读取 data |
| 0 | 通用失败 | 读取 resultMsg 展示给用户 |
| 400 | 参数错误 | 检查参数格式并重试 |
| 403 | 无权限 | 提示用户无权限 |
| 500 | 系统异常 | 稍后重试 |

### 2.6 命名约定与特殊口径
- **命名规范**：请求体、Query 参数中的业务字段统一为 **camelCase**。
- **ID 精度**：ID 统一为 `Long` 类型，为防止 JS 精度丢失，JSON 中建议使用 `String` 解析和传递。
- **时间规范**：时间字段统一遵循 ISO 8601 UTC 格式。

---
"""

    sec1_idx = content.find('## 1. 公共资源 API')
    if sec1_idx != -1:
        body = content[sec1_idx:]
        
        # Standardize headers in body
        body = body.replace('## 1. 公共资源 API (Resources API)', '## 三、接口简要索引\n\n### 3.1 公共资源 API')
        body = body.replace('## 2. 配置管理 API (Admin API)', '### 3.2 配置管理 API')
        body = body.replace('### 2.1', '#### 3.2.1')
        body = body.replace('### 2.2', '#### 3.2.2')
        body = body.replace('### 2.3', '#### 3.2.3')
        
        body = body.replace('### 2.4 创建类接口详细文档（标准格式）', '## 四、接口详细说明')
        body = body.replace('#### 2.4.1', '### 4.1')
        body = body.replace('#### 2.4.2', '### 4.2')
        body = body.replace('#### 2.4.3', '### 4.3')
        body = body.replace('#### 2.4.4', '### 4.4')
        body = body.replace('#### 2.4.5', '### 4.5')
        body = body.replace('#### 2.4.6', '### 4.6')

        # Remove old common agreements
        body = re.sub(r'## 3\. 公共约定.*', '', body, flags=re.DOTALL)

        # Add Response param tables
        def add_response_table(match):
            res_json = match.group(0)
            return res_json + "\n\n**响应参数**\n\n`data` 类型为 `String` (ID):\n\n| 字段名 | 类型 | AI决策 | 说明 |\n|---|---|---|---|\n| `data` | String | 是 | 返回的主键 ID |\n"
        
        body = re.sub(r'\*\*成功响应示例\*\*\s+```json.*?```', add_response_table, body, flags=re.DOTALL)
        
        # Add basic info tables
        def replace_basic_info(match):
            url = match.group(1)
            return f"**基本信息**\n\n| 项目 | 说明 |\n|---|---|\n| 接口地址 | `{url}` |\n| 请求方式 | POST |\n| Content-Type | application/json |\n| 数据量级别 | 小 |\n| 预估响应体积 | 约 0.5KB |\n"

        body = re.sub(r'- \*\*Method\*\*: `POST`\s+- \*\*URL\*\*: `([^`]+)`\s+- \*\*Content-Type\*\*: `application/json`\s+- \*\*鉴权\*\*: 需要', replace_basic_info, body)

        final_content = new_header + body
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print("Reformatted and saved successfully.")
    else:
        print("Could not find section 1")

if __name__ == '__main__':
    format_doc()
