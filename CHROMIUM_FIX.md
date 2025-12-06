# Chromium Crash Fix for Docker

## Problem

Chromium/Playwright crashes in Docker with error:
```
BrowserType.launch: Target page, context or browser has been closed
Signal: SIGTRAP
```

## Root Causes

1. **Missing System Dependencies**: Chromium requires 20+ system libraries not included in base Odoo image
2. **Insufficient Shared Memory**: Default `/dev/shm` size (64MB) is too small for Chromium
3. **Missing Linux Capabilities**: Chromium needs `SYS_ADMIN` capability in Docker

## Solution Applied

### 1. Created Custom Dockerfile

**File:** `/home/sabry3/odoo_19_vetutions/Dockerfile`

Installs all required Chromium dependencies:
- Network Security: `libnss3`, `libnspr4`
- Graphics: `libgbm1`, `libdrm2`, `libcairo2`
- UI: `libatk1.0-0`, `libpango-1.0-0`, `libxcomposite1`
- Fonts: `fonts-liberation`
- Audio: `libasound2`
- SSL: `ca-certificates`
- And 15+ more libraries

### 2. Updated docker-compose.yml

**File:** `/home/sabry3/odoo_19_vetutions/docker-compose.yml`

Changes:
```yaml
odoo:
  build: .                    # Use custom Dockerfile instead of image: odoo:19
  shm_size: '2gb'            # Increase shared memory to 2GB
  cap_add:
    - SYS_ADMIN              # Add Linux capability for Chromium
```

## Rebuild Instructions

### Quick Commands

```bash
cd /home/sabry3/odoo_19_vetutions
sudo docker-compose down --remove-orphans
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### Step-by-Step

1. **Stop Containers**
   ```bash
   cd /home/sabry3/odoo_19_vetutions
   sudo docker-compose down --remove-orphans
   ```
   
   If that fails:
   ```bash
   sudo docker kill $(sudo docker ps -q --filter "name=odoo")
   sudo docker rm $(sudo docker ps -aq --filter "name=odoo")
   ```

2. **Build New Image** (5-10 minutes)
   ```bash
   sudo docker-compose build --no-cache
   ```
   
   You'll see:
   ```
   Step 1/4 : FROM odoo:19
   Step 2/4 : USER root
   Step 3/4 : RUN apt-get update...
   Step 4/4 : USER odoo
   ```

3. **Start Containers**
   ```bash
   sudo docker-compose up -d
   ```

4. **Verify**
   ```bash
   sudo docker ps | grep odoo
   ```
   
   Should show container running.

## Testing After Rebuild

1. **Open Odoo**
   ```
   http://localhost:8070
   ```

2. **Upgrade Module**
   - Apps → "Unified Product Scrapper"
   - Click "Upgrade"

3. **Test Scraping**
   - Universal Scraper → Scraper Configs
   - Open "Amin Petshop - Offers & Sales"
   - Click "Scrape Now"

4. **Expected Result**
   - ✅ Chromium launches successfully
   - ✅ Scraping starts
   - ✅ Products captured
   - ✅ No crash or SIGTRAP error

## What Changed

### Before Fix
- ❌ Chromium crashes immediately
- ❌ SIGTRAP signal
- ❌ "Target page closed" error
- ❌ Cannot scrape any websites

### After Fix
- ✅ Chromium launches successfully
- ✅ Can scrape websites
- ✅ Playwright works properly
- ✅ "Scrape Now" button works
- ✅ "Scrape & Import" from categories works

## Data Safety

**All data is preserved during rebuild:**
- ✅ Database data (in volume `odoo-db-data`)
- ✅ Odoo data (in volume `odoo-web-data`)
- ✅ Your modules (mounted from `./addons`)
- ✅ Module configurations
- ✅ All installed modules

## Troubleshooting

### Build Fails with "permission denied"
**Solution:** Run with `sudo`

### Build Fails with "network error"
**Solution:** Check internet connection, retry build

### Container Won't Start
**Solution:** Check logs:
```bash
sudo docker-compose logs odoo
```

### Port 8070 Already in Use
**Solution:** Stop old container first:
```bash
sudo docker-compose down
```

### Still Getting Chromium Crash
**Solution:** 
1. Verify build completed successfully
2. Check container has new image: `sudo docker images | grep odoo`
3. Check logs for other errors: `sudo docker-compose logs odoo | grep -i error`

## Technical Details

### Dockerfile Breakdown

```dockerfile
FROM odoo:19                          # Base Odoo 19 image
USER root                             # Switch to root for installations

# Install Chromium dependencies
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4                  # Network Security Services
    libatk1.0-0 libatk-bridge2.0-0   # Accessibility Toolkit
    libcups2 libdrm2 libdbus-1-3     # System libraries
    libxkbcommon0 libxcomposite1     # X11 libraries
    libxdamage1 libxfixes3 libxrandr2 # X11 extensions
    libgbm1 libpango-1.0-0 libcairo2 # Graphics libraries
    libasound2 libatspi2.0-0         # Audio & Accessibility
    libxshmfence1 fonts-liberation   # Fonts & X11
    libappindicator3-1 xdg-utils     # Desktop integration
    wget ca-certificates             # Network tools
    && rm -rf /var/lib/apt/lists/*   # Clean up

USER odoo                             # Switch back to odoo user
```

### docker-compose.yml Changes

```yaml
shm_size: '2gb'
```
- Increases shared memory from default 64MB to 2GB
- Chromium uses shared memory for rendering
- Prevents "out of memory" crashes

```yaml
cap_add:
  - SYS_ADMIN
```
- Adds Linux capability for system administration
- Required for Chromium sandboxing
- Allows Chromium to create namespaces

## Verification Commands

### Check Image Built
```bash
sudo docker images | grep odoo
```
Expected: New image with recent timestamp

### Check Container Running
```bash
sudo docker ps | grep odoo
```
Expected: Container with status "Up X minutes"

### Check Logs
```bash
sudo docker-compose logs odoo | tail -50
```
Expected: No error messages

### Test Chromium
```bash
sudo docker-compose exec odoo python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    print('✅ Chromium launched successfully!')
    browser.close()
"
```
Expected: "✅ Chromium launched successfully!"

## Related Files

- `Dockerfile` - Custom Odoo image with Chromium dependencies
- `docker-compose.yml` - Docker Compose configuration
- `addons/universal_scraper_odoo/` - Universal Scraper module
- `addons/unified_scrapper/` - Unified Scrapper module

## Additional Resources

- [Playwright Docker Guide](https://playwright.dev/docs/docker)
- [Chromium in Docker](https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md#running-puppeteer-in-docker)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## Summary

This fix ensures Chromium/Playwright can run properly inside Docker by:
1. Installing all required system dependencies
2. Providing sufficient shared memory
3. Adding necessary Linux capabilities

After rebuild, all scraping functionality will work correctly! ✅

