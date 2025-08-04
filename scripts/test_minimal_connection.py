#!/usr/bin/env python3
"""
Minimal connection test to debug authentication issues
"""

import asyncio
import logging
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luanti_voyager import UDPLuantiConnection

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def test_connection():
    """Test basic connection"""
    # Get credentials from environment or use defaults
    import os
    
    username = os.environ.get('MINETEST_USERNAME', 'TestBot')
    password = os.environ.get('MINETEST_PASSWORD', '')
    host = os.environ.get('MINETEST_HOST', 'localhost')
    port = int(os.environ.get('MINETEST_PORT', '50000'))
    
    if not password:
        print("Warning: No password set. Use MINETEST_PASSWORD environment variable.")
        print("Example: MINETEST_PASSWORD=yourpass python test_minimal_connection.py")
    
    conn = UDPLuantiConnection(
        host=host,
        port=port,
        username=username,
        password=password
    )
    
    # Override the auth check to be more lenient
    original_check = conn.auth_complete
    conn.connected = False
    
    try:
        await conn.connect()
        print(f"Connected! Peer ID: {conn.peer_id}")
        
        # Try to send a chat message
        await conn.send_chat_message("Hello from minimal bot!")
        
        # Send a test chat message
        await asyncio.sleep(1)
        await conn.send_chat_message("Hello from Toby bot!")
        
        # Keep alive for a bit
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.disconnect()


if __name__ == "__main__":
    asyncio.run(test_connection())