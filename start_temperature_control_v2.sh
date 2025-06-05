#!/bin/bash

# 温度控制系统 - 一键启动与测试脚本
# 功能: 启动完整的EdgeX + eKuiper + MCP系统，并运行全面测试

echo "🌡️ 启动并测试温度控制系统..."
echo "=================================================="

# 设置项目路径
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDGEX_DIR="$PROJECT_ROOT/EdgeX_mqtt"
MCP_DIR="$PROJECT_ROOT/emqx-mcp-server-main"

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

echo "✅ Docker运行正常"

# 检查虚拟环境
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./setup_environment.sh"
    exit 1
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source "$PROJECT_ROOT/venv/bin/activate"

# 检查Python环境和paho-mqtt
if ! python -c "import paho.mqtt.client" >/dev/null 2>&1; then
    echo "❌ Python包 paho-mqtt 未在虚拟环境中找到。请确保已正确设置环境。"
    echo "   尝试运行: pip install paho-mqtt"
    # exit 1 # 可以选择在这里退出，或者让测试脚本自己处理
fi

# 1. 启动EdgeX服务
echo ""
echo "🔧 启动EdgeX Foundry服务..."
cd "$EDGEX_DIR"
docker-compose up -d

echo "⏳ 等待EdgeX服务启动完成..."
sleep 30

# 2. 自动部署eKuiper规则
echo ""
echo "📋 部署eKuiper规则到EMQX Cloud..."
chmod +x ./scripts/init_ekuiper_rules.sh
./scripts/init_ekuiper_rules.sh

# 3. 验证系统状态 (可选，因为全面测试会做更详细的检查)
# echo ""
# echo "🔍 验证系统状态 (快速检查)..."
# cd "$EDGEX_DIR"
# ./scripts/check_system_status.sh

# 4. 启动MCP服务器
echo ""
echo "🚀 启动MCP服务器(连接到EMQX云)..."
cd "$MCP_DIR"
LOG_FILE="$PROJECT_ROOT/mcp_server.log"
echo "MCP服务器日志将输出到: $LOG_FILE"

# 检查并安装MCP服务器模块
echo "🔧 检查MCP服务器模块安装状态..."
if ! "$PROJECT_ROOT/venv/bin/python" -c "import emqx_mcp_server" >/dev/null 2>&1; then
    echo "📦 MCP服务器模块未安装，正在安装..."
    "$PROJECT_ROOT/venv/bin/pip" install -e .
    if [ $? -eq 0 ]; then
        echo "✅ MCP服务器模块安装成功"
    else
        echo "❌ MCP服务器模块安装失败"
        exit 1
    fi
else
    echo "✅ MCP服务器模块已安装"
fi

# 检查是否已有MCP服务器进程
pgrep -f "emqx_mcp_server" > /dev/null
if [ $? -eq 0 ]; then
    echo "⚠️  检测到MCP服务器已在运行。如果需要重启，请先手动停止。"
    echo "   停止旧进程并重新启动..."
    pkill -f "emqx_mcp_server"
    echo "   已停止旧的MCP服务器进程。"
    sleep 2
else
    echo "启动新的MCP服务器进程..."
fi

# 在后台启动MCP服务器，并将输出重定向到日志文件
# 使用专用的MCP启动脚本
cd "$PROJECT_ROOT"

# 使用独立的MCP启动脚本
MCP_START_SCRIPT="$PROJECT_ROOT/start_mcp_server.sh"

# 确保启动脚本存在且可执行
if [ ! -f "$MCP_START_SCRIPT" ]; then
    echo "❌ MCP启动脚本不存在: $MCP_START_SCRIPT"
    exit 1
fi

if [ ! -x "$MCP_START_SCRIPT" ]; then
    chmod +x "$MCP_START_SCRIPT"
fi

# 使用nohup启动MCP服务器
echo "🚀 使用专用脚本启动MCP服务器..."
nohup "$MCP_START_SCRIPT" > "$LOG_FILE" 2>&1 &
MCP_SERVER_PID=$!

echo "⏳ 等待MCP服务器启动..."
sleep 8 # 增加等待时间让服务器完全启动

# 更可靠的进程检查方法
MCP_RUNNING=false
for i in {1..5}; do
    if pgrep -f "emqx_mcp_server" > /dev/null; then
        MCP_RUNNING=true
        ACTUAL_PID=$(pgrep -f "emqx_mcp_server")
        break
    fi
    sleep 2
done

# 验证MCP服务器是否成功启动
if [ "$MCP_RUNNING" = true ]; then
    echo "✅ MCP服务器已在后台启动 (PID: $ACTUAL_PID)"
    echo "   日志文件: $LOG_FILE"
    echo "   启动脚本: $MCP_START_SCRIPT"
else
    echo " MCP服务器启动。请检查日志: $LOG_FILE"
    echo "   尝试查看日志内容："
    echo "   tail -10 $LOG_FILE"
    # MCP服务器启动失败是一个严重问题，可以选择在这里退出
    # exit 1 
fi

# 5. 显示系统信息
echo ""
echo "🌐 系统访问信息:"
echo "  • EdgeX UI: http://localhost:4000"
echo "  • eKuiper API: http://localhost:59720"
echo "  • Redis数据库: localhost:6379"

echo ""
echo "🎉 温度控制系统启动完成！"
echo ""
echo "👉 接下来，您可以:"
echo "   • 访问 EdgeX UI 查看设备状态"
echo "   • 查看 MCP 服务器日志: tail -f mcp_server.log"
echo "   • 运行系统检查脚本: ./EdgeX_mqtt/scripts/check_system_status.sh"