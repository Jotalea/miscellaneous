#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# watch_url.sh — Notify when URL stops returning 404
# Usage: bash watch_url.sh [interval_seconds]
# Default interval: 300 seconds (5 minutes)
# ============================================================

URL="FIND THE URL FROM YOUR ANIME PROVIDER"
INTERVAL="${1:-300}"
LOG_FILE="$HOME/watch_url.log"

echo "[$(date)] Starting watch on: $URL" | tee -a "$LOG_FILE"
echo "[$(date)] Checking every ${INTERVAL}s" | tee -a "$LOG_FILE"

while true; do
    STATUS=$(curl -o /dev/null -s -w "%{http_code}" \
        --max-time 15 \
        --user-agent "Mozilla/5.0 (Android 13; Mobile) AppleWebKit/537.36" \
        "$URL")

    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] HTTP status: $STATUS" | tee -a "$LOG_FILE"

    if [ "$STATUS" != "404" ] && [ "$STATUS" != "000" ]; then
        # Send notification via Termux API
        termux-notification \
            --title "TIME TO AURA FARM" \
            --content "re:zero s4e9 is out" \
            --sound \
            --vibrate 0,500,200,500 \
            --priority high \
            --id 9001

        echo "[$TIMESTAMP] Status $STATUS — notification sent!" | tee -a "$LOG_FILE"
        exit 0
    fi

    sleep "$INTERVAL"
done