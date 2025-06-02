#!/bin/bash

# MCP服务器启动脚本
# 功能: 持续运行MCP服务器，适用于独立测试

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$PROJECT_ROOT/emqx-mcp-server-main"
LOG_FILE="$PROJECT_ROOT/mcp_server.log"

echo "🚀 启动MCP服务器..."
echo "项目根目录: $PROJECT_ROOT"
echo "MCP目录: $MCP_DIR"
echo "日志文件: $LOG_FILE"

# 激活虚拟环境
source "$PROJECT_ROOT/venv/bin/activate"

# 检查并安装MCP服务器模块
if ! python -c "import emqx_mcp_server" >/dev/null 2>&1; then
    echo "📦 MCP服务器模块未安装，正在自动安装..."
    cd "$MCP_DIR"
    
    # 安装依赖
    pip install -e .
    
    if ! python -c "import emqx_mcp_server" >/dev/null 2>&1; then
        echo "❌ MCP服务器模块安装失败"
        exit 1
    fi
    
    echo "✅ MCP服务器模块安装成功"
    cd "$PROJECT_ROOT"
else
    echo "✅ MCP服务器模块已安装"
fi

# 停止已有的MCP服务器进程
echo "🛑 停止已有的MCP服务器进程..."
pkill -f "emqx_mcp_server" 2>/dev/null || true
sleep 2

# 进入MCP目录
cd "$MCP_DIR"

# 设置Python路径
export PYTHONPATH="$MCP_DIR/src:$PYTHONPATH"

echo "🔄 启动MCP服务器..."
echo "使用Python: $(which python)"
echo "工作目录: $(pwd)"

# 使用exec在前台运行，避免进程退出
exec python -m emqx_mcp_server
