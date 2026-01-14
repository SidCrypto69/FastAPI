🏥 Patient Health Management System

FastAPI • PostgreSQL • Chatbot • MCP • CrewAI

📌 Project Overview

This project is a Patient Health Management System that allows clinics to:

Manage patients (Create, Update, Delete, View)

Store medical history

Calculate BMI automatically

Manage doctor availability and appointment slots

Book appointments

Provide a chatbot interface for patient queries

Prepare for AI agents using CrewAI + MCP

It is designed as a real-world healthcare backend with future-ready agent architecture.

🏗️ System Architecture
Frontend (HTML/JS)
        ↓
FastAPI Backend
        ↓
PostgreSQL Database
        ↓
Business Logic (slots, booking, BMI)
        ↓
Chatbot Layer
        ↓
MCP Server (tools)
        ↓
CrewAI Agents (automation & AI)

✨ Features
👩‍⚕️ Patient Management

Add new patients

Update patient details

Delete patients

View all patients

View medical history

📊 Health Analytics

Auto BMI calculation

Health verdict (Underweight / Normal / Overweight / Obese)

📅 Appointment System

Provider schedules

Slot generation

Slot availability check

Appointment booking

💬 Chatbot

Ask about:

BMI

Allergies

Last visit

Available slots

Booking instructions

🤖 Agentic AI (Design Ready)

MCP server exposes tools

CrewAI agents automate scheduling

LLM-ready for natural language workflows

🛠️ Tech Stack
Layer	Technology
Backend	FastAPI
Database	PostgreSQL
Frontend	HTML, CSS, JavaScript
AI Framework	CrewAI
Tool Protocol	MCP
ORM/Driver	psycopg2
Server	Uvicorn
📂 Project Structure
FastApi Project/
│
├── main.py              # FastAPI app
├── db.py                # Database connection
├── migrate.py           # Patient table migration
├── migrate_slots.py     # Slot tables migration
├── mcp_server.py        # MCP tool server
├── crew_runner.py       # CrewAI agent runner
├── index.html           # Frontend UI
├── requirements.txt
└── myenv/               # Virtual environment

🚀 How It Works (Workflow)

User opens index.html

UI sends request to FastAPI

FastAPI:

Reads/writes to PostgreSQL

Handles slot logic & booking

Chatbot endpoint:

Understands intent

Fetches patient data

MCP server:

Exposes booking & info tools

CrewAI:

Uses MCP tools

Automates scheduling tasks

▶️ Running the Project
1️⃣ Activate environment
.\myenv\Scripts\activate

2️⃣ Start PostgreSQL

Make sure DB is running on port 5432.

3️⃣ Run migrations
python migrate.py
python migrate_slots.py

4️⃣ Start FastAPI server
uvicorn main:app --reload


Open:
👉 http://127.0.0.1:8000

👉 http://127.0.0.1:8000/docs

5️⃣ (Optional) Run MCP server
python mcp_server.py

6️⃣ (Optional) Run CrewAI agent
python crew_runner.py


Try:

Show available slots for D001 on 2025-12-30
Book D001 for patient P001 on 2025-12-30 10:00 to 10:30
What allergies does patient P001 have?

🔧 Troubleshooting
1. Server not starting

Activate env:

.\myenv\Scripts\activate


Reinstall:

pip install -r requirements.txt

2. Database connection error

Check:

PostgreSQL is running

DATABASE_URL is correct

Port 5432 is free

3. Booking fails

Make sure:

Slot time is valid

No overlapping appointment exists

4. CrewAI / MCP errors

If you see:

OPENAI_API_KEY is required


or

insufficient_quota


That means:

API key missing OR

Quota exhausted

Solution:

Add API credits

🆘 Support

Need help?

📧 Email: sidchavan6557@gmail.com

💼 LinkedIn: https://www.linkedin.com/in/siddhesh-chavan-36718622b/

🐞 Issues: Open an issue in this repository

You can ask about:

FastAPI

PostgreSQL

Booking logic

Chatbot flow

MCP / CrewAI

🔮 Future Enhancements
🤖 AI & Automation

Full CrewAI agent for appointment scheduling

MCP tool expansion for billing & reports

Smarter LLM chatbot

🔐 Security

Login system

Role-based access (Admin / Doctor / Patient)

📊 UI & UX

Doctor dashboard

Appointment calendar

Patient self-service portal

🗄️ Backend

Alembic migrations

Redis caching

Email/SMS reminders

☁️ Deployment

Docker support

Cloud hosting (AWS / Azure / GCP / Render)

👨‍💻 Author

Siddhesh Chavan
Data Engineer | Backend Developer | AI Enthusiast

This project demonstrates real-world backend engineering combined with modern agentic AI architecture using FastAPI, PostgreSQL, MCP, and CrewAI.
