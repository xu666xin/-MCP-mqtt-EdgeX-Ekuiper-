#!/usr/bin/env python3
"""
测试脚本：验证EMQX MCP Server的新功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emqx_mcp_server.server import EMQXMCPServer

def test_server_initialization():
    """测试服务器初始化"""
    print("🧪 测试EMQX MCP Server初始化...")
    try:
        server = EMQXMCPServer()
        print("✅ 服务器初始化成功")
        print(f"📊 服务器名称: {server.name}")
        return True
    except Exception as e:
        print(f"❌ 服务器初始化失败: {e}")
        return False

def test_tool_imports():
    """测试工具模块导入"""
    print("\n🔧 测试工具模块导入...")
    
    try:
        from emqx_mcp_server.tools.emqx_message_tools import EMQXMessageTools
        print("✅ EMQX消息工具导入成功")
    except Exception as e:
        print(f"❌ EMQX消息工具导入失败: {e}")
        return False
    
    try:
        from emqx_mcp_server.tools.emqx_client_tools import EMQXClientTools
        print("✅ EMQX客户端工具导入成功")
    except Exception as e:
        print(f"❌ EMQX客户端工具导入失败: {e}")
        return False
    
    try:
        from emqx_mcp_server.tools.emqx_subscription_tools import EMQXSubscriptionTools
        print("✅ EMQX订阅工具导入成功")
    except Exception as e:
        print(f"❌ EMQX订阅工具导入失败: {e}")
        return False
    
    try:
        from emqx_mcp_server.tools.temperature_control_tools import TemperatureControlTools
        print("✅ 温度控制工具导入成功")
    except Exception as e:
        print(f"❌ 温度控制工具导入失败: {e}")
        return False
    
    return True

def list_available_tools():
    """列出可用工具"""
    print("\n📋 新增的MCP工具功能:")
    
    print("\n🌡️ 温度控制工具:")
    print("  • get_temperature - 获取环境温度")
    print("  • get_humidity - 获取环境湿度")
    print("  • set_ac_power - 控制空调开关")
    print("  • set_ac_temperature - 设置空调目标温度")
    print("  • get_ac_status - 获取空调状态")
    
    print("\n📡 MQTT订阅工具:")
    print("  • subscribe_mqtt_topic - 订阅MQTT主题")
    print("  • unsubscribe_mqtt_topic - 取消订阅主题")
    print("  • get_mqtt_messages - 获取历史消息")
    print("  • get_subscribed_topics - 获取订阅列表")
    print("  • monitor_classroom_data - 监控教室数据")
    
    print("\n🔧 原有工具:")
    print("  • list_mqtt_clients - 列出MQTT客户端")
    print("  • get_mqtt_client - 获取客户端信息")
    print("  • kick_mqtt_client - 断开客户端")
    print("  • publish_mqtt_message - 发布MQTT消息")

def main():
    print("🚀 EMQX MCP Server 功能测试")
    print("=" * 50)
    
    # 测试服务器初始化
    if not test_server_initialization():
        sys.exit(1)
    
    # 测试工具导入
    if not test_tool_imports():
        sys.exit(1)
    
    # 列出可用工具
    list_available_tools()
    
    print(f"\n🎉 所有测试通过！EMQX MCP Server已准备就绪")
    print(f"📝 请配置.env文件中的EMQX连接信息")
    print(f"🔗 支持您的智能教室温度监控系统")

if __name__ == "__main__":
    main()
