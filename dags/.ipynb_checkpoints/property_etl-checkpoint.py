from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from etl.extract import load_raw_data
from etl.transform import PropertyTransformer
from etl.load import DatabaseLoader
from config.settings import Config
import logging

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': Config.SMTP_CONFIG['recipients']
}

dag = DAG(
    'property_data_etl',
    default_args=default_args,
    description='Daily Property Data Pipeline',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['real_estate']
)

def run_full_etl():
    """Orchestrate the ETL process"""
    transformer = PropertyTransformer()
    loader = DatabaseLoader()
    
    try:
        # Extract
        raw_df = load_raw_data()
        
        # Transform
        dimensions = {
            'property_dim': transformer.create_property_dim(raw_df),
            'location_dim': transformer.create_location_dim(raw_df),
            'owner_dim': transformer.create_owner_dim(raw_df)
        }
        
        # Load
        for name, df in dimensions.items():
            loader.load_dimension(df, name)
            
        # Load fact table
        facts = transformer.create_fact_table(raw_df)
        loader.load_fact_table(facts)
        
    except Exception as e:
        logging.error(f"ETL failed: {str(e)}")
        raise

etl_task = PythonOperator(
    task_id='run_etl',
    python_callable=run_full_etl,
    dag=dag
)