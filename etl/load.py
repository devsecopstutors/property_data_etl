from sqlalchemy import create_engine
from config.settings import Config
import pandas as pd
import logging
import psycopg2
from psycopg2 import sql, extras
from psycopg2.extras import execute_values



logger = logging.getLogger(__name__)

# Now connect to the new database as etl_user
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="etl_pipeline_db",   # new database
            user="etl_user",
            password="pipeline",
            host="localhost",
            port=5432
        )
        print("✅ Connected to 'etl_pipeline_db' as etl_user ")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to new db: {e}")
        return None

conn = get_connection()
cursor = conn.cursor()
print("✅  function called get_connection is defined")


class DatabaseLoader:
    def __init__(self):
        self.conn = None
        self.engine = None
        self.configure_logging()
        self.create_database()

    def __del__(self):
        if self.conn:
            self.conn.close()
            logger.info("PostgreSQL connection closed.")

    def configure_logging(self):
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler("etl.log"), logging.StreamHandler()]
        )
        logger.info("Logging configured.")

    def create_database(self):
        try:
            # Connect to default postgres db first
            conn = psycopg2.connect(
                dbname='postgres',
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            conn.autocommit = True
            
            # Create database if not exists
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (Config.POSTGRES_DB,))
                if not cursor.fetchone():
                    cursor.execute(f"CREATE DATABASE {Config.POSTGRES_DB}")
                    logger.info(f"Created database {Config.POSTGRES_DB}")
            conn.close()

            # Create main connection
            self.conn = psycopg2.connect(
                dbname=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            self.engine = create_engine(f'postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}')
            
            # Create schema and tables
            with self.conn.cursor() as cursor:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {Config.POSTGRES_SCHEMA}")
                self.create_tables(cursor)
                self.create_indexes(cursor)
                self.conn.commit()
                
            logger.info("Database setup completed successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {str(e)}")
            raise

    def load_data(self, df, table_name, table_type='dimension'):
        """Generic method to load data"""
        try:
            df.to_sql(
                table_name,
                self.engine,
                schema=Config.POSTGRES_SCHEMA,
                if_exists='replace',
                index=False,
                chunksize=Config.CHUNK_SIZE
            )
            logger.info(f"Loaded {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")
            raise

    def save_data(self, df, file_path, format_type):
        """Generic method to save data"""
        try:
            save_methods = {
                'csv': df.to_csv,
                'json': lambda p: df.to_json(p, orient='records', lines=True),
                'parquet': df.to_parquet,
                'excel': df.to_excel
            }
            save_methods[format_type](file_path)
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to {format_type}: {str(e)}")
            raise

    def __init__(self):
        self.conn = None
        self.engine = None
        self.create_database()
        self.create_postgresql_connection()
        self.create_schema()
        self.create_tables()
        self.create_indexes()

    def __del__(self):
        """Close the connection when the object is deleted"""
        if self.conn:
            self.conn.close()
            logger.info("PostgreSQL connection closed.")

    def load_dimension(self, df, table_name):
        """Load dimension table to database"""
        try:
            df.to_sql(
                table_name,
                self.engine,
                schema=Config.POSTGRES_SCHEMA,
                if_exists='replace',
                index=False,
                chunksize=Config.CHUNK_SIZE
            )
            logger.info(f"Loaded {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")
            raise
    def load_fact(self, df, table_name):
        """Load fact table to database"""
        try:
            df.to_sql(
                table_name,
                self.engine,
                schema=Config.POSTGRES_SCHEMA,
                if_exists='replace',
                index=False,
                chunksize=Config.CHUNK_SIZE
            )
            logger.info(f"Loaded {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")
            raise
    def load_raw_data(self, df, table_name):
        """Load raw data to database"""
        try:
            df.to_sql(
                table_name,
                self.engine,
                schema=Config.POSTGRES_SCHEMA,
                if_exists='replace',
                index=False,
                chunksize=Config.CHUNK_SIZE
            )
            logger.info(f"Loaded {len(df)} rows to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {str(e)}")
            raise
    def save_to_csv(self, df, file_path):
        """Save DataFrame to CSV"""
        try:
            df.to_csv(file_path, index=False)
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to CSV: {str(e)}")
            raise
    
    def save_to_json(self, df, file_path):
        """Save DataFrame to JSON"""
        try:
            df.to_json(file_path, orient='records', lines=True)
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to JSON: {str(e)}")
            raise
    
    def save_to_parquet(self, df, file_path):
        """Save DataFrame to Parquet"""
        try:
            df.to_parquet(file_path, index=False)
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to Parquet: {str(e)}")
            raise
    
    def save_to_excel(self, df, file_path):
        """Save DataFrame to Excel"""
        try:
            df.to_excel(file_path, index=False)
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to Excel: {str(e)}")
            raise
    
    def save_to_sql(self, df, table_name):
        """Save DataFrame to SQL"""
        try:
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            logger.info(f"Data saved to SQL table {table_name}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to SQL: {str(e)}")
            raise

    def load_to_postgres(self, df, table_name):
        conn = get_connection()
        if conn is None:
            print("❌ No connection available.")
            return

        try:
            cur = conn.cursor()

            # Drop table if needed (optional)
            cur.execute(sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                sql.Identifier(Config.POSTGRES_SCHEMA),
                sql.Identifier(table_name)
            ))

            # Infer column names and types from df and create table
            cols = ', '.join([f'"{col}" TEXT' for col in df.columns])  # You can adjust types
            create_table = sql.SQL("CREATE TABLE {}.{} ({})").format(
                sql.Identifier(Config.POSTGRES_SCHEMA),
                sql.Identifier(table_name),
                sql.SQL(cols)
            )
            cur.execute(create_table)

            # Insert data
            values = [tuple(x) for x in df.to_numpy()]
            insert = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
                sql.Identifier(Config.POSTGRES_SCHEMA),
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, df.columns))
            )
            execute_values(cur, insert, values)

            conn.commit()
            print(f"✅ Data loaded into table {table_name}")

        except Exception as e:
            print(f"❌ Error loading data to PostgreSQL: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
            


    def configure_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("etl.log"),
                logging.StreamHandler()
            ]
        )
        logger.info("Logging configured.")

    def use_existing_database(self):
        """Connect to existing database if it exists, or create new one"""
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (Config.POSTGRES_DB,))
                exists = cursor.fetchone()
                if exists:
                    logger.info(f"Using existing database {Config.POSTGRES_DB}")
                else:
                    cursor.execute(f"CREATE DATABASE {Config.POSTGRES_DB}")
                    logger.info(f"Created new database {Config.POSTGRES_DB}")
            conn.close()
        except Exception as e:
            logger.error(f"Error checking/creating database: {str(e)}")
            raise
        
    def create_postgresql_connection(self):
        """Create PostgreSQL connection"""
        try:
            import psycopg2
            from sqlalchemy import create_engine

            # Create a connection to the PostgreSQL database
            self.conn = psycopg2.connect(
                dbname=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            self.engine = create_engine(f'postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}')
            return self.conn, self.engine
        
        except Exception as e:
            logger.error(f"Error creating PostgreSQL connection: {str(e)}")
            raise
    def create_schema(self):
        """Create schema in PostgreSQL"""
        try:
            conn, engine = self.create_postgresql_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {Config.POSTGRES_SCHEMA};")
                conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            raise

    def create_database(self):
        """Create database in PostgreSQL"""
        try:
            # Connect to default postgres database first
            conn = psycopg2.connect(
                dbname='postgres',
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (Config.POSTGRES_DB,))
                exists = cursor.fetchone()
                if not exists:
                    if Config.POSTGRES_DB is None:
                        raise ValueError("POSTGRES_DB configuration is not set")
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(Config.POSTGRES_DB)
                    ))
                    logger.info(f"Created database {Config.POSTGRES_DB}")
                else:
                    logger.info(f"Database {Config.POSTGRES_DB} already exists")
            conn.close()
        
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise

    def create_tables(self):    
        """Create tables in PostgreSQL"""
        try:
            conn, engine = self.create_postgresql_connection()
            with conn.cursor() as cursor:
                # Create dimensions
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {Config.POSTGRES_SCHEMA}.location (
                        id SERIAL PRIMARY KEY,
                        zip_code VARCHAR(10),
                        county VARCHAR(50),
                        state VARCHAR(50),
                        city VARCHAR(50)
                    );
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {Config.POSTGRES_SCHEMA}.features (
                        id SERIAL PRIMARY KEY,
                        features TEXT
                    );
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {Config.POSTGRES_SCHEMA}.property (
                        id SERIAL PRIMARY KEY,
                        property_type VARCHAR(50),
                        bedrooms INT,
                        bathrooms INT,
                        square_footage INT,
                        lot_size FLOAT,
                        year_built INT,
                        property_age INT
                    );
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {Config.POSTGRES_SCHEMA}.owner (
                        id SERIAL PRIMARY KEY,
                        owner VARCHAR(100),
                        owner_occupied BOOLEAN
                    );
                """)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {Config.POSTGRES_SCHEMA}.date (
                        id SERIAL PRIMARY KEY,
                        last_sale_date DATE,
                        year INT,
                        month INT,
                        day INT
                    );
                """)
                
                # Create fact table
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {Config.POSTGRES_SCHEMA}.fact_table (
                        id SERIAL PRIMARY KEY,
                        last_sale_price FLOAT,
                        property_taxes FLOAT,
                        hoa_fees FLOAT
                    );
                """)
                
                conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise


    def create_indexes(self):
        """Create indexes in PostgreSQL"""
        try:
            conn, engine = self.create_postgresql_connection()
            with conn.cursor() as cursor:
                # Create indexes for dimensions
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_location_zip_code ON {Config.POSTGRES_SCHEMA}.location (zip_code);
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_features ON {Config.POSTGRES_SCHEMA}.features (features);
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_property_type ON {Config.POSTGRES_SCHEMA}.property (property_type);
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_owner ON {Config.POSTGRES_SCHEMA}.owner (owner);
                """)
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_date ON {Config.POSTGRES_SCHEMA}.date (last_sale_date);
                """)
                
                # Create indexes for fact table
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_fact_table ON {Config.POSTGRES_SCHEMA}.fact_table (last_sale_price);
                """)
                
                conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
        # Close the connection
        finally:
            if conn:
                conn.close()
                logger.info("PostgreSQL connection closed.")
        
        