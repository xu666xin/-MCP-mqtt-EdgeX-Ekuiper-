#!/bin/bash

# eKuiper规则初始化脚本
# 在容器启动后自动部署所有规则

EKUIPER_URL="http://localhost:59720"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_DIR="$SCRIPT_DIR/../rules"

echo "🚀 初始化eKuiper规则..."

# 等待eKuiper服务启动
echo "⏳ 等待eKuiper服务启动..."
for i in {1..30}; do
    if curl -s "$EKUIPER_URL" > /dev/null 2>&1; then
        echo "✅ eKuiper服务已启动"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ eKuiper服务启动超时"
        exit 1
    fi
    sleep 2
done

# 1. 创建数据流
echo "📊 创建classroom_stream数据流..."
curl -X POST "$EKUIPER_URL/streams" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/create_classroom_stream.json"

echo ""
echo "🔌 创建空调控制数据源..."
curl -X POST "$EKUIPER_URL/streams" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/create_ac_control_stream.json"

echo ""
echo "📊 创建空调状态数据源..."
curl -X POST "$EKUIPER_URL/streams" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/create_ac_status_stream.json"

echo ""
echo "⏳ 等待数据源创建完成..."
sleep 3

# 2. 创建规则
echo "🌡️ 创建温度数据转发规则..."
curl -X POST "$EKUIPER_URL/rules" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/simple_data_forward.json"

echo ""
echo "💧 创建湿度数据转发规则..."
curl -X POST "$EKUIPER_URL/rules" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/humidity_forward.json"

echo ""
echo "🔌 创建空调开关控制规则..."
curl -X POST "$EKUIPER_URL/rules" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/ac_power_control.json"

echo ""
echo "🎛️ 创建空调温度控制规则..."
curl -X POST "$EKUIPER_URL/rules" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/ac_temperature_control.json"

echo ""
echo "📋 创建空调状态监控规则..."
curl -X POST "$EKUIPER_URL/rules" \
  -H "Content-Type: application/json" \
  -d @"$RULES_DIR/ac_status_monitor.json"

echo ""
echo "✅ 所有规则初始化完成！"

# 3. 验证规则状态
echo ""
echo "📋 验证规则状态:"
curl -s "$EKUIPER_URL/rules" | jq -r '.[] | "  • \(.id): \(.status)"'

echo ""
echo "📊 验证数据流:"
curl -s "$EKUIPER_URL/streams" | jq -r '.[] | "  • \(.)"'

echo ""
echo "🎉 eKuiper规则引擎初始化完成！"
