from db import get_conn

DDL = """
CREATE TABLE IF NOT EXISTS providers (
  provider_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  specialty TEXT
);

-- 0=Sunday .. 6=Saturday
CREATE TABLE IF NOT EXISTS provider_hours (
  provider_id TEXT REFERENCES providers(provider_id) ON DELETE CASCADE,
  dow INT CHECK (dow BETWEEN 0 AND 6),
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  slot_minutes INT NOT NULL DEFAULT 30,
  PRIMARY KEY (provider_id, dow)
);

CREATE TABLE IF NOT EXISTS appointments (
  appointment_id BIGSERIAL PRIMARY KEY,
  provider_id TEXT REFERENCES providers(provider_id) ON DELETE CASCADE,
  patient_id TEXT REFERENCES patients(id) ON DELETE SET NULL,
  start_at TIMESTAMP NOT NULL,
  end_at TIMESTAMP NOT NULL,
  status TEXT NOT NULL DEFAULT 'booked',
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_appt_provider_time ON appointments(provider_id, start_at);

-- Prevent double-booking (overlaps)
CREATE EXTENSION IF NOT EXISTS btree_gist;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'no_overlap_per_provider') THEN
    ALTER TABLE appointments
    ADD CONSTRAINT no_overlap_per_provider
    EXCLUDE USING gist (
      provider_id WITH =,
      tsrange(start_at, end_at, '[)') WITH &&
    )
    WHERE (status = 'booked');
  END IF;
END$$;
"""

def main():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
    print("providers/provider_hours/appointments tables created")

if __name__ == "__main__":
    main()
