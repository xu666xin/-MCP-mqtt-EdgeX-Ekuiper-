"""
EMQX Subscription Tools Module

简化版MQTT订阅工具，提供基础的MQTT订阅和消息获取功能。
"""

import logging
import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import ssl
from ..config import EMQX_BROKER_HOST, EMQX_BROKER_PORT, EMQX_USERNAME, EMQX_PASSWORD, EMQX_USE_SSL, MESSAGE_HISTORY_SIZE, SSL_VERIFY_CERTS

class EMQXSubscriptionTools:
    """
    EMQX订阅工具类
    
    提供MQTT主题订阅、取消订阅和消息历史查询功能。
    """
    
    def __init__(self, logger: logging.Logger):
        """
        初始化EMQX订阅工具
        
        Args:
            logger: 日志记录器实例
        """
        self.logger = logger
        self.mqtt_client = None
        self.subscribed_topics = {}
        self.message_history = {}
        self.max_history_size = MESSAGE_HISTORY_SIZE
        
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker")
        else:
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """接收到消息的回调"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        timestamp = datetime.now()
        
        # 保存消息到历史记录
        if topic not in self.message_history:
            self.message_history[topic] = []
        
        message_data = {
            "timestamp": timestamp.isoformat(),
            "topic": topic,
            "payload": payload,
            "qos": msg.qos,
            "retain": msg.retain
        }
        
        self.message_history[topic].append(message_data)
        
        # 限制历史记录大小
        if len(self.message_history[topic]) > self.max_history_size:
            self.message_history[topic] = self.message_history[topic][-self.max_history_size:]
        
        self.logger.info(f"Received message from {topic}: {payload}")
    
    def _setup_mqtt_client(self):
        """设置MQTT客户端"""
        if self.mqtt_client is None:
            try:
                self.mqtt_client = mqtt.Client()
                self.mqtt_client.username_pw_set(EMQX_USERNAME, EMQX_PASSWORD)
                self.mqtt_client.on_connect = self._on_connect
                self.mqtt_client.on_message = self._on_message
                
                # 如果启用SSL，配置SSL/TLS
                if EMQX_USE_SSL:
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                    # 根据配置决定是否验证证书
                    if not SSL_VERIFY_CERTS:
                        # 开发环境：允许自签名证书
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        self.logger.warning("SSL certificate verification disabled - only use in development!")
                    else:
                        # 生产环境：验证证书
                        self.logger.info("SSL certificate verification enabled")
                    
                    self.mqtt_client.tls_set_context(context)
                    self.logger.info("SSL/TLS enabled for MQTT connection")
                
                # 使用非阻塞连接
                self.mqtt_client.connect_async(EMQX_BROKER_HOST, EMQX_BROKER_PORT, 60)
                self.mqtt_client.loop_start()
                self.logger.info(f"MQTT client setup initiated (async, SSL: {EMQX_USE_SSL})")
                return True
            except Exception as e:
                self.logger.error(f"Failed to setup MQTT client: {str(e)}")
                self.mqtt_client = None
                return False
        return True

    def register_tools(self, mcp: Any):
        """Register EMQX Subscription tools."""
        
        @mcp.tool(name="subscribe_mqtt_topic", 
                  description="订阅MQTT主题以监听教室设备数据")
        async def subscribe_topic(topic: str, qos: int = 0):
            """订阅MQTT主题
            
            Args:
                topic: MQTT主题 (支持通配符如 classroom/# 或 classroom/+/temperature)
                qos: 服务质量等级 (0, 1, 或 2)
            
            Returns:
                MCPResponse: 订阅结果
            """
            self.logger.info("Handling subscribe request")
            
            if not topic:
                return {"error": "Missing required parameter: topic"}
            
            # 设置MQTT客户端
            if not self._setup_mqtt_client():
                return {"error": "Failed to setup MQTT client"}
            
            try:
                result, mid = self.mqtt_client.subscribe(topic, qos)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    self.subscribed_topics[topic] = {
                        "qos": qos,
                        "subscribed_at": datetime.now().isoformat()
                    }
                    return {
                        "success": True,
                        "message": f"Successfully subscribed to topic: {topic}",
                        "topic": topic,
                        "qos": qos,
                        "message_id": mid
                    }
                else:
                    return {"error": f"Failed to subscribe to topic {topic}: {result}"}
            except Exception as e:
                self.logger.error(f"Error subscribing to topic {topic}: {str(e)}")
                return {"error": str(e)}
        
        @mcp.tool(name="unsubscribe_mqtt_topic", 
                  description="取消订阅MQTT主题")
        async def unsubscribe_topic(topic: str):
            """取消订阅MQTT主题
            
            Args:
                topic: MQTT主题
            
            Returns:
                MCPResponse: 取消订阅结果
            """
            if not topic:
                return {"error": "Missing required parameter: topic"}
            
            if self.mqtt_client is None:
                return {"error": "MQTT client not initialized"}
            
            try:
                result, mid = self.mqtt_client.unsubscribe(topic)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    if topic in self.subscribed_topics:
                        del self.subscribed_topics[topic]
                    return {
                        "success": True,
                        "message": f"Successfully unsubscribed from topic: {topic}",
                        "topic": topic
                    }
                else:
                    return {"error": f"Failed to unsubscribe from topic {topic}: {result}"}
            except Exception as e:
                self.logger.error(f"Error unsubscribing from topic {topic}: {str(e)}")
                return {"error": str(e)}
        
        @mcp.tool(name="get_mqtt_messages", 
                  description="获取接收到的MQTT消息历史记录")
        async def get_messages(topic: str = None, limit: int = 10, since_minutes: int = None):
            """获取MQTT消息历史
            
            Args:
                topic: 主题过滤器 (可选)
                limit: 返回消息数量限制 (默认10)
                since_minutes: 获取多少分钟内的消息 (可选)
            
            Returns:
                MCPResponse: 消息历史数据
            """
            topic_filter = topic
            
            # 过滤消息
            filtered_messages = []
            
            for topic, messages in self.message_history.items():
                # 主题过滤
                if topic_filter and topic_filter not in topic:
                    continue
                
                for msg in messages:
                    # 时间过滤
                    if since_minutes:
                        msg_time = datetime.fromisoformat(msg["timestamp"])
                        if datetime.now() - msg_time > timedelta(minutes=since_minutes):
                            continue
                    
                    filtered_messages.append(msg)
            
            # 按时间排序并限制数量
            filtered_messages.sort(key=lambda x: x["timestamp"], reverse=True)
            if limit:
                filtered_messages = filtered_messages[:limit]
            
            return {
                "success": True,
                "messages": filtered_messages,
                "count": len(filtered_messages),
                "total_topics": len(self.message_history)
            }
        
        @mcp.tool(name="get_subscribed_topics", 
                  description="获取当前已订阅的MQTT主题列表")
        async def get_subscriptions():
            """获取已订阅主题
            
            Returns:
                MCPResponse: 已订阅主题列表
            """
            return {
                "success": True,
                "subscribed_topics": self.subscribed_topics,
                "count": len(self.subscribed_topics)
            }
