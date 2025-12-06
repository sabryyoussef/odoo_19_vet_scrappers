#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to re-import product data from JSON and CSV files
Run this from Odoo shell: exec(open('/mnt/extra-addons/vetution_product_extension/scripts/reimport_data.py').read())
"""

import json
import csv
import os
import sys

# Import the hook functions
sys.path.insert(0, '/mnt/extra-addons/vetution_product_extension')
from hooks import load_product_data

# Load the data
print("Starting data import...")
load_product_data(env)
print("Data import completed!")

