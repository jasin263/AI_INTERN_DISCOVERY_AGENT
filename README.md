# 🤖 AI Intern Discovery Agent

> An intelligent, multi-trigger internship discovery agent that automatically finds, ranks, and notifies you about the best internship opportunities — powered by Google Jobs API and real-time messaging triggers.

---

## 📌 Overview

The **AI Intern Discovery Agent** is a full-stack autonomous agent that continuously scans the web for internship opportunities tailored to your profile. It supports multiple trigger mechanisms (Email, Telegram, WhatsApp), performs smart ranking based on your skills and preferences, and proactively notifies you via email and Telegram.

---

## ✨ Features

- 🔍 **Automated Internship Discovery** — Searches across LinkedIn, Indeed, Internshala, Wellfound, and Tech Giant portals using the Google Jobs engine via SearchAPI.io
- 🧠 **Smart Profile-Based Ranking** — Scores and ranks internships based on your skills, preferred locations, target companies, and target roles
- 📬 **Multi-Trigger Support** — Initiate scans on-demand via:
  - **Email** — Send an email with a query and the agent replies with results
  - **Telegram Bot** — Message your bot with a keyword and get instant results
  - **WhatsApp Webhook** — Trigger discovery via WhatsApp messages
- 📅 **Scheduled Daily Scans** — Automatically runs background scans every 24 hours
- 📤 **Proactive Notifications** — Sends results via Email (SMTP/Gmail) and Telegram
- 📁 **Local Job Database** — Persists discovered jobs in a deduplicated JSON store (up to 500 records)
- 📄 **Resume Upload & Parsing** — Upload your PDF resume to auto-populate your profile
- 🖥️ **React Frontend Dashboard** — Browse, filter, and manage discovered internships through a modern UI

---

## 🏗️ Architecture

```
AI_INTERN_DISCOVERY_AGENT/
├── backend/
│   ├── run_server.py         # FastAPI server + lifespan trigger management
│   ├── searcher.py           # SearchAPI.io (Google Jobs) integration
│   ├── processor.py          # Profile-based scoring & ranking engine
│   ├── notifier.py           # Email (SMTP) & Telegram notification dispatcher
│   ├── profile_manager.py    # User profile & resume parsing
│   ├── internship.py         # Internship & InternshipReport data models
│   ├── email_listener.py     # IMAP-based email trigger listener
│   ├── telegram_listener.py  # Telegram Bot polling listener
│   ├── whatsapp_listener.py  # WhatsApp webhook handler
│   ├── discovered_jobs.json  # Local internship database
│   └── .env                  # Environment variables (not committed)
├── frontend/
│   ├── src/                  # React + Vite UI components
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- A [SearchAPI.io](https://www.searchapi.io/) account (Google Jobs engine)
- A Gmail account with App Password enabled (for Email notifications)
- *(Optional)* A Telegram Bot token from [@BotFather](https://t.me/BotFather)

---

### 1. Clone the Repository

```bash
git clone https://github.com/jasin263/AI_INTERN_DISCOVERY_AGENT.git
cd AI_INTERN_DISCOVERY_AGENT
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install fastapi uvicorn apscheduler requests python-dotenv beautifulsoup4 python-telegram-bot PyPDF2
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASS=your_gmail_app_password
IMAP_SERVER=imap.gmail.com
```

> ⚠️ **Never commit your `.env` file to GitHub.** It is already listed in `.gitignore`.

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`

---

### 4. Run the Backend Server

```bash
cd backend
python run_server.py
```

The API server starts at `http://0.0.0.0:8011`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/profile` | Retrieve current user profile |
| `POST` | `/profile/update` | Update user profile |
| `POST` | `/profile/upload-resume` | Upload PDF resume for auto-parsing |
| `GET` | `/discover` | Discover & rank internships (optional `?keywords=`) |
| `POST` | `/scan/now` | Trigger an immediate background scan |
| `POST` | `/whatsapp/webhook` | WhatsApp incoming message webhook |

---

## 🔔 Trigger Setup Guide

### Email Trigger
1. Configure IMAP credentials in `.env`
2. Send an email to your configured address with your search query in the subject line (e.g., `Find Python internships in Bangalore`)
3. The agent polls every 30 seconds and replies with the top 5 matches

### Telegram Trigger
1. Create a bot via [@BotFather](https://t.me/BotFather) and get your token
2. Add `telegram_token` and `telegram_chat_id` to your profile via `/profile/update`
3. Message your bot: `Find data science internships`
4. The agent polls every 5 seconds and sends results directly to your chat

### WhatsApp Trigger
1. Set up a WhatsApp Business API webhook pointing to `POST /whatsapp/webhook`
2. Send a message with your query to the configured number

---

## 🧠 Ranking Algorithm

The `Processor` module evaluates each internship against your profile:

| Criteria | Score Bonus |
|----------|------------|
| Skill match (per skill) | +10 points |
| Preferred location match | +20 points |
| Target company match | +30 points |
| Target role name match | +40 points |
| **Maximum score** | **100 points** |

Internships scoring **≥ 70** are marked as high-priority and sent in notifications.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — High-performance async API framework
- **APScheduler** — Background job scheduling
- **SearchAPI.io** — Google Jobs search engine integration
- **smtplib / imaplib** — Email send/receive
- **python-telegram-bot** — Telegram Bot API integration
- **PyPDF2** — Resume PDF parsing

### Frontend
- **React 18** — UI framework
- **Vite** — Fast dev server & bundler
- **Axios** — HTTP client
- **Framer Motion** — Animations
- **Lucide React** — Icon library

---

## 📋 User Profile Schema

The agent uses a JSON profile to personalize searches:

```json
{
  "name": "Your Name",
  "email": "you@example.com",
  "skills": ["Python", "Machine Learning", "React"],
  "target_roles": ["ML Engineer", "Data Science", "Software Developer"],
  "locations": ["Bangalore", "Remote", "Hyderabad"],
  "target_companies": ["Google", "Microsoft", "Amazon"],
  "telegram_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID"
}
```

---

## 🔒 Security Notes

- Store all secrets in `.env` — **never hardcode API keys**
- Add `.env` and `venv/` to `.gitignore`
- Use Gmail App Passwords (not your main password) for SMTP/IMAP
- Rotate SearchAPI.io keys periodically

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**jasin263** — [GitHub Profile](https://github.com/jasin263)

---

*Built with ❤️ to automate the internship hunt so you can focus on what matters.*
