#!/bin/bash
# 温度控制系统 - 快速环境设置脚本
# Quick Environment Setup Script for Temperature Control System

echo "🌡️ 温度控制系统 - 环境设置"
echo "======================================"

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查 Python 版本
echo "🐍 检查 Python 版本..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ $python_version"
else
    echo "❌ Python3 未找到，请先安装 Python 3.10+"
    exit 1
fi

# 在根目录中创建虚拟环境
cd "$PROJECT_ROOT" || {
    echo "❌ 无法进入项目根目录"
    exit 1
}

# 删除旧的虚拟环境 (如果存在)
if [ -d "venv" ]; then
    echo "🗑️  删除旧的虚拟环境..."
    rm -rf venv
fi

# 创建新的虚拟环境
echo "📦 在根目录创建新的虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "❌ requirements.txt 文件未找到"
    exit 1
fi

# 验证安装
echo ""
echo "🧪 验证安装..."
python -c "import mcp; print('✅ MCP 安装成功')" 2>/dev/null || echo "❌ MCP 安装失败"
python -c "import paho.mqtt.client; print('✅ MQTT 客户端安装成功')" 2>/dev/null || echo "❌ MQTT 客户端安装失败"
python -c "import requests; print('✅ Requests 安装成功')" 2>/dev/null || echo "❌ Requests 安装失败"

echo ""
echo "🎉 环境设置完成！"
echo ""
echo "📝 使用说明:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 配置 .env 文件: cd emqx-mcp-server-main && cp .env.example .env (然后编辑实际配置)"
echo "3. 启动 MCP 服务器: cd emqx-mcp-server-main && python -m emqx_mcp_server"
echo "4. 运行测试: cd emqx-mcp-server-main && python tests/test_server.py"
echo "5. 运行演示: cd emqx-mcp-server-main && python demo_temperature_control.py"
echo ""
echo "🔗 相关命令:"
echo "- 启动 EdgeX 系统: cd EdgeX_mqtt && ./scripts/start_classroom_system.sh"
echo "- 检查系统状态: cd EdgeX_mqtt && ./scripts/check_system_status.sh"
echo "- 监控 MQTT 数据: cd EdgeX_mqtt && python scripts/monitor_mqtt_data.py"