#!/usr/bin/env python3
"""
Database migration script to add summary_content field to existing databases.

This script safely adds the new summary_content column to the conversions table
for users upgrading from a version without LLM support.

Usage:
    python migrate_db.py [database_path]
    
If no database_path is provided, it will use the default 'markitdown.db'
"""

import sys
import os
import sqlite3
from pathlib import Path


def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def migrate_database(db_path):
    """Add summary_content column to conversions table if it doesn't exist."""
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("No migration needed - database will be created with new schema on first run.")
        return True
    
    print(f"Migrating database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if summary_content column already exists
        if check_column_exists(cursor, 'conversions', 'summary_content'):
            print("✓ Column 'summary_content' already exists in 'conversions' table")
            print("No migration needed.")
            conn.close()
            return True
        
        # Add the new column
        print("Adding 'summary_content' column to 'conversions' table...")
        cursor.execute("""
            ALTER TABLE conversions 
            ADD COLUMN summary_content TEXT
        """)
        
        conn.commit()
        
        # Verify the column was added
        if check_column_exists(cursor, 'conversions', 'summary_content'):
            print("✓ Successfully added 'summary_content' column")
            
            # Get count of existing records
            cursor.execute("SELECT COUNT(*) FROM conversions")
            count = cursor.fetchone()[0]
            print(f"✓ Existing records ({count}) will have NULL summary_content (can be filled later)")
            
            conn.close()
            return True
        else:
            print("✗ Failed to add column")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main migration function."""
    print("=" * 70)
    print("MarkItDown API Database Migration")
    print("Adding LLM summary_content field to conversions table")
    print("=" * 70)
    print()
    
    # Get database path from command line or use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = 'markitdown.db'
    
    # Perform migration
    success = migrate_database(db_path)
    
    print()
    print("=" * 70)
    if success:
        print("Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Start your application normally")
        print("2. Enable LLM processing in the settings if desired")
        print("3. New conversions will have summary_content populated automatically")
        print("4. Existing conversions can be re-processed to add summaries")
    else:
        print("Migration failed!")
        print()
        print("Please check the error messages above and try again.")
        print("If the problem persists, you may need to backup and recreate your database.")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
