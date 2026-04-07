import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

class MatchesDB:
    def __init__(self):
        self.db_url = os.getenv("SUPABASE_DB_URL")
        # Fix for potential URI prefix issues
        if self.db_url and self.db_url.startswith("postgresql://"):
            self.db_url = self.db_url.replace("postgresql://", "postgres://", 1)

    def store_generated_matches(self, match_results):
        """
        Stores a list of match dictionaries into the 'matches' table.
        
        Expected match_results format:
        [
            {
                "user_a_id": "uuid-1", 
                "user_b_id": "uuid-2", 
                "intent": "Networking", 
                "compatibility": 0.85
            },
            ...
        ]
        """
        if not match_results:
            print("⚠️ No matches provided to store.")
            return False

        # Prepare the data for bulk insertion
        # We extract tuples: (user_a_id, user_b_id, intent, compatibility)
        data_to_insert = [
            (
                m.get('user_a_id'), 
                m.get('user_b_id'), 
                m.get('intent', 'General'), 
                m.get('compatibility', 0.0)
            ) 
            for m in match_results
        ]

        query = """
            INSERT INTO matches (user_a_id, user_b_id, intent, compatibility)
            VALUES %s
            ON CONFLICT (user_a_id, user_b_id, match_date) DO NOTHING;
        """

        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Using execute_values for high-performance bulk insertion
            execute_values(cur, query, data_to_insert)
            
            conn.commit()
            print(f"✅ Successfully stored {len(data_to_insert)} matches in the database.")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Database Error while storing matches: {e}")
            return False
        finally:
            if conn:
                cur.close()
                conn.close()

    def store_single_match(self, match_data):
        """
        Stores one match dictionary into the 'matches' table.
        match_data: {"user_a_id": uuid, "user_b_id": uuid, "intent": str, "compatibility": float}
        """
        query = """
            INSERT INTO matches (user_a_id, user_b_id, intent, compatibility)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_a_id, user_b_id, match_date) DO NOTHING;
        """
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            cur.execute(query, (
                match_data.get('user_a_id'),
                match_data.get('user_b_id'),
                match_data.get('intent'),
                match_data.get('compatibility')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error storing match: {e}")
            return False
        finally:
            if conn:
                cur.close()
                conn.close()