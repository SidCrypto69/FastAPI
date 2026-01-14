from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Annotated, Literal, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from db import get_conn
import psycopg2
import re
 
app = FastAPI()
templates= Jinja2Templates(directory='templates')

def db_execute(fetch: str, query: str, params=()):
    """
    fetch: 'one' | 'all' | 'none'
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch == "one":
                    return cur.fetchone()
                if fetch == "all":
                    return cur.fetchall()
                return None
    except psycopg2.OperationalError:
        # database down / refused / wrong url
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again.")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected database error.")

class MedicalHistory(BaseModel):
    conditions: list[str] = Field(default_factory=list, description='List of medical conditions')
    surgeries: list[str] = Field(default_factory=list, description='List of surgeries undergone')
    medications: list[str] = Field(default_factory=list, description='List of medications taken and Current dosses')
    allergies: list[str] = Field(default_factory=list, description='List of allergies')


class Patient(BaseModel):
    id: Annotated [str, Field(..., description='ID of the patient', examples=['P001'])] 
    name: Annotated [str, Field(..., description='Name of the patient')] 
    city: Annotated[str, Field(..., description='City of the patient')]
    age: Annotated[int , Field(..., gt=0, description='Age of the patient in years')]
    gender: Annotated[Literal['Male','Female','Others'], Field(..., description= 'Gender of the Patient')]
    height: Annotated[float, Field(..., gt=0, description='Patients height in mts')] 
    weight: Annotated[float, Field(..., gt=0, description='Patients weight in KGs')]
    phone: Annotated[str, Field (..., description='Phone number of the patient')]
    email: Annotated[Optional[str], Field(default=None, description='Email Address')]
    smoker : Annotated[Literal['Yes','No'], Field(..., description='Is the patient a smoker')]
    last_visit_date: Annotated[Optional[str], Field(default=None, description='Last visit date')]
    medical_history: Annotated[Optional[MedicalHistory], Field(default=None, description='Medical history of the patient')]
    activity_level: Annotated[Literal['Low','Medium','High'], Field(..., description='Activity level of the patient')]
    
    @field_validator('gender', 'smoker', 'activity_level', mode='before')
    @classmethod
    def normalize_case(cls, v):
        return v.strip().capitalize() if isinstance(v, str) else v

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
         if self.bmi < 18.5:
           return 'Underweight'
         elif self.bmi < 25:
              return 'Normal'
         elif self.bmi < 30:
             return 'Overweight'
         else:
            return 'Obese'    

class BookSlotRequest(BaseModel):
    provider_id: str
    patient_id: str
    start_at: str   # "YYYY-MM-DD HH:MM"
    end_at: str     # "YYYY-MM-DD HH:MM"

def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M")

class ChatRequest(BaseModel):
    patient_id: str
    message: str

PENDING_BOOKINGS: Dict[str, Dict[str, Any]] = {}

def get_patient_or_404(patient_id: str):
    row = db_execute("one", "SELECT * FROM patients WHERE id=%s;", (patient_id,))
    if not row:
        raise HTTPException(404, detail="Patient not found")
    return row

def calc_bmi(p) -> Optional[float]:
    h = float(p.get("height") or 0)
    w = float(p.get("weight") or 0)
    if h > 0 and w > 0:
        return round(w / (h * h), 2)
    return None

class patientupdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['Male','Female','Others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    phone: Annotated[Optional[str], Field(default=None)]
    email: Annotated[Optional[str], Field(default=None)]
    smoker: Annotated[Optional[Literal['Yes','No']], Field(default=None)]
    last_visit_date: Annotated[Optional[str], Field(default=None)]
    medical_history: Annotated[Optional[MedicalHistory], Field(default=None)]
    activity_level: Annotated[Optional[Literal['Low','Medium','High']], Field(default=None)]

    @field_validator('gender', 'smoker', 'activity_level', mode='before')
    @classmethod
    def normalize_case(cls, v):
        return v.strip().capitalize() if isinstance(v, str) else v

def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def root():
    return {"message": "patient health management system api"}

@app.get("/about")
def about():
    return{"message": "A fully functional API to manage patient health data and provide insights based on BMI calculations."}

@app.get("/view")
def view_all_patients():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM patients ORDER BY id;")
            rows = cur.fetchall()

    # keep SAME response shape your frontend expects
    return {r["id"]: {k: v for k, v in r.items() if k != "id"} for r in rows}

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID of the patient", example="P001")):
    row = db_execute("one", "SELECT * FROM patients WHERE id=%s;", (patient_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Return same shape as you use everywhere else
    return {k: v for k, v in row.items() if k != "id"}

@app.get("/sort")
def sort_patients(
    sort_by: str = Query("age"),
    order: str = Query("asc")
):
    valid = {"height", "weight", "age"}
    # bmi is computed; we can calculate it in SQL
    valid_with_bmi = valid.union({"bmi"})

    if sort_by not in valid_with_bmi:
        raise HTTPException(400, f"sort_by must be one of: {sorted(valid_with_bmi)}")

    if order not in {"asc", "desc"}:
        raise HTTPException(400, "order must be 'asc' or 'desc'")

    if sort_by == "bmi":
        sql = f"""
        SELECT *, (weight / NULLIF(height*height, 0)) AS bmi
        FROM patients
        ORDER BY bmi {order};
        """
        rows = db_execute("all", sql)
    else:
        sql = f"SELECT * FROM patients ORDER BY {sort_by} {order};"
        rows = db_execute("all", sql)

    return rows

@app.post("/create")
async def create_patient(request: Request):
    p = await request.json()
    mh = p.get("medical_history") or {}

    sql = """
    INSERT INTO patients (
      id,name,city,age,gender,height,weight,phone,email,
      smoker,activity_level,last_visit_date,medical_history
    ) VALUES (
      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb
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

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    p["id"], p["name"], p.get("city"), p["age"], p.get("gender"),
                    p["height"], p["weight"], p.get("phone"), p.get("email"),
                    p.get("smoker"), p.get("activity_level"), p.get("last_visit_date"),
                    json.dumps(mh)
                ))
        return {"message": f"Patient {p['id']} saved in PostgreSQL"}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")

@app.put("/edit/{patient_id}")
async def edit_patient(patient_id: str, request: Request):
    u = await request.json()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT medical_history FROM patients WHERE id=%s;", (patient_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Patient not found")

            mh = row["medical_history"] or {}
            if "medical_history" in u and isinstance(u["medical_history"], dict):
                mh.update(u["medical_history"])

            sql = """
            UPDATE patients SET
              name = COALESCE(%s, name),
              city = COALESCE(%s, city),
              age = COALESCE(%s, age),
              gender = COALESCE(%s, gender),
              height = COALESCE(%s, height),
              weight = COALESCE(%s, weight),
              phone = COALESCE(%s, phone),
              email = COALESCE(%s, email),
              smoker = COALESCE(%s, smoker),
              activity_level = COALESCE(%s, activity_level),
              last_visit_date = COALESCE(%s, last_visit_date),
              medical_history = %s::jsonb
            WHERE id = %s;
            """
            cur.execute(sql, (
                u.get("name"), u.get("city"), u.get("age"), u.get("gender"),
                u.get("height"), u.get("weight"), u.get("phone"), u.get("email"),
                u.get("smoker"), u.get("activity_level"), u.get("last_visit_date"),
                json.dumps(mh),
                patient_id
            ))

    return {"message": f"Patient {patient_id} updated in PostgreSQL"}

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM patients WHERE id=%s;", (patient_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": f"Patient {patient_id} deleted from PostgreSQL"}

@app.get('/UI')
def ui_home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get("/slots/{provider_id}/{day}")
def get_slots(provider_id: str, day: str):
    try:
        day_date = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Use YYYY-MM-DD")

    sql = """
    WITH params AS (
      SELECT %s::text AS provider_id, %s::date AS day
    ),
    hours AS (
      SELECT ph.*
      FROM provider_hours ph
      JOIN params p ON p.provider_id = ph.provider_id
      WHERE ph.dow = EXTRACT(DOW FROM (SELECT day FROM params))::int
    ),
    slots AS (
      SELECT
        (p.day + h.start_time) + (n * make_interval(mins => h.slot_minutes)) AS start_at,
        (p.day + h.start_time) + ((n+1) * make_interval(mins => h.slot_minutes)) AS end_at
      FROM params p
      JOIN hours h ON true
      CROSS JOIN generate_series(
        0,
        FLOOR(
          EXTRACT(EPOCH FROM ((p.day + h.end_time) - (p.day + h.start_time))) / 60 / h.slot_minutes
        )::int - 1
      ) AS n
    ),
    blocked AS (
      SELECT a.start_at, a.end_at
      FROM appointments a
      JOIN params p ON p.provider_id = a.provider_id
      WHERE a.status = 'booked'
        AND a.start_at::date = (SELECT day FROM params)
    )
    SELECT s.start_at, s.end_at
    FROM slots s
    LEFT JOIN blocked b
      ON s.start_at < b.end_at AND s.end_at > b.start_at
    WHERE b.start_at IS NULL
    ORDER BY s.start_at;
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (provider_id, day_date))
            rows = cur.fetchall()

    return {"provider_id": provider_id, "day": day, "available": rows}


@app.post("/book")
def book_slot(req: BookSlotRequest):
    try:
        start_dt = parse_dt(req.start_at)
        end_dt = parse_dt(req.end_at)
    except ValueError:
        raise HTTPException(400, "Use format YYYY-MM-DD HH:MM")

    if end_dt <= start_dt:
        raise HTTPException(400, "end_at must be after start_at")

    # Validate provider hours + slot alignment
    sql_hours = """
    SELECT start_time, end_time, slot_minutes
    FROM provider_hours
    WHERE provider_id=%s AND dow = EXTRACT(DOW FROM %s::date)::int;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_hours, (req.provider_id, start_dt.date()))
            h = cur.fetchone()

            if not h:
                raise HTTPException(400, "Provider has no working hours for this day")

            slot_minutes = int(h["slot_minutes"])
            work_start = datetime.combine(start_dt.date(), h["start_time"])
            work_end = datetime.combine(start_dt.date(), h["end_time"])

            if start_dt < work_start or end_dt > work_end:
                raise HTTPException(400, "Requested time is outside provider working hours")

            duration_mins = int((end_dt - start_dt).total_seconds() // 60)
            if duration_mins != slot_minutes:
                raise HTTPException(400, f"Appointments must be exactly {slot_minutes} minutes")

            # Align to slot boundaries (e.g., :00, :30)
            offset = int((start_dt - work_start).total_seconds() // 60)
            if offset % slot_minutes != 0:
                raise HTTPException(400, "Start time must align to slot boundaries")

            # Insert booking
            try:
                cur.execute("""
                    INSERT INTO appointments (provider_id, patient_id, start_at, end_at)
                    VALUES (%s, %s, %s, %s);
                """, (req.provider_id, req.patient_id, start_dt, end_dt))
            except psycopg2.Error as e:
                # Overlap constraint or other DB errors
                msg = str(e).lower()
                if "no_overlap_per_provider" in msg or "exclude constraint" in msg:
                    raise HTTPException(409, "That slot is already booked. Pick another time.")
                raise HTTPException(500, "Database error while booking.")

    return {"message": "Appointment booked"}

EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "shortness of breath",
    "stroke", "fainting", "severe bleeding", "suicidal", "suicide"
]

@app.post("/chat")
def chat(req: ChatRequest):
    pid = req.patient_id.strip()
    msg = req.message.strip()
    lower = msg.lower()

    # Emergency guardrail
    if any(k in lower for k in EMERGENCY_KEYWORDS):
        return {"reply": "If this may be an emergency, call emergency services immediately. I can help with scheduling and general info."}

    # Confirm pending booking
    if pid in PENDING_BOOKINGS:
        if lower in ["yes", "y", "confirm", "ok", "okay"]:
            pending = PENDING_BOOKINGS.pop(pid)
            try:
                book_slot(BookSlotRequest(**pending))
                return {"reply": f"✅ Confirmed! Booked {pending['provider_id']} on {pending['start_at']}."}
            except Exception as e:
                return {"reply": f"❌ Booking failed: {str(e)}"}

        if lower in ["no", "n", "cancel", "stop"]:
            PENDING_BOOKINGS.pop(pid, None)
            return {"reply": "❌ Booking cancelled."}

        return {"reply": "You have a pending booking. Reply YES to confirm or NO to cancel."}

    # Load patient
    p = get_patient_or_404(pid)
    mh = p.get("medical_history") or {}

    # BMI
    if "bmi" in lower:
        bmi = calc_bmi(p)
        return {"reply": f"Your BMI is {bmi}." if bmi else "Not enough data to calculate BMI."}

    # Allergies
    if "allerg" in lower:
        allergies = mh.get("allergies", [])
        return {"reply": f"Allergies: {', '.join(allergies) if allergies else 'None listed.'}"}

    # Slots
    if "slot" in lower or "available" in lower:
        pm = re.search(r"\bD\d+\b", msg, flags=re.IGNORECASE)
        dm = re.search(r"\b\d{4}-\d{2}-\d{2}\b", msg)
        if pm and dm:
            provider_id = pm.group(0).upper()
            day = dm.group(0)
            slots_data = get_slots(provider_id, day)
            av = slots_data.get("available", [])
            if not av:
                return {"reply": f"No available slots for {provider_id} on {day}."}
            lines = "\n".join([f"- {x['start_at']} to {x['end_at']}" for x in av[:8]])
            return {"reply": f"Available slots for {provider_id} on {day}:\n{lines}"}

    # Booking intent
    if "book" in lower:
        pm = re.search(r"\bD\d+\b", msg, flags=re.IGNORECASE)
        dm = re.search(r"\b\d{4}-\d{2}-\d{2}\b", msg)
        tm = re.search(r"\b\d{1,2}:\d{2}\b", msg)
        if not (pm and dm and tm):
            return {"reply": "To book, send: Book D001 2025-12-30 10:00"}

        provider_id = pm.group(0).upper()
        day = dm.group(0)
        t = tm.group(0)
        if len(t.split(":")[0]) == 1:
            t = "0" + t

        start_at = f"{day} {t}"

        h = db_execute(
            "one",
            "SELECT slot_minutes FROM provider_hours WHERE provider_id=%s AND dow = EXTRACT(DOW FROM %s::date)::int;",
            (provider_id, day)
        )
        if not h:
            return {"reply": f"{provider_id} has no working hours on {day}."}

        mins = int(h["slot_minutes"])
        start_dt = datetime.strptime(start_at, "%Y-%m-%d %H:%M")
        end_at = (start_dt + timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M")

        PENDING_BOOKINGS[pid] = {
            "provider_id": provider_id,
            "patient_id": pid,
            "start_at": start_at,
            "end_at": end_at
        }

        return {"reply": f"Confirm booking {provider_id} on {start_at} to {end_at}? Reply YES or NO."}

    return {"reply": "Ask: BMI, allergies, available slots (D001 + date), or book (provider + date + time)."}

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("select 1 AS ok;")
                row = cur.fetchone()
        return {"status": "ok", "db": row['ok']}
    except Exception as e:
        return {"status": "error", "details": str(e)}