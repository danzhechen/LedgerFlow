#!/bin/bash
# Monitor processing and show filtered output

LOG_FILE="/tmp/process_all_sheets.log"

echo "Monitoring processing progress..."
echo "Press Ctrl+C to stop monitoring (processing will continue in background)"
echo ""

while true; do
    if [ -f "$LOG_FILE" ]; then
        clear
        echo "=== Processing Progress ==="
        echo ""
        grep -E "(Processing sheet|✅|❌|Generated|ledger entries|Output directory|Journal entries|Summary)" "$LOG_FILE" | tail -30
        echo ""
        echo "---"
        echo "Last updated: $(date '+%H:%M:%S')"
        echo "Full log: $LOG_FILE"
    fi
    
    # Check if process is still running
    if ! ps aux | grep -q "[p]rocess_multi_sheet.py"; then
        echo ""
        echo "=== Processing Complete ==="
        grep -E "(Processing sheet|✅|❌|Generated|ledger entries|Output directory|Journal entries|Summary)" "$LOG_FILE"
        break
    fi
    
    sleep 5
done
