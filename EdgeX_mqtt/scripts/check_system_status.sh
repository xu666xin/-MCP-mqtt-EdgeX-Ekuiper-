#!/bin/bash

# 🔍 温度控制系统状态检查脚本

echo "🌡️ 温度控制系统 - 状态检查"
echo "================================"

# 检查Docker容器状态
echo "🐳 Docker容器状态："
docker-compose ps

echo ""
echo "📊 EdgeX设备状态："
device_count=$(curl -s http://localhost:59881/api/v2/device/all | jq '.totalCount // 0' 2>/dev/null)
if [ "$device_count" -gt 0 ]; then
    echo "  ✅ 检测到 $device_count 个设备"
    echo "  教室相关设备："
    curl -s http://localhost:59881/api/v2/device/all | jq -r '.devices[] | select(.name | contains("classroom")) | "    - " + .name + " (" + .operatingState + ")"' 2>/dev/null
else
    echo "  ❌ 无法获取设备信息"
fi

echo ""
echo "📡 eKuiper规则状态："
rules=$(curl -s http://localhost:59720/rules 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$rules" | jq -r '.[] | "  " + (if .status == "Running" then "✅" else "❌" end) + " " + .id + " (" + .status + ")"' 2>/dev/null
else
    echo "  ❌ 无法连接到eKuiper"
fi

echo ""
echo "💾 最新数据读取："
echo "温度传感器："
curl -s "http://localhost:59880/api/v2/reading/device/name/classroom-temp-sensor?limit=1" | jq -r '.readings[0] | "  📊 " + ((.value | tonumber * 100 | round / 100) | tostring) + "°C (更新时间: " + ((.origin // 0) / 1000000 | strftime("%H:%M:%S")) + ")"' 2>/dev/null || echo "  ❌ 无法获取温度数据"

echo "湿度传感器："
curl -s "http://localhost:59880/api/v2/reading/device/name/classroom-humidity-sensor?limit=1" | jq -r '.readings[0] | "  💧 " + ((.value | tonumber * 100 | round / 100) | tostring) + "% (更新时间: " + ((.origin // 0) / 1000000 | strftime("%H:%M:%S")) + ")"' 2>/dev/null || echo "  ❌ 无法获取湿度数据"

echo ""
echo "🔗 管理界面："
echo "  📊 EdgeX UI: http://localhost:4000"
echo "  🌊 eKuiper Manager: http://localhost:9082"
echo "  📡 eKuiper API: http://localhost:59720"
