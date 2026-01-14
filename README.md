# 🏥 Patient Health Management System  
**FastAPI • PostgreSQL • Chatbot • MCP • CrewAI**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-success)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

A modern healthcare backend system to manage patients, appointments, and medical data — built with a **future-ready agentic AI architecture** using **MCP + CrewAI**.

---

## 📌 Project Overview

The **Patient Health Management System** helps clinics:

- Manage patient records  
- Store and retrieve medical history  
- Automatically calculate BMI  
- Handle doctor schedules and appointment slots  
- Book appointments  
- Provide a chatbot interface  
- Prepare for AI automation using **CrewAI + MCP**

Designed as a **real-world production-style backend** with extensibility for AI agents.

---

## 🏗️ System Architecture

Frontend (HTML/JS) → FastAPI → PostgreSQL → Business Logic → Chatbot → MCP Server → CrewAI Agents

---

## ✨ Features

### 👩‍⚕️ Patient Management
- Create, update, delete patients  
- View all patients  
- View medical history  

### 📊 Health Analytics
- Auto BMI calculation  
- Health verdict (Underweight, Normal, Overweight, Obese)

### 📅 Appointment System
- Provider schedules  
- Slot generation  
- Slot availability  
- Appointment booking  
- Overlap prevention  

### 💬 Chatbot
Ask about BMI, allergies, last visit, slots, and booking instructions.

### 🤖 Agentic AI
- MCP server exposes backend tools  
- CrewAI agents automate workflows  

---

## 🛠️ Tech Stack

FastAPI | PostgreSQL | HTML/CSS/JS | CrewAI | MCP | psycopg2 | Uvicorn

---

## ▶️ Getting Started

```bash
python -m venv myenv
.\myenv\Scriptsctivate
pip install -r requirements.txt
python migrate.py
python migrate_slots.py
uvicorn main:app --reload
```

---

## 👨‍💻 Author

**Siddhesh Chavan**  
Data Engineer | Backend Developer | AI Enthusiast
