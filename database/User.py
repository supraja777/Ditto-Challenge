import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self):
        self.db_url = os.getenv("SUPABASE_DB_URL")
        # Fix for potential URI prefix issues in SQLAlchemy/Psycopg2
        if self.db_url and self.db_url.startswith("postgresql://"):
            self.db_url = self.db_url.replace("postgresql://", "postgres://", 1)

    def get_all_users(self):
        """
        Retrieves all user records with the Dual-Vector Rich Schema.
        """
        query = """
            SELECT 
                id, name, age, traits, profile_summary, 
                embedding, trait_embedding,
                social_energy, intent, intellectual_focus, 
                dealbreakers, hobbies
            FROM users;
        """
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "age": row[2],
                    "traits": row[3],      # Python List
                    "profile_summary": row[4],
                    "embedding": row[5],           # Vibe Vector (List of floats)
                    "trait_embedding": row[6],     # Trait Vector (List of floats)
                    "social_energy": row[7],
                    "intent": row[8],
                    "intellectual_focus": row[9],
                    "dealbreakers": row[10],       # List of strings
                    "hobbies": row[11]             # List of strings
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
        Generic update method for any user attribute (including embeddings).
        Example: payload = {"trait_embedding": [...], "traits": ["A", "B"]}
        """
        if not payload:
            return False

        conn = None
        try:
            set_clause = ", ".join([f"{key} = %s" for key in payload.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = %s;"
    
            values = list(payload.values())
            values.append(user_id)
            
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute(query, tuple(values))
            conn.commit()
            
            print(f"✅ Successfully updated user {user_id} columns: {list(payload.keys())}")
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

    def add_user(self, data_object):
        """
        Inserts a new user with Dual-Vector support and Rich Computation factors.
        """
        query = """
            INSERT INTO users (
                name, age, traits, profile_summary, 
                embedding, trait_embedding,
                social_energy, intent, intellectual_focus, 
                dealbreakers, hobbies
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute(query, (
                data_object.get('name'),
                data_object.get('age'),
                data_object.get('traits', []),
                data_object.get('profile_summary'),
                data_object.get('embedding'),       # Vibe vector
                data_object.get('trait_embedding'), # Trait vector
                data_object.get('social_energy', 5),
                data_object.get('intent', 'Exploring'),
                data_object.get('intellectual_focus', 'General'),
                data_object.get('dealbreakers', []),
                data_object.get('hobbies', [])
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
                
    def get_user_by_id(self, user_id):
        """
        Retrieves a single user record by its UUID/ID.
        Returns a dictionary if found, otherwise None.
        """
        query = """
            SELECT 
                id, name, age, traits, profile_summary, 
                embedding, trait_embedding,
                social_energy, intent, intellectual_focus, 
                dealbreakers, hobbies
            FROM users
            WHERE id = %s;
        """
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            
            if row:
                return {
                    "id": str(row[0]),
                    "name": row[1],
                    "age": row[2],
                    "traits": row[3],
                    "profile_summary": row[4],
                    "embedding": row[5],
                    "trait_embedding": row[6],
                    "social_energy": row[7],
                    "intent": row[8],
                    "intellectual_focus": row[9],
                    "dealbreakers": row[10],
                    "hobbies": row[11]
                }
            else:
                print(f"⚠️ User with ID {user_id} not found.")
                return None

        except Exception as e:
            print(f"❌ Error fetching user by ID: {e}")
            return None
        finally:
            if conn:
                cur.close()
                conn.close()