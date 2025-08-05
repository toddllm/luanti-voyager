#!/bin/bash
# Quick Ollama traffic monitor - captures snippets periodically

LOG_DIR="logs/ollama_traffic"
DEBUG_LOG="logs/ollama_monitor_debug.log"
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_debug() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_LOG"
}

log_debug "Starting Ollama traffic monitor on port 11434"
log_debug "Capture files will be saved to: $LOG_DIR"

while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    CAPTURE_FILE="$LOG_DIR/capture_${TIMESTAMP}.txt"
    
    log_debug "Starting 30-second capture..."
    
    # Capture for 30 seconds, filter for POST requests and responses
    # Using full path to tcpdump for sudoers compatibility
    sudo /opt/homebrew/bin/timeout 30 /usr/sbin/tcpdump -i lo0 -A -s 0 'tcp port 11434' 2>>"$DEBUG_LOG" | \
        grep -E -A 10 -B 2 "(POST|HTTP/1.1|prompt|response|model|generate)" > "$CAPTURE_FILE" 2>>"$DEBUG_LOG"
    
    # Check if we captured anything
    if [ -s "$CAPTURE_FILE" ]; then
        LINES_CAPTURED=$(wc -l < "$CAPTURE_FILE")
        log_debug "Captured $LINES_CAPTURED lines of Ollama traffic"
        
        # Save a preview to debug log
        echo "--- Preview of capture at $(date) ---" >> "$DEBUG_LOG"
        head -20 "$CAPTURE_FILE" | grep -E "(POST|prompt|model)" >> "$DEBUG_LOG" 2>&1
        echo "--- End preview ---" >> "$DEBUG_LOG"
    else
        log_debug "No Ollama traffic detected in this capture window"
        rm -f "$CAPTURE_FILE"  # Remove empty files
    fi
    
    log_debug "Waiting 2 minutes before next capture..."
    sleep 120
done