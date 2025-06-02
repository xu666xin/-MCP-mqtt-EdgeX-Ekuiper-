"""
EMQX HTTP API Client Module

This module provides a client for interacting with the EMQX MQTT broker's HTTP API.
It handles authentication, request formatting, and response processing.
"""

import httpx
import base64
import logging
from .config import EMQX_API_URL, EMQX_API_KEY, EMQX_API_SECRET

class EMQXClient:
    """
    EMQX HTTP API Client
    
    Provides methods to interact with EMQX Cloud or self-hosted EMQX broker 
    through its HTTP API. Handles authentication and error processing.
    
    Attributes:
        api_url (str): The base URL for the EMQX HTTP API
        api_key (str): API key for authentication
        api_secret (str): API secret for authentication
        logger (Logger): Logger instance for logging messages
    """

    def __init__(self, logger: logging.Logger):
        """
        初始化EMQX HTTP API客户端
        
        Args:
            logger: 日志记录器实例，用于记录API调用和错误信息
        """
        self.api_url = EMQX_API_URL
        self.api_key = EMQX_API_KEY
        self.api_secret = EMQX_API_SECRET
        self.logger = logger
        
    def _get_auth_header(self):
        """Create authorization header for EMQX Cloud API"""
        auth_string = f"{self.api_key}:{self.api_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response):
        """Process API response, extract data and handle errors"""
        try:
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            else:
                error_msg = f"EMQX API Error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error processing response: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    async def publish_message(self, topic: str, payload: str, qos: int=0, retain: bool=False):
        """
        Publish a message to an MQTT topic.
        
        Uses the EMQX HTTP API to publish a message to a specific MQTT topic.
        
        Args:
            topic (str): The MQTT topic to publish to
            payload (str): The message payload to publish
            qos (int, optional): Quality of Service level (0, 1, or 2). Defaults to 0.
            retain (bool, optional): Whether to retain the message. Defaults to False.
            
        Returns:
            dict: Response from the EMQX API or error information
        """
        url = f"{self.api_url}/publish"
        data = {
            "topic": topic,
            "payload": payload,
            "qos": qos,
            "retain": retain
        }
        self.logger.info(f"Publishing message to topic {topic}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self._get_auth_header(), json=data, timeout=30)
                response.raise_for_status()
                return self._handle_response(response)
            except Exception as e:
                self.logger.error(f"Error publishing message: {str(e)}")
                return {"error": str(e)}
            
    async def list_clients(self, params=None):
        """
        Get a list of connected MQTT clients.

        Uses the EMQX HTTP API to retrieve information about connected clients.
        
        Args:
            params (dict, optional): Query parameters to filter results:
                - page: Page number (default: 1)
                - limit: Results per page, max 10000 (default: 10)
                - clientid: Client ID
                - username: Username
                - ip_address: Client IP address
                - conn_state: Connection state
                - clean_start: Clean start flag
                - proto_ver: Protocol version
                - like_clientid: Fuzzy search by client ID pattern
                - like_username: Fuzzy search by username pattern
                - like_ip_address: Fuzzy search by IP address pattern

        Returns:
            dict: Response from the EMQX API containing client data or error information
        """
        url = f"{self.api_url}/clients"

        # Default params if none provided
        if params is None:
            params = {"page": 1, "limit": 10}

        self.logger.info("Retrieving list of MQTT clients")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._get_auth_header(),
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                return self._handle_response(response)
            except Exception as e:
                self.logger.error(f"Error retrieving clients: {str(e)}")
                return {"error": str(e)}
                
    async def get_client_info(self, clientid: str):
        """
        Get detailed information about a specific MQTT client by client ID.
        
        Uses the EMQX HTTP API to retrieve detailed information about a specific
        client identified by its client ID.
        
        Args:
            clientid (str): The unique identifier of the client to retrieve
            
        Returns:
            dict: Response from the EMQX API containing client data or error information
        """
        url = f"{self.api_url}/clients/{clientid}"
        
        self.logger.info(f"Retrieving information for client ID: {clientid}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._get_auth_header(),
                    timeout=30
                )
                response.raise_for_status()
                return self._handle_response(response)
            except Exception as e:
                self.logger.error(f"Error retrieving client info for {clientid}: {str(e)}")
                return {"error": str(e)}
                
    async def kick_client(self, clientid: str):
        """
        Kick out (disconnect) a client from the MQTT broker.
        
        Uses the EMQX HTTP API to forcibly disconnect a client identified by its client ID.
        
        Args:
            clientid (str): The unique identifier of the client to disconnect
            
        Returns:
            dict: Response from the EMQX API or error information
        """
        url = f"{self.api_url}/clients/{clientid}"
        
        self.logger.info(f"Kicking out client with ID: {clientid}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    url,
                    headers=self._get_auth_header(),
                    timeout=30
                )
                response.raise_for_status()
                # For successful delete operations, return a success message
                if response.status_code == 204:  # No Content
                    return {"success": True, "message": f"Client {clientid} has been disconnected"}
                return self._handle_response(response)
            except Exception as e:
                self.logger.error(f"Error kicking out client {clientid}: {str(e)}")
                return {"error": str(e)}