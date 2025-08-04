#!/usr/bin/env python3
"""
Direct auth.txt management for Minetest/Luanti servers

This script directly modifies the auth.txt file to create users and grant privileges
without needing to connect to the server.
"""

import os
import hashlib
import base64
import secrets
import argparse
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AuthManager')


class MinetestAuth:
    """Manage Minetest authentication database"""
    
    def __init__(self, auth_file_path):
        self.auth_file = auth_file_path
        self.users = {}
        self.load_auth()
        
    def load_auth(self):
        """Load existing auth.txt"""
        if not os.path.exists(self.auth_file):
            logger.warning(f"Auth file {self.auth_file} does not exist")
            return
            
        with open(self.auth_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split(':', 3)
                if len(parts) >= 3:
                    username = parts[0]
                    auth_data = parts[1]
                    privs = parts[2] if len(parts) > 2 else ""
                    timestamp = parts[3] if len(parts) > 3 else str(int(datetime.now().timestamp()))
                    
                    self.users[username] = {
                        'auth': auth_data,
                        'privs': privs,
                        'timestamp': timestamp
                    }
                    
        logger.info(f"Loaded {len(self.users)} users from auth.txt")
        
    def save_auth(self):
        """Save auth.txt with backup"""
        # Create backup
        if os.path.exists(self.auth_file):
            backup_file = f"{self.auth_file}.backup.{int(datetime.now().timestamp())}"
            os.rename(self.auth_file, backup_file)
            logger.info(f"Created backup: {backup_file}")
            
        # Write new auth file
        with open(self.auth_file, 'w') as f:
            for username, data in self.users.items():
                line = f"{username}:{data['auth']}:{data['privs']}:{data['timestamp']}\n"
                f.write(line)
                
        logger.info(f"Saved {len(self.users)} users to auth.txt")
        
    def hash_password(self, username, password):
        """
        Create Minetest-style password hash
        Format: #1#salt#hash
        Where hash is base64(sha256(username + salt + password))
        """
        # Generate random salt
        salt_bytes = secrets.token_bytes(16)
        salt_b64 = base64.b64encode(salt_bytes).decode('ascii').rstrip('=')
        
        # Create hash: sha256(name + salt + password)
        data = username.encode('utf-8') + salt_bytes + password.encode('utf-8')
        hash_bytes = hashlib.sha256(data).digest()
        hash_b64 = base64.b64encode(hash_bytes).decode('ascii').rstrip('=')
        
        return f"#1#{salt_b64}#{hash_b64}"
        
    def create_user(self, username, password, privileges="interact,shout"):
        """Create a new user with password and privileges"""
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return False
            
        auth_hash = self.hash_password(username, password)
        timestamp = str(int(datetime.now().timestamp()))
        
        self.users[username] = {
            'auth': auth_hash,
            'privs': privileges,
            'timestamp': timestamp
        }
        
        logger.info(f"Created user {username} with privileges: {privileges}")
        return True
        
    def update_privileges(self, username, privileges):
        """Update user privileges"""
        if username not in self.users:
            logger.error(f"User {username} does not exist")
            return False
            
        self.users[username]['privs'] = privileges
        logger.info(f"Updated {username} privileges to: {privileges}")
        return True
        
    def delete_user(self, username):
        """Delete a user"""
        if username not in self.users:
            logger.error(f"User {username} does not exist")
            return False
            
        del self.users[username]
        logger.info(f"Deleted user {username}")
        return True
        
    def list_users(self):
        """List all users and their privileges"""
        for username, data in self.users.items():
            privs = data['privs'] if data['privs'] else "(no privileges)"
            print(f"{username}: {privs}")


def main():
    parser = argparse.ArgumentParser(description='Manage Minetest auth.txt directly')
    parser.add_argument('--auth-file', required=True, help='Path to auth.txt')
    parser.add_argument('--action', choices=['create', 'update', 'delete', 'list'], 
                        required=True, help='Action to perform')
    parser.add_argument('--username', help='Username')
    parser.add_argument('--password', help='Password (for create)')
    parser.add_argument('--privileges', help='Privileges (comma-separated)')
    
    args = parser.parse_args()
    
    auth = MinetestAuth(args.auth_file)
    
    if args.action == 'list':
        auth.list_users()
        
    elif args.action == 'create':
        if not args.username or not args.password:
            logger.error("Username and password required for create")
            return
            
        privs = args.privileges or "interact,shout"
        if auth.create_user(args.username, args.password, privs):
            auth.save_auth()
            
    elif args.action == 'update':
        if not args.username or not args.privileges:
            logger.error("Username and privileges required for update")
            return
            
        if auth.update_privileges(args.username, args.privileges):
            auth.save_auth()
            
    elif args.action == 'delete':
        if not args.username:
            logger.error("Username required for delete")
            return
            
        if args.username == "Toby":
            # Delete Toby as requested
            if auth.delete_user(args.username):
                auth.save_auth()
                logger.info("Removed Toby user as requested")


if __name__ == "__main__":
    main()