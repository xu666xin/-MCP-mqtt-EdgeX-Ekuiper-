# EdgeX MQTT 温度控制系统

本目录包含温度控制系统的EdgeX Foundry配置和相关组件，实现了基于EdgeX、eKuiper和EMQX Cloud的物联网数据处理架构。

## 📁 目录结构

```
EdgeX_mqtt/
├── docker-compose.yml              # EdgeX Foundry容器编排配置
├── test_ac_control.py              # 空调控制测试脚本
├── test_ac_status.py               # 空调状态监控测试脚本
├── config/                         # 配置文件目录
│   ├── classroom-device-profile.yaml  # 教室设备档案配置
│   ├── classroom-devices.toml         # 虚拟设备配置
│   └── mqtt_source.yaml              # MQTT数据源配置
├── rules/                          # eKuiper规则配置
│   ├── ac_power_control.json         # 空调电源控制规则
│   ├── ac_power_status.json          # 空调电源状态转发规则
│   ├── ac_temp_status.json           # 空调温度状态转发规则
│   ├── ac_temperature_control.json   # 空调温度控制规则
│   ├── create_ac_control_stream.json # AC控制数据流定义
│   ├── create_classroom_stream.json  # 教室数据流定义
│   ├── humidity_forward.json         # 湿度数据转发规则
│   └── simple_data_forward.json      # 简单数据转发规则（已废弃）
└── scripts/                        # 脚本目录
    ├── check_system_status.sh        # 系统状态检查脚本
    └── init_ekuiper_rules.sh         # eKuiper规则初始化脚本
```

## 🏗️ 系统架构

### 核心组件

1. **EdgeX Foundry**: 物联网边缘计算平台
   - Core Services: Consul, Core Data, Core Metadata, Core Command
   - Application Services: Rules Engine (eKuiper)
   - Device Services: Virtual Device Service

2. **eKuiper**: 边缘流数据处理引擎
   - 数据流处理
   - 规则引擎
   - MQTT数据转发

3. **EMQX Cloud**: 外部MQTT云服务
   - 消息队列
   - 设备通信
   - 数据持久化

### 数据流向

```
虚拟设备 → EdgeX Core Data → eKuiper → EMQX Cloud → MCP工具
     ↑                                        ↓
     ←───── EdgeX Core Command ←── eKuiper ←────
```

## 🎯 功能特性

### 传感器监控

- **温度监控**: 每15秒自动采集教室温度数据 (16-35°C)
- **湿度监控**: 每20秒自动采集教室湿度数据 (30-80%RH)

### 空调控制

- **电源控制**: 远程开关空调设备
- **温度调节**: 设置目标温度 (18-28°C)
- **状态反馈**: 实时监控空调运行状态

### 数据处理

- **实时流处理**: 使用eKuiper进行数据清洗和转换
- **规则引擎**: 自动化控制逻辑
- **MQTT转发**: 数据推送到云端MQTT服务

## 🚀 快速开始

### 1. 启动EdgeX服务

```bash
cd EdgeX_mqtt
docker-compose up -d
```

### 2. 检查服务状态

```bash
# 查看容器状态
docker-compose ps

# 检查EdgeX UI
open http://localhost:4000
```

### 3. 初始化eKuiper规则

```bash
./scripts/init_ekuiper_rules.sh
```

### 4. 验证数据流

```bash
# 监控温湿度数据
python test_ac_status.py

# 测试空调控制
python test_ac_control.py
```

## ⚙️ 配置说明

### 设备配置

**classroom-device-profile.yaml**: 定义设备能力和数据类型

- 温度传感器 (只读)
- 湿度传感器 (只读)  
- 空调状态 (读写)
- 目标温度 (读写)

**classroom-devices.toml**: 虚拟设备实例配置

- 设备名称和标识
- 自动事件时间间隔
- 设备协议配置

### 规则配置

规则分为两类：

**控制规则** (Control Rules):

- `ac_power_control.json`: 处理空调开关命令
- `ac_temperature_control.json`: 处理温度设置命令

**状态规则** (Status Rules):

- `ac_power_status.json`: 转发空调电源状态
- `ac_temp_status.json`: 转发空调温度状态
- `humidity_forward.json`: 转发湿度数据

## 🔧 故障排除

### 常见问题

1. **容器启动失败**

   ```bash
   # 检查端口占用
   docker-compose down
   docker-compose up -d
   ```

2. **设备数据不更新**

   ```bash
   # 重启虚拟设备服务
   docker-compose restart device-virtual
   ```

3. **eKuiper规则异常**

   ```bash
   # 检查规则状态
   curl -X GET http://localhost:59720/rules
   
   # 重新部署规则
   ./scripts/init_ekuiper_rules.sh
   ```

### 日志查看

```bash
# EdgeX Core服务日志
docker-compose logs core-data
docker-compose logs core-metadata

# eKuiper日志  
docker-compose logs kuiper

# 虚拟设备日志
docker-compose logs device-virtual
```

## 📊 监控指标

### 系统状态检查

```bash
# 运行系统状态检查
./scripts/check_system_status.sh
```

### 关键指标

- **设备连接状态**: EdgeX UI → Devices
- **数据采集频率**: 温度15s, 湿度20s, AC状态30s
- **规则执行状态**: eKuiper API `/rules`
- **MQTT连接状态**: EMQX Cloud控制台

## 🔗 相关链接

- [EdgeX Foundry官方文档](https://docs.edgexfoundry.org/)
- [eKuiper用户指南](https://ekuiper.org/docs/zh/latest/)
- [EMQX Cloud控制台](https://cloud.emqx.com/)

## 📝 开发说明

### 添加新设备

1. 修改 `classroom-device-profile.yaml` 添加设备资源
2. 更新 `classroom-devices.toml` 配置设备实例
3. 重启EdgeX容器使配置生效
4. 创建对应的eKuiper规则

### 修改数据采集频率

编辑 `classroom-devices.toml` 中的 `AutoEvents` 配置:

```toml
[[DeviceList.AutoEvents]]
Interval = "10s"  # 修改采集间隔
OnChange = false
SourceName = "temperature"
```

### 自定义规则

在 `rules/` 目录下创建新的JSON规则文件，然后使用eKuiper API部署:

```bash
curl -X POST http://localhost:59720/rules \
  -H "Content-Type: application/json" \
  -d @rules/your_new_rule.json
```
