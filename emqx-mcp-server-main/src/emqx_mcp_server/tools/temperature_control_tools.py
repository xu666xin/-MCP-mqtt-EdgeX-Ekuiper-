"""
简化温度控制工具模块

提供核心的环境设备控制功能：
- 获取温度数据
- 获取湿度数据  
- 控制空调开关
- 设置空调目标温度
- 检查空调状态
"""

import logging
import json
import ssl
from typing import Any, Dict, Optional
from datetime import datetime
import paho.mqtt.client as mqtt
from ..emqx_client import EMQXClient
from ..config import (EMQX_BROKER_HOST, EMQX_BROKER_PORT, EMQX_USERNAME, EMQX_PASSWORD, 
                     EMQX_USE_SSL, MESSAGE_HISTORY_SIZE, AC_TEMP_MIN, AC_TEMP_MAX, 
                     MQTT_KEEPALIVE, CLASSROOM_TOPIC_PREFIX)

class TemperatureControlTools:
    """
    温度控制设备控制工具类
    
    提供环境温湿度数据获取和空调控制功能。
    """
    
    def __init__(self, logger: logging.Logger):
        """
        初始化温度控制工具
        
        Args:
            logger: 日志记录器实例
        """
        self.logger = logger
        self.emqx_client = EMQXClient(logger)
        self.mqtt_client = None
        self.message_history = {}
        self.max_history_size = MESSAGE_HISTORY_SIZE
        self.mqtt_connected = False
        
        # 核心设备主题 - 使用配置的前缀
        self.topics = {
            "temperature": f"{CLASSROOM_TOPIC_PREFIX}/temperature",
            "humidity": f"{CLASSROOM_TOPIC_PREFIX}/humidity",
            "ac_control": f"{CLASSROOM_TOPIC_PREFIX}/control/ac",
            "ac_power_status": f"{CLASSROOM_TOPIC_PREFIX}/ac/power/status",
            "ac_temperature_status": f"{CLASSROOM_TOPIC_PREFIX}/ac/temperature/status"
        }

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            self.mqtt_connected = True
            self.logger.info("Temperature Control MQTT client connected")
            # 自动订阅传感器数据主题
            client.subscribe(self.topics["temperature"])
            client.subscribe(self.topics["humidity"])
            # 订阅空调状态主题
            client.subscribe(self.topics["ac_power_status"])
            client.subscribe(self.topics["ac_temperature_status"])
            self.logger.info("Subscribed to all temperature control sensor and AC status topics")
        else:
            self.mqtt_connected = False
            self.logger.error(f"Temperature Control MQTT connection failed: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """接收消息回调"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        timestamp = datetime.now()
        
        # 保存消息到历史记录
        if topic not in self.message_history:
            self.message_history[topic] = []
        
        message_data = {
            "timestamp": timestamp.isoformat(),
            "payload": payload
        }
        
        self.message_history[topic].append(message_data)
        
        # 限制历史记录大小
        if len(self.message_history[topic]) > self.max_history_size:
            self.message_history[topic] = self.message_history[topic][-self.max_history_size:]
        
        self.logger.info(f"Received data from {topic}: {payload}")

    def _setup_mqtt_client(self):
        """设置MQTT客户端（完全非阻塞）"""
        if self.mqtt_client is None:
            try:
                # 创建客户端时加上时间戳避免冲突
                client_id = f"temperature_control_{datetime.now().strftime('%H%M%S')}"
                self.mqtt_client = mqtt.Client(client_id=client_id)
                
                # 设置认证
                if EMQX_USERNAME and EMQX_PASSWORD:
                    self.mqtt_client.username_pw_set(EMQX_USERNAME, EMQX_PASSWORD)
                
                # 设置回调
                self.mqtt_client.on_connect = self._on_connect
                self.mqtt_client.on_message = self._on_message
                
                # SSL配置（如果需要）
                if EMQX_USE_SSL:
                    import ssl
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    self.mqtt_client.tls_set_context(context)
                
                # 使用完全异步连接，不等待连接结果
                self.mqtt_client.connect_async(EMQX_BROKER_HOST, EMQX_BROKER_PORT, MQTT_KEEPALIVE)
                self.mqtt_client.loop_start()
                self.logger.info("Temperature Control MQTT client setup initiated (fully async)")
                return True
            except Exception as e:
                self.logger.error(f"Failed to setup MQTT client: {str(e)}")
                self.mqtt_client = None
                return False
        return True

    def register_tools(self, mcp: Any):
        """注册简化的温度控制工具"""
        
        @mcp.tool(name="get_temperature", 
                  description="获取教室当前温度")
        async def get_temperature():
            """获取最新温度数据"""
            self.logger.info("Getting current temperature")
            
            # 延迟设置MQTT客户端（非阻塞）
            self._setup_mqtt_client()
            
            # 检查是否有历史数据（即使MQTT还未连接）
            temp_topic = self.topics["temperature"]
            if temp_topic in self.message_history and self.message_history[temp_topic]:
                latest_msg = self.message_history[temp_topic][-1]
                try:
                    # 解析JSON数据，支持数组和对象格式
                    payload_data = json.loads(latest_msg["payload"])
                    
                    # 如果是数组，取第一个元素
                    if isinstance(payload_data, list) and len(payload_data) > 0:
                        payload_data = payload_data[0]
                    
                    # 提取温度值
                    temperature = payload_data.get("temperature")
                    if temperature is not None:
                        return {
                            "success": True,
                            "temperature": temperature,
                            "unit": payload_data.get("unit", "°C"),
                            "timestamp": latest_msg["timestamp"],
                            "sensor_id": payload_data.get("sensor_id", "classroom-temp-sensor"),
                            "message": f"当前教室温度: {temperature}°C"
                        }
                    else:
                        return {
                            "success": False,
                            "raw_data": latest_msg["payload"],
                            "timestamp": latest_msg["timestamp"],
                            "message": "温度数据格式异常"
                        }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "raw_data": latest_msg["payload"],
                        "timestamp": latest_msg["timestamp"],
                        "message": "JSON解析失败"
                    }
            else:
                # 提供连接状态信息
                mqtt_status = "已连接" if self.mqtt_connected else "连接中"
                return {
                    "success": False,
                    "mqtt_status": mqtt_status,
                    "message": f"暂无温度数据，MQTT状态: {mqtt_status}。请等待传感器发送数据"
                }

        @mcp.tool(name="get_humidity", 
                  description="获取教室当前湿度")
        async def get_humidity():
            """获取最新湿度数据"""
            self.logger.info("Getting current humidity")
            
            # 尝试设置MQTT客户端（非阻塞）
            self._setup_mqtt_client()
            
            # 检查是否有历史数据（即使MQTT还未连接）
            humidity_topic = self.topics["humidity"]
            if humidity_topic in self.message_history and self.message_history[humidity_topic]:
                latest_msg = self.message_history[humidity_topic][-1]
                try:
                    # 解析JSON数据，支持数组和对象格式
                    payload_data = json.loads(latest_msg["payload"])
                    
                    # 如果是数组，取第一个元素
                    if isinstance(payload_data, list) and len(payload_data) > 0:
                        payload_data = payload_data[0]
                    
                    # 提取湿度值
                    humidity = payload_data.get("humidity")
                    if humidity is not None:
                        return {
                            "success": True,
                            "humidity": humidity,
                            "unit": payload_data.get("unit", "%"),
                            "timestamp": latest_msg["timestamp"],
                            "sensor_id": payload_data.get("sensor_id", "classroom-humidity-sensor"),
                            "message": f"当前教室湿度: {humidity}%"
                        }
                    else:
                        # 检查是否有错误信息
                        if "error" in payload_data:
                            return {
                                "success": False,
                                "error": payload_data["error"],
                                "timestamp": latest_msg["timestamp"],
                                "message": "湿度传感器数据错误"
                            }
                        return {
                            "success": False,
                            "raw_data": latest_msg["payload"],
                            "timestamp": latest_msg["timestamp"],
                            "message": "湿度数据格式异常"
                        }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "raw_data": latest_msg["payload"],
                        "timestamp": latest_msg["timestamp"],
                        "message": "JSON解析失败"
                    }
            else:
                # 提供连接状态信息
                mqtt_status = "已连接" if self.mqtt_connected else "连接中"
                return {
                    "success": False,
                    "mqtt_status": mqtt_status,
                    "message": f"暂无湿度数据，MQTT状态: {mqtt_status}。请等待传感器发送数据"
                }

        @mcp.tool(name="set_ac_power", 
                  description="控制空调开关")
        async def set_ac_power(power: bool):
            """控制空调开关
            
            Args:
                power: True=开启, False=关闭
            """
            self.logger.info(f"Setting AC power to: {power}")
            
            # 尝试设置MQTT客户端（非阻塞）
            self._setup_mqtt_client()
            
            # 检查MQTT连接状态
            if not self.mqtt_connected:
                return {
                    "success": False,
                    "mqtt_status": "连接中",
                    "message": "MQTT连接中，请稍后重试空调控制"
                }
            
            # 构造控制命令
            command = {
                "command": "set_power",
                "value": power,
                "timestamp": datetime.now().isoformat(),
                "device": "classroom-ac-controller"
            }
            
            try:
                # 发送控制命令
                result = self.mqtt_client.publish(
                    self.topics["ac_control"], 
                    json.dumps(command), 
                    qos=1
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    return {
                        "success": True,
                        "message": f"空调已{'开启' if power else '关闭'}",
                        "command": command
                    }
                else:
                    return {"error": f"发送命令失败: {result.rc}"}
                    
            except Exception as e:
                self.logger.error(f"Error controlling AC power: {str(e)}")
                return {"error": str(e)}

        @mcp.tool(name="set_ac_temperature", 
                  description="设置空调目标温度")
        async def set_ac_temperature(temperature: float):
            """设置空调目标温度
            
            Args:
                temperature: 目标温度 (18-28°C)
            """
            self.logger.info(f"Setting AC target temperature to: {temperature}°C")
            
            # 温度范围检查 - 使用配置的范围
            if not (AC_TEMP_MIN <= temperature <= AC_TEMP_MAX):
                return {"error": f"温度必须在{AC_TEMP_MIN}-{AC_TEMP_MAX}°C范围内"}
            
            # 尝试设置MQTT客户端（非阻塞）
            self._setup_mqtt_client()
            
            # 检查MQTT连接状态
            if not self.mqtt_connected:
                return {
                    "success": False,
                    "mqtt_status": "连接中",
                    "message": "MQTT连接中，请稍后重试空调控制"
                }
            
            # 构造控制命令
            command = {
                "command": "set_temperature",
                "value": temperature,
                "unit": "°C",
                "timestamp": datetime.now().isoformat(),
                "device": "classroom-ac-controller"
            }
            
            try:
                # 发送控制命令
                result = self.mqtt_client.publish(
                    self.topics["ac_control"], 
                    json.dumps(command), 
                    qos=1
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    return {
                        "success": True,
                        "message": f"空调目标温度已设置为 {temperature}°C",
                        "command": command
                    }
                else:
                    return {"error": f"发送命令失败: {result.rc}"}
                    
            except Exception as e:
                self.logger.error(f"Error setting AC temperature: {str(e)}")
                return {"error": str(e)}

        @mcp.tool(name="get_ac_status", 
                  description="检查空调当前状态")
        async def get_ac_status():
            """获取空调当前状态"""
            self.logger.info("Getting AC status")
            
            # 尝试设置MQTT客户端（非阻塞）
            self._setup_mqtt_client()
            
            # 从消息历史中获取最新的空调状态数据
            power_topic = self.topics["ac_power_status"]
            temp_topic = self.topics["ac_temperature_status"]
            
            status_data = {}
            
            # 获取空调电源状态 - 使用与传感器相同的逻辑
            if power_topic in self.message_history and self.message_history[power_topic]:
                latest_power_msg = self.message_history[power_topic][-1]
                try:
                    # 解析JSON数据，支持数组和对象格式
                    payload_data = json.loads(latest_power_msg["payload"])
                    
                    # 如果是数组，取第一个元素
                    if isinstance(payload_data, list) and len(payload_data) > 0:
                        payload_data = payload_data[0]
                    
                    # 提取电源状态值 - 支持多种字段名
                    power_status = payload_data.get("power", payload_data.get("status", payload_data.get("ac_status")))
                    if power_status is not None:
                        status_data["power"] = {
                            "status": power_status,
                            "timestamp": latest_power_msg["timestamp"],
                            "device_id": payload_data.get("device_id", "classroom-ac")
                        }
                    else:
                        status_data["power"] = {
                            "success": False,
                            "raw_data": latest_power_msg["payload"],
                            "timestamp": latest_power_msg["timestamp"],
                            "message": "电源状态数据格式异常"
                        }
                except json.JSONDecodeError:
                    status_data["power"] = {
                        "success": False,
                        "raw_data": latest_power_msg["payload"],
                        "timestamp": latest_power_msg["timestamp"],
                        "message": "电源状态JSON解析失败"
                    }
            
            # 获取空调温度状态 - 使用与传感器相同的逻辑
            if temp_topic in self.message_history and self.message_history[temp_topic]:
                latest_temp_msg = self.message_history[temp_topic][-1]
                try:
                    # 解析JSON数据，支持数组和对象格式
                    payload_data = json.loads(latest_temp_msg["payload"])
                    
                    # 如果是数组，取第一个元素
                    if isinstance(payload_data, list) and len(payload_data) > 0:
                        payload_data = payload_data[0]
                    
                    # 提取温度状态值
                    target_temp = payload_data.get("target_temperature", payload_data.get("temperature"))
                    if target_temp is not None:
                        status_data["temperature"] = {
                            "target_temperature": target_temp,
                            "unit": payload_data.get("unit", "°C"),
                            "timestamp": latest_temp_msg["timestamp"],
                            "device_id": payload_data.get("device_id", "classroom-ac")
                        }
                    else:
                        # 检查是否有错误信息
                        if "error" in payload_data:
                            status_data["temperature"] = {
                                "success": False,
                                "error": payload_data["error"],
                                "timestamp": latest_temp_msg["timestamp"],
                                "message": "空调温度状态数据错误"
                            }
                        else:
                            status_data["temperature"] = {
                                "success": False,
                                "raw_data": latest_temp_msg["payload"],
                                "timestamp": latest_temp_msg["timestamp"],
                                "message": "温度状态数据格式异常"
                            }
                except json.JSONDecodeError:
                    status_data["temperature"] = {
                        "success": False,
                        "raw_data": latest_temp_msg["payload"],
                        "timestamp": latest_temp_msg["timestamp"],
                        "message": "温度状态JSON解析失败"
                    }
            
            # 构造返回结果 - 使用与传感器相同的结构
            if status_data:
                # 构造状态消息
                status_message = "空调状态: "
                
                # 检查电源状态
                if "power" in status_data:
                    if "status" in status_data["power"]:
                        power_status = status_data["power"]["status"]
                        status_message += f"电源{'开启' if power_status else '关闭'}"
                    elif "message" in status_data["power"]:
                        status_message += f"电源状态异常 ({status_data['power']['message']})"
                
                # 检查温度状态
                if "temperature" in status_data:
                    if "target_temperature" in status_data["temperature"]:
                        target_temp = status_data["temperature"]["target_temperature"]
                        status_message += f", 目标温度: {target_temp}°C"
                    elif "message" in status_data["temperature"]:
                        status_message += f", 温度状态异常 ({status_data['temperature']['message']})"
                
                return {
                    "success": True,
                    "status": status_data,
                    "message": status_message,
                    "device": "classroom-ac-controller"
                }
            else:
                # 提供连接状态信息
                mqtt_status = "已连接" if self.mqtt_connected else "连接中"
                return {
                    "success": False,
                    "mqtt_status": mqtt_status,
                    "message": f"暂无空调状态数据，MQTT状态: {mqtt_status}。请等待系统发送状态信息或控制空调后重试"
                }
