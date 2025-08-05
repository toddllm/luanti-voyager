#!/bin/bash
# Simple Ollama monitor using curl to check if it's active

LOG_DIR="logs/ollama_traffic"
DEBUG_LOG="logs/ollama_monitor_simple.log"
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log_debug() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEBUG_LOG"
}

log_debug "Starting simple Ollama monitor (no sudo required)"

while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # Check if Ollama is responding
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_debug "Ollama is active"
        
        # Try to capture any ongoing generation info
        MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o '"name":"[^"]*"' | head -5)
        if [ ! -z "$MODELS" ]; then
            log_debug "Active models: $MODELS"
        fi
        
        # Check if any ollama processes are running
        OLLAMA_PROCS=$(ps aux | grep -E "(ollama run|ollama serve)" | grep -v grep | wc -l)
        if [ $OLLAMA_PROCS -gt 0 ]; then
            log_debug "Found $OLLAMA_PROCS Ollama processes running"
        fi
    else
        log_debug "Ollama not responding on port 11434"
    fi
    
    # Also log any running synthesis processes
    SYNTH_PROCS=$(ps aux | grep -E "(enhanced_batch_processor|qwen2.5-coder)" | grep -v grep | head -2)
    if [ ! -z "$SYNTH_PROCS" ]; then
        log_debug "Active synthesis processes detected"
        echo "$SYNTH_PROCS" >> "$DEBUG_LOG"
    fi
    
    sleep 120  # Check every 2 minutes
done