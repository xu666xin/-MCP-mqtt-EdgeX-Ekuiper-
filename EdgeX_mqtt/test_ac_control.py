#!/usr/bin/env python3
"""
测试AC控制消息格式
模拟MCP工具发送的MQTT消息
"""

import json
import time
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime

# EMQX Cloud连接配置
BROKER_HOST = "zd89891c.ala.cn-hangzhou.emqxsl.cn"
BROKER_PORT = 8883
USERNAME = "xu666xin"
PASSWORD = "123456"
TOPIC = "classroom/control/ac"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")

def test_ac_control():
    """测试空调控制消息"""
    
    # 创建MQTT客户端
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    
    # 设置SSL
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        # 连接到EMQX Cloud
        print(f"Connecting to {BROKER_HOST}:{BROKER_PORT}...")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
        
        # 等待连接
        time.sleep(2)
        
        print("\n=== 测试MCP工具发送的数据格式 ===")
        
        # 1. 测试空调开关控制 (MCP工具格式)
        ac_power_command = {
            "command": "set_power",
            "value": True,  # 布尔值
            "timestamp": datetime.now().isoformat(),
            "device": "classroom-ac-controller"
        }
        
        print(f"\n1. 发送空调开启命令:")
        print(f"   Topic: {TOPIC}")
        print(f"   Payload: {json.dumps(ac_power_command, indent=2)}")
        
        result = client.publish(TOPIC, json.dumps(ac_power_command), qos=1)
        time.sleep(1)
        
        # 2. 测试空调温度控制 (MCP工具格式)
        ac_temp_command = {
            "command": "set_temperature",
            "value": 24.5,  # 浮点数
            "unit": "°C",
            "timestamp": datetime.now().isoformat(),
            "device": "classroom-ac-controller"
        }
        
        print(f"\n2. 发送空调温度设置命令:")
        print(f"   Topic: {TOPIC}")
        print(f"   Payload: {json.dumps(ac_temp_command, indent=2)}")
        
        result = client.publish(TOPIC, json.dumps(ac_temp_command), qos=1)
        time.sleep(1)
        
        # 3. 测试空调关闭
        ac_power_off_command = {
            "command": "set_power",
            "value": False,  # 布尔值
            "timestamp": datetime.now().isoformat(),
            "device": "classroom-ac-controller"
        }
        
        print(f"\n3. 发送空调关闭命令:")
        print(f"   Topic: {TOPIC}")
        print(f"   Payload: {json.dumps(ac_power_off_command, indent=2)}")
        
        result = client.publish(TOPIC, json.dumps(ac_power_off_command), qos=1)
        time.sleep(2)
        
        print("\n=== 测试完成 ===")
        print("检查eKuiper规则是否接收到这些消息:")
        print("curl -s 'http://localhost:59720/rules/ac_power_control/status'")
        print("curl -s 'http://localhost:59720/rules/ac_temperature_control/status'")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    test_ac_control()