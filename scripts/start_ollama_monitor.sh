#!/bin/bash
# Wrapper to start Ollama monitor in background

echo "Starting Ollama traffic monitor..."
echo "This will require your sudo password for tcpdump"
echo ""

# Get sudo password upfront
sudo -v

if [ $? -eq 0 ]; then
    echo "✅ Authentication successful"
    echo "Starting monitor in background..."
    
    # Keep sudo alive in background
    (while true; do sudo -n true; sleep 50; done) &
    SUDO_KEEPER=$!
    
    # Start the monitor
    nohup ./scripts/monitor_ollama_traffic.sh > /dev/null 2>&1 &
    MONITOR_PID=$!
    
    echo "📡 Monitor started with PID: $MONITOR_PID"
    echo "📝 Debug log: logs/ollama_monitor_debug.log"
    echo ""
    echo "To stop monitoring:"
    echo "  kill $MONITOR_PID $SUDO_KEEPER"
    
    # Save PIDs for later
    echo "$MONITOR_PID $SUDO_KEEPER" > logs/ollama_monitor.pid
else
    echo "❌ Failed to authenticate. Monitor not started."
fi