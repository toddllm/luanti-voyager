#!/bin/bash
# Batch reprocess notebooks in background

LOG_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/notebook_reprocess_batch_$TIMESTAMP.log"

echo "Starting notebook reprocessing batch"
echo "This will take time on MacBook - running in background"
echo "Log file: $LOG_FILE"
echo ""

# Run the reprocessing in background
nohup python scripts/simple_notebook_reprocess.py > "$LOG_FILE" 2>&1 &
PID=$!

echo "Started batch process with PID: $PID"
echo "To monitor progress: tail -f $LOG_FILE"
echo "To check if complete: ps -p $PID"
echo ""
echo "The process will:"
echo "  - Re-synthesize Multi-Agent Swarm (with 26 code cells)"
echo "  - Re-synthesize Production RAG"
echo "  - Re-synthesize LLM Optimization"  
echo "  - Re-synthesize Guardrails"
echo ""
echo "Each synthesis may take 5-10 minutes on MacBook with qwen2.5-coder:32b"
echo "Total estimated time: 20-40 minutes"