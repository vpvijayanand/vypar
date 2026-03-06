#!/usr/bin/env python
"""
Database setup script for PostgreSQL
Run this script to create the database if it doesn't exist.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'wl_web_scraper')

def create_database():
    """Create PostgreSQL database if it doesn't exist"""
    try:
        # Connect to PostgreSQL default database
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists")
        else:
            # Create database
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✓ Database '{DB_NAME}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"✗ Error connecting to PostgreSQL:")
        print(f"  {e}")
        print(f"\nMake sure PostgreSQL is running and credentials are correct:")
        print(f"  Host: {DB_HOST}")
        print(f"  Port: {DB_PORT}")
        print(f"  User: {DB_USER}")
        return False

if __name__ == '__main__':
    print("🔧 Setting up PostgreSQL database...\n")
    if create_database():
        print("\n✓ Database setup complete!")
        print(f"\nConnection string: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    else:
        sys.exit(1)
