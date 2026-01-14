import json
from db import get_conn

# Read your existing JSON file
with open("patients.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

# Your JSON format is: { "P001": {...}, "P002": {...} }
patients = [{"id": pid, **p} for pid, p in raw.items()]

SQL = """
INSERT INTO patients (
  id,name,city,age,gender,height,weight,phone,email,
  smoker,activity_level,last_visit_date,medical_history
) VALUES (
  %(id)s,%(name)s,%(city)s,%(age)s,%(gender)s,%(height)s,%(weight)s,%(phone)s,%(email)s,
  %(smoker)s,%(activity_level)s,%(last_visit_date)s,%(medical_history)s::jsonb
)
ON CONFLICT (id) DO UPDATE SET
  name=EXCLUDED.name,
  city=EXCLUDED.city,
  age=EXCLUDED.age,
  gender=EXCLUDED.gender,
  height=EXCLUDED.height,
  weight=EXCLUDED.weight,
  phone=EXCLUDED.phone,
  email=EXCLUDED.email,
  smoker=EXCLUDED.smoker,
  activity_level=EXCLUDED.activity_level,
  last_visit_date=EXCLUDED.last_visit_date,
  medical_history=EXCLUDED.medical_history;
"""

with get_conn() as conn:
    with conn.cursor() as cur:
        for p in patients:
            p = dict(p)

            # Make sure missing fields don't crash the insert
            p.setdefault("city", None)
            p.setdefault("phone", None)
            p.setdefault("email", None)
            p.setdefault("smoker", None)
            p.setdefault("activity_level", None)
            p.setdefault("last_visit_date", None)

            p["medical_history"] = json.dumps(p.get("medical_history") or {})

            cur.execute(SQL, p)

print(f"Loaded {len(patients)} patients into PostgreSQL")
