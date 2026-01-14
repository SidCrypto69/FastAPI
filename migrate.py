from db import get_conn

DDL = """
CREATE TABLE IF NOT EXISTS patients (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT,
  age INT CHECK (age > 0),
  gender TEXT,
  height DOUBLE PRECISION CHECK (height > 0),
  weight DOUBLE PRECISION CHECK (weight > 0),
  phone TEXT,
  email TEXT,
  smoker TEXT,
  activity_level TEXT,
  last_visit_date DATE,
  medical_history JSONB DEFAULT '{}'::jsonb
);
"""

def main():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
    print("patients table created")

if __name__ == "__main__":
    main()
