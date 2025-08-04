#!/bin/bash
# Grant admin privileges to specific users on test server

echo "🔑 Granting Admin Privileges"
echo "==========================="

# Find the server PID
SERVER_PID=$(ps aux | grep -E "minetestserver.*50000" | grep -v grep | awk '{print $2}')

if [ -z "$SERVER_PID" ]; then
    echo "❌ Test server not running on port 50000"
    exit 1
fi

echo "✅ Found server PID: $SERVER_PID"

# Create a temporary file with commands
TEMP_CMD="/tmp/devkorth_grant_privs.txt"

cat > "$TEMP_CMD" << EOF
/grant ToddLLM all
/grant Toby all
/grant VoyagerTestBot all
/grant DevkorthTester all
EOF

echo "📝 Granting privileges to:"
echo "   - ToddLLM"
echo "   - Toby"
echo "   - VoyagerTestBot"
echo "   - DevkorthTester"

# Note: Since we can't directly inject commands into the running server,
# we'll add them to the auth file
AUTH_FILE="/home/tdeshane/luanti/devkorth_test_world/auth.txt"

# Check if auth.txt exists
if [ -f "$AUTH_FILE" ]; then
    echo "📋 Updating auth.txt directly..."
    
    # Backup original
    cp "$AUTH_FILE" "${AUTH_FILE}.backup"
    
    # Update privileges for each user
    for user in ToddLLM Toby VoyagerTestBot DevkorthTester; do
        if grep -q "^${user}:" "$AUTH_FILE"; then
            # User exists, update privileges
            sed -i "s/^${user}:.*:.*$/${user}::[all]/" "$AUTH_FILE"
            echo "   ✅ Updated $user"
        else
            # Add new user with all privileges
            echo "${user}::[all]" >> "$AUTH_FILE"
            echo "   ✅ Added $user"
        fi
    done
    
    echo
    echo "✅ Privileges granted!"
    echo "⚠️  Changes will take effect on next login or server restart"
else
    echo "❌ Auth file not found at $AUTH_FILE"
    echo "💡 Users will need to be granted privileges after joining"
fi

# Clean up
rm -f "$TEMP_CMD"

echo
echo "📋 To verify, check the server log or use:"
echo "   grep -E '(ToddLLM|Toby|VoyagerTestBot|DevkorthTester)' $AUTH_FILE"