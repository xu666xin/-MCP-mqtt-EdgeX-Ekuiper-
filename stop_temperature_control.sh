#!/bin/bash

# 温度控制系统 - 一键关闭脚本
# 功能: 停止所有相关服务和进程

echo "🛑 关闭温度控制系统..."
echo "================================="

# 设置项目路径
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDGEX_DIR="$PROJECT_ROOT/EdgeX_mqtt"

# 1. 停止 MCP 服务器
echo "🔌 停止 MCP 服务器..."
MCP_PIDS=$(pgrep -f "emqx_mcp_server")
if [ -n "$MCP_PIDS" ]; then
    echo "   找到 MCP 服务器进程: $MCP_PIDS"
    pkill -f "emqx_mcp_server"
    sleep 2
    
    # 检查是否还有残留进程
    REMAINING_PIDS=$(pgrep -f "emqx_mcp_server")
    if [ -n "$REMAINING_PIDS" ]; then
        echo "   强制终止残留进程: $REMAINING_PIDS"
        pkill -9 -f "emqx_mcp_server"
    fi
    echo "✅ MCP 服务器已停止"
else
    echo "   没有发现运行中的 MCP 服务器"
fi

# 2. 停止 EdgeX 服务
echo ""
echo "🐳 停止 EdgeX Foundry 服务..."
cd "$EDGEX_DIR"
if [ -f "docker-compose.yml" ]; then
    docker-compose down
    echo "✅ EdgeX 服务已停止"
else
    echo "   未找到 docker-compose.yml 文件"
fi

# 3. 清理相关容器和网络
echo ""
echo "🧹 清理 Docker 资源..."

# 停止所有相关容器
EDGEX_CONTAINERS=$(docker ps -q --filter "name=edgex")
if [ -n "$EDGEX_CONTAINERS" ]; then
    echo "   停止 EdgeX 容器..."
    docker stop $EDGEX_CONTAINERS
fi

# 清理停止的容器
STOPPED_CONTAINERS=$(docker ps -aq --filter "status=exited" --filter "name=edgex")
if [ -n "$STOPPED_CONTAINERS" ]; then
    echo "   删除停止的 EdgeX 容器..."
    docker rm $STOPPED_CONTAINERS
fi

# 清理网络
EDGEX_NETWORKS=$(docker network ls -q --filter "name=edgex")
if [ -n "$EDGEX_NETWORKS" ]; then
    echo "   清理 EdgeX 网络..."
    docker network rm $EDGEX_NETWORKS 2>/dev/null || true
fi

echo "✅ Docker 资源清理完成"

# 4. 检查端口占用
echo ""
echo "🔍 检查关键端口状态..."
PORTS=("4000" "59720" "6379" "1883" "8883")
for port in "${PORTS[@]}"; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "   ⚠️  端口 $port 仍被进程 $PID 占用"
    else
        echo "   ✅ 端口 $port 已释放"
    fi
done

# 5. 清理日志文件
echo ""
echo "📝 清理日志文件..."
LOG_FILE="$PROJECT_ROOT/mcp_server.log"
if [ -f "$LOG_FILE" ]; then
    rm -f "$LOG_FILE"
    echo "✅ 已删除 MCP 服务器日志文件"
fi

# 6. 显示系统状态
echo ""
echo "📊 系统关闭状态报告:"
echo "  • MCP 服务器: $(pgrep -f 'emqx_mcp_server' >/dev/null && echo '❌ 仍在运行' || echo '✅ 已停止')"
echo "  • Docker 容器: $(docker ps -q --filter 'name=edgex' | wc -l | tr -d ' ') 个 EdgeX 容器运行中"
echo "  • 虚拟环境: $([ -n "$VIRTUAL_ENV" ] && echo '🔌 已激活' || echo '🔌 未激活')"

echo ""
echo "🎉 温度控制系统关闭完成！"
echo ""
echo "💡 提示:"
echo "  • 如需重新启动系统: ./start_temperature_control_v2.sh"
echo "  • 如需重新设置环境: ./setup_environment.sh"
echo "  • 如需清理虚拟环境: rm -rf venv"
