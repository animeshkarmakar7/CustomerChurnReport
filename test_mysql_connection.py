"""
Quick test script to verify MySQL database connection.
Run this before executing the main analysis pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.db_utils import test_connection, get_table_info
from src.config import DB_CONFIG

def main():
    print("=" * 80)
    print("MYSQL DATABASE CONNECTION TEST")
    print("=" * 80)
    print()
    
    print("Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print()
    
    print("Testing connection...")
    if test_connection():
        print("✓ SUCCESS: MySQL connection works!")
        print()
        
        # Try to list tables
        try:
            from src.db_utils import query_to_df
            
            query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
            """
            
            tables = query_to_df(query, params=(DB_CONFIG['database'],))
            
            if len(tables) > 0:
                print(f"Found {len(tables)} tables in database:")
                for table in tables['TABLE_NAME']:
                    print(f"  - {table}")
            else:
                print("No tables found in database.")
                print("This is normal if you haven't run the SQL scripts yet.")
            
        except Exception as e:
            print(f"Could not list tables: {e}")
            print("This is OK - database connection works!")
        
        print()
        print("=" * 80)
        print("You're ready to run the analysis pipeline!")
        print("=" * 80)
        return True
        
    else:
        print("✗ FAILED: Could not connect to MySQL database")
        print()
        print("Troubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check your .env file has correct credentials:")
        print("   - DB_HOST (usually 'localhost')")
        print("   - DB_PORT (usually 3306)")
        print("   - DB_USER (usually 'root')")
        print("   - DB_PASSWORD (your MySQL password)")
        print("3. Make sure the database exists:")
        print(f"   CREATE DATABASE {DB_CONFIG['database']};")
        print()
        print("=" * 80)
        print("If connection fails, scripts will use CSV files instead")
        print("=" * 80)
        return False

if __name__ == "__main__":
    main()
