# Installation Guide

## Issue: Module Not Appearing in Apps Menu

If the module doesn't appear in the Apps menu, follow these steps:

### 1. Start Odoo Container

```bash
cd /home/sabry3/odoo_19_vetutions
docker-compose up -d
```

### 2. Verify Module Location

The module should be at:
```
/home/sabry3/odoo_19_vetutions/addons/vetution_product_extension/
```

And it's mounted in Docker as:
```
/mnt/extra-addons/vetution_product_extension/
```

### 3. Check Module Structure

Ensure these files exist:
- ✅ `__manifest__.py` (not `manifest.py`)
- ✅ `__init__.py`
- ✅ `models/__init__.py`
- ✅ `wizard/__init__.py`
- ✅ `security/ir.model.access.csv`

### 4. Update Apps List in Odoo

1. Log into Odoo at `http://localhost:8069`
2. Go to **Apps** menu
3. Click **Update Apps List** button (top right)
4. Wait for the update to complete

### 5. Enable Developer Mode (if needed)

If the module still doesn't appear:
1. Go to **Settings**
2. Enable **Developer Mode**
3. Go back to **Apps**
4. Remove the **Apps** filter (click the X on "Apps" filter)
5. Search for "Vetution" or "vetution_product_extension"

### 6. Check Odoo Logs

If issues persist, check the logs:
```bash
docker-compose logs odoo | grep -i "vetution\|error\|warning" | tail -50
```

### 7. Restart Odoo Container

Sometimes a restart helps:
```bash
docker-compose restart odoo
```

### Common Issues

1. **Manifest file name**: Must be `__manifest__.py` (not `manifest.py`)
2. **Syntax errors**: Check Python syntax in all `.py` files
3. **Missing dependencies**: Ensure `product` and `base` modules are installed
4. **File permissions**: Ensure files are readable by Odoo user
5. **Cache**: Clear browser cache or use incognito mode

### Verify Module is Loaded

After installation, you can verify in Odoo:
1. Go to **Settings > Technical > Database Structure > Models**
2. Search for `product.product`
3. Check if `vetution_*` fields are listed

Or check in Python shell:
```bash
docker-compose exec odoo odoo shell -d your_database_name
```

Then in Python:
```python
self.env['product.product']._fields.get('vetution_brand')
```

