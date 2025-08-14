#!/bin/bash

# Check progress of GPT-OSS analysis

PID_FILE="docs/video-analysis/analysis.pid"
LOG_FILE="docs/video-analysis/gpt_oss_analysis.log"
ANALYSIS_DIR="docs/video-analysis/multi-agent-systems/analysis"

echo "📊 GPT-OSS Analysis Status"
echo "=========================="
echo ""

# Check if PID file exists
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # Check if process is still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Analysis is RUNNING (PID: $PID)"
        
        # Show CPU usage
        CPU=$(ps -p $PID -o %cpu | tail -1 | tr -d ' ')
        echo "   CPU Usage: ${CPU}%"
        
        # Check Ollama connection
        if lsof -p $PID 2>/dev/null | grep -q ":11434"; then
            echo "   📡 Connected to Ollama"
        else
            echo "   ⏳ Waiting for Ollama connection"
        fi
        echo ""
    else
        echo "⏹️  Analysis has COMPLETED or STOPPED"
        echo ""
    fi
else
    echo "❓ No analysis PID found"
    echo ""
fi

# Check log file
if [ -f "$LOG_FILE" ]; then
    echo "📝 Recent log entries:"
    echo "----------------------"
    tail -10 "$LOG_FILE"
    echo ""
fi

# Check for renamed files
echo "📁 File Renaming Status:"
echo "------------------------"
NEW_COUNT=$(ls -1 $ANALYSIS_DIR/*GPT_OSS* 2>/dev/null | wc -l | tr -d ' ')
OLD_COUNT=$(ls -1 $ANALYSIS_DIR/*Multi_Agent* 2>/dev/null | wc -l | tr -d ' ')

if [ "$NEW_COUNT" -gt 0 ]; then
    echo "✅ Files renamed to GPT_OSS format: $NEW_COUNT files"
else
    echo "⏳ Files not yet renamed (still $OLD_COUNT files with old name)"
fi

# Check for analysis output
if [ -f "$ANALYSIS_DIR/GPT_OSS_Analysis_Report.md" ]; then
    echo ""
    echo "✅ Analysis report available!"
    echo "   View with: cat $ANALYSIS_DIR/GPT_OSS_Analysis_Report.md"
elif [ -f "$ANALYSIS_DIR/nyb3TnUkwE8_GPT_OSS_Harmony_Response_Format_llm_analysis.json" ]; then
    echo ""
    echo "✅ Analysis JSON available!"
    echo "   Processing report generation..."
else
    echo ""
    echo "⏳ Analysis in progress..."
fi

echo ""
echo "💡 Commands:"
echo "  Watch logs:     tail -f $LOG_FILE"
echo "  Check network:  lsof -p \$(cat $PID_FILE) | grep 11434"
echo "  Stop analysis:  kill \$(cat $PID_FILE)"