# -*- coding: utf-8 -*-
"""
Common utilities for scripts
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Data directories - organized by scraper
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
VETUTION_DATA_DIR = os.path.join(DATA_DIR, 'vetution')
AMIN_PETSHOP_DATA_DIR = os.path.join(DATA_DIR, 'amin_petshop')
EXTERNAL_SCRAPERS_DATA_DIR = os.path.join(DATA_DIR, 'external_scrapers')

# Vetution product files (default for scripts)
PRODUCTS_JSON = os.path.join(VETUTION_DATA_DIR, 'products.json')
PRODUCTS_CSV = os.path.join(VETUTION_DATA_DIR, 'products.csv')

def get_data_dir():
    """Get the main data directory path"""
    os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR

def get_vetution_data_dir():
    """Get Vetution data directory"""
    os.makedirs(VETUTION_DATA_DIR, exist_ok=True)
    return VETUTION_DATA_DIR

def get_amin_petshop_data_dir():
    """Get Amin Petshop data directory"""
    os.makedirs(AMIN_PETSHOP_DATA_DIR, exist_ok=True)
    return AMIN_PETSHOP_DATA_DIR

def get_external_scrapers_data_dir():
    """Get external scrapers data directory"""
    os.makedirs(EXTERNAL_SCRAPERS_DATA_DIR, exist_ok=True)
    return EXTERNAL_SCRAPERS_DATA_DIR

def get_products_json(scraper='vetution'):
    """Get the products.json file path for a specific scraper"""
    if scraper == 'vetution':
        os.makedirs(VETUTION_DATA_DIR, exist_ok=True)
        return PRODUCTS_JSON
    elif scraper == 'amin_petshop':
        os.makedirs(AMIN_PETSHOP_DATA_DIR, exist_ok=True)
        return os.path.join(AMIN_PETSHOP_DATA_DIR, 'products.json')
    else:
        return PRODUCTS_JSON  # Default to vetution

def get_products_csv(scraper='vetution'):
    """Get the products.csv file path for a specific scraper"""
    if scraper == 'vetution':
        os.makedirs(VETUTION_DATA_DIR, exist_ok=True)
        return PRODUCTS_CSV
    elif scraper == 'amin_petshop':
        os.makedirs(AMIN_PETSHOP_DATA_DIR, exist_ok=True)
        return os.path.join(AMIN_PETSHOP_DATA_DIR, 'products.csv')
    else:
        return PRODUCTS_CSV  # Default to vetution

