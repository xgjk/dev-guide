# Obsidian 同步场景 API 实测报告

**测试目标**：验证 `uploadContent` 新建文本与更新版本机制，以及 `getFullFileContent` 拉取内容的实时性（排查是否存在之前使用物理资源上传导致的异步解析滞后问题）。

## Step 1: 新建纯文本文件 (uploadContent)

**Request**: `POST https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/uploadContent`
**Request Body**:
```json
{
  "content": "# V1 初始内容\n\n这是来自 Agent 的第一次自动化创建。",
  "fileName": "API测试_Obsidian同步用例",
  "fileSuffix": "md",
  "folderName": "自动测试专用"
}
```
**Response**:
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "projectId": "1760145882959187970",
    "projectName": "成伟的个人知识库",
    "folderId": "2050604725472133121",
    "folderName": "自动测试专用",
    "fileId": "2050604737211990017",
    "fileName": "API测试_Obsidian同步用例.md",
    "downloadUrl": "https://minio-szkz.mediportal.com.cn:9443/files/58/2050604733772845058.md?response-accept-ranges=bytes&response-content-disposition=attachment%3B%20filename%3D%22API%E6%B5%8B%E8%AF%95_Obsidian%E5%90%8C%E6%AD%A5%E7%94%A8%E4%BE%8B.md%22&response-content-type=application%2Foctet-stream&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=dev%2F20260502%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260502T155402Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=8f135654ccc95cc70d2f890f1e6b5005eb2a23db12e070c9c1e1d4221cbe8ad2"
  }
}
```
---

## Step 2: 获取全文验证 V1 (getFullFileContent)

**Request**: `GET https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/getFullFileContent?fileId=2050604737211990017`
**Response**:
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```
---

## Step 3: 追加新版本 (uploadContent 版本更新模式)

**Request**: `POST https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/uploadContent`
**Request Body**:
```json
{
  "updateFileId": "2050604737211990017",
  "content": "# V2 更新内容\n\n这是第二次覆盖更新的内容，验证是否会立刻生效。",
  "fileName": "API测试_Obsidian同步用例",
  "fileSuffix": "md",
  "versionName": "V2.0",
  "versionRemark": "自动测试脚本更新"
}
```
**Response**:
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "fileId": "2050604737211990017",
    "fileName": "API测试_Obsidian同步用例.md"
  }
}
```
---

## Step 4: 获取全文验证 V2 更新是否实时生效 (getFullFileContent)

**Request**: `GET https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/getFullFileContent?fileId=2050604737211990017`
**Response**:
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": null
}
```
---

## Step 5: 获取历史版本列表 (getVersionList)

**Request**: `GET https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/getVersionList?fileId=2050604737211990017`
**Response**:
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": [
    {
      "id": "2050604749350305794",
      "fileId": "2050604737211990017",
      "versionNumber": 2,
      "versionName": "V2.0",
      "remark": "自动测试脚本更新",
      "status": 1,
      "resourceId": "2050604748683603971",
      "resourceType": "upload",
      "fileType": "file",
      "label": null,
      "createBy": "1514822118611259394",
      "creator": "成伟",
      "createTime": 1777737245000,
      "updater": "成伟",
      "updateTime": 1777737245000,
      "lastVersion": true,
      "fileName": null
    },
    {
      "id": "2050604737216184321",
      "fileId": "2050604737211990017",
      "versionNumber": 1,
      "versionName": null,
      "remark": null,
      "status": 2,
      "resourceId": "2050604733772845058",
      "resourceType": "upload",
      "fileType": "file",
      "label": null,
      "createBy": "1514822118611259394",
      "creator": "成伟",
      "createTime": 1777737242000,
      "updater": "成伟",
      "updateTime": 1777737242000,
      "lastVersion": null,
      "fileName": null
    }
  ]
}
```
---

## Step 6: 清理测试产生的脏数据 (deleteFile)

**Request**: `POST https://sg-al-cwork-web.mediportal.com.cn/open-api/document-database/file/deleteFile`
**Request Body**:
```json
{
  "fileId": "2050604737211990017",
  "isPhysical": true
}
```
**Response**:
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": true
}
```
---
