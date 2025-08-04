#!/usr/bin/env python3
"""
Example of using the UDP connection to connect to a Minetest/Luanti server.

This demonstrates the basic connection flow and how to send chat messages.
"""

import asyncio
import logging
from luanti_voyager import UDPLuantiConnection

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.INFO)


async def main():
    """Main example function"""
    # Create connection instance
    # Default connects to localhost:30000
    conn = UDPLuantiConnection(
        host="localhost",
        port=30000,  # Change to your server port
        username="VoyagerBot",
        password=""  # Empty password for servers that allow it
    )
    
    try:
        print("Connecting to server...")
        await conn.connect()
        
        if conn.connected:
            print(f"Successfully connected! Peer ID: {conn.peer_id}")
            
            # Send a chat message
            await conn.send_chat_message("Hello from luanti-voyager!")
            
            # Keep connection alive for a bit
            print("Waiting for server messages...")
            await asyncio.sleep(5)
            
        else:
            print("Failed to establish connection")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Always disconnect cleanly
        await conn.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())