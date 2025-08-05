#!/usr/bin/env python3
"""
Test actual connection to Minetest server
"""

import asyncio
import logging
from luanti_voyager.connection import LuantiConnection

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_connection():
    """Test connecting to the server"""
    conn = LuantiConnection(host="localhost", port=50000)
    
    try:
        logger.info("Attempting to connect to localhost:50000...")
        await conn.connect()
        logger.info("Connected successfully!")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Try to get nearby blocks
        blocks = conn.get_nearby_blocks(radius=5)
        logger.info(f"Nearby blocks: {blocks}")
        
        # Try to move
        logger.info("Attempting to move...")
        await conn.send_player_pos(10, 10, 10)
        
        await asyncio.sleep(2)
        
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Disconnecting...")
        await conn.disconnect()


if __name__ == "__main__":
    asyncio.run(test_connection())