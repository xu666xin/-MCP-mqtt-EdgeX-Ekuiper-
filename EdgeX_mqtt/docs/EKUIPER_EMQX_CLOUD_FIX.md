# eKuiper连接EMQX Cloud问题解决方案

## 问题描述

AC开头的两个规则（ac_power_control 和 ac_temperature_control）每次都说连接本地MQTT失败，但实际需要连接的是EMQX Cloud。

## 问题原因

1. **MQTT源配置问题**：eKuiper的MQTT源配置键名不正确
2. **环境变量配置错误**：Docker Compose中的环境变量格式不符合eKuiper要求
3. **配置文件缺失**：缺少正确的MQTT源配置文件
4. **流定义问题**：AC控制规则使用了错误的数据源

## 解决方案

### 1. 修复Docker Compose配置

在 `docker-compose.yml` 中的 `rulesengine` 服务环境变量已修复为：

```yaml
environment:
  # ... 其他配置 ...
  CONNECTIONS__MQTT__EMQX_CLOUD__SERVER: "ssl://zd89891c.ala.cn-hangzhou.emqxsl.cn:8883"
  CONNECTIONS__MQTT__EMQX_CLOUD__USERNAME: "xu666xin"
  CONNECTIONS__MQTT__EMQX_CLOUD__PASSWORD: "123456"
  CONNECTIONS__MQTT__EMQX_CLOUD__PROTOCOLVERSION: "3.1.1"
  CONNECTIONS__MQTT__EMQX_CLOUD__INSECURESKIPVERIFY: "true"
  CONNECTIONS__MQTT__EMQX_CLOUD__QOS: 1
  CONNECTIONS__MQTT__EMQX_CLOUD__BUFFERLENGTH: 1024
```

### 2. 创建MQTT源配置文件

创建了 `config/mqtt_source.yaml` 文件，包含EMQX Cloud连接配置。

### 3. 修复AC控制规则

- 创建了专门的 `ac_control_stream` 数据流
- 更新了 `ac_power_control.json` 和 `ac_temperature_control.json` 规则文件

### 4. 更新脚本

创建了 `update_ekuiper_rules.sh` 脚本来重新部署AC控制规则。

## 执行步骤

### 步骤1：重新部署Docker服务

```bash
cd EdgeX_mqtt
docker-compose down
docker-compose up -d
```

### 步骤2：等待服务启动

等待约30秒让所有服务完全启动。

### 步骤3：运行更新脚本

```bash
./update_ekuiper_rules.sh
```

### 步骤4：验证连接

检查规则状态：

```bash
curl -s http://localhost:59720/rules | jq '.'
```

检查数据流状态：

```bash
curl -s http://localhost:59720/streams | jq '.'
```

## 验证方法

### 1. 检查AC控制规则状态

```bash
curl -s http://localhost:59720/rules/ac_power_control | jq '.'
curl -s http://localhost:59720/rules/ac_temperature_control | jq '.'
```

### 2. 测试MQTT连接

可以通过EMQX Cloud的WebSocket客户端测试连接：

- 服务器：`wss://zd89891c.ala.cn-hangzhou.emqxsl.cn:8084/mqtt`
- 用户名：`xu666xin`
- 密码：`123456`

### 3. 发送测试消息

向以下主题发送测试消息：

- `classroom/control/ac/power`
- `classroom/control/ac/temperature`

## 常见问题

### Q: 规则仍然报连接错误？

A: 检查EMQX Cloud服务是否正常，确认网络连接正常。

### Q: 环境变量不生效？

A: 重新启动Docker容器：`docker-compose restart rulesengine`

### Q: 如何查看eKuiper日志？

A: `docker logs edgex-kuiper -f`

## 配置文件说明

### docker-compose.yml

- 正确的eKuiper环境变量格式
- 挂载MQTT配置文件

### config/mqtt_source.yaml

- EMQX Cloud连接参数
- SSL/TLS配置

### rules/create_ac_control_stream.json

- 专门为AC控制创建的MQTT数据流
- 使用 `emqx_cloud` 配置键

### AC控制规则文件

- `ac_power_control.json`：空调开关控制
- `ac_temperature_control.json`：空调温度控制

这些修改确保eKuiper正确连接到EMQX Cloud而不是本地MQTT服务器。
