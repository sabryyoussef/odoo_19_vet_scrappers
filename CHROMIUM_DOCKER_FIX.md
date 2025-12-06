# Chromium Docker Fix

## Problem

Chromium was crashing in Docker with `SIGTRAP` signal when launched by Playwright:

```
Scraping failed: BrowserType.launch: Target page, context or browser has been closed
<process did exit: exitCode=null, signal=SIGTRAP>
```

## Root Cause

Chromium's default multi-process architecture conflicts with Docker's containerized environment:

1. **Process Isolation**: Docker's process isolation interferes with Chrome's multi-process model
2. **Shared Memory**: Limited `/dev/shm` can cause child processes to fail
3. **Signal Handling**: Signals are handled differently in containers
4. **Missing System Features**: Some browser features require system capabilities not available in containers

## Solution

### 1. Docker Configuration (`docker-compose.yml`)

```yaml
services:
  odoo:
    shm_size: '2gb'           # Increase shared memory
    cap_add:
      - SYS_ADMIN             # Grant necessary capabilities
```

### 2. System Dependencies (`Dockerfile`)

Install all required Chromium libraries:

```dockerfile
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    wget \
    ca-certificates
```

### 3. Chrome Launch Arguments (`unified_scraper.py`)

**CRITICAL**: Add Docker-compatible launch arguments:

```python
launch_args = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--single-process',  # ⭐ MOST IMPORTANT
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-ipc-flooding-protection',
    '--disable-hang-monitor',
    '--disable-breakpad',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--disable-sync',
    '--metrics-recording-only',
    '--mute-audio',
    '--no-default-browser-check',
    '--no-pings',
    '--password-store=basic',
    '--use-mock-keychain',
    '--disable-blink-features=AutomationControlled',
]

self.browser = self.playwright.chromium.launch(
    headless=headless,
    args=launch_args
)
```

## Key Flags Explained

### Critical Flags

- `--single-process`: **MOST IMPORTANT** - Forces Chrome to run in a single process, avoiding Docker's multi-process issues
- `--no-sandbox`: Disables Chrome's sandbox (required in containers)
- `--disable-setuid-sandbox`: Disables setuid sandbox
- `--disable-dev-shm-usage`: Uses `/tmp` instead of `/dev/shm` for shared memory
- `--no-zygote`: Disables the zygote process (child process spawner)

### Stability Flags

- `--disable-gpu`: Disables GPU hardware acceleration
- `--disable-software-rasterizer`: Disables software rasterizer
- `--disable-background-timer-throttling`: Prevents background tab throttling
- `--disable-backgrounding-occluded-windows`: Keeps windows active even when hidden
- `--disable-renderer-backgrounding`: Prevents renderer from being backgrounded

### Performance Flags

- `--disable-ipc-flooding-protection`: Allows more IPC messages
- `--disable-hang-monitor`: Disables hang detection
- `--disable-breakpad`: Disables crash reporting
- `--disable-component-update`: Disables component updates

### Privacy/Security Flags

- `--disable-domain-reliability`: Disables domain reliability monitoring
- `--disable-sync`: Disables Chrome sync
- `--metrics-recording-only`: Only records metrics, doesn't send
- `--mute-audio`: Mutes all audio
- `--no-pings`: Disables ping tracking
- `--disable-blink-features=AutomationControlled`: Hides automation detection

## Testing

After applying the fix:

1. **Test Scraping**:
   ```
   Universal Scraper → Category Mappings → Select Category → "Scrape & Import"
   ```

2. **Expected Result**:
   - ✅ Chromium launches successfully
   - ✅ Page navigates without crashes
   - ✅ Products are scraped
   - ✅ Draft products created

3. **Check Logs**:
   ```bash
   sudo docker logs odoo_19_vetutions-odoo-1 | grep -i chromium
   ```

## Files Modified

1. `docker-compose.yml` - Added `shm_size` and `cap_add`
2. `Dockerfile` - Added Chromium dependencies
3. `addons/universal_scraper_odoo/lib/unified_scraper/unified_scraper.py` - Added launch arguments
4. `addons/universal_scraper_odoo/__manifest__.py` - Bumped version to 19.0.1.2.0

## Rebuild Instructions

If you need to rebuild the container:

```bash
# Stop and remove old container
sudo systemctl restart docker
sleep 5

# Rebuild and start
cd /home/sabry3/odoo_19_vetutions
sudo docker-compose build --no-cache
sudo docker-compose up -d

# Verify
sudo docker ps
sudo docker logs odoo_19_vetutions-odoo-1
```

## Troubleshooting

### Still Getting SIGTRAP?

1. Verify `--single-process` is in the launch args
2. Check shared memory: `df -h | grep shm`
3. Verify dependencies: `docker exec <container> dpkg -l | grep libnss3`

### Permission Denied?

1. Check capabilities: `docker inspect <container> | grep CapAdd`
2. Verify SYS_ADMIN is granted

### Out of Memory?

1. Increase `shm_size` in docker-compose.yml
2. Monitor memory: `docker stats`

## References

- [Playwright Docker Guide](https://playwright.dev/docs/docker)
- [Chrome Headless Docker](https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md#running-puppeteer-in-docker)
- [Chrome Command Line Switches](https://peter.sh/experiments/chromium-command-line-switches/)

## Status

✅ **FIXED** - Chromium now runs successfully in Docker container

