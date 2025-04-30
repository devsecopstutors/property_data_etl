import json
import pandas as pd
from pathlib import Path
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

def load_raw_data():
    """Load raw JSON data with validation"""
    try:
        with open(Config.DATA_PATHS['raw']) as f:
            data = json.load(f)
        
        df = pd.json_normalize(data)
        logger.info(f"Loaded {len(df)} records from {Config.DATA_PATHS['raw']}")
        return df
    
    except Exception as e:
        logger.error(f"Data loading failed: {str(e)}")
        raise