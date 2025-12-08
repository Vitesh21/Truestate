""Database module for Truestate application."""
import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database.log')
    ]
)

class DatabaseManager:
    """
    A class to manage database connections and operations.
    """
    
    def __init__(self, db_path: str = 'truestate.db'):
        """
        Initialize the database manager with the path to the SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the database file exists and has the required tables."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(
                f"Database file not found at {self.db_path}. "
                "Please run database_setup.py first."
            )
    
    @contextmanager
    def get_connection(self):
        ""
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: A connection to the SQLite database
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        try:
            yield conn
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_columns(self) -> List[str]:
        """Get the list of columns in the properties table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(properties)")
            return [col[1] for col in cursor.fetchall()]
    
    def get_properties(
        self, 
        limit: int = 10, 
        offset: int = 0, 
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'ASC'
    ) -> List[Dict[str, Any]]:
        """
        Retrieve properties from the database with optional filtering and pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            filters: Dictionary of filters to apply (column_name: value)
            sort_by: Column to sort by
            sort_order: Sort order ('ASC' or 'DESC')
            
        Returns:
            List of property records as dictionaries
        """
        query = "SELECT * FROM properties"
        params = []
        
        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        placeholders = ', '.join(['?'] * len(value))
                        conditions.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    else:
                        conditions.append(f"{key} LIKE ?")
                        params.append(f"%{value}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # Apply sorting
        if sort_by:
            query += f" ORDER BY {sort_by} {sort_order.upper()}"
        
        # Apply pagination
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_property_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Get the total number of properties matching the given filters.
        
        Args:
            filters: Dictionary of filters to apply (column_name: value)
            
        Returns:
            Total count of matching properties
        """
        query = "SELECT COUNT(*) as count FROM properties"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        placeholders = ', '.join(['?'] * len(value))
                        conditions.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    else:
                        conditions.append(f"{key} LIKE ?")
                        params.append(f"%{value}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    def get_unique_values(self, column: str) -> List[Any]:
        """
        Get all unique values for a specific column.
        
        Args:
            column: Name of the column
            
        Returns:
            List of unique values
        """
        query = f"SELECT DISTINCT {column} FROM properties WHERE {column} IS NOT NULL ORDER BY {column}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]

# Create a singleton instance
db = DatabaseManager()

# For backward compatibility
def get_db_connection():
    return db.get_connection()

def get_properties(limit=10, offset=0, filters=None, sort_by=None, sort_order='ASC'):
    return db.get_properties(limit, offset, filters, sort_by, sort_order)

def get_property_count(filters=None):
    return db.get_property_count(filters)

def get_unique_values(column):
    return db.get_unique_values(column)
