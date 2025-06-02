"""
Configuration Module for EMQX MCP Server

This module loads configuration parameters from environment variables,
specifically for connecting to the EMQX Cloud or self-hosted EMQX API.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# EMQX Cloud API configuration. 
# These variables should be set in the environment or .env file
EMQX_API_URL = os.getenv("EMQX_API_URL", "")  # Base URL for the EMQX HTTP API
EMQX_API_KEY = os.getenv("EMQX_API_KEY", "")  # API key for authentication
EMQX_API_SECRET = os.getenv("EMQX_API_SECRET", "")  # API secret for authentication

# EMQX MQTT Broker configuration for direct MQTT connections
# Used for subscribing to topics and real-time message monitoring
EMQX_BROKER_HOST = os.getenv("EMQX_BROKER_HOST", "")  # MQTT broker hostname
EMQX_BROKER_PORT = int(os.getenv("EMQX_BROKER_PORT", "1883"))  # MQTT broker port
EMQX_USERNAME = os.getenv("EMQX_USERNAME", "")  # MQTT username
EMQX_PASSWORD = os.getenv("EMQX_PASSWORD", "")  # MQTT password
EMQX_USE_SSL = os.getenv("EMQX_USE_SSL", "false").lower() == "true"  # Enable SSL/TLS

# Temperature Control System specific configuration
CLASSROOM_ID = os.getenv("CLASSROOM_ID", "classroom_01")  # Default classroom ID
CLASSROOM_TOPIC_PREFIX = os.getenv("CLASSROOM_TOPIC_PREFIX", "classroom")  # Topic prefix for classroom messages

# Temperature Control tool configuration
MESSAGE_HISTORY_SIZE = int(os.getenv("MESSAGE_HISTORY_SIZE", "20"))  # Number of messages to keep in history
AC_TEMP_MIN = float(os.getenv("AC_TEMP_MIN", "18"))  # Minimum AC temperature (°C)
AC_TEMP_MAX = float(os.getenv("AC_TEMP_MAX", "28"))  # Maximum AC temperature (°C)
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))  # MQTT keepalive timeout
SSL_VERIFY_CERTS = os.getenv("SSL_VERIFY_CERTS", "false").lower() == "true"  # Verify SSL certificates