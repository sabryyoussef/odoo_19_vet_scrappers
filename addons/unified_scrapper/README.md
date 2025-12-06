# Unified Product Scrapper

## Overview

The **Unified Product Scrapper** module provides a centralized framework for importing and managing products from multiple external data sources (Vetution, Amin Petshop, Amazon, etc.).

## Key Features

- 🔌 **Configurable Data Sources** - Define CSV/JSON/API sources via UI
- 🗺️ **Flexible Field Mapping** - Map external fields to Odoo fields without code
- 🏷️ **Source Tagging** - Identify and filter products by their origin
- 📊 **Import History** - Track all imports with detailed logs
- 🔄 **Sync Management** - Keep products up-to-date with external sources
- 🎯 **Generic Design** - Easily add new sources without module changes

## Important Note

> **All web scraping is done externally.** This module only consumes structured data (CSV/JSON/API) provided by external scraping systems. No web scraping logic is embedded in Odoo.

## Current Status

**Phase 1: Planning** ✅ COMPLETE

The module skeleton has been created with a comprehensive implementation plan. See `document/unified_scrapper_plan.md` for detailed architecture and roadmap.

**Next Phase: Data Models**

Implementation of core models (data source, field mapping, product extensions) is planned next.

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install "Unified Product Scrapper" from the Apps menu

## Documentation

- **Implementation Plan:** `document/unified_scrapper_plan.md`
- **Odoo Version:** 19.0
- **License:** LGPL-3

## Dependencies

- `base` - Odoo base module
- `product` - Odoo product module

## Roadmap

- [ ] Phase 1: Module Skeleton & Data Models
- [ ] Phase 2: Settings & UI
- [ ] Phase 3: Import Engine
- [ ] Phase 4: Migration from Old Modules
- [ ] Phase 5: Advanced Features

## Support

For questions or issues, please contact your system administrator or refer to the implementation plan document.

