"""
Database utility functions for connecting to MySQL and executing queries.
"""
import mysql.connector
from mysql.connector import Error
import pandas as pd
from sqlalchemy import create_engine
from typing import Optional
import logging
from src.config import DB_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_connection():
    """
    Create and return a MySQL connection.
    
    Returns:
        mysql.connector.connection: Database connection object
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("MySQL database connection established successfully")
        return conn
    except Error as e:
        logger.error(f"Failed to connect to MySQL database: {e}")
        raise


def get_engine():
    """
    Create and return a SQLAlchemy engine for pandas operations.
    
    Returns:
        sqlalchemy.engine.Engine: SQLAlchemy engine object
    """
    try:
        conn_string = (
            f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        engine = create_engine(conn_string)
        logger.info("SQLAlchemy engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create SQLAlchemy engine: {e}")
        raise


def query_to_df(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Execute SQL query and return results as pandas DataFrame.
    
    Args:
        query (str): SQL query to execute
        params (dict, optional): Query parameters for parameterized queries
    
    Returns:
        pd.DataFrame: Query results as DataFrame
    """
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine, params=params)
        logger.info(f"Query executed successfully. Returned {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Failed to execute query: {e}")
        raise


def export_table_to_csv(table_name: str, output_path: str) -> None:
    """
    Export entire database table to CSV file.
    
    Args:
        table_name (str): Name of the table to export
        output_path (str): Path where CSV file will be saved
    """
    try:
        query = f"SELECT * FROM {table_name}"
        df = query_to_df(query)
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} rows from '{table_name}' to '{output_path}'")
    except Exception as e:
        logger.error(f"Failed to export table '{table_name}': {e}")
        raise


def execute_sql_file(sql_file_path: str) -> None:
    """
    Execute SQL commands from a file.
    
    Args:
        sql_file_path (str): Path to SQL file
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        with open(sql_file_path, 'r') as f:
            sql_commands = f.read()
        
        # Split by semicolon and execute each statement
        for statement in sql_commands.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully executed SQL file: {sql_file_path}")
    except Exception as e:
        logger.error(f"Failed to execute SQL file '{sql_file_path}': {e}")
        raise


def get_table_info(table_name: str) -> pd.DataFrame:
    """
    Get column information for a specific table.
    
    Args:
        table_name (str): Name of the table
    
    Returns:
        pd.DataFrame: Table column information
    """
    query = f"""
    SELECT 
        COLUMN_NAME as column_name,
        DATA_TYPE as data_type,
        IS_NULLABLE as is_nullable
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{table_name}'
    AND TABLE_SCHEMA = '{DB_CONFIG['database']}'
    ORDER BY ORDINAL_POSITION;
    """
    return query_to_df(query)


def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        logger.info(f"Database connection test successful. MySQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection when running this file directly
    print("Testing MySQL database connection...")
    if test_connection():
        print("✓ MySQL database connection successful!")
    else:
        print("✗ MySQL database connection failed. Please check your .env configuration.")
