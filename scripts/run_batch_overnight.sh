#!/bin/bash
# Run AI Makerspace batch processing overnight

cd "$(dirname "$0")/.."

# Create log directory
mkdir -p logs

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/ai_makerspace_batch_${TIMESTAMP}.log"

echo "Starting AI Makerspace batch processing..."
echo "Log file: $LOG_FILE"
echo "Process will run in background. Check log for progress."

# Run the batch process in background with nohup
nohup .venv-whisper/bin/python scripts/process_all_resources.py > "$LOG_FILE" 2>&1 &

# Get the process ID
PID=$!
echo "Process started with PID: $PID"

# Save PID to file for later reference
echo $PID > logs/batch_process.pid

echo ""
echo "To check progress:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To check if still running:"
echo "  ps -p $PID"
echo ""
echo "To stop the process:"
echo "  kill $PID"