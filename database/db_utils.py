import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def run_user_schema():
    db_url = os.getenv("SUPABASE_DB_URL")
    conn = psycopg2.connect(db_url)
    try:
        # Connect to your Cloud DB
        # conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Read the SQL file
        with open('user_schema.sql', 'r') as f:
            schema_sql = f.read()

        # Execute the commands
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema deployed to Supabase successfully!")
        
    except Exception as e:
        print(f"❌ Error deploying schema: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def run_config_schema():
    db_url = os.getenv("SUPABASE_DB_URL")
    conn = psycopg2.connect(db_url)
    try:
        # Connect to your Cloud DB
        # conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Read the SQL file
        with open('config_schema.sql', 'r') as f:
            schema_sql = f.read()

        # Execute the commands
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema deployed to Supabase successfully!")
        
    except Exception as e:
        print(f"❌ Error deploying schema: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def run_matches_schema():
    db_url = os.getenv("SUPABASE_DB_URL")
    conn = psycopg2.connect(db_url)
    try:
        # Connect to your Cloud DB
        # conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Read the SQL file
        with open('matches_schema.sql', 'r') as f:
            schema_sql = f.read()

        # Execute the commands
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema deployed to Supabase successfully!")
        
    except Exception as e:
        print(f"❌ Error deploying schema: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    # run_user_schema()
    # run_config_schema()
    run_matches_schema()