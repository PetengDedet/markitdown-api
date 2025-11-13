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
    """Add new analysis columns to conversions table if they don't exist."""
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("No migration needed - database will be created with new schema on first run.")
        return True
    
    print(f"Migrating database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Track if any migration was performed
        migration_performed = False
        
        # Check and add summary_content column if needed
        if not check_column_exists(cursor, 'conversions', 'summary_content'):
            print("Adding 'summary_content' column to 'conversions' table...")
            cursor.execute("""
                ALTER TABLE conversions 
                ADD COLUMN summary_content TEXT
            """)
            migration_performed = True
            print("✓ Successfully added 'summary_content' column")
        else:
            print("✓ Column 'summary_content' already exists")
        
        # Check and add predicted_title column if needed
        if not check_column_exists(cursor, 'conversions', 'predicted_title'):
            print("Adding 'predicted_title' column to 'conversions' table...")
            cursor.execute("""
                ALTER TABLE conversions 
                ADD COLUMN predicted_title VARCHAR(500)
            """)
            migration_performed = True
            print("✓ Successfully added 'predicted_title' column")
        else:
            print("✓ Column 'predicted_title' already exists")
        
        # Check and add categories column if needed
        if not check_column_exists(cursor, 'conversions', 'categories'):
            print("Adding 'categories' column to 'conversions' table...")
            cursor.execute("""
                ALTER TABLE conversions 
                ADD COLUMN categories TEXT
            """)
            migration_performed = True
            print("✓ Successfully added 'categories' column")
        else:
            print("✓ Column 'categories' already exists")
        
        # Check and add keywords column if needed
        if not check_column_exists(cursor, 'conversions', 'keywords'):
            print("Adding 'keywords' column to 'conversions' table...")
            cursor.execute("""
                ALTER TABLE conversions 
                ADD COLUMN keywords TEXT
            """)
            migration_performed = True
            print("✓ Successfully added 'keywords' column")
        else:
            print("✓ Column 'keywords' already exists")
        
        # Check and add severity column if needed
        if not check_column_exists(cursor, 'conversions', 'severity'):
            print("Adding 'severity' column to 'conversions' table...")
            cursor.execute("""
                ALTER TABLE conversions 
                ADD COLUMN severity VARCHAR(50)
            """)
            migration_performed = True
            print("✓ Successfully added 'severity' column")
        else:
            print("✓ Column 'severity' already exists")
        
        # Check and add corrected_content column if needed
        if not check_column_exists(cursor, 'conversions', 'corrected_content'):
            print("Adding 'corrected_content' column to 'conversions' table...")
            cursor.execute("""
                ALTER TABLE conversions 
                ADD COLUMN corrected_content TEXT
            """)
            migration_performed = True
            print("✓ Successfully added 'corrected_content' column")
        else:
            print("✓ Column 'corrected_content' already exists")
        
        if not migration_performed:
            print("No migration needed - all columns already exist.")
            conn.close()
            return True
        
        conn.commit()
        
        # Get count of existing records
        cursor.execute("SELECT COUNT(*) FROM conversions")
        count = cursor.fetchone()[0]
        print(f"✓ Existing records ({count}) will have NULL for new columns (can be filled later)")
        
        conn.close()
        return True
            
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
    print("Adding analysis fields (categories, keywords, severity, corrections)")
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
