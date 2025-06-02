# EMQX MCP Server - Smart Classroom Edition

[![smithery badge](https://smithery.ai/badge/@Benniu/emqx-mcp-server)](https://smithery.ai/server/@Benniu/emqx-mcp-server)

<a href="https://glama.ai/mcp/servers/m7zgbcr053">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/m7zgbcr053/badge" alt="emqx-mcp-server MCP server" />
</a>

A [Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) server implementation specifically enhanced for **Smart Classroom Temperature Monitoring Systems**. This server provides comprehensive EMQX MQTT broker interaction capabilities, enabling seamless integration with classroom IoT devices, EdgeX virtual devices, and eKuiper data processing.

## 🏫 Smart Classroom Integration

This enhanced version is designed to work with:

- **EdgeX Virtual Device Services** - Simulating temperature and humidity sensors
- **eKuiper Stream Processing** - Real-time data analysis and alerting  
- **EMQX Cloud/Local Brokers** - Reliable MQTT message handling
- **Claude Desktop Integration** - AI-powered classroom management

## 🚀 Key Features

### 🌡️ Smart Classroom Tools

- **Real-time Temperature Monitoring**: Monitor classroom temperature and humidity data
- **Intelligent AC Control**: Automatically control air conditioning based on temperature thresholds  
- **Alert System**: Send customizable alerts for temperature anomalies
- **Trend Analysis**: Analyze temperature trends and provide intelligent suggestions
- **Device Management**: Monitor and control classroom IoT devices

### 📡 Enhanced MQTT Capabilities

- **Topic Subscription**: Subscribe to MQTT topics with wildcard support (classroom/#)
- **Real-time Message Monitoring**: Continuous monitoring with message history
- **Bi-directional Communication**: Both publish and subscribe functionality
- **EdgeX Integration**: Direct integration with EdgeX virtual device data streams

### 🔧 Core MQTT Operations

- **Client Management**: View, monitor, and disconnect MQTT clients
- **Message Publishing**: Send messages with QoS control and retention
- **Topic Subscription**: Subscribe to topics with pattern matching
- **Connection Control**: Manage broker connections and authentication

## 📁 Project Structure

```
emqx-mcp-server-main/
├── src/emqx_mcp_server/          # Main source code
│   ├── __main__.py               # Package entry point
│   ├── server.py                 # MCP server implementation
│   ├── config.py                 # Configuration management
│   └── tools/                    # MCP tool modules
├── config/                       # Configuration files
├── tests/                        # Test files
├── docs/                         # Documentation
└── README.md                     # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- EMQX broker (local or cloud)
- Claude Desktop (for MCP integration)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd emqx-mcp-server-main
   ```

2. **Install dependencies**

   ```bash
   pip install -e .
   ```

3. **Configure environment**

   Copy `.env.example` to `.env` and update with your EMQX settings:

   ```bash
   cp .env.example .env
   ```

4. **Configure Claude Desktop**

   Copy the configuration to your Claude Desktop config:

   ```json
   {
     "mcpServers": {
       "emqx-smart-classroom": {
         "command": "python",
         "args": ["-m", "emqx_mcp_server"],
         "cwd": "/path/to/your/emqx-mcp-server-main",
         "env": {
           "EMQX_BROKER_HOST": "broker.emqx.io",
           "EMQX_BROKER_PORT": "1883",
           "CLASSROOM_ID": "classroom_01",
           "CLASSROOM_TOPIC_PREFIX": "classroom"
         }
       }
     }
   }
   ```

## 🚀 Quick Start

### Running the MCP Server

```bash
python -m emqx_mcp_server
```

### Testing MQTT Connection

```bash
python tests/test_mqtt_connection.py
```

## 📖 Usage Examples

### Subscribe to Classroom Topics

Use the MCP tools to subscribe to all classroom-related messages:

```
Topic Pattern: classroom/#
```

### Publish Temperature Data

Send temperature readings to the monitoring system:

```
Topic: classroom/temperature/sensor01
Payload: {"temperature": 23.5, "humidity": 45.2, "timestamp": "2025-05-31T10:30:00Z"}
```

### Monitor Device Status

Track classroom device connectivity and status:

```
Topic: classroom/devices/status
```

## 🔧 Configuration

### Environment Variables

- `EMQX_BROKER_HOST`: MQTT broker hostname
- `EMQX_BROKER_PORT`: MQTT broker port
- `EMQX_USERNAME`: MQTT username (optional)
- `EMQX_PASSWORD`: MQTT password (optional)
- `CLASSROOM_ID`: Unique classroom identifier
- `CLASSROOM_TOPIC_PREFIX`: Topic prefix for classroom messages

### MQTT Topics

- `classroom/{classroom_id}/temperature` - Temperature sensor data
- `classroom/{classroom_id}/humidity` - Humidity sensor data
- `classroom/{classroom_id}/ac/control` - AC control commands
- `classroom/{classroom_id}/alerts` - Alert notifications

## 🧪 Testing

Run the test suite:

```bash
# Test MQTT connectivity
python tests/test_mqtt_connection.py

# Test MCP server functionality  
python tests/test_server.py
```

## 📚 Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed project organization
- [Setup Guide](docs/CLASSROOM_SETUP_GUIDE.md) - Complete setup instructions
- [Setup Complete](docs/SETUP_COMPLETE.md) - Feature completion status

## 🤝 Integration with EdgeX

This MCP server integrates seamlessly with EdgeX virtual devices:

1. EdgeX virtual devices generate temperature/humidity data
2. Data flows through eKuiper for processing and alerting
3. EMQX handles reliable message delivery
4. MCP server provides AI-powered monitoring and control

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🆘 Support

For issues and questions:

1. Check the [documentation](docs/)
2. Review [test files](tests/) for usage examples
3. Open an issue on the repository

---

**Note**: This version is specifically optimized for smart classroom environments with enhanced MQTT subscription capabilities and real-time monitoring features.
