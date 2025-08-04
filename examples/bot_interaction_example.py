#!/usr/bin/env python3
"""
Example demonstrating bot movement and world interaction.

This shows how to move the bot, dig blocks, and place blocks.
"""

import asyncio
import logging
from luanti_voyager import UDPLuantiConnection

logging.basicConfig(level=logging.INFO)


async def bot_demo():
    """Demonstrate bot interaction capabilities"""
    conn = UDPLuantiConnection(
        host="localhost",
        port=30000,
        username="InteractionBot"
    )
    
    try:
        print("Connecting to server...")
        await conn.connect()
        
        if not conn.connected:
            print("Failed to connect!")
            return
            
        print(f"Connected! Peer ID: {conn.peer_id}")
        
        # Announce arrival
        await conn.send_chat_message("InteractionBot has joined! Watch me work!")
        await asyncio.sleep(1)
        
        # Move to a specific position
        print("Moving to position (10, 5, 10)...")
        await conn.move_to(10.0, 5.0, 10.0)
        await asyncio.sleep(1)
        
        # Look at a block
        print("Looking at block (10, 4, 12)...")
        await conn.look_at(10.0, 4.0, 12.0)
        await asyncio.sleep(1)
        
        # Jump
        print("Jumping...")
        await conn.jump()
        await asyncio.sleep(1)
        
        # Dig a block
        print("Digging block at (10, 4, 11)...")
        await conn.dig_block(10, 4, 11)
        await asyncio.sleep(1)
        
        # Place a block
        print("Placing block at (10, 4, 11)...")
        await conn.place_block(10, 4, 11)
        await asyncio.sleep(1)
        
        # Move in a square pattern
        print("Moving in a square pattern...")
        positions = [
            (10.0, 5.0, 10.0),
            (15.0, 5.0, 10.0),
            (15.0, 5.0, 15.0),
            (10.0, 5.0, 15.0),
            (10.0, 5.0, 10.0)
        ]
        
        for x, y, z in positions:
            await conn.move_to(x, y, z)
            await asyncio.sleep(0.5)
            
        await conn.send_chat_message("Demo complete! Goodbye!")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await conn.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    asyncio.run(bot_demo())