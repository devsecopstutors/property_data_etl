
import pandas as pd
import numpy as np
from datetime import datetime
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

class PropertyTransformer:
    @staticmethod
    def preprocess_data(df):
        """Cell 4-7: Data cleaning and standardization"""
        propertyrecords_df = df.copy()
        propertyrecords_df.columns = [col.lower() for col in propertyrecords_df.columns]
        propertyrecords_df.rename(columns={
            'zipcode': 'zip_code',
            'squarefootage': 'square_footage',
            'lotsize': 'lot_size',
            'yearbuilt': 'year_built',
            'assessorid': 'assessor_id',
            'legaldescription': 'legal_description',
            'lastsaledate': 'last_sale_date',
            'lastsaleprice': 'last_sale_price',
            'propertytaxes': 'property_taxes',
            'taxassessments': 'tax_assessments',
            'formattedaddress': 'formatted_address',
            'propertytype': 'property_type',
            'addressline1': 'address_line1',
            'addressline2': 'address_line2',
            'owneroccupied': 'owner_occupied',
            'hoa': 'hoa_fees'
        }, inplace=True)
        
        propertyrecords_df.dropna(subset=['last_sale_price'], inplace=True)
        propertyrecords_df.dropna(subset=['tax_assessments'], inplace=True)
        # Convert features column to string if it contains dictionaries
        if 'features' in propertyrecords_df.columns:
            propertyrecords_df['features'] = propertyrecords_df['features'].apply(lambda x: str(x) if isinstance(x, dict) else x)

        propertyrecords_df.fillna({
            'address_line2': 'Unknown',
            'county': 'Unknown',
            'property_type': 'Unknown',
            'lot_size': propertyrecords_df['lot_size'].median(),
            'bedrooms': propertyrecords_df['bedrooms'].median(),
            'bathrooms': propertyrecords_df['bathrooms'].median(),
            'square_footage': propertyrecords_df['square_footage'].median(),
            'year_built': int(propertyrecords_df['year_built'].median()),
            'assessor_id': 'Unknown',
            'legal_description': 'Unknown',
            'subdivision': 'Unknown',
            'last_sale_date': propertyrecords_df['last_sale_date'].mode().iloc[0],
            'features': 'Unknown',
            'property_taxes': 0,
            'owner': 'Unknown',
            'owner_occupied': 'Unknown',
            'history': 'Unknown',
            'zoning': 'Unknown',
            'hoa_fees': 0
        }, inplace=True)
        return propertyrecords_df

    def create_dimensions(self, df):
        """Cell 8: Create dimensions"""
        propertyrecords_df = df.copy()
        location_dim = self.create_location_dim(propertyrecords_df)
        features_dim = self.create_feature_dim(propertyrecords_df)
        property_dim = self.create_property_dim(propertyrecords_df)
        owner_dim = self.create_owner_dim(propertyrecords_df) 
        date_dim = self.create_date_dim(propertyrecords_df)

        
        return {
            'location': location_dim,
            'features': features_dim,
            'property': property_dim,
            'owner': owner_dim,
            'date': date_dim
        }
    @staticmethod
    def create_location_dim(propertyrecords_df):
        """Transform raw data into location dimension"""
        try:
            location_dim = propertyrecords_df[['address_line1', 'city', 'state', 'zip_code', 'county', 'latitude', 'longitude', 'subdivision', 'zoning']].drop_duplicates().reset_index(drop = True)
            location_dim['location_id'] = location_dim.index + 1
            location_dim = location_dim[['location_id', 'address_line1', 'city', 'state', 'zip_code', 'county', 'latitude', 'longitude', 'subdivision', 'zoning']]
            return location_dim
        
        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise

    @staticmethod
    def create_feature_dim(propertyrecords_df):
        """Transform raw data into features dimension"""
        try:
            features_dim = propertyrecords_df[['features', 'property_type', 'zoning']].drop_duplicates().reset_index(drop=True)
            features_dim['features_id'] = features_dim.index + 1
            features_dim = features_dim[['features_id', 'features', 'property_type', 'zoning']]
            return features_dim

        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise
    
    @staticmethod
    def create_property_dim(propertyrecords_df):
        """Transform raw data into property dimension"""
        try:
            property_dim = propertyrecords_df[['property_type', 'assessor_id', 'bedrooms', 'bathrooms', 'square_footage', 'legal_description', 'subdivision', 'features', 'zoning']].drop_duplicates().reset_index(drop=True)
            property_dim['property_id'] = property_dim.index + 1
            property_dim = property_dim[['property_id', 'property_type', 'assessor_id', 'bedrooms', 'bathrooms', 'square_footage', 'legal_description', 'subdivision', 'features', 'zoning']]
            return property_dim

        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise

    @staticmethod
    def create_owner_dim(propertyrecords_df):
        """Transform raw data into owner dimension"""
        try:
            df_copy = propertyrecords_df.copy()
            df_copy['owner'] = df_copy['owner'].apply(lambda x: str(x) if isinstance(x, dict) else x)
            df_copy['owner_occupied'] = df_copy['owner_occupied'].apply(lambda x: str(x) if isinstance(x, dict) else x)
            owner_dim = df_copy[['owner', 'owner_occupied']].drop_duplicates().reset_index(drop=True)
            owner_dim['owner_id'] = owner_dim.index + 1
            owner_dim = owner_dim[['owner_id', 'owner', 'owner_occupied']]
            return owner_dim

        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise

    @staticmethod
    def create_date_dim(propertyrecords_df):
        """Transform raw data into date dimension"""
        try:
            propertyrecords_df['last_sale_date'] = pd.to_datetime(propertyrecords_df['last_sale_date'], errors='coerce', utc=True)
            propertyrecords_df['year'] = propertyrecords_df['last_sale_date'].dt.year
            propertyrecords_df['month'] = propertyrecords_df['last_sale_date'].dt.month_name()
            propertyrecords_df['quarter'] = propertyrecords_df['last_sale_date'].dt.quarter
            propertyrecords_df['day_name'] = propertyrecords_df['last_sale_date'].dt.day_name()

            date_dim = propertyrecords_df[['day_name', 'month', 'quarter', 'year', 'last_sale_date']].drop_duplicates().reset_index(drop=True)
            date_dim['date_id'] = date_dim.index + 1
            date_dim = date_dim[['date_id', 'day_name', 'month', 'quarter', 'year', 'last_sale_date']]
            return date_dim

        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise


    @staticmethod
    def create_fact_table(propertyrecords_df):
        """Transform raw data into fact table"""
        try:
            fact_table = propertyrecords_df[['last_sale_price', 'property_taxes', 'tax_assessments']].copy()
            
            # Add dimension keys
            fact_table['location_id'] = propertyrecords_df.index + 1
            fact_table['features_id'] = propertyrecords_df.index + 1
            fact_table['property_id'] = propertyrecords_df.index + 1
            fact_table['owner_id'] = propertyrecords_df.index + 1
            fact_table['date_id'] = propertyrecords_df.index + 1
            
            return fact_table
        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise

    
'''    @staticmethod
    def create_fact_table(self, df):
        """Cell 9: Create fact table"""
        propertyrecords_df = df.copy()
        try:
            fact_table = propertyrecords_df[[
                'id', 'last_sale_price', 'property_taxes', 'hoa_fees', 'location_id', 'features_id', 'property_id', 'owner_id', 'date_id', 'tax_assessments'
            ]].copy()
            return fact_table
        
        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            raise
'''

class pre_process_check:
    @staticmethod # @classmethod for independent methods
    def check_data_types(df):
        """Check data types of columns"""
        propertyrecords_df = df.copy()
        print("=== Data Types ===")
        print(propertyrecords_df.dtypes)

        print("\n=== Data Types Summary ===")
        print(propertyrecords_df.dtypes.value_counts())

        print("\n=== Data Types by Column ===")
        for col in propertyrecords_df.columns:
            print(f"{col}: {propertyrecords_df[col].dtype}")


    def quick_check(df):
        """Quick check of the data"""
        # Copy the DataFrame to avoid modifying the original
        print("=== df copy and Quick Check ===")
        propertyrecords_df = df.copy()
        # Initial checks
        print("=== Initial Data Shape ===")
        print(propertyrecords_df.shape)

        print("\n=== Data Types ===")
        print(propertyrecords_df.dtypes)

        print("\n=== Null Values ===")
        print(propertyrecords_df.isnull().sum())

        for col in propertyrecords_df.columns:
            try:
                print(f"{col}: {propertyrecords_df[col].nunique()} unique values")
            except TypeError:
                print(f"{col}: Contains unhashable type (e.g., dict/list)")            


