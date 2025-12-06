#!/bin/bash
# Daily update scheduler script
# Add this to crontab to run daily updates automatically

# Change to script directory
cd /home/sabry3/vetutions

# Activate virtual environment
source venv/bin/activate

# Run daily update (quick mode for prices only)
# This will run in headless mode - you may need to adjust for login
python daily_update.py <<EOF
1
EOF

# Log the update
echo "$(date): Daily update completed" >> update_log.txt

