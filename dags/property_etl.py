from datetime import datetime, timedelta
"""
Property Data ETL Pipeline DAG
This DAG orchestrates the Extract, Transform, Load (ETL) process for property data.
It extracts raw property data, transforms it into a dimensional model, and loads it
into the target database.
DAG Structure:
    extract_data -> transform_data -> load_data
Parameters:
    default_args (dict): Default arguments for the DAG including:
        - owner: data_engineering
        - retries: 2 (with 5 min delay)
        - email notifications on failure
Schedule:
    Runs daily at 2 AM
    # Cron: 0 2 * * *
    # MIN HR DY MON DOW
Dependencies:
    - etl.extract.load_raw_data
    - etl.transform.PropertyTransformer  
    - etl.load.DatabaseLoader
    - config.settings.Config
Tasks:
    extract_data: Extracts raw property data
    transform_data: Creates dimension and fact tables from raw data
    load_data: Loads transformed data into database
Dimension Tables:
    - property_dim
    - location_dim  
    - owner_dim
    - fact_table (measurements/metrics)
Error Handling:
    - Logs errors during ETL process
    - Retries failed tasks up to 2 times
    - Sends email notifications on failure
"""
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

dag = DAG(          # DAG object**Directed Acyclic Graph** for  ETL (Extract, Transform, Load) pipeline
    'property_data_etl',  # Unique identifier for the DAG
    default_args=default_args,  # Default arguments for the DAG
    description='Daily Property Data Pipeline',  # Description of the DAG
    schedule_interval=timedelta(days=1),  # Schedule interval for the DAG
    # Cron expression for scheduling
    # Cron format: MIN HR DAY MON DOW
    # Example: 0 2 * * * means the DAG runs at 2 AM every day
    
    # MIN HR DAY MON DOW
    # * * * *
    # 0 2 * * *  # 2 AM daily## 
    # In the context of cron expressions and Apache Airflow scheduling
    #- `MIN`: Minutes (0-59)
    #- `HR`: Hours (0-23)
    #- `DAY`: Day of Month (1-31)
    #- `MON`: Month (1-12)
    #- `DOW`: Day of Week (0-6 where 0=Sunday, or SUN-SAT)


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

# Extract task
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=load_raw_data,
    dag=dag
)

# Transform task
def transform_data(**context):
    raw_df = context['task_instance'].xcom_pull(task_ids='extract_data')
    transformer = PropertyTransformer()
    dimensions = {
        'property_dim': transformer.create_property_dim(raw_df),
        'location_dim': transformer.create_location_dim(raw_df),
        'owner_dim': transformer.create_owner_dim(raw_df)
    }
    facts = transformer.create_fact_table(raw_df)
    return {'dimensions': dimensions, 'facts': facts}

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

# Load task
def load_data(**context):
    transformed_data = context['task_instance'].xcom_pull(task_ids='transform_data')
    loader = DatabaseLoader()
    
    for name, df in transformed_data['dimensions'].items():
        loader.load_dimension(df, name)
    
    loader.load_fact_table(transformed_data['facts'])

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag
)

# Set task dependencies (in this case, we only have one task)
extract_task >> transform_task >> load_task
