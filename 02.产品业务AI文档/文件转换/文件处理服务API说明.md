# 文件处理服务 API 文档

> **服务**：`file-processing-service` — 将办公文档转为 **Markdown**，供检索、AI 摘要等场景使用。  
> **鉴权**：所有 `/v1/*` 业务接口须在请求头携带 **`appKey`**，由服务端校验并解析调用方身份。

## 修订记录

| 版本 | 日期       | 变更摘要 | 变更人 |
| ---- | ---------- | -------- | ------ |
| 1.0  | 2026-05-13 | 初版 | 待补充 |
| 1.1  | 2026-05-13 | 补充同步类接口约束说明 | 待补充 |
| 1.2  | 2026-05-13 | 补充体积、超时、PDF/OCR 限制说明 | 待补充 |
| 1.3  | 2026-05-19 | 整理结构：接口总览、缓存字段、Webhook | 待补充 |
| 1.4  | 2026-05-19 | 对接文档改为 appKey 鉴权；固定生产 Base URL | 待补充 |
| 1.5  | 2026-05-19 | 对接范围仅保留 multipart 直传及任务查询 | 待补充 |
| 1.6  | 2026-05-21 | 补充生产网关 500MB、同步/异步体积分层及同步大文件网关超时说明 | 待补充 |

---

## 一、接口总览

**生产 Base URL**：`https://file-processing-service.mediportal.com.cn`

| 方法 | 路径 | 说明 | HTTP |
| ---- | ---- | ---- | ---- |
| GET | `/health` | 存活探针 | 200 |
| GET | `/ready` | 就绪探针 | 200 |
| POST | `/v1/convert/upload-sync` | 上传文件 **同步**转 Markdown | 200 |
| POST | `/v1/convert/upload-jobs` | 上传文件 **异步**建单 | **202** |
| GET | `/v1/convert/jobs/{job_id}` | 查询异步任务状态与结果 | 200 |

**完整 URL 示例**：`https://file-processing-service.mediportal.com.cn/v1/convert/upload-sync`

**不参与统一信封**：`/health`、`/ready`（见 **2.3**）。

---

## 二、通用说明

### 2.1 访问地址

```
https://file-processing-service.mediportal.com.cn{接口路径}
```

示例：

```
https://file-processing-service.mediportal.com.cn/v1/convert/upload-sync
https://file-processing-service.mediportal.com.cn/v1/convert/upload-jobs
```

### 2.2 公共请求头

| 请求头 | 必填 | 说明 |
| ------ | ---- | ---- |
| **`appKey`** | 是 | 应用密钥；服务端经协同 **`getEmpInfoByAppKey`** 解析调用方身份，用于落库审计及（若开启）FileGPT OCR |

亦支持 **`X-App-Key`**（与 **`appKey`** 等价）；**本文示例统一使用 `appKey`**。

**鉴权失败**：返回 **401**，`resultMsg` 多为 appKey 缺失、无效或协同返回的错误说明。

### 2.3 统一响应体（`/v1/*`）

成功时根级结构：

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": { }
}
```

| 字段 | 说明 |
| ---- | ---- |
| `resultCode` | **`1`** 成功；失败一般为 **`0`** |
| `resultMsg` | 失败说明；成功多为 `null` |
| `data` | 业务对象（下文「响应」均指 `data` 内容） |

### 2.4 Content-Type

业务接口使用 **`multipart/form-data`**，表单字段名 **`file`**（上传源文件）。

### 2.5 网关与业务体积、超时（生产）

生产域名 `file-processing-service.mediportal.com.cn` 前为 **OpenResty** 反向代理。调用方须区分 **网关限制** 与 **应用服务限制**（两层叠加，任一不满足即失败）。

| 层级 | 配置项（运维） | 生产当前值 | 说明 |
| ---- | -------------- | ---------- | ---- |
| **网关** | `client_max_body_size` 等 | **500 MB** | 单次 HTTP 请求体（含 multipart 上传）最大约 **500MB**；此前约 20MB 时大文件会返回 **413**，响应体为 HTML 且页脚含 `openresty` |
| **应用 · 同步** | `SYNC_MAX_BYTES` / `UPLOAD_SYNC_MAX_BYTES` | 默认约 **100 MB** | `upload-sync` 等业务校验；超限返回 **413**，响应为统一 JSON 信封，`detail` 含字节上限 |
| **应用 · 异步** | `ASYNC_JOB_MAX_BYTES` / `UPLOAD_ASYNC_MAX_BYTES` | 默认约 **500 MB** | `upload-jobs` 及异步任务下载源文件上限 |

**同步接口与网关超时**：`upload-sync` 在一次 HTTP 连接内完成「上传 + 转换 +（可选）内嵌图 OCR」，大体积 PPTX/PDF 或开启 OCR 时**处理时间可达数分钟**。生产网关 **upstream 读超时**（如 `proxy_read_timeout`，常见默认约 **60s**）往往**小于**实际转换耗时，此时客户端会看到 **504 Gateway Time-out**，响应体为 **HTML** 且页脚含 **`openresty`**——**并非**应用返回的 JSON，也**不代表**转换一定失败（后台可能仍在执行，但同步响应已无法通过该连接返回）。

**对接建议**：

| 场景 | 推荐接口 |
| ---- | -------- |
| 单文件较大（如数十 MB 的 PPTX）、或需内嵌图 OCR | **`POST /v1/convert/upload-jobs`** + **`GET /v1/convert/jobs/{job_id}`** 轮询（见 **场景二**） |
| 小文件、需立即拿 `markdown` | **`POST /v1/convert/upload-sync`**（见 **场景一**） |
| 同步出现 **504 HTML + openresty** | 改用异步；勿反复用 `upload-sync` 重试同一超大文件 |

若业务必须坚持同步且文件接近 100MB，须与运维协调**同步调大**网关 upstream 超时（如 `proxy_read_timeout`），并评估连接占用；**仍建议大文件走异步**。

---

## 三、业务流程

### 场景一：同步直传

适用于**小文件、低耗时**场景（如小 docx/txt）。大体积或 OCR 场景见 **2.5**，易遇网关 **504**。

1. 请求头携带 **`appKey`**，表单上传 **`file`**。
2. 调用 `POST /v1/convert/upload-sync`。
3. 从 `data.markdown` 取正文。

### 场景二：异步直传 + 轮询（大文件推荐）

适用于**数十 MB 级 PPTX/PDF**、内嵌图 OCR 等耗时较长的场景；不受同步网关「单次 HTTP 须等完全部算完」限制。

1. 调用 `POST /v1/convert/upload-jobs` → 记录 `data.job_id`（HTTP **202**）。
2. 每 **2～5 秒** 调用 `GET /v1/convert/jobs/{job_id}`，直至 `status` 为 `succeeded` 或 `failed`。
3. 关注 `expires_at`（结果默认保留约 **7 天**）。

### 场景三：异步直传 + Webhook

1. 建单时在表单中填写 `callback_url`（可选 `callback_secret`）。
2. 任务终态后服务向回调地址 **POST** JSON；亦可用 **场景二** 查询 `callback_delivery_status`。

---

## 四、接口详情

**占位符**：`{appKey}` 替换为实际应用密钥；`{jobId}` 为任务 UUID。

**curl 示例**统一使用请求头 **`appKey`**：

```bash
-H 'appKey: {appKey}'
```

### 4.0 探针

#### GET `/health`

- **响应**：`{"status":"ok"}`，无统一信封。

#### GET `/ready`

- **响应**：`status` 为 `ready` 或 `not_ready`；HTTP 仍为 **200**。

```bash
curl -sS "https://file-processing-service.mediportal.com.cn/health"
curl -sS "https://file-processing-service.mediportal.com.cn/ready"
```

---

### 4.1 POST `/v1/convert/upload-sync` — 直传同步

| 项目 | 值 |
| ---- | -- |
| 请求头 | **`appKey`**（必填） |
| Content-Type | `multipart/form-data` |
| 成功 HTTP | 200 |

**表单字段**

| 字段 | 必填 | 说明 |
| ---- | ---- | ---- |
| `file` | 是 | 源文件 |
| `force_reconvert` | 否 | `true` / `1` / `yes` / `on`（不区分大小写）为真；为真时跳过结果缓存并强制重算 |

**响应 `data`**：见 **5.1**。

**约束**

| 项 | 说明 |
| -- | ---- |
| 单文件 | 每请求仅一个 **`file`** |
| 网关请求体 | 生产 OpenResty 约 **500MB**；超过返回 **413**（HTML，`openresty`），见 **2.5** |
| 应用体积上限 | 同步默认约 **100MB**（`SYNC_MAX_BYTES`）；超过返回 **413**（JSON 统一信封） |
| 并发 | 服务内转换槽有限，高峰可能 **503** 或 **429** |
| 处理耗时 | 大文件或 OCR 场景耗时可至数分钟 |
| 网关超时 | 同步须在一次 HTTP 内等待完成；生产网关 upstream 超时常见约 **60s**，大文件易 **504**（HTML，`openresty`），见 **2.5** |
| **大文件推荐** | **勿依赖** `upload-sync`；使用 **`upload-jobs`** 异步（**4.2**、**4.3**） |

```bash
curl -sS --compressed -X POST \
  "https://file-processing-service.mediportal.com.cn/v1/convert/upload-sync" \
  -H 'appKey: {appKey}' \
  -F "file=@/path/to/document.pdf"
```

**响应示例**

```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "markdown": "# 标题\n\n正文...",
    "metadata": {},
    "converter_version": "0.1.0",
    "output_schema_version": "1.0",
    "file_name": "示例.docx",
    "suffix": ".docx",
    "record_job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "cache_hit": false,
    "content_md5": "d41d8cd98f00b204e9800998ecf8427e"
  }
}
```

---

### 4.2 POST `/v1/convert/upload-jobs` — 直传异步建单

| 项目 | 值 |
| ---- | -- |
| 请求头 | **`appKey`**（必填） |
| Content-Type | `multipart/form-data` |
| 成功 HTTP | **202** Accepted |

**表单字段**

| 字段 | 必填 | 说明 |
| ---- | ---- | ---- |
| `file` | 是 | 源文件 |
| `callback_url` | 否 | Webhook URL（须 HTTPS，且通过服务端安全校验） |
| `callback_secret` | 否 | HMAC-SHA256 密钥 |
| `callback_include_result` | 否 | `true` / `1` / `yes` / `on` 为真时，回调体含完整 `markdown` 等 |
| `force_reconvert` | 否 | 同 **4.1** |

**响应 `data`**：见 **5.2**。

**约束**

| 项 | 说明 |
| -- | ---- |
| 网关请求体 | 生产约 **500MB**，与 **2.5** 一致 |
| 应用体积上限 | 默认约 **500MB**（`ASYNC_JOB_MAX_BYTES`） |
| 建单响应 | HTTP **202**，仅返回 `job_id`；转换在后台执行，**不受**同步网关「单次连接须等完全部算完」的限制 |
| 结果获取 | 轮询 **4.3** 或配置 **Webhook**（**场景三**） |

```bash
curl -sS --compressed -X POST \
  "https://file-processing-service.mediportal.com.cn/v1/convert/upload-jobs" \
  -H 'appKey: {appKey}' \
  -F "file=@/path/to/document.docx" \
  -F "callback_url=https://example.com/hook"
```

---

### 4.3 GET `/v1/convert/jobs/{jobId}` — 查询任务

| 项目 | 值 |
| ---- | -- |
| 请求头 | **`appKey`**（必填） |
| 路径参数 | `jobId`（**4.2** 返回的 `job_id`） |

**响应 `data`**：见 **5.3**。

| `status` | 说明 |
| -------- | ---- |
| `queued` / `running` | 进行中，`markdown` 为空 |
| `succeeded` | 含 `markdown`、`metadata` 等 |
| `failed` | 含 `error`、`error_status` |

| HTTP | 场景 |
| ---- | ---- |
| 404 | 任务不存在或已清理 |
| 410 | 已超过 `expires_at` |

```bash
curl -sS --compressed -X GET \
  "https://file-processing-service.mediportal.com.cn/v1/convert/jobs/{jobId}" \
  -H 'appKey: {appKey}'
```

---

## 五、数据结构

### 5.1 ConvertSyncResponse（`data`）

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `markdown` | string | Markdown 正文 |
| `metadata` | object | 扩展元数据（见 **5.4**） |
| `converter_version` | string | 转换栈版本 |
| `output_schema_version` | string | 默认 `"1.0"` |
| `file_name` | string | 文件名 |
| `suffix` | string | 后缀，如 `.pdf` |
| `record_job_id` | string | 可选；同步审计记录 ID，可用 **4.3** 查询 |
| `cache_hit` | bool | 是否命中内容 MD5 缓存 |
| `content_md5` | string | 源文件 MD5（十六进制小写） |

### 5.2 JobAcceptedResponse（`data`）

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `job_id` | string | 任务 UUID |
| `status` | string | 固定 `queued` |

### 5.3 JobStatusResponse（`data`）

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `job_id` | string | 任务 ID |
| `status` | string | `queued` / `running` / `succeeded` / `failed` |
| `created_at` / `started_at` / `finished_at` / `expires_at` | string | 东八区 `YYYY-MM-DD HH:MM:SS` |
| `markdown` / `metadata` / `converter_version` / `file_name` / `suffix` | — | `succeeded` 时 |
| `error` / `error_status` | — | `failed` 时 |
| `cache_hit` / `content_md5` | — | `succeeded` 时 |
| `callback_delivery_status` 等 | — | 建单时配置了 `callback_url` 时有值 |

### 5.4 metadata 常见字段

| 键 | 说明 |
| -- | ---- |
| `title` | 文档标题 |
| `ocr` | 是否走过 FileGPT OCR |
| `pdf_hybrid` | PDF 混合管线 |
| `pdf_pages_total` | PDF 总页数 |
| `embedded_image_count` | 内嵌图数量 |
| `embedded_ocr_count` | 成功写入正文的内嵌图 OCR 节数量 |
| `embedded_ocr_skipped_empty` | OCR 结果 clean 后为空（1-based 图序号） |
| `embedded_ocr_skipped_small` | 因体积过小跳过 OCR |
| `embedded_ocr_skipped_gif` | 因 GIF 跳过 OCR |
| `embedded_ocr_failed_indices` | OCR 失败序号 |
| `embedded_ocr_placeholder_unmatched` | 占位与抽取图数量不一致 |
| `embedded_source_format` | 内嵌图来源：`docx` / `pptx` / `pdf` |

PPTX 转换（RT-018/020）相关配置见部署环境变量：`PPTX_READING_ORDER`、`PPTX_SKIP_BACKGROUND_PICTURES`、`PPTX_LIST_FROM_OOXML`、`PPTX_TABLE_MERGED_CELLS`、`PPTX_CHART_HTML` 等；变更后需 `force_reconvert=true` 刷新缓存。

---

## 六、Webhook 回调

在 **4.2** 建单时可填 `callback_url`。任务 **`succeeded`** 或 **`failed`** 后，服务 **POST** `application/json` 至该地址。

**签名**（配置了 `callback_secret`）：

```
X-Callback-Signature: sha256=<hex>
```

算法：对规范 JSON 正文的 UTF-8 字节做 HMAC-SHA256。

**查询投递结果**：**4.3** 响应中的 `callback_delivery_status`（`sent` / `failed`）、`callback_attempts`、`callback_last_error`。

---

## 七、错误码

### 7.1 `resultCode`

| 值 | 说明 |
| -- | ---- |
| `1` | 成功 |
| `0` | 失败 |

### 7.2 常见 HTTP 状态

| HTTP | 典型场景 |
| ---- | -------- |
| 400 | 缺少 `file`、文件名为空 |
| 401 | appKey 缺失、无效或协同校验失败 |
| 404 | 任务不存在或接口关闭 |
| 410 | 任务结果已过期 |
| 413 | 文件超过体积上限：网关超限多为 **HTML + openresty**（约 **500MB**）；应用超限为 **JSON** 信封（同步约 **100MB**、异步约 **500MB**） |
| 422 | 回调 URL 非法、转换失败等 |
| 429 | 服务繁忙（同步槽满） |
| 502 | OCR 等上游异常 |
| 503 | 服务未就绪或转换排队超时（同步等待转换槽超时，JSON，`detail` 常含 `[convert_slot]`） |
| 504 | **网关** upstream 超时（多见于 **`upload-sync`** 大文件/OCR）；响应多为 **HTML + openresty**，见 **2.5** |

### 7.3 网关错误与业务错误的区分

| 现象 | 来源 | 处理建议 |
| ---- | ---- | -------- |
| **413**，HTML，`<center>openresty</center>` | 网关 `client_max_body_size`（生产约 **500MB**） | 压缩/拆文件，或确认未超过 500MB |
| **413**，JSON，`resultCode: 0` | 应用 `SYNC_MAX_BYTES` / `ASYNC_JOB_MAX_BYTES` | 同步改用异步，或缩小文件至应用上限内 |
| **504**，HTML，`openresty` | 网关 `proxy_read_timeout` 等（同步连接等待过久） | 改用 **`upload-jobs`** + 轮询，勿依赖 `upload-sync` |
| **503**，JSON，`[convert_slot]` | 应用转换槽排队超时 | 稍后重试或改用 **`upload-jobs`** |

---

## 八、注意事项

1. **appKey 保密**：勿写入前端公开代码或日志；由后端服务持有并转发。
2. **大文件与网关 500MB**：生产网关已允许约 **500MB** 请求体，但 **`upload-sync` 应用侧仍约 100MB**，且同步易遇网关 **504**；**数十 MB 以上的 PPTX/PDF、或需 OCR 的文件，应使用 `upload-jobs` 异步接口**（见 **2.5**、**场景二**）。
3. **缓存**：`force_reconvert=true` 强制重新转换；成功响应含 `cache_hit`、`content_md5`。
4. **轮询**：异步任务建议间隔 **2～5 秒**，并关注 `expires_at`。
5. **勿将 504 当作转换失败**：同步连接超时后任务状态不确定；请用异步重新提交并凭 `job_id` 查询终态。
