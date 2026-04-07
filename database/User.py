import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self):
        self.db_url = os.getenv("SUPABASE_DB_URL")
        # Fix for potential URI prefix issues
        if self.db_url and self.db_url.startswith("postgresql://"):
            self.db_url = self.db_url.replace("postgresql://", "postgres://", 1)

    def get_all_users(self):
        """
        Retrieves all user records from the Supabase 'users' table.
        Returns a list of dictionaries.
        """
        query = "SELECT id, name, age, current_traits, profile_summary, embedding FROM users;"
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute(query)
            rows = cur.fetchall()
            
            # Map the database rows to a list of dictionaries
            users = []
            for row in rows:
                users.append({
                    "id": str(row[0]), # Convert UUID to string
                    "name": row[1],
                    "age": row[2],
                    "current_traits": row[3], # This will be a Python list automatically
                    "profile_summary": row[4],
                    "embedding": row[5] # This will be a Python list of floats
                })
            
            return users

        except Exception as e:
            print(f"❌ Error fetching users: {e}")
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def update_traits(self, user_id, payload):
        """
        Updates user traits and summary in the database using psycopg2.
        Payload should look like: {"current_traits": ["A", "B"], "profile_summary": "..."}
        """
        conn = None
        try:
            # 1. Build the SET clause dynamically based on the payload keys
            # This converts {"name": "val"} into "name = %s"
            set_clause = ", ".join([f"{key} = %s" for key in payload.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = %s;"
    
            values = list(payload.values())
            values.append(user_id)
            
            # 3. Construct the full SQL query
            query = f"UPDATE users SET {set_clause} WHERE id = %s;"
            
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # 4. Execute safely using parameterized queries
            cur.execute(query, tuple(values))
            conn.commit()
            
            print(f"✅ Successfully updated columns: {list(payload.keys())}")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Database Update Error: {e}")
            return False
        finally:
            if conn:
                cur.close()
                conn.close()

    
 
        
    def update_user_traits(self, user_id, new_traits, new_summary):
        """
        Updates the traits and summary for a specific user in Supabase.
        """
        try:
            data = {
                "Traits": new_traits,
                "Summary": new_summary
            }
            response = self.supabase.table("users").update(data).eq("ID", user_id).execute()
            return response
        except Exception as e:
            print(f"Error updating database: {e}")
            return None

    def add_data(self, data_object):
        """
        Receives a dictionary and inserts it into the 'users' table.
        Example data_object: 
        {
            "name": "Alice", 
            "age": 25, 
            "current_traits": ["Kind", "Introverted"],
            "profile_summary": "A software dev who loves cats.",
            "embedding": [0.12, -0.05, ...]
        }
        """
        query = """
            INSERT INTO users (name, age, current_traits, profile_summary, embedding)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Execute the insert using dictionary keys
            cur.execute(query, (
                data_object.get('name'),
                data_object.get('age'),
                data_object.get('current_traits', []), # Default to empty list
                data_object.get('profile_summary'),
                data_object.get('embedding')
            ))
            
            user_id = cur.fetchone()[0]
            conn.commit()
            print(f"✅ User added successfully with ID: {user_id}")
            return user_id

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error adding user: {e}")
            return None
        finally:
            if conn:
                cur.close()
                conn.close()