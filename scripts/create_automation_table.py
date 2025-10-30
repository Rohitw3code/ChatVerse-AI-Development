import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_automation_table():
    """Create the automation_traces table in Supabase"""
    
    # Database connection config from environment
    params = {
        "user": os.getenv("PSQL_USERNAME"),
        "password": os.getenv("PSQL_PASSWORD"),
        "host": os.getenv("PSQL_HOST"),
        "port": int(os.getenv("PSQL_PORT", "5432")),
        "dbname": os.getenv("PSQL_DATABASE"),
        "sslmode": os.getenv("PSQL_SSLMODE", "require"),
        "connect_timeout": 10,
    }
    
    print("Connecting to Supabase PostgreSQL...")
    print(f"  Host: {params['host']}")
    print(f"  Database: {params['dbname']}")
    print(f"  User: {params['user']}")
    
    with psycopg.connect(**params) as conn:
        with conn.cursor() as cur:
            try:
                # Read the SQL file
                sql_file = Path(__file__).parent.parent / "tabels" / "automation.sql"
                print(f"Reading SQL file: {sql_file}")
                
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                
                print("Executing SQL script...")
                # Execute the SQL - it has IF NOT EXISTS clauses
                try:
                    cur.execute(sql_content)
                    conn.commit()
                    print("✅ Successfully executed SQL script!")
                except psycopg.errors.DuplicateObject as e:
                    # Table/trigger already exists, that's fine
                    conn.rollback()
                    print("ℹ️  Table already exists (this is OK)")
                    print(f"   Details: {e}")
                
                # Verify the table was created
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'automation_traces'
                    ORDER BY ordinal_position
                """)
                
                result = cur.fetchall()
                print("\nTable structure:")
                for row in result:
                    print(f"  - {row[0]}: {row[1]}")
                
                # Check indexes
                cur.execute("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = 'automation_traces'
                """)
                
                indexes = cur.fetchall()
                print("\nIndexes created:")
                for idx in indexes:
                    print(f"  - {idx[0]}")
                
                # Check functions
                cur.execute("""
                    SELECT proname 
                    FROM pg_proc 
                    WHERE proname LIKE '%automation_trace%'
                """)
                
                functions = cur.fetchall()
                print("\nHelper functions created:")
                for func in functions:
                    print(f"  - {func[0]}()")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                conn.rollback()
                raise
    
    print("\nDatabase connection closed.")

if __name__ == "__main__":
    create_automation_table()
