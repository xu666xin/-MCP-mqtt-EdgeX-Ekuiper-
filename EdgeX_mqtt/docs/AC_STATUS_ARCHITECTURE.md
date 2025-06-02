# 智能教室空调状态查询架构设计

## 概述

重新设计了空调状态查询系统，将控制命令流和状态查询流分离，实现了正确的数据流向。

## 数据流架构

### 1. 控制流 (AC Control Stream)

- **输入源**: MQTT 主题 `classroom/control/ac`
- **数据流向**: Smart Classroom Tools → MQTT → eKuiper → EdgeX
- **功能**: 处理空调开关和温度设置命令

```
Smart Classroom Tools 
    ↓ (发送控制命令)
MQTT Topic: classroom/control/ac
    ↓
eKuiper AC Control Stream
    ↓ (处理命令)
EdgeX Device Service
```

### 2. 状态查询流 (AC Status Stream)

- **输入源**: EdgeX Events
- **数据流向**: EdgeX → eKuiper → MQTT → Smart Classroom Tools
- **功能**: 当收到状态请求时，从 EdgeX 获取设备状态并转发到 MQTT

```
Smart Classroom Tools 
    ↓ (发送状态请求)
MQTT Topic: classroom/request/status
    ↓
eKuiper Status Request Handler
    ↓ (触发 EdgeX 查询)
EdgeX Device Service
    ↓ (返回设备状态)
eKuiper Status Forward Rule
    ↓ (转发状态数据)
MQTT Topics: classroom/ac/power/status, classroom/ac/temperature/status
    ↓
Smart Classroom Tools (接收状态)
```

## 新增的 eKuiper 流和规则

### 数据流 (Streams)

1. **ac_control_stream** - 空调控制流
   - 监听: `classroom/control/ac`
   - 处理: 控制命令 (set_power, set_temperature)

2. **ac_status_stream** - 空调状态流 (新增)
   - 监听: EdgeX Events
   - 处理: 设备状态数据

3. **status_request_stream** - 状态请求流 (新增)
   - 监听: `classroom/request/status`
   - 处理: 状态查询请求

### 规则 (Rules)

1. **ac_power_control** - 空调电源控制
   - 处理 `set_power` 命令
   - 发送状态到 `classroom/ac/power/status`

2. **ac_temperature_control** - 空调温度控制
   - 处理 `set_temperature` 命令
   - 发送状态到 `classroom/ac/temperature/status`

3. **ac_status_forward** - 空调状态转发 (新增)
   - 从 EdgeX Events 获取设备状态
   - 转发到 MQTT 状态主题

4. **ac_status_request_handler** - 状态请求处理器 (新增)
   - 监听状态请求
   - 触发 EdgeX 设备读取

## 工作流程

### 空调控制流程

1. Smart Classroom Tools 发送控制命令到 `classroom/control/ac`
2. eKuiper 接收命令并解析
3. eKuiper 调用 EdgeX REST API 执行设备操作
4. eKuiper 发送操作状态到对应的状态主题

### 状态查询流程

1. Smart Classroom Tools 发送状态请求到 `classroom/request/status`
2. eKuiper 接收请求并触发 EdgeX 设备读取
3. EdgeX 返回设备当前状态
4. eKuiper 将状态数据转发到 MQTT 状态主题
5. Smart Classroom Tools 从状态主题接收最新状态

## 主题映射

| 功能 | MQTT 主题 | 方向 | 说明 |
|------|-----------|------|------|
| 空调控制 | `classroom/control/ac` | Tools → eKuiper | 发送控制命令 |
| 状态请求 | `classroom/request/status` | Tools → eKuiper | 请求设备状态 |
| 电源状态 | `classroom/ac/power/status` | eKuiper → Tools | 电源开关状态 |
| 温度状态 | `classroom/ac/temperature/status` | eKuiper → Tools | 目标温度状态 |

## 优势

1. **清晰的数据流分离**: 控制流和状态流完全分离，逻辑清晰
2. **正确的数据源**: 状态数据来自 EdgeX，确保数据的权威性
3. **实时响应**: 状态请求触发即时的设备读取
4. **统一的数据格式**: 所有工具使用相同的数据解析逻辑
5. **可扩展性**: 可以轻松添加更多设备类型和状态
