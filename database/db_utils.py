import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def run_schema():
    db_url = os.getenv("SUPABASE_DB_URL")
    conn = psycopg2.connect(db_url)
    try:
        # Connect to your Cloud DB
        # conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Read the SQL file
        with open('schema.sql', 'r') as f:
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
    run_schema()