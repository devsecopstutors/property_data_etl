import pandas as pd
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

class PropertyTransformer:
    @staticmethod
    def create_property_dim(raw_df):
        """Transform raw data into property dimension"""
        try:
            dim = raw_df[[
                'id', 'property_type', 'bedrooms', 'bathrooms',
                'square_footage', 'lot_size', 'year_built'
            ]].copy()
            
            dim['property_age'] = pd.Timestamp.now().year - dim['year_built']
            return dim
        
        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise