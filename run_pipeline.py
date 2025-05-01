#!/usr/bin/env python3
"""
ETL Pipeline Runner for Property Data
This script orchestrates the entire ETL (Extract, Transform, Load) pipeline for property data processing.
It handles the extraction of raw property data, transformation into a star schema model,
and loading into a PostgreSQL database.
The pipeline performs the following main steps:
1. Configures logging for the ETL process
2. Loads raw property data
3. Preprocesses and transforms the data into dimension and fact tables
4. Creates necessary database schema and tables
5. Loads the transformed data into PostgreSQL
6. Creates required database indexes
Functions:
    configure_logging(): Sets up logging configuration with both file and console output
    main(): Orchestrates the complete ETL pipeline execution
Dependencies:
    - etl.extract: Contains data extraction functionality
    - etl.transform: Contains data transformation logic
    - etl.load: Contains database loading operations
    - config.settings: Contains configuration settings
Environment Requirements:
    - PostgreSQL database instance
    - Appropriate file system permissions for logging
    - Required Python packages (specified in requirements.txt)
File Structure:
    The script expects certain paths defined in Config.DATA_PATHS:
    - logs/: Directory for log files
    - dimensions/: Directory for saving dimension table CSVs
Returns:
    None
Raises:
    Various exceptions may be raised during ETL process:
    - DatabaseError: For database connection/operation failures
    - FileNotFoundError: For missing input files
    - ValueError: For data validation issues
"""

import logging
import json
import os
from etl.extract import load_raw_data, extract_from_api
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
    logger = logging.getLogger(__name__)
    logger.info("Starting ETL process...")

    # Initialize
    transformer = PropertyTransformer()
    loader = DatabaseLoader()
    logger = logging.getLogger(__name__)
    logger.info("Starting ETL process...")

    # Exztract data from API
    logger.info("Extracting data from API...")
    extract_from_api()
    logger.info("Data extracted from API.")

    # Load raw data
    logger.info("Loading raw data...")
    propertyrecords_df = load_raw_data()
    logger.info(f"Raw data loaded with {len(propertyrecords_df)} records.")
    
    # Preprocess data
    logger.info("Preprocessing data...")
    propertyrecords_df = transformer.preprocess_data(propertyrecords_df)
    logger.info(f"Data preprocessed with {len(propertyrecords_df)} records.")     
    
    # Transform data
    logger.info("Transforming data...")

    # Create dimensions
    dimensions = transformer.create_dimensions(propertyrecords_df)
    logger.info("Dimensions created.")

    # Save dimensions to CSV and load to Postgres
    for name, df in dimensions.items():
        loader.save_to_csv(df, Config.DATA_PATHS['dimensions'] / f"{name}.csv")
        loader.load_to_postgres(df, name)
        logger.info(f"Dimension {name} saved and loaded to Postgres.")

    # Create fact table
    logger.info("Creating fact table...")
    facts = transformer.create_fact_table(propertyrecords_df)

    # Database operations should be done at the end
    logger.info("Performing database operations...")
    loader.create_postgresql_connection()
    logger.info("PostgreSQL connection created.")
    loader.create_schema()
    logger.info("Schema created.")
    loader.create_database()
    logger.info("Database created.")

    # create tables
    logger.info("Creating tables...")
    loader.create_tables()
    logger.info("Tables created.")

    # create indexes
    logger.info("Creating indexes...")
    loader.create_indexes()
    logger.info("Indexes created.")


if __name__ == "__main__":
    main()

