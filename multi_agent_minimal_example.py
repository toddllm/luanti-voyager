#!/usr/bin/env python3
"""Minimal multi-agent example - 20 lines of working code!"""

import asyncio
from luanti_voyager.multi_agent import AgentCommunication

async def minimal_multi_agent():
    # Create two agents with different roles
    builder = AgentCommunication("BuilderBot", "team_alpha")
    explorer = AgentCommunication("ExplorerBot", "team_alpha") 
    
    # Connect them
    builder.register_listener("ExplorerBot", explorer)
    explorer.register_listener("BuilderBot", builder)
    
    # Explorer makes a discovery and shares it
    await explorer.share_discovery("Found diamonds at coordinates (100, -58, 200)!", importance=9)
    
    # Builder receives and processes the message
    messages = await builder.process_messages()
    print(f"BuilderBot received: {messages[0].content}")
    
    # Builder responds with help request
    await builder.request_help("mining the diamonds safely")
    
    # Explorer receives and can respond
    explorer_msgs = await explorer.process_messages()
    print(f"ExplorerBot received help request: {explorer_msgs[0].content}")

if __name__ == "__main__":
    asyncio.run(minimal_multi_agent())