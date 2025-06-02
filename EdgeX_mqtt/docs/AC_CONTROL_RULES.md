# 空调控制规则说明

## 🎯 空调控制的工作流程

### 📡 MQTT 主题结构

```
classroom/
├── temperature          # EdgeX传感器 → EMQX (温度数据)
├── humidity            # EdgeX传感器 → EMQX (湿度数据)
└── control/ac          # EMQX → EdgeX (空调控制命令)
```

### 🔄 双向数据流

#### 1. 传感器数据流出 (EdgeX → EMQX)

```
EdgeX虚拟设备 → eKuiper规则 → EMQX Cloud → MCP工具
```

#### 2. 控制命令流入 (EMQX → EdgeX)

```
MCP工具 → EMQX Cloud → eKuiper规则 → EdgeX虚拟设备
```

## 🛠️ eKuiper 规则配置

### 创建的规则文件

1. **`create_classroom_stream.json`** - 创建数据流
2. **`create_ac_control_source.json`** - 创建空调控制数据源
3. **`simple_data_forward.json`** - 温度数据转发
4. **`humidity_forward.json`** - 湿度数据转发
5. **`ac_power_control.json`** - 空调开关控制
6. **`ac_temperature_control.json`** - 空调温度控制

### 空调控制规则详解

#### 1. 创建MQTT数据源

```json
{
  "id": "ac_control_subscriber",
  "sql": "CREATE SOURCE ac_control_source WITH (
    FORMAT=\"json\", 
    TYPE=\"mqtt\", 
    SERVERS=\"[\\\"ssl://zd89891c.ala.cn-hangzhou.emqxsl.cn:8883\\\"]\", 
    TOPIC=\"classroom/control/ac\", 
    USERNAME=\"xu666xin\", 
    PASSWORD=\"123456\"
  )"
}
```

#### 2. 空调开关控制

```json
{
  "sql": "SELECT command, value, device FROM ac_control_source WHERE command = 'set_power'",
  "actions": [{
    "rest": {
      "url": "http://localhost:59882/api/v3/device/name/classroom-ac-controller/ac_power",
      "method": "PUT",
      "bodyTemplate": "{\"ac_power\": \"{{.value}}\"}"
    }
  }]
}
```

#### 3. 空调温度控制

```json
{
  "sql": "SELECT command, value, device FROM ac_control_source WHERE command = 'set_temperature'",
  "actions": [{
    "rest": {
      "url": "http://localhost:59882/api/v3/device/name/classroom-ac-controller/target_temperature",
      "method": "PUT",
      "bodyTemplate": "{\"target_temperature\": \"{{.value}}\"}"
    }
  }]
}
```

## 🚀 部署方式

### 方式1: 使用自动部署脚本

```bash
cd EdgeX_mqtt/scripts
./deploy_complete_rules.sh
```

### 方式2: 手动部署

```bash
cd EdgeX_mqtt

# 1. 创建数据流
curl -X POST "http://localhost:9081/streams" \
  -H "Content-Type: application/json" \
  -d @rules/create_classroom_stream.json

# 2. 创建空调控制源  
curl -X POST "http://localhost:9081/streams" \
  -H "Content-Type: application/json" \
  -d @rules/create_ac_control_source.json

# 3. 部署所有规则
for rule in rules/*.json; do
  if [[ $rule != *"create"* ]]; then
    curl -X POST "http://localhost:9081/rules" \
      -H "Content-Type: application/json" \
      -d @$rule
  fi
done
```

## 🔧 控制命令格式

### 空调开关控制

发送到 `classroom/control/ac`:

```json
{
  "command": "set_power",
  "value": true,
  "timestamp": "2025-06-01T12:00:00Z",
  "device": "classroom-ac-controller"
}
```

### 空调温度控制

发送到 `classroom/control/ac`:

```json
{
  "command": "set_temperature", 
  "value": 24.5,
  "unit": "°C",
  "timestamp": "2025-06-01T12:00:00Z",
  "device": "classroom-ac-controller"
}
```

## 🔍 故障排除

### 检查规则状态

```bash
curl http://localhost:9081/rules
```

### 检查数据流

```bash
curl http://localhost:9081/streams
```

### 检查EdgeX设备

```bash
curl http://localhost:59881/api/v3/device/all
```

### 测试空调控制

```bash
# 开启空调
curl -X PUT "http://localhost:59882/api/v3/device/name/classroom-ac-controller/ac_power" \
  -H "Content-Type: application/json" \
  -d '{"ac_power": "true"}'

# 设置温度
curl -X PUT "http://localhost:59882/api/v3/device/name/classroom-ac-controller/target_temperature" \
  -H "Content-Type: application/json" \
  -d '{"target_temperature": "24.0"}'
```

## 📋 API端口说明

- **eKuiper**: 9081 (规则引擎)
- **EdgeX Core Data**: 59880 (数据服务)
- **EdgeX Core Metadata**: 59881 (元数据服务)
- **EdgeX Core Command**: 59882 (命令服务)
- **EdgeX UI**: 4000 (管理界面)

---

💡 **关键点**: 空调控制是通过eKuiper订阅MQTT消息，然后调用EdgeX Command API来实现的！
