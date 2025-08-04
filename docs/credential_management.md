# Credential Management Guide

This guide explains how to securely manage credentials when using luanti-voyager.

## Security Best Practices

1. **Never hardcode credentials** in scripts or code
2. **Never commit credentials** to version control
3. **Use environment variables** for passing credentials
4. **Store credentials securely** using a password manager or secure vault

## Setting Up Test Users

### Creating a Test User

Use the `create_test_user.py` script to create users directly in the auth database:

```bash
python scripts/create_test_user.py \
    --world-path /path/to/world \
    --username TestBot \
    --password "your-secure-password"
```

The script will display the credentials. Save them securely!

### Using Environment Variables

Set credentials using environment variables:

```bash
export MINETEST_USERNAME="TestBot"
export MINETEST_PASSWORD="your-secure-password"
export MINETEST_HOST="localhost"
export MINETEST_PORT="30000"
```

### Using a .env File (Not Committed)

Create a `.env` file (already in .gitignore):

```bash
# .env
MINETEST_USERNAME=TestBot
MINETEST_PASSWORD=your-secure-password
MINETEST_HOST=localhost
MINETEST_PORT=30000
```

Then source it:
```bash
source .env
```

## Running Scripts with Credentials

### Using Environment Variables

```bash
# Set credentials
export MINETEST_PASSWORD="your-password"

# Run scripts
python scripts/test_minimal_connection.py
python scripts/voyager_shrine_builder_udp.py --username TestBot
```

### Using Command Line Arguments

Some scripts support password as argument (use with caution):

```bash
python scripts/voyager_shrine_builder_udp.py \
    --username TestBot \
    --password "your-password"
```

## Managing auth.txt Directly

The `manage_auth.py` script allows direct management of the auth database:

```bash
# List users
python scripts/manage_auth.py --auth-file /path/to/auth.txt --action list

# Create user
python scripts/manage_auth.py \
    --auth-file /path/to/auth.txt \
    --action create \
    --username NewUser \
    --password "secure-password" \
    --privileges "interact,shout,give,creative"

# Update privileges
python scripts/manage_auth.py \
    --auth-file /path/to/auth.txt \
    --action update \
    --username ExistingUser \
    --privileges "all"
```

## Security Considerations

1. **File Permissions**: Ensure auth.txt has restrictive permissions:
   ```bash
   chmod 600 /path/to/world/auth.txt
   ```

2. **Password Strength**: Use strong, unique passwords for each user

3. **Privilege Separation**: Only grant necessary privileges:
   - `interact,shout` - Basic player privileges
   - `give,creative,fly` - Builder privileges
   - `all` - Admin privileges (use sparingly)

4. **Regular Audits**: Periodically review auth.txt for unused accounts

## Troubleshooting

### Connection Timeout with Valid Credentials

Some servers may not send AUTH_ACCEPT for users with certain configurations. The scripts handle this by continuing after HELLO if connected.

### Permission Denied

Ensure the user has necessary privileges:
```bash
python scripts/manage_auth.py \
    --auth-file /path/to/auth.txt \
    --action update \
    --username YourBot \
    --privileges "interact,shout,give,creative,fly,fast,noclip"
```

### Testing Credentials

Use the minimal connection test:
```bash
MINETEST_PASSWORD="your-password" python scripts/test_minimal_connection.py
```