# -*- coding: utf-8 -*-

from . import models
from . import wizards

def post_init_hook(env):
    """Post-initialization hook to check dependencies"""
    import logging
    _logger = logging.getLogger(__name__)
    
    try:
        import playwright
        import bs4
        import lxml
        _logger.info("✅ Universal Scraper: All Python dependencies are installed")
    except ImportError as e:
        _logger.warning(f"⚠️ Universal Scraper: Missing Python dependency: {e}")
        _logger.warning("Please install: pip install playwright beautifulsoup4 lxml")
        _logger.warning("Then run: playwright install chromium")

