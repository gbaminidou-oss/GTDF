# GTDF Platform
**Gamified Tailored Development Framework**  
Adaptive Cybersecurity Awareness Training — MSc Dissertation Artefact

---

## What It Is

GTDF is a personalised, gamified cybersecurity awareness training web application. It delivers training across **7 domains** using a pre-assessment that routes each user to the right difficulty level, then adjusts difficulty in real time as they answer scenarios.

Built on **Protection Motivation Theory** (Rogers, 1975) and evaluated using **Design Science Research Methodology** (Peffers et al., 2007).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Flask 3.1.1 |
| Database | SQLite (dev) / PostgreSQL (production) |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Auth | Flask-Login 0.6.3, Werkzeug PBKDF2 |
| Templating | Jinja2 (HTML5) |
| Styling | CSS3, custom properties, Flexbox/Grid |
| Frontend | Vanilla JavaScript (ES6) |
| Charts | Chart.js 4.4.2 (CDN) |
| Icons | Font Awesome 6.5.0 (CDN) |
| Production | Gunicorn + Render |

---

## Features

- **Pre-assessment** — 14 questions across 7 domains; routes each domain to Beginner / Intermediate / Advanced
- **Adaptive Rule Engine** — 3 consecutive correct answers upgrades difficulty; 2 wrong answers downgrades it and enables hints
- **7 Modules** — Phishing, Social Engineering, Password Security, Safe Browsing, Pretexting, Data Handling, Incident Reporting
- **20 Lessons** — expandable lesson content with key learning points per module
- **22 Scenarios** — simulated phishing emails, SMS, websites, USB prompts, phone scripts
- **Sequential unlocking** — modules unlock in order of the user's weakest domains
- **Gamification** — XP points, levels, 12 badges, streak tracking, live leaderboard
- **Post-assessment** — measures improvement against the pre-assessment baseline
- **Growth Report** — per-domain pre vs post comparison chart, scenario accuracy, time on task, activity timeline
- **CSV Export** — each user can download their complete dataset for research analysis

---

## Project Structure

```
GTDF/
├── run.py                      # Entry point — runs on port 5001
├── config.py                   # Dev / Prod / Test config
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment
├── .gitignore
└── app/
    ├── __init__.py             # Application factory (create_app)
    ├── models/
    │   ├── user.py             # User — XP, level, streak, risk_level
    │   ├── module.py           # Module, Lesson, Scenario, Progress
    │   ├── assessment.py       # Assessment, AssessmentResult, Question
    │   ├── gamification.py     # Badge, UserBadge, Achievement, Leaderboard
    │   └── feedback.py         # LearningActivity — time on task
    ├── routes/
    │   ├── auth.py             # Register, Login, Logout, Profile
    │   ├── modules.py          # Learning path, module detail, completion
    │   ├── scenarios.py        # Scenario player, answer submit, feedback
    │   ├── assessment.py       # Pre/post assessment, scoring
    │   ├── dashboard.py        # Dashboard, progress overview
    │   ├── gamification.py     # Leaderboard, achievements
    │   └── feedback.py         # Growth report, CSV export, lesson logging
    ├── services/
    │   ├── AdaptiveRuleEngine.py       # Difficulty routing + streak logic
    │   └── gamification_service.py     # XP award, badge unlock, leaderboard
    ├── database/
    │   └── seed.py             # All seed data — modules, lessons, scenarios, badges
    ├── static/
    │   ├── css/main.css        # 28 CSS custom properties, dual-theme
    │   └── js/main.js          # Timer, XP animation, adaptive UI
    └── templates/
        ├── base.html           # Sidebar layout, XP bar, nav
        ├── auth/               # login, register, profile, settings
        ├── modules/            # learning_path, module_detail
        ├── scenarios/          # scenario_player, feedback
        ├── assessment/         # pre_assessment, post_assessment, result
        ├── dashboard/          # home, progress
        ├── gamification/       # leaderboard, achievements
        └── feedback/           # growth (growth report page)
```

---

## Local Setup

### 1. Clone or download the project

```bash
git clone https://github.com/YOUR-USERNAME/GTDF.git
cd GTDF
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python run.py
```

Open your browser at **http://127.0.0.1:5001**

The database is created automatically on first run and seeded with all modules, lessons, scenarios, questions, and badges. No manual database setup is needed.

---

## First Use

1. Go to `http://127.0.0.1:5001` — you will be redirected to the login page
2. Click **Create Free Account** and register
3. You are automatically redirected to the **Pre-Assessment** (14 questions, ~5 minutes)
4. Your results route you to the correct difficulty level per domain
5. Start training from the **Learning Path**

---

## Adaptive Rule Engine Thresholds

| Pre-assessment score | Assigned level | Priority |
|---|---|---|
| < 40% | Beginner | High — trained first |
| 40 – 74% | Intermediate | Medium |
| ≥ 75% | Advanced | Low |

**In-session adjustments (per module):**
- 3 consecutive correct answers → upgrade to next difficulty
- 2 consecutive wrong answers → downgrade + enable hints

---

## Modules & Badges

| # | Module | Badge | Bloom's Level |
|---|---|---|---|
| 1 | Phishing Recognition | Eagle Eye | L4 Analyse |
| 2 | Authority and Urgency Resistance | Unbreakable | L3 Apply |
| 3 | Credential Security | Vault Guardian | L2 Understand |
| 4 | Safe Browsing | Web Detective | L4 Analyse |
| 5 | Pretexting Detection | Human Firewall | L3 Apply |
| 6 | Data Handling & Classification | Data Steward | L4 Analyse |
| 7 | Incident Reporting | First Responder | L2 Understand |

---

## Growth Report & Research Data

Every user has a **Growth Report** page (`/feedback/growth`) that shows:

- Pre-assessment vs post-assessment scores per domain (bar chart)
- Overall improvement percentage
- Scenario accuracy rate
- Time spent on task
- Difficulty distribution (beginner / intermediate / advanced attempts)
- Recent activity timeline

**Download CSV** exports the user's complete dataset — suitable for analysis in SPSS, Excel, or Python. Each CSV row contains:

- Pre-assessment scores (overall + per domain)
- Post-assessment scores (overall + per domain)
- Improvement delta per domain
- Modules completed, scenarios attempted, accuracy %, time (minutes)
- XP earned, level reached

---

## Cloud Deployment (Render)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/GTDF.git
git push -u origin main
```

### 2. Create a PostgreSQL database on Render

- Go to [render.com](https://render.com) → **New → PostgreSQL**
- Name: `gtdf-db`, Plan: **Free**
- Copy the **Internal Database URL**

### 3. Create a Web Service

- **New → Web Service** → connect your GitHub repo
- Runtime: **Python 3**, Build: `pip install -r requirements.txt`
- Start command: `gunicorn run:app`

### 4. Set environment variables

| Variable | Value |
|---|---|
| `DATABASE_URL` | Internal Database URL from step 2 |
| `SECRET_KEY` | Any long random string |

Click **Deploy**. The app will be live at `https://gtdf-platform.onrender.com` in ~3 minutes.

> **Note:** Render's free tier spins down after 15 minutes of inactivity. The first request after idle takes ~30 seconds to wake up.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Production only | PostgreSQL connection string (Render injects this) |
| `SECRET_KEY` | Recommended | Flask session signing key — change in production |

In development neither variable is needed — the app defaults to SQLite and a built-in dev secret key.

---

## Resetting the Database

To wipe all data and re-seed from scratch (development only):

```python
from app import create_app, db
from app.database.seed import seed_all

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    seed_all()
```

---

## Theoretical Framework

| Framework | Reference | Application |
|---|---|---|
| Protection Motivation Theory | Rogers (1975) | Threat/coping appraisal content design |
| Design Science Research Methodology | Peffers et al. (2007) | Research lifecycle (problem → artefact → evaluation) |
| Bloom's Taxonomy | Bloom (1956) | Cognitive level per module (L2 → L4) |

---

## License

This project is developed for academic research purposes as part of an MSc dissertation. Not for commercial use.
