# Unified Product Scrapper - Implementation Plan

## 1. Module Purpose & Scope

### Overview
The `unified_scrapper` module serves as a **central integration layer** for managing products sourced from multiple external marketplaces and e-commerce platforms. It consolidates functionality previously scattered across:
- `amin_petshop_scraper_module`
- `vetution_product_extension`
- `vetution_scraper_module`

### Core Responsibilities
The module will:
- Act as a **unified configuration hub** for external data sources
- Manage product-level metadata including source identification, external IDs, and marketplace-specific fields
- Provide flexible field mapping from external data structures to Odoo product models
- Enable filtering, reporting, and analytics by product source
- Support multiple data formats: CSV, JSON, and API endpoints

### Critical Design Principle
> **All web scraping is done externally.** This module only consumes structured data (CSV/JSON/API) provided by external scraping systems. No web scraping logic will be embedded in Odoo.

This separation ensures:
- Odoo performance is not impacted by scraping operations
- Scraping can be scaled independently (separate servers, containers, etc.)
- Scraping tools can be updated without Odoo module changes
- Better error isolation and debugging

---

## 2. High-Level Architecture

### 2.1 Data Source Configuration Model (`unified.data.source`)

**Purpose:** Define and manage external data sources that provide product information.

**Planned Fields:**
- `name` (Char, required) - Human-readable name (e.g., "Vetution Products Feed")
- `source_system` (Selection, required) - System identifier:
  - `vetution` - Vetution marketplace
  - `amin_petshop` - Amin Petshop
  - `amazon` - Amazon
  - `other` - Generic/custom source
- `source_type` (Selection, required) - Data format:
  - `csv` - CSV file
  - `json` - JSON file
  - `api` - REST API endpoint
- `source_url` (Char) - URL or file path to data source
- `active` (Boolean, default=True) - Enable/disable source
- `auto_import` (Boolean, default=False) - Enable automatic scheduled imports
- `import_frequency` (Selection) - For auto_import: daily, weekly, manual
- `last_import_date` (Datetime, readonly) - Timestamp of last successful import
- `last_import_status` (Selection, readonly) - success, failed, partial
- `import_log` (Text, readonly) - Log of last import operation
- `authentication_type` (Selection) - For API sources: none, basic, token, oauth
- `api_key` (Char) - API authentication key (encrypted)
- `notes` (Text) - Additional configuration notes

**Methods:**
- `action_test_connection()` - Validate source URL/API is accessible
- `action_import_now()` - Trigger manual import
- `action_view_import_history()` - View import logs

### 2.2 Field Mapping Model (`unified.field.mapping`)

**Purpose:** Define how external data fields map to Odoo product fields, with optional transformations.

**Planned Fields:**
- `data_source_id` (Many2one to `unified.data.source`, required) - Parent data source
- `sequence` (Integer) - Order of mapping application
- `external_field_name` (Char, required) - Field name in external data (e.g., "product_name", "price_egp")
- `target_model` (Selection, required) - Target Odoo model:
  - `product.template` - Product template
  - `product.product` - Product variant
- `target_field` (Char, required) - Technical field name in Odoo (e.g., "name", "list_price")
- `field_type` (Selection, readonly, computed) - Inferred from target field: char, text, float, integer, boolean, date, datetime, selection, many2one
- `is_required` (Boolean, default=False) - Fail import if external field is missing
- `default_value` (Char) - Default value if external field is empty
- `transformation_rule` (Selection) - Optional transformation:
  - `none` - Direct mapping
  - `lowercase` - Convert to lowercase
  - `uppercase` - Convert to uppercase
  - `strip_html` - Remove HTML tags
  - `price_conversion` - Apply currency conversion
  - `date_format` - Parse date with custom format
  - `custom_python` - Execute custom Python expression
- `transformation_params` (Text) - JSON parameters for transformation (e.g., date format string, currency rate)
- `active` (Boolean, default=True) - Enable/disable this mapping
- `notes` (Text) - Mapping documentation

**Methods:**
- `_apply_transformation(value)` - Apply configured transformation to a value
- `action_test_mapping()` - Test mapping with sample data

### 2.3 Product Extension (`product.product` / `product.template`)

**Purpose:** Extend Odoo products with fields for external source tracking and marketplace-specific data.

**Planned Core Fields (applicable to all sources):**
- `external_source` (Selection, indexed) - Source system:
  - `vetution`
  - `amin_petshop`
  - `amazon`
  - `other`
- `external_product_id` (Char, indexed) - External system's product ID/SKU
- `external_product_url` (Char) - Direct link to product on external site
- `external_last_sync` (Datetime) - Last successful sync timestamp
- `external_sync_status` (Selection) - Sync status:
  - `synced` - Up to date
  - `pending` - Needs update
  - `error` - Last sync failed
  - `manual` - Manually created, not synced
- `external_data_json` (Text) - Raw JSON dump of last external data (for debugging/audit)

**Planned Source-Specific Fields:**

*Vetution-specific:*
- `vetution_brand`, `vetution_brand_link`
- `vetution_rating`, `vetution_review_count`
- `vetution_ingredients`, `vetution_species`
- `vetution_vendor_price_ids` (One2many to vendor price model)
- All existing fields from `vetution_product_extension`

*Amin Petshop-specific:*
- `amin_petshop_sku`, `amin_petshop_brand`
- `amin_petshop_price`, `amin_petshop_regular_price`
- `amin_petshop_discount_percentage`, `amin_petshop_has_discount`
- `amin_petshop_stock_status`, `amin_petshop_available`
- `amin_petshop_price_history_ids` (One2many to price history model)
- All existing fields from `amin_petshop_scraper_module`

*Amazon-specific (future):*
- `amazon_asin`, `amazon_seller_id`
- `amazon_prime_eligible`, `amazon_fulfillment_type`
- `amazon_rating`, `amazon_review_count`
- `amazon_price_history_ids`

**Planned Product Tabs (in form view):**
- **"External Source"** tab - Shows:
  - Source system, external ID, URL
  - Last sync info, sync status
  - Quick action buttons: "Open External Link", "Force Sync", "View Sync History"
- **"Marketplace Data"** tab - Shows source-specific fields dynamically based on `external_source` value
- **"Price History"** tab - Shows price tracking over time (for sources that support it)

**Methods:**
- `action_open_external_link()` - Open external product URL in browser
- `action_sync_from_source()` - Trigger re-import of this product
- `action_view_sync_history()` - View import/sync logs for this product

### 2.4 Import History Model (`unified.import.history`)

**Purpose:** Track all import operations for auditing and debugging.

**Planned Fields:**
- `data_source_id` (Many2one to `unified.data.source`)
- `import_date` (Datetime)
- `status` (Selection) - success, failed, partial
- `products_created` (Integer)
- `products_updated` (Integer)
- `products_skipped` (Integer)
- `products_failed` (Integer)
- `error_log` (Text)
- `import_file` (Binary) - Copy of imported file (optional)
- `import_duration` (Float) - Seconds

---

## 3. Settings & UI Plan

### 3.1 Configuration Menu Structure

**Primary Menu:** `Unified Scrapper` (top-level menu in Odoo)

**Sub-menus:**
1. **Configuration**
   - Data Sources
   - Field Mappings
   - Import Settings (global preferences)

2. **Operations**
   - Import Now (wizard)
   - Import History
   - Sync Status Dashboard

3. **Products**
   - Products by Source (filtered views)
   - Sync Errors (products with sync issues)

### 3.2 Settings Pages

#### Data Sources Page
- **List View:**
  - Columns: Name, Source System, Type, Status, Last Import, Actions
  - Filters: By source system, by status (active/inactive), by last import date
  - Actions: Import Now, Test Connection, View History

- **Form View:**
  - Grouped fields:
    - **General Info:** Name, Source System, Active
    - **Connection:** Source Type, URL, Authentication
    - **Import Settings:** Auto Import, Frequency, Match Strategy
    - **Status:** Last Import Date, Status, Log (readonly)
  - Smart buttons: Import History, Mapped Products Count
  - Action buttons: Test Connection, Import Now, View Logs

#### Field Mappings Page
- **List View:**
  - Grouped by data source
  - Columns: Sequence, External Field, Target Model, Target Field, Transformation, Active
  - Drag-and-drop reordering by sequence
  - Bulk actions: Activate/Deactivate, Duplicate

- **Form View:**
  - Grouped fields:
    - **Source:** Data Source, External Field Name
    - **Target:** Target Model, Target Field (with domain filter)
    - **Transformation:** Rule, Parameters
    - **Validation:** Is Required, Default Value
  - Action buttons: Test Mapping (with sample data input)

#### Import Settings (Global)
- **Settings Page (res.config.settings):**
  - Default match strategy (by URL, SKU, name)
  - Default action on duplicates (skip, update, create new)
  - Enable/disable automatic image download
  - Enable/disable price history tracking
  - Default currency for imports
  - Logging level (errors only, info, debug)

### 3.3 Import Wizard

**Purpose:** Manual import interface with preview and validation.

**Wizard Steps:**
1. **Select Source:**
   - Choose configured data source OR upload ad-hoc file
   - Preview first 10 rows of data

2. **Validate Mappings:**
   - Show all field mappings for selected source
   - Highlight missing required fields
   - Option to adjust mappings temporarily

3. **Import Options:**
   - Match strategy override
   - Duplicate handling override
   - Dry run mode (preview changes without committing)

4. **Execute & Review:**
   - Progress bar during import
   - Summary: Created, Updated, Skipped, Errors
   - Download error report (CSV)
   - View imported products (filtered list)

---

## 4. Data Flow (Future Implementation)

### 4.1 End-to-End Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. External Scraping System                                 │
│    - Python scripts, Scrapy, Selenium, etc.                 │
│    - Runs on separate server/container                      │
│    - Outputs: CSV or JSON files                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Data Storage                                              │
│    - File server, S3 bucket, or API endpoint                │
│    - Accessible via URL or mounted volume                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Unified Scrapper - Data Source Config                    │
│    - Registered in Odoo: URL, format, mappings              │
│    - Scheduled cron OR manual trigger                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Import Engine (unified_scrapper)                         │
│    - Fetch data from URL/file                               │
│    - Parse CSV/JSON                                         │
│    - Apply field mappings & transformations                 │
│    - Match existing products (by URL, SKU, name)            │
│    - Create/Update product.template & product.product       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Product Records in Odoo                                  │
│    - Tagged with:                                           │
│      * external_source (vetution, amin_petshop, etc.)       │
│      * external_product_id                                  │
│      * external_product_url                                 │
│    - Source-specific fields populated                       │
│    - Sync status updated                                    │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Matching Strategy

When importing a product, the system will attempt to match existing products using:

1. **By External URL** (highest priority)
   - Match on `external_product_url` field
   - Most reliable for re-imports from same source

2. **By External SKU/ID**
   - Match on `external_product_id` or `default_code`
   - Useful when URL structure changes

3. **By Product Name** (lowest priority)
   - Exact match on `name` field
   - Fallback option, less reliable

4. **Fuzzy Name Matching** (optional)
   - Use string similarity algorithms
   - Configurable threshold (e.g., 85% similarity)

**Conflict Resolution:**
- If multiple matches found → log warning, skip import (or create new based on settings)
- If no match found → create new product (or skip based on settings)
- If match found → update existing product with new data

### 4.3 Update Strategy

When updating existing products:
- **Always update:** External metadata (last_sync, external_data_json)
- **Update if changed:** Prices, stock status, descriptions
- **Never overwrite:** Manually edited fields (configurable per field)
- **Merge strategy:** For multi-value fields (tags, categories)

---

## 5. Integration with Existing Modules (Strategy Only)

### 5.1 Current State Analysis

**Existing Modules:**
1. `amin_petshop_scraper_module`
   - Contains: Product fields, price history model, import wizard
   - Scraping: Likely embedded or external (to be verified)

2. `vetution_product_extension`
   - Contains: Product fields, vendor price model, import wizard
   - Scraping: Likely embedded or external (to be verified)

3. `vetution_scraper_module`
   - Contains: Scraping logic (to be kept external)

### 5.2 Migration Strategy

#### Phase 1: Field Consolidation
- **Action:** Copy all product extension fields from existing modules into `unified_scrapper`
- **Implementation:**
  - Create single `product.product` / `product.template` inheritance in `unified_scrapper`
  - Prefix fields with source name (e.g., `vetution_*`, `amin_*`) to avoid conflicts
  - Add `external_source` selection field as master identifier

#### Phase 2: Data Migration
- **Action:** Migrate existing product data to use new fields
- **Implementation:**
  - Write SQL migration script or Python migration function
  - Copy field values from old fields to new fields
  - Set `external_source` based on which fields are populated
  - Populate `external_product_id` and `external_product_url` from existing data

#### Phase 3: View Consolidation
- **Action:** Merge product form views into unified tabs
- **Implementation:**
  - Create dynamic tabs that show/hide based on `external_source`
  - Use `invisible="external_source != 'vetution'"` to conditionally display fields
  - Consolidate tree views with smart columns (show relevant fields per source)

#### Phase 4: Import Logic Migration
- **Action:** Replace existing import wizards with unified import engine
- **Implementation:**
  - Create data source configs for each existing source
  - Define field mappings based on existing import logic
  - Test imports side-by-side with old modules
  - Deprecate old import wizards once validated

#### Phase 5: Scraping Externalization
- **Action:** Ensure all scraping happens outside Odoo
- **Implementation:**
  - Extract any embedded scraping code to standalone scripts
  - Set up external scraping infrastructure (cron jobs, containers)
  - Configure scrapers to output to files/APIs consumed by `unified_scrapper`
  - **Do NOT** re-implement scraping in `unified_scrapper`

#### Phase 6: Module Deprecation
- **Action:** Mark old modules as deprecated
- **Implementation:**
  - Add deprecation notices to old module manifests
  - Set `installable=False` in old manifests
  - Provide uninstall guide (after data migration)
  - Eventually remove old modules from codebase

### 5.3 Backward Compatibility

During migration period:
- Both old and new modules can coexist
- Use `related` fields to keep old field names working (read-only)
- Provide migration wizard to help users transition
- Document breaking changes clearly

---

## 6. Phased Implementation Roadmap

### Phase 1: Module Skeleton & Data Models
**Duration:** 1-2 weeks  
**Deliverables:**
- ✅ Module skeleton created (`__init__.py`, `__manifest__.py`, folder structure)
- ✅ This planning document completed
- ⬜ Implement `unified.data.source` model
- ⬜ Implement `unified.field.mapping` model
- ⬜ Implement `unified.import.history` model
- ⬜ Extend `product.product` with core fields:
  - `external_source`, `external_product_id`, `external_product_url`
  - `external_last_sync`, `external_sync_status`
- ⬜ Extend `product.template` with related fields
- ⬜ Create security rules (access rights for new models)
- ⬜ Write unit tests for models

**Success Criteria:**
- All models installable without errors
- Fields visible in Odoo developer mode
- Basic CRUD operations work

---

### Phase 2: Settings & UI
**Duration:** 2-3 weeks  
**Deliverables:**
- ⬜ Create menu structure (`Unified Scrapper` top menu)
- ⬜ Implement Data Sources views:
  - List view with filters
  - Form view with all fields
  - Smart buttons (Import History, Product Count)
- ⬜ Implement Field Mappings views:
  - List view grouped by source
  - Form view with field selection widgets
  - Sequence drag-and-drop
- ⬜ Implement Import History views:
  - List view with filters
  - Form view with logs
  - Graph view (imports over time)
- ⬜ Add Settings page (res.config.settings)
- ⬜ Create product form view extensions:
  - "External Source" tab
  - Action buttons (Open Link, Force Sync)
- ⬜ Add product filters (by source, by sync status)
- ⬜ Create sync status dashboard (kanban/graph views)

**Success Criteria:**
- All menus and views accessible
- Can create/edit data sources and mappings via UI
- Product form shows external source info
- No UI errors or missing translations

---

### Phase 3: Import Engine
**Duration:** 3-4 weeks  
**Deliverables:**
- ⬜ Implement CSV parser
- ⬜ Implement JSON parser
- ⬜ Implement API connector (basic HTTP GET)
- ⬜ Implement field mapping engine:
  - Direct mapping
  - Transformations (lowercase, uppercase, strip_html, etc.)
  - Date/number parsing
- ⬜ Implement product matching logic:
  - By URL, by SKU, by name
  - Fuzzy matching (optional)
- ⬜ Implement product create/update logic:
  - Create new products
  - Update existing products
  - Handle duplicates per settings
- ⬜ Implement import history logging
- ⬜ Create import wizard:
  - Source selection
  - Preview data
  - Validation
  - Execute import
  - Results summary
- ⬜ Add scheduled cron job for auto-imports
- ⬜ Implement error handling and rollback
- ⬜ Write integration tests

**Success Criteria:**
- Can import CSV file and create products
- Can import JSON file and update products
- Mappings applied correctly
- Import history logged
- Errors handled gracefully

---

### Phase 4: Migration from Old Modules
**Duration:** 2-3 weeks  
**Deliverables:**
- ⬜ Analyze existing modules:
  - Document all fields in `vetution_product_extension`
  - Document all fields in `amin_petshop_scraper_module`
  - Identify overlapping fields
- ⬜ Migrate Vetution fields:
  - Copy field definitions to `unified_scrapper`
  - Prefix with `vetution_*`
  - Add to "Marketplace Data" tab with conditional visibility
- ⬜ Migrate Amin Petshop fields:
  - Copy field definitions to `unified_scrapper`
  - Prefix with `amin_*`
  - Add to "Marketplace Data" tab with conditional visibility
- ⬜ Migrate related models:
  - `vetution.vendor.price` → `unified.vendor.price` (or keep separate)
  - `amin.petshop.price.history` → `unified.price.history`
- ⬜ Create data migration script:
  - SQL or Python script to copy data from old fields to new fields
  - Set `external_source` based on populated fields
  - Populate `external_product_id` and `external_product_url`
- ⬜ Create data source configs for existing sources:
  - Vetution data source
  - Amin Petshop data source
- ⬜ Create field mappings based on existing import logic
- ⬜ Test imports with real data files
- ⬜ Create migration guide document
- ⬜ Mark old modules as deprecated

**Success Criteria:**
- All existing product data migrated successfully
- No data loss
- Old modules can be uninstalled without errors
- Imports work with new unified system

---

### Phase 5: Advanced Features (Optional/Future)
**Duration:** Ongoing  
**Deliverables:**
- ⬜ API authentication (OAuth, token-based)
- ⬜ Advanced transformations (regex, custom Python)
- ⬜ Price history tracking and analytics
- ⬜ Stock level monitoring and alerts
- ⬜ Automated price comparison across sources
- ⬜ Product matching suggestions (ML-based)
- ⬜ Bulk product operations (bulk sync, bulk update)
- ⬜ Export functionality (export products to external format)
- ⬜ Webhook support (receive real-time updates from sources)
- ⬜ Multi-language support for product descriptions
- ⬜ Image management (download, resize, optimize)
- ⬜ Category mapping (external categories → Odoo categories)

---

## 7. Risks & Design Decisions

### 7.1 Key Design Decisions

#### Decision 1: No Embedded Scraping
**Rationale:**
- Web scraping is resource-intensive and can block Odoo workers
- Scraping logic changes frequently (website structure changes)
- Scraping may require specialized tools (Selenium, Playwright) not suitable for Odoo
- Separation of concerns: Odoo for ERP, external tools for scraping

**Trade-off:**
- Requires separate infrastructure for scraping
- More complex deployment (Odoo + scraper services)
- But: Better performance, scalability, and maintainability

#### Decision 2: Generic Field Mapping vs. Hardcoded
**Rationale:**
- Generic mapping allows adding new sources without code changes
- Future-proof: Can support any data structure
- User-configurable: Non-developers can adjust mappings

**Trade-off:**
- More complex implementation
- Requires UI for mapping configuration
- But: Much more flexible and maintainable long-term

#### Decision 3: Source-Specific Fields vs. Generic JSON Storage
**Rationale:**
- Source-specific fields (e.g., `vetution_brand`, `amin_petshop_sku`) provide:
  - Type safety (float, date, selection)
  - Searchability and indexing
  - Better UI (proper widgets)
  - Computed fields and validations
- Generic JSON storage would be simpler but less functional

**Trade-off:**
- More fields in database (but manageable with prefixes)
- Larger module codebase
- But: Much better UX and data integrity

#### Decision 4: Product Matching Strategy
**Rationale:**
- External URL is most reliable (unique, stable)
- SKU/ID as fallback (may not be unique across sources)
- Name matching as last resort (least reliable)

**Trade-off:**
- Requires external systems to provide stable URLs
- May create duplicates if URLs change
- But: Best balance of accuracy and flexibility

### 7.2 Identified Risks

#### Risk 1: Data Quality from External Sources
**Impact:** High  
**Probability:** High  
**Mitigation:**
- Implement robust validation in import engine
- Log all data quality issues
- Provide data preview before import
- Allow manual review and correction

#### Risk 2: Performance with Large Datasets
**Impact:** Medium  
**Probability:** Medium  
**Mitigation:**
- Batch imports (commit every N records)
- Async processing for large files
- Optimize database queries (indexes on match fields)
- Provide progress indicators

#### Risk 3: Breaking Changes in External Data Structure
**Impact:** Medium  
**Probability:** High  
**Mitigation:**
- Version field mappings (track changes over time)
- Alert on unmapped fields
- Provide mapping validation tools
- Document expected data structure per source

#### Risk 4: Duplicate Products
**Impact:** Medium  
**Probability:** Medium  
**Mitigation:**
- Strong matching logic with multiple strategies
- Duplicate detection report
- Manual merge tool
- Configurable duplicate handling rules

#### Risk 5: Migration Complexity
**Impact:** High  
**Probability:** Medium  
**Mitigation:**
- Phased migration approach
- Extensive testing on copy of production database
- Rollback plan
- Detailed migration documentation
- Support for coexistence of old and new modules

### 7.3 Technical Constraints

- **Odoo Version:** 19.0 (ensure compatibility with ORM, views, and APIs)
- **Python Version:** 3.10+ (as per Odoo 19 requirements)
- **Database:** PostgreSQL (leverage full-text search, JSON fields)
- **External Dependencies:** Minimize (only standard library + Odoo)
- **Performance Target:** Import 1000 products in < 5 minutes

### 7.4 Security Considerations

- **API Keys:** Store encrypted in database
- **File Uploads:** Validate file types and sizes
- **Access Control:** Restrict import operations to authorized users
- **Data Privacy:** Ensure external data complies with privacy regulations
- **Audit Trail:** Log all imports and changes for compliance

---

## 8. Success Metrics

### 8.1 Technical Metrics
- Module installs without errors on fresh Odoo 19 instance
- All unit tests pass (target: 80%+ code coverage)
- Import performance: 1000 products in < 5 minutes
- Zero data loss during migration
- < 1% duplicate product rate

### 8.2 User Experience Metrics
- Configuration time: < 30 minutes to set up new data source
- Import success rate: > 95% of products imported without errors
- User training time: < 2 hours for admin users
- Support tickets: < 5 per month after stabilization

### 8.3 Business Metrics
- Consolidation: 3 modules → 1 module (reduced maintenance)
- Extensibility: Add new source in < 1 day (vs. 1 week previously)
- Data freshness: Products updated within 24 hours of external changes
- Catalog coverage: > 95% of external products represented in Odoo

---

## 9. Appendix

### 9.1 Glossary
- **External Source:** A marketplace, e-commerce site, or data provider (e.g., Vetution, Amazon)
- **Data Source Config:** Configuration record defining how to connect to an external source
- **Field Mapping:** Definition of how an external field maps to an Odoo field
- **Sync:** Process of updating Odoo product data from external source
- **Match Strategy:** Algorithm for identifying if an imported product already exists in Odoo

### 9.2 References
- Odoo 19 Documentation: https://www.odoo.com/documentation/19.0/
- Existing modules to consolidate:
  - `amin_petshop_scraper_module`
  - `vetution_product_extension`
  - `vetution_scraper_module`

### 9.3 Document History
- **v1.0** - 2025-12-05 - Initial plan created (Phase 1 deliverable)

---

**End of Planning Document**

This document will be updated as implementation progresses through each phase.

