import sqlite3
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_setup.log')
    ]
)

def setup_database():
    """
    Set up the SQLite database and import data from CSV.
    """
    start_time = datetime.now()
    logging.info("Starting database setup...")
    
    # File paths
    csv_path = 'truestate_assignment_dataset.csv'
    db_path = 'truestate.db'
    
    try:
        # Check if CSV file exists
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Read the CSV file in chunks
        logging.info(f"Reading CSV file: {csv_path}")
        chunk_size = 10000  # Process 10,000 rows at a time
        
        # Connect to SQLite database
        logging.info("Connecting to SQLite database...")
        conn = sqlite3.connect(db_path)
        
        # Read and process CSV in chunks
        first_chunk = True
        total_rows = 0
        
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
            total_rows += len(chunk)
            logging.info(f"Processing chunk with {len(chunk)} rows (total: {total_rows} rows)")
            
            # Clean column names (remove spaces, special characters, etc.)
            chunk.columns = [col.strip().replace(' ', '_').lower() for col in chunk.columns]
            
            # Write the chunk to the database
            chunk.to_sql('properties', conn, if_exists='append' if not first_chunk else 'replace', index=False)
            first_chunk = False
        
        # Create indexes for better query performance
        logging.info("Creating indexes...")
        cursor = conn.cursor()
        
        # Get column names to create appropriate indexes
        cursor.execute("PRAGMA table_info(properties)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Create indexes on common query fields if they exist
        index_columns = ['id', 'property_id', 'price', 'location', 'city', 'state', 'zip_code']
        for col in index_columns:
            if col in columns:
                index_name = f'idx_{col}'
                logging.info(f"Creating index on {col}...")
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON properties({col})")
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()
        
        # Log completion
        duration = (datetime.now() - start_time).total_seconds()
        logging.info(f"Database setup completed successfully in {duration:.2f} seconds")
        logging.info(f"Total rows imported: {total_rows}")
        
    except Exception as e:
        logging.error(f"Error during database setup: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        setup_database()
        print("\nDatabase setup completed successfully!")
        print("You can now start using the database with the API.")
    except Exception as e:
        print(f"\nError during database setup: {str(e)}")
        print("Check the database_setup.log file for more details.")
