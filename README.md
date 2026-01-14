# 🏥 Patient Health Management System
**FastAPI • PostgreSQL • Chatbot • MCP • CrewAI**

A modern backend system designed to help clinics manage patients, appointments, and health data — with a future-ready architecture for AI agents and automation.

---

## 📌 Project Overview

The Patient Health Management System is a real-world healthcare backend that enables clinics to:

- Manage patient records  
- Store and retrieve medical history  
- Automatically calculate BMI  
- Handle doctor schedules and appointment slots  
- Book appointments seamlessly  
- Provide a chatbot interface for patient queries  
- Prepare for AI automation using **CrewAI + MCP**  

This project is built with scalability and AI integration in mind.

---

## 🏗️ System Architecture

```
Frontend (HTML/JS)
        ↓
FastAPI Backend
        ↓
PostgreSQL Database
        ↓
Business Logic (Slots, Booking, BMI)
        ↓
Chatbot Layer
        ↓
MCP Server (Tools)
        ↓
CrewAI Agents (Automation & AI)
```

---

## ✨ Features

### 👩‍⚕️ Patient Management
- Add new patients  
- Update patient details  
- Delete patients  
- View all patients  
- View medical history  

### 📊 Health Analytics
- Automatic BMI calculation  
- Health verdict:
  - Underweight  
  - Normal  
  - Overweight  
  - Obese  

### 📅 Appointment System
- Provider schedules  
- Slot generation  
- Slot availability check  
- Appointment booking  
- Overlap prevention  

### 💬 Chatbot
Patients can ask about:
- BMI  
- Allergies  
- Last visit  
- Available slots  
- Booking instructions  

### 🤖 Agentic AI (Design Ready)
- MCP server exposes backend tools  
- CrewAI agents automate workflows  
- LLM-ready for natural language operations  

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|------------|
| Backend | FastAPI |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| AI Framework | CrewAI |
| Tool Protocol | MCP |
| ORM / Driver | psycopg2 |
| Server | Uvicorn |

---

## 📂 Project Structure

```
FastApi Project/
│
├── main.py            # FastAPI application
├── db.py              # Database connection
├── migrate.py         # Patient table migration
├── migrate_slots.py   # Slot tables migration
├── mcp_server.py      # MCP tool server
├── crew_runner.py     # CrewAI agent runner
├── index.html         # Frontend UI
├── requirements.txt
└── myenv/             # Virtual environment
```

---

## 🚀 How It Works (Workflow)

1. User opens `index.html`  
2. UI sends requests to FastAPI  
3. FastAPI:
   - Reads/writes to PostgreSQL  
   - Handles slot logic & booking  
4. Chatbot endpoint:
   - Understands intent  
   - Fetches patient data  
5. MCP server:
   - Exposes booking & info tools  
6. CrewAI:
   - Uses MCP tools  
   - Automates scheduling tasks  

---

## ▶️ Running the Project

### 1️⃣ Activate Virtual Environment
```bash
.\myenv\Scripts\activate
```

### 2️⃣ Start PostgreSQL
Make sure PostgreSQL is running on port **5432**.

### 3️⃣ Run Migrations
```bash
python migrate.py
python migrate_slots.py
```

### 4️⃣ Start FastAPI Server
```bash
uvicorn main:app --reload
```

Open:
- http://127.0.0.1:8000  
- http://127.0.0.1:8000/docs  

### 5️⃣ (Optional) Run MCP Server
```bash
python mcp_server.py
```

### 6️⃣ (Optional) Run CrewAI Agent
```bash
python crew_runner.py
```

---

## 🧪 Example Queries

```
Show available slots for D001 on 2025-12-30
Book D001 for patient P001 on 2025-12-30 10:00 to 10:30
What allergies does patient P001 have?
```

---

## 🔧 Troubleshooting

### ❌ Server Not Starting
```bash
.\myenv\Scripts\activate
pip install -r requirements.txt
```

### ❌ Database Connection Error
Check:
- PostgreSQL is running  
- `DATABASE_URL` is correct  
- Port **5432** is free  

### ❌ Booking Fails
Make sure:
- Slot time is valid  
- No overlapping appointment exists  

### ❌ CrewAI / MCP Errors
If you see:
```
OPENAI_API_KEY is required
```
or
```
insufficient_quota
```
That means:
- API key is missing **or**
- Quota is exhausted  

✅ Solution:
- Add API credits  
- Set `OPENAI_API_KEY` in environment variables  

---

## 🆘 Support

- 📧 Email: sidchavan6557@gmail.com  
- 💼 LinkedIn: https://www.linkedin.com/in/siddhesh-chavan-36718622b/  
- 🐞 Issues: Open an issue in this repository  

You can ask about:
- FastAPI  
- PostgreSQL  
- Booking logic  
- Chatbot flow  
- MCP / CrewAI  

---

## 🔮 Future Enhancements

### 🤖 AI & Automation
- Full CrewAI agent for appointment scheduling  
- MCP tools for billing & reports  
- Smarter LLM chatbot  

### 🔐 Security
- Login system  
- Role-based access (Admin / Doctor / Patient)  

### 📊 UI & UX
- Doctor dashboard  
- Appointment calendar  
- Patient self-service portal  

### 🗄️ Backend
- Alembic migrations  
- Redis caching  
- Email/SMS reminders  

### ☁️ Deployment
- Docker support  
- Cloud hosting (AWS / Azure / GCP / Render)  

---

## 👨‍💻 Author

**Siddhesh Chavan**  
*Data Engineer | Backend Developer | AI Enthusiast*

This project demonstrates real-world backend engineering combined with modern agentic AI architecture using **FastAPI, PostgreSQL, MCP, and CrewAI**.
