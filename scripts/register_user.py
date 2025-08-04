#!/usr/bin/env python3
"""
Automated user registration for Minetest/Luanti servers

This script creates a new user account on the server with a specified password.
It connects as an admin user first to grant privileges to the new user.
"""

import asyncio
import logging
import sys
import os
import argparse
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luanti_voyager import UDPLuantiConnection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UserRegistration')


def generate_password(length=12):
    """Generate a secure random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


async def register_new_user(host, port, new_username, 
                          new_password=None,
                          admin_user=None,
                          admin_pass=None):
    """
    Register a new user on the server
    
    Note: Minetest handles user registration automatically on first login.
    The user is created when they first connect with a password.
    """
    if new_password is None:
        new_password = generate_password()
        
    logger.info(f"Registering new user: {new_username}")
    logger.info(f"Generated password: {new_password}")
    
    # Step 1: Connect as the new user to create the account
    logger.info("Step 1: Creating user by first login...")
    new_conn = UDPLuantiConnection(
        host=host,
        port=port,
        username=new_username,
        password=new_password
    )
    
    try:
        # Try to connect - this will create the user
        try:
            await new_conn.connect()
        except TimeoutError:
            # Expected on first connection without privileges
            if new_conn.connected:
                logger.info("User created (connected but no auth)")
            else:
                logger.warning("Connection failed - user may not be created")
                
        # Send a message to confirm we're connected
        if new_conn.connected:
            await new_conn.send_chat_message(f"Hello! I'm {new_username}")
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error creating user: {e}")
    finally:
        await new_conn.disconnect()
        
    # Step 2: Connect as admin to grant privileges
    logger.info("Step 2: Connecting as admin to grant privileges...")
    admin_conn = UDPLuantiConnection(
        host=host,
        port=port,
        username=admin_user,
        password=admin_pass
    )
    
    try:
        # Connect as admin
        try:
            await admin_conn.connect()
        except TimeoutError:
            if admin_conn.connected:
                logger.warning("Admin connected but auth timeout - continuing")
                admin_conn.auth_complete = True
            else:
                logger.error("Admin connection failed!")
                return False
                
        logger.info(f"Admin connected, granting privileges to {new_username}")
        
        # Grant privileges
        await admin_conn.send_chat_message(f"/grant {new_username} interact,shout")
        await asyncio.sleep(1)
        
        # Grant additional privileges for testing
        await admin_conn.send_chat_message(f"/grant {new_username} give,creative,fly,fast,noclip")
        await asyncio.sleep(1)
        
        # Grant all privileges for shrine building
        await admin_conn.send_chat_message(f"/grant {new_username} all")
        await asyncio.sleep(1)
        
        logger.info(f"Privileges granted to {new_username}")
        
    except Exception as e:
        logger.error(f"Error granting privileges: {e}")
        return False
    finally:
        await admin_conn.disconnect()
        
    # Step 3: Test the new user
    logger.info("Step 3: Testing new user connection...")
    test_conn = UDPLuantiConnection(
        host=host,
        port=port,
        username=new_username,
        password=new_password
    )
    
    try:
        try:
            await test_conn.connect()
        except TimeoutError:
            if test_conn.connected:
                logger.info("Test connection successful (with timeout)")
                test_conn.auth_complete = True
            else:
                logger.error("Test connection failed!")
                return False
                
        # Test commands
        await test_conn.send_chat_message("/status")
        await asyncio.sleep(1)
        
        await test_conn.send_chat_message(f"I'm {new_username} and I have privileges!")
        await asyncio.sleep(1)
        
        logger.info("User registration and testing complete!")
        
        # Save credentials for future use
        creds_file = f"{new_username}_credentials.txt"
        with open(creds_file, 'w') as f:
            f.write(f"Username: {new_username}\n")
            f.write(f"Password: {new_password}\n")
            f.write(f"Server: {host}:{port}\n")
        logger.info(f"Credentials saved to {creds_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing user: {e}")
        return False
    finally:
        await test_conn.disconnect()


async def main():
    parser = argparse.ArgumentParser(description='Register new user on Minetest server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=50000, help='Server port')
    parser.add_argument('--username', default='VoyagerBot', help='New username to create')
    parser.add_argument('--password', help='Password for new user (auto-generated if not provided)')
    parser.add_argument('--admin-user', default='admin', help='Admin username')
    parser.add_argument('--admin-pass', default='admin', help='Admin password')
    
    args = parser.parse_args()
    
    success = await register_new_user(
        host=args.host,
        port=args.port,
        new_username=args.username,
        new_password=args.password,
        admin_user=args.admin_user,
        admin_pass=args.admin_pass
    )
    
    if success:
        logger.info("✅ User registration successful!")
    else:
        logger.error("❌ User registration failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())