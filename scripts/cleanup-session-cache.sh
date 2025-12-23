#!/bin/bash
# Cleanup old session-specific cache files
# Run this periodically to clean up /tmp cache files from old sessions

echo "🧹 Cleaning up old session cache files..."

# Remove prompt cache files older than 24 hours
find /tmp -name ".claude_last_prompt_*" -type f -mtime +1 -delete 2>/dev/null

# Count remaining cache files
remaining=$(ls -1 /tmp/.claude_last_prompt_* 2>/dev/null | wc -l)
echo "✅ Cleanup complete. ${remaining} active session cache files remaining."
