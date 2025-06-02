"""
EMQX MCP Server Package

This is the main package for the EMQX MCP Server
"""

from .server import EMQXMCPServer


def main():
    """
    EMQX MCP服务器主入口点
    
    创建并启动EMQX MCP服务器实例。
    """
    # Main entry point for the EMQX MCP Server
    server = EMQXMCPServer()
    server.run()

if __name__ == "__main__":
    main()