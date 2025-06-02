"""
EMQX Client Tools Module

This module provides tools for managing MQTT clients connected to an EMQX broker.
It registers these tools with the MCP server, making them available for clients
to use through the MCP protocol.
"""

import logging
from typing import Any
from ..emqx_client import EMQXClient

class EMQXClientTools:
    """
    EMQX客户端管理工具类
    
    提供MQTT客户端的查询、获取详细信息和踢出等管理功能。
    """
    
    def __init__(self, logger: logging.Logger):
        """
        初始化EMQX客户端工具
        
        Args:
            logger: 日志记录器实例
        """
        self.logger = logger
        self.emqx_client = EMQXClient(logger)

    def register_tools(self, mcp: Any):
        """Register EMQX Client management tools."""
        
        @mcp.tool(name="list_mqtt_clients", 
                  description="List MQTT clients connected to your EMQX Cluster")
        async def list_clients(page: int = 1, limit: int = 100, node: str = None, clientid: str = None, 
                             username: str = None, ip_address: str = None, conn_state: str = None,
                             clean_start: bool = None, proto_ver: str = None, like_clientid: str = None,
                             like_username: str = None, like_ip_address: str = None):
            """Handle list clients request
            
            Args:
                page: Page number (default: 1)
                limit: Results per page, max 10000 (default: 100)
                node: Node name
                clientid: Client ID
                username: Username
                ip_address: Client IP address
                conn_state: Connection state
                clean_start: Clean start flag
                proto_ver: Protocol version
                like_clientid: Fuzzy search by client ID pattern
                like_username: Fuzzy search by username pattern
                like_ip_address: Fuzzy search by IP address pattern
            
            Returns:
                MCPResponse: Response object with list of clients
            """
            self.logger.info("Handling list clients request")
            
            # Build parameters dictionary with non-None values
            params = {
                "page": page,
                "limit": limit
            }
            
            # Add optional parameters if provided
            optional_params = {
                "node": node, "clientid": clientid, "username": username, 
                "ip_address": ip_address, "conn_state": conn_state, 
                "clean_start": clean_start, "proto_ver": proto_ver, 
                "like_clientid": like_clientid, "like_username": like_username, 
                "like_ip_address": like_ip_address
            }
            
            for param_name, param_value in optional_params.items():
                if param_value is not None:
                    params[param_name] = param_value
            
            # Get list of clients from EMQX
            result = await self.emqx_client.list_clients(params)
            
            self.logger.info("Client list retrieved successfully")
            return result 

        @mcp.tool(name="get_mqtt_client", 
                  description="Get detailed information about a specific MQTT client by client ID")
        async def get_client_info(clientid: str):
            """Handle get client info request
            
            Args:
                clientid: Client ID (required) - The unique identifier of the client to retrieve

            Returns:
                MCPResponse: Response object with detailed client information
            """
            self.logger.info("Handling get client info request")
            
            # Validate required parameter
            if not clientid:
                self.logger.error("Client ID is required but was not provided")
                return {"error": "Client ID is required"}
            
            # Get client information from EMQX
            result = await self.emqx_client.get_client_info(clientid)
            
            self.logger.info(f"Client info for '{clientid}' retrieved successfully")
            return result 

        @mcp.tool(name="kick_mqtt_client", 
                  description="Disconnect a client from the MQTT broker by client ID")
        async def kick_client(clientid: str):
            """Handle kick client request
            
            Args:
                clientid: Client ID (required) - The unique identifier of the client to disconnect

            Returns:
                MCPResponse: Response object with the result of the disconnect operation
            """
            self.logger.info("Handling kick client request")
            
            # Validate required parameter
            if not clientid:
                self.logger.error("Client ID is required but was not provided")
                return {"error": "Client ID is required"}
            
            # Kick client from EMQX
            result = await self.emqx_client.kick_client(clientid)
            
            self.logger.info(f"Client '{clientid}' disconnect request processed")
            return result 