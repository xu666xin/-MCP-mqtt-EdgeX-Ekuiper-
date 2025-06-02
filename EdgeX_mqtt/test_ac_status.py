#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import ssl
import json
import time
from datetime import datetime

# EMQX Cloud 连接配置
EMQX_HOST = "zd89891c.ala.cn-hangzhou.emqxsl.cn"
EMQX_PORT = 8883
EMQX_USERNAME = "xu666xin"
EMQX_PASSWORD = "123456"

# AC状态主题
AC_STATUS_TOPICS = [
    "classroom/ac/power/status",
    "classroom/ac/temperature/status"
]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"🎉 成功连接到 EMQX Cloud!")
        print(f"连接时间: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # 订阅AC状态主题
        for topic in AC_STATUS_TOPICS:
            client.subscribe(topic)
            print(f"📡 订阅AC状态主题: {topic}")
            
        print("=" * 50)
        print("🔄 等待AC状态数据...")
        print()
    else:
        print(f"❌ 连接失败，错误代码: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"⏰ {timestamp} | 📨 {topic}")
        print(f"数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print("-" * 60)
    except json.JSONDecodeError:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"⏰ {timestamp} | 📨 {topic}")
        print(f"原始数据: {msg.payload.decode()}")
        print("-" * 60)

def main():
    # 创建MQTT客户端
    client = mqtt.Client()
    
    # 设置SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)
    
    # 设置认证
    client.username_pw_set(EMQX_USERNAME, EMQX_PASSWORD)
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # 连接到EMQX Cloud
        print(f"🔗 正在连接到 {EMQX_HOST}:{EMQX_PORT}...")
        client.connect(EMQX_HOST, EMQX_PORT, 60)
        
        # 保持连接并监听消息
        client.loop_forever()
        
    except Exception as e:
        print(f"❌ 连接错误: {e}")
    finally:
        client.disconnect()
        print("👋 断开连接")

if __name__ == "__main__":
    main()
