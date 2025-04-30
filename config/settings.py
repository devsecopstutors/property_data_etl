import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
             f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    POSTGRES_USER = os.getenv('DB_USER')
    POSTGRES_PASSWORD = os.getenv('DB_PASSWORD')
    POSTGRES_HOST = os.getenv('DB_HOST')
    POSTGRES_PORT = os.getenv('DB_PORT')
    POSTGRES_DB = os.getenv('DB_NAME')
    POSTGRES_SCHEMA = os.getenv('DB_SCHEMA', 'public')

    # API
    API_URL = os.getenv('API_URL')
    API_KEY = os.getenv('API_KEY')
    API_HEADERS = {
        'Authorization': f"Bearer {API_KEY}",
        'Content-Type': 'application/json'
    }
    API_PARAMS = {
        'limit': 1000,
        'offset': 0
    }
    API_TIMEOUT = 30  # seconds
    API_RETRIES = 3
    API_RETRY_DELAY = 5  # seconds
    API_MAX_TIMEOUT = 60  # seconds
    API_MAX_RETRIES = 5
    
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
    MAX_RETRIES = 5
    RETRY_DELAY = 60  # seconds
    MAX_TIMEOUT = 3600  # seconds
    
    # Logging
    LOGGING_LEVEL = 'INFO'
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_DIR = DATA_PATHS['logs']
    LOGGING_FILE = LOGGING_DIR / 'etl.log'
    LOGGING_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Create log file if it doesn't exist
    if not LOGGING_FILE.exists():
        LOGGING_FILE.touch()
    # Create directories if they don't exist
    for path in DATA_PATHS.values():
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    # Schedule
    DAILY_SCHEDULE = {
        'start_time': '09:00',  # 24-hour format
        'retries': 3,
        'retry_delay': 300,  # seconds
        'timeout': 3600  # seconds
    }
