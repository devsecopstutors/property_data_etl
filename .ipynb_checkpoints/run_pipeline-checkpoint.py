#!/usr/bin/env python3
import logging
from etl.extract import load_raw_data
from etl.transform import PropertyTransformer
from etl.load import DatabaseLoader
from config.settings import Config

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.DATA_PATHS['logs'] / 'etl.log'),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    
    try:
        # ETL Process
        raw_data = load_raw_data()
        property_dim = PropertyTransformer.create_property_dim(raw_data)
        
        loader = DatabaseLoader()
        loader.load_dimension(property_dim, 'property_dim')
        
    except Exception as e:
        logging.error(f"ETL pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()