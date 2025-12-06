# Daily Update Guide

## Overview
The daily update scripts allow you to keep your product data synchronized with the Vetution website, focusing on price and availability changes.

## Update Scripts

### 1. Interactive Update (`daily_update.py`)
Best for manual daily updates with visual feedback.

**Usage:**
```bash
python daily_update.py
```

**Features:**
- Two modes: Quick (prices only) or Full (all data)
- Browser window opens for login
- Shows progress in real-time
- Creates automatic backups
- Detailed summary report

### 2. Automated Update (`daily_update_auto.py`)
Best for scheduled/cron jobs (requires setup).

**Usage:**
```bash
python daily_update_auto.py
```

**Features:**
- Runs headless (no browser window)
- Uses persistent browser context (saves login)
- Faster execution
- Designed for automation

## What Gets Updated

### Quick Update Mode:
- ✅ Product prices (primary price)
- ✅ Vendor prices (all vendor prices with availability)
- ✅ Min/Max prices
- ✅ Express delivery flag
- ✅ Cold chain flag
- ✅ Review counts
- ✅ New products (adds any new products found)

### Full Update Mode:
- ✅ Everything in Quick Update, plus:
- ✅ Detailed sections (Composition, Indications, etc.)
- ✅ Tags and species
- ✅ Product images
- ✅ All other fields

## Setting Up Automated Daily Updates

### Option 1: Using Cron (Linux/Mac)

1. **First, setup persistent login:**
   ```bash
   # Run once to create browser context with login
   python daily_update_auto.py
   # Login when browser opens, then close
   ```

2. **Add to crontab:**
   ```bash
   crontab -e
   ```

3. **Add this line (runs daily at 2 AM):**
   ```
   0 2 * * * cd /home/sabry3/vetutions && /home/sabry3/vetutions/venv/bin/python /home/sabry3/vetutions/daily_update_auto.py >> /home/sabry3/vetutions/update_log.txt 2>&1
   ```

### Option 2: Using Systemd Timer (Linux)

Create a service file:
```ini
# /etc/systemd/system/vetution-update.service
[Unit]
Description=Vetution Daily Product Update
After=network.target

[Service]
Type=oneshot
User=sabry3
WorkingDirectory=/home/sabry3/vetutions
ExecStart=/home/sabry3/vetutions/venv/bin/python /home/sabry3/vetutions/daily_update_auto.py
StandardOutput=append:/home/sabry3/vetutions/update_log.txt
StandardError=append:/home/sabry3/vetutions/update_log.txt
```

Create a timer file:
```ini
# /etc/systemd/system/vetution-update.timer
[Unit]
Description=Run Vetution update daily
Requires=vetution-update.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable vetution-update.timer
sudo systemctl start vetution-update.timer
```

## Backup System

- Automatic backups are created before each update
- Backups stored in `backups/` directory
- Format: `products_backup_YYYYMMDD_HHMMSS.json`
- Keep last 7 days of backups (manual cleanup recommended)

## Monitoring Updates

### Check Update Log:
```bash
tail -f update_log.txt
```

### Check Latest Backup:
```bash
ls -lt backups/ | head -5
```

### Verify Update Results:
```bash
python monitor_progress.py
```

## Troubleshooting

### Login Issues
- If automated login fails, run interactive script once to refresh session
- Browser context may expire - re-run setup if needed

### Performance
- Quick update: ~5-10 minutes for 706 products
- Full update: ~15-20 minutes
- Adjust `time.sleep()` values in script if needed

### Errors
- Check `update_log.txt` for error messages
- Verify internet connection
- Ensure website is accessible
- Check if website structure changed

## Best Practices

1. **Run Quick Update Daily** - Fastest way to keep prices current
2. **Run Full Update Weekly** - Complete data refresh
3. **Monitor Backups** - Keep backups organized
4. **Check Logs** - Review update_log.txt regularly
5. **Test First** - Run manually before scheduling

## Update Statistics

After each update, you'll see:
- Number of products updated
- Number of new products found
- Price changes detected
- Availability changes
- Any errors encountered

This helps you track what changed and verify the update worked correctly.

