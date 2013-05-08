#!/usr/bin/env bash
FEED_URL="$1"
NEW_NAME="$2"
REL_PATH=$( dirname `readlink -f "$0"` )
SOURCES_FILE="$REL_PATH/sources"

wget -O "$NEW_NAME" "$FEED_URL"
if [ $? -eq 0 ]; then
    echo "$NEW_NAME = $FEED_URL" >> "$SOURCES_FILE"
    echo "New file added"
else
    echo "Download did not complete. Not adding feed."
fi
