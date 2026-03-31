## 安装

通过 npm 包安装，一条命令完成安装，依赖由 OpenClaw 自动处理：
openclaw plugins install @xgjktech/xg_cwork_im

## 配置

### 步骤 1：启用并信任插件

执行以下命令，将 xg_cwork_im 插件添加到 OpenClaw 的信任白名单中：
openclaw plugins enable xg_cwork_im

### 步骤 2：配置 Channel 账户信息

#### 2.1 注册玄关开放平台机器人虚拟账号

需要通过此通道聊天的agent，必须先注册一个机器人appkey，注册方式（调用以下接口）：

``` 

curl --location 'https://sg-al-cwork-web.mediportal.com.cn/open-api/im/robot/register' \
--header 'appKey: \${需替换为你个人的appKey}' \
--header 'Content-Type: application/json' \
--data '{
    "agentId": "机器人agentId,必填",\
    "name": "机器人名称，必填",
    "remark": "备注信息",
     //visibleType=2时必填
    "visibleRange": \[
        {
            "targetId": "人员id或者部门id",
            "targetType": "USER表示人员, DEPT表示部门"
        }
    ],
    "visibleType": 0//可见性类型: 0-私有(默认), 1-公开, 2-指定范围
}'
```
响应参数示例：

```json
{
    "resultCode": 1,
    "data": {
		"appKey":"机器人的认证AppKey"
	}
}
```

#### 2.3 修改openclaw.json配置文件

编辑 \~/.openclaw/openclaw.json，添加以下配置（main为agentId，如果有定义其他的agentId，请替换为实际的）：

```json
{
  "channels": {
    "xg_cwork_im": {
      "baseUrl": "https://sg-al-cwork-web.mediportal.com.cn",
      "wsBaseUrl": "wss://sg-al-cwork-web.mediportal.com.cn",
      "accounts": {
        "main": { "appKey": "你的机器人 appKey", "agentId": "main", "name": "个人助手" }
      }
    }
  }
}
```

### 完整配置参考

```json
{
  "channels": {
    "xg_cwork_im": {
      "baseUrl": "https://sg-al-cwork-web.mediportal.com.cn",
      "wsBaseUrl": "wss://sg-al-cwork-web.mediportal.com.cn",
      "debug": false,
      "maxConnectionAttempts": 200,
      "maxReconnectDelay": 120000,
      // 生产环境可根据需要调整首回复超时时间（毫秒）
      "firstReplyTimeoutMs": 600000,
      "accounts": {
         "main": { "appKey": "机器人的认证AppKey", "agentId": "main", "name": "个人助手" }
         "sales": { "appKey": "机器人的认证AppKey", "agentId": "sales", "name": "销售助理" }
      }
    }
  },
  
  "bindings": [
    { "type": "route", "agentId": "main", "match": { "channel": "xg_cwork_im", "accountId": "main" } },
    { "type": "route", "agentId": "sales", "match": { "channel": "xg_cwork_im", "accountId": "sales" } }
  ]
}
```

### 步骤 3：重启 Gateway

配置完成后，重启网关使配置生效：
openclaw gateway restart

## 更新插件

openclaw plugins update xg_cwork_im

## 注意事项

1、注册机器人，相当于在玄关开发平台注册了一个虚拟用户，对应的appKey是这个虚拟用户的身份信息，xg_cwork_im插件是依赖这个appKey打通openclaw的agent和玄关开放平台的机器人。

2、注册机器人的接口，header需要的appKey是当前真实用户的key，后台为了记录是谁注册的机器人。

3、openclaw.json配置文件中，需要的appKey是机器人的,不是当前用户的，请注意区分。

4、修改openclaw.json文件时，请务必小心，不要修改其示例之外的其他配置。如果channels中已有其他通道的配置，请注意保留，不要随意修改或者删除。