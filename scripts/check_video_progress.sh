#!/bin/bash

# Check progress of video processing

LOG_FILE="docs/video-analysis/processing.log"
PID_FILE="docs/video-analysis/processing.pid"
OUTPUT_DIR="docs/video-analysis/multi-agent-systems"

echo "📊 Video Processing Status"
echo "=========================="
echo ""

# Check if PID file exists
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # Check if process is still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Processing is RUNNING (PID: $PID)"
        echo ""
        
        # Show process info
        echo "Process details:"
        ps -p $PID -o pid,ppid,%cpu,%mem,etime,command | tail -n 1
        echo ""
    else
        echo "⏹️  Processing has COMPLETED or STOPPED"
        echo ""
    fi
else
    echo "❓ No processing PID found"
    echo ""
fi

# Check outputs created so far
echo "📁 Output files created:"
echo "------------------------"

if [ -d "$OUTPUT_DIR" ]; then
    # Count files in each subdirectory
    for dir in videos audio transcripts frames extracted-code analysis; do
        if [ -d "$OUTPUT_DIR/$dir" ]; then
            count=$(ls -1 "$OUTPUT_DIR/$dir" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$count" -gt 0 ]; then
                echo "  $dir: $count files"
                # Show latest file
                latest=$(ls -t "$OUTPUT_DIR/$dir" 2>/dev/null | head -1)
                if [ ! -z "$latest" ]; then
                    echo "    Latest: $latest"
                fi
            fi
        fi
    done
else
    echo "  Output directory not created yet"
fi

echo ""

# Show last few lines of log
if [ -f "$LOG_FILE" ]; then
    echo "📝 Recent log entries:"
    echo "----------------------"
    tail -n 10 "$LOG_FILE"
    echo ""
    
    # Check for specific progress indicators
    echo "🔄 Processing stages completed:"
    echo "-------------------------------"
    
    if grep -q "Downloaded:" "$LOG_FILE" 2>/dev/null; then
        echo "  ✅ Video download"
    else
        echo "  ⏳ Video download (in progress or pending)"
    fi
    
    if grep -q "Transcribing with Whisper" "$LOG_FILE" 2>/dev/null; then
        if grep -q "Transcript saved:" "$LOG_FILE" 2>/dev/null; then
            echo "  ✅ Audio transcription"
        else
            echo "  ⏳ Audio transcription (in progress)"
        fi
    else
        echo "  ⏳ Audio transcription (pending)"
    fi
    
    if grep -q "Analyzing video for code frames" "$LOG_FILE" 2>/dev/null; then
        if grep -q "Found.*code frames" "$LOG_FILE" 2>/dev/null; then
            frames=$(grep -o "Found [0-9]* code frames" "$LOG_FILE" | tail -1)
            echo "  ✅ Frame extraction ($frames)"
        else
            echo "  ⏳ Frame extraction (in progress)"
        fi
    else
        echo "  ⏳ Frame extraction (pending)"
    fi
    
    if grep -q "Extracting code from" "$LOG_FILE" 2>/dev/null; then
        code_count=$(grep -c "Extracting code from" "$LOG_FILE")
        echo "  ⏳ Code extraction ($code_count frames processed)"
    else
        echo "  ⏳ Code extraction (pending)"
    fi
    
    if grep -q "Analyzing content with" "$LOG_FILE" 2>/dev/null; then
        if grep -q "Processing complete" "$LOG_FILE" 2>/dev/null; then
            echo "  ✅ LLM analysis"
        else
            echo "  ⏳ LLM analysis (in progress)"
        fi
    else
        echo "  ⏳ LLM analysis (pending)"
    fi
    
    if grep -q "Markdown report saved" "$LOG_FILE" 2>/dev/null; then
        echo "  ✅ Report generation"
    fi
    
else
    echo "Log file not found: $LOG_FILE"
fi

echo ""
echo "💡 Tips:"
echo "  - Watch logs: tail -f $LOG_FILE"
echo "  - View results: ls -la $OUTPUT_DIR/"
echo "  - Stop process: kill \$(cat $PID_FILE)"