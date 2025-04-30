from sqlalchemy import create_engine
from config.settings import Config
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DatabaseLoader:
    def __init__(self):
        self.engine = create_engine(Config.DB_URI)
    
    def load_dimension(self, df, table_name):
        """Load dimension table to database"""
        try:
            df.to_sql(
                table_name,
                self.engine,
                schema='etl_pipeline',
                if_exists='replace',
                index=False,
                chunksize=Config.CHUNK_SIZE
            )
            logger.info(f"Loaded {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")
            raise