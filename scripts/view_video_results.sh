#!/bin/bash

# View results of video processing

OUTPUT_DIR="docs/video-analysis/multi-agent-systems"
ANALYSIS_DIR="$OUTPUT_DIR/analysis"

echo "📺 Video Processing Results"
echo "==========================="
echo ""

# Check if analysis is complete
if [ -f "$ANALYSIS_DIR"/*_report.md ]; then
    echo "✅ Processing COMPLETE!"
    echo ""
    
    # Show report summary
    REPORT=$(ls -t "$ANALYSIS_DIR"/*_report.md | head -1)
    echo "📄 Report: $REPORT"
    echo ""
    echo "Summary (first 50 lines):"
    echo "-------------------------"
    head -n 50 "$REPORT"
    echo ""
    echo "... (truncated - view full report at $REPORT)"
    echo ""
    
    # Check for extracted code
    if [ -f "$ANALYSIS_DIR"/*_complete.json ]; then
        JSON_FILE=$(ls -t "$ANALYSIS_DIR"/*_complete.json | head -1)
        echo ""
        echo "📊 Statistics:"
        echo "--------------"
        
        # Count code frames using Python
        python3 -c "
import json
with open('$JSON_FILE') as f:
    data = json.load(f)
    code_frames = [f for f in data.get('code_frames', []) if f.get('code')]
    print(f'  Total code frames extracted: {len(code_frames)}')
    print(f'  Video duration: {data.get(\"transcript\", {}).get(\"duration\", 0):.1f} seconds')
    print(f'  Processing time: {data.get(\"processing_time\", 0):.1f} seconds')
" 2>/dev/null || echo "  Unable to parse statistics"
    fi
    
    echo ""
    echo "📁 All output files:"
    echo "-------------------"
    ls -lh "$OUTPUT_DIR"/*/* 2>/dev/null | grep -v "^total" | tail -20
    
else
    echo "⏳ Processing not complete yet"
    echo ""
    echo "Run ./scripts/check_video_progress.sh to see current status"
fi

echo ""
echo "💡 Quick commands:"
echo "  View full report:  cat $ANALYSIS_DIR/*_report.md"
echo "  View JSON data:    jq . $ANALYSIS_DIR/*_complete.json"
echo "  View code frames:  ls $OUTPUT_DIR/frames/"
echo "  Check progress:    ./scripts/check_video_progress.sh"