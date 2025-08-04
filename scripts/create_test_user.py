#!/usr/bin/env python3
"""
Create a test user for Minetest/Luanti by directly modifying auth.txt

This script creates a new user with all privileges without needing
to connect to the server or have an existing admin user.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manage_auth import MinetestAuth

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CreateTestUser')


def create_test_user(auth_file, username, password, privileges="all"):
    """
    Create a test user with specified privileges
    
    Args:
        auth_file: Path to auth.txt
        username: Username to create
        password: Password for the user
        privileges: Privileges to grant (default: all)
    """
    logger.info(f"Creating test user: {username}")
    
    # Load auth database
    auth = MinetestAuth(auth_file)
    
    # Check if user already exists
    if username in auth.users:
        logger.warning(f"User {username} already exists, updating password and privileges")
        # Update existing user
        auth.delete_user(username)
    
    # Create user with privileges
    if privileges == "all":
        # Full privilege set for testing
        priv_list = "interact,shout,privs,basic_privs,password,ban,kick,give,teleport,bring,settime,server,protection_bypass,rollback,debug,fly,fast,noclip,creative"
    else:
        priv_list = privileges
        
    success = auth.create_user(username, password, priv_list)
    
    if success:
        auth.save_auth()
        logger.info(f"✅ Created user {username} with privileges: {priv_list}")
        
        # Don't save credentials to file for security
        # Instead, display them for the user to save securely
        print("\n" + "="*60)
        print("USER CREATED SUCCESSFULLY")
        print("="*60)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Privileges: {priv_list}")
        print("\nIMPORTANT: Save these credentials securely!")
        print("Use environment variables to pass credentials:")
        print(f"  export MINETEST_USERNAME={username}")
        print(f"  export MINETEST_PASSWORD={password}")
        print("="*60 + "\n")
        
        return True
    else:
        logger.error(f"Failed to create user {username}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Create test user for Minetest/Luanti directly in auth.txt'
    )
    parser.add_argument('--world-path', required=True, 
                        help='Path to world directory (contains auth.txt)')
    parser.add_argument('--username', default='TestBot',
                        help='Username to create (default: TestBot)')
    parser.add_argument('--password', default='test123',
                        help='Password for user (default: test123)')
    parser.add_argument('--privileges', default='all',
                        help='Privileges to grant (default: all)')
    
    args = parser.parse_args()
    
    # Find auth.txt
    auth_file = os.path.join(args.world_path, 'auth.txt')
    if not os.path.exists(auth_file):
        logger.error(f"auth.txt not found at {auth_file}")
        logger.error("Make sure the world path is correct")
        sys.exit(1)
    
    # Create the test user
    success = create_test_user(
        auth_file=auth_file,
        username=args.username,
        password=args.password,
        privileges=args.privileges
    )
    
    if success:
        print(f"\n✅ Test user '{args.username}' created successfully!")
        print(f"You can now use this user to connect to the server.")
        print(f"\nExample usage:")
        print(f"  python scripts/voyager_shrine_builder_udp.py --username {args.username} --password {args.password}")
    else:
        print(f"\n❌ Failed to create test user")
        sys.exit(1)


if __name__ == "__main__":
    main()