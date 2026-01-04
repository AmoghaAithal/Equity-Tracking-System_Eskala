# backend/db.py
import os
from urllib.parse import quote_plus  # 👈 NEW
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ---- Build DB components safely ----
db_user = os.getenv('DB_USER', 'root')
db_password = quote_plus(os.getenv('DB_PASSWORD', ''))  # 👈 encodes @ to %40
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'user_management')

# ✅ ALWAYS construct the URL ourselves
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print("SQLALCHEMY DATABASE_URL:", DATABASE_URL)  # 👈 temporary debug

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_connection():
    """
    Legacy function for mysql.connector compatibility
    Use SessionLocal() for SQLAlchemy sessions
    """
    import mysql.connector
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "user_management"),
        port=int(os.getenv("DB_PORT", 3306)),
    )
    return connection

def run_query(query, params=None, fetch=True, raw=False, **kwargs):
    """
    Helper function to run queries with mysql.connector
    Used by auth.py and other legacy code
    
    Args:
        query: SQL query string (supports both :name and %(name)s placeholders)
        params: Query parameters (tuple, dict, or None)
        fetch: If True, return results; if False, return last_insert_id
        raw: If True, return raw list instead of QueryResult wrapper
        **kwargs: Additional keyword arguments (for compatibility)
    
    Returns:
        QueryResult object with .first() method for compatibility (or raw list if raw=True)
    """
    import mysql.connector
    import re
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Convert SQLAlchemy-style :param to mysql.connector %(param)s style
        if ':' in query and (kwargs or isinstance(params, dict)):
            # Replace :param with %(param)s
            query = re.sub(r':(\w+)', r'%(\1)s', query)
            
            # Use kwargs if provided, otherwise use params
            query_params = kwargs if kwargs else params
        else:
            query_params = params or ()
        
        cursor.execute(query, query_params)
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            # Return raw list if requested, otherwise QueryResult wrapper
            if raw:
                return result
            return QueryResult(result)
        else:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise e


class DictObject:
    """
    Wrapper to allow both dict['key'] and obj.key access
    """
    def __init__(self, data):
        self._data = data
    
    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()
    
    def items(self):
        return self._data.items()


class QueryResult:
    """
    Wrapper class to make list results compatible with SQLAlchemy-style .first() method
    """
    def __init__(self, results):
        # Convert each dict to DictObject for attribute access
        self.results = [DictObject(r) if isinstance(r, dict) else r for r in results]
    
    def first(self):
        """Return first result or None"""
        return self.results[0] if self.results else None
    
    def all(self):
        """Return all results"""
        return self.results
    
    def mappings(self):
        """Return self for SQLAlchemy compatibility"""
        return self
    
    def scalar(self):
        """Return first column of first row"""
        if self.results:
            first = self.results[0]
            if isinstance(first, DictObject):
                # Get first value from the dict
                return list(first._data.values())[0] if first._data else None
            return first
        return None
    
    def scalar_one(self):
        """Return first column of first row, raise if no results"""
        result = self.scalar()
        if result is None and not self.results:
            raise Exception("No row was found")
        return result
    
    def __iter__(self):
        """Allow iteration"""
        return iter(self.results)
    
    def __len__(self):
        """Allow len()"""
        return len(self.results)
    
    def __getitem__(self, index):
        """Allow indexing"""
        return self.results[index]
    
    def __bool__(self):
        """Allow truthiness check"""
        return bool(self.results)
