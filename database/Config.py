import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.db_url = os.getenv("SUPABASE_DB_URL")
        if self.db_url and self.db_url.startswith("postgresql://"):
            self.db_url = self.db_url.replace("postgresql://", "postgres://", 1)
        
        # Internal cache to avoid hitting the DB on every single match calculation
        self._cache = {}

    def load_all_thresholds(self):
        """
        Reads all system thresholds from the 'system_config' table.
        Returns a dictionary of { "key": value }
        """
        query = "SELECT key, value FROM system_config;"
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            
            # Update local cache
            self._cache = {row[0]: row[1] for row in rows}
            print(f"✅ Config: Loaded {len(self._cache)} thresholds from database.")
            return self._cache

        except Exception as e:
            print(f"❌ Config Error: {e}")
            # Fallback to hardcoded safe defaults if DB is unreachable
            return self.get_defaults()
        finally:
            if conn:
                cur.close()
                conn.close()

    def get(self, key, default=None):
        """Retrieves a specific threshold from the loaded cache."""
        if not self._cache:
            self.load_all_thresholds()
        return self._cache.get(key, default)

    def update_threshold(self, key, new_value):
        """
        Updates a threshold value in the database.
        Useful for building an 'Admin Dashboard' later.
        """
        query = "UPDATE system_config SET value = %s WHERE key = %s;"
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            # Note: We pass new_value as a string/JSON-compatible type
            cur.execute(query, (str(new_value), key))
            conn.commit()
            
            # Refresh cache
            self._cache[key] = new_value
            print(f"🚀 Config Updated: {key} is now {new_value}")
            return True
        except Exception as e:
            print(f"❌ Failed to update config: {e}")
            return False
        finally:
            if conn:
                cur.close()
                conn.close()

    @staticmethod
    def get_defaults():
        """Standard backup values for the system."""
        return {
            "cosine_threshold": 0.5,
            "exploration_rate": 0.1,
            "weight_vibe": 0.40,
            "weight_traits": 0.15,
            "weight_intellect": 0.15,
            "weight_age": 0.10,
            "social_energy_bonus": 0.05,
            "hobby_bonus_unit": 0.02
        }

if __name__ == "__main__":
    config = Config()
    print(config.load_all_thresholds())
   