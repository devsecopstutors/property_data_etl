import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
             f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    # Email
    SMTP_CONFIG = {
        'server': os.getenv('SMTP_SERVER'),
        'port': os.getenv('SMTP_PORT'),
        'user': os.getenv('SMTP_USER'),
        'password': os.getenv('SMTP_PASSWORD'),
        'recipients': os.getenv('ALERT_RECIPIENTS').split(',')
    }
    
    # Paths
    DATA_PATHS = {
        'raw': Path(os.getenv('RAW_DATA_PATH')),  #'raw': Path('data/raw/propertyrecords.json'),
        'processed': Path('data/processed'),
        'dimensions': Path('data/dimensions'),
        'facts': Path('data/facts'),
        'logs': Path('logs')
    }

    # ETL Parameters
    CHUNK_SIZE = 10000


