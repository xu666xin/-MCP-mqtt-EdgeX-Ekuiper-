"""
MQTT基础客户端模块

提供共享的MQTT连接和消息处理功能，减少代码重复。
"""

import logging
import ssl
from datetime import datetime
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt
from .config import (EMQX_BROKER_HOST, EMQX_BROKER_PORT, EMQX_USERNAME, EMQX_PASSWORD, 
                    EMQX_USE_SSL, MESSAGE_HISTORY_SIZE, MQTT_KEEPALIVE, SSL_VERIFY_CERTS)


class BaseMQTTClient:
    """
    基础MQTT客户端类
    
    提供共享的MQTT连接、消息历史管理和SSL配置功能。
    """
    
    def __init__(self, logger: logging.Logger, client_id_prefix: str = "mcp_client"):
        """
        初始化基础MQTT客户端
        
        Args:
            logger: 日志记录器实例
            client_id_prefix: 客户端ID前缀，用于区分不同的客户端实例
        """
        self.logger = logger
        self.mqtt_client = None
        self.message_history: Dict[str, List[Dict]] = {}
        self.max_history_size = MESSAGE_HISTORY_SIZE
        self.client_id_prefix = client_id_prefix
        self.subscribed_topics: Dict[str, Dict] = {}
        
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调 - 子类可以重写"""
        if rc == 0:
            self.logger.info(f"{self.client_id_prefix} connected to MQTT broker")
        else:
            self.logger.error(f"{self.client_id_prefix} failed to connect: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """接收消息回调 - 子类可以重写"""
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
    
    def _setup_ssl_context(self):
        """设置SSL上下文"""
        if EMQX_USE_SSL:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
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
    
    def setup_client(self) -> bool:
        """设置MQTT客户端"""
        if self.mqtt_client is None:
            client_id = f"{self.client_id_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.mqtt_client = mqtt.Client(client_id=client_id)
            self.mqtt_client.username_pw_set(EMQX_USERNAME, EMQX_PASSWORD)
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            
            # 设置SSL
            self._setup_ssl_context()
            
            try:
                self.mqtt_client.connect_async(EMQX_BROKER_HOST, EMQX_BROKER_PORT, MQTT_KEEPALIVE)
                self.mqtt_client.loop_start()
                self.logger.info(f"{self.client_id_prefix} MQTT client setup initiated (async)")
                return True
            except Exception as e:
                self.logger.error(f"Failed to setup {self.client_id_prefix} MQTT client: {str(e)}")
                self.mqtt_client = None
                return False
        return True
    
    def get_latest_message(self, topic: str) -> Optional[Dict]:
        """获取指定主题的最新消息"""
        if topic in self.message_history and self.message_history[topic]:
            return self.message_history[topic][-1]
        return None
    
    def get_message_history(self, topic: str = None, limit: int = 10) -> List[Dict]:
        """获取消息历史"""
        if topic:
            messages = self.message_history.get(topic, [])
            return messages[-limit:] if limit else messages
        else:
            # 返回所有主题的消息
            all_messages = []
            for topic_messages in self.message_history.values():
                all_messages.extend(topic_messages)
            
            # 按时间排序
            all_messages.sort(key=lambda x: x["timestamp"], reverse=True)
            return all_messages[:limit] if limit else all_messages
    
    def cleanup(self):
        """清理MQTT客户端连接"""
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                self.logger.info(f"{self.client_id_prefix} MQTT client disconnected")
            except Exception as e:
                self.logger.error(f"Error cleaning up {self.client_id_prefix} MQTT client: {str(e)}")
            finally:
                self.mqtt_client = None
