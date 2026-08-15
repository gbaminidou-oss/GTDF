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
| Database Host | Neon (PostgreSQL serverless) |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Auth | Flask-Login 0.6.3, Werkzeug PBKDF2 |
| Templating | Jinja2 (HTML5) |
| Styling | CSS3, custom properties, Flexbox/Grid |
| Frontend | Vanilla JavaScript (ES6) |
| Charts | Chart.js 4.4.2 (CDN) |
| Icons | Font Awesome 6.5.0 (CDN) |
| Hosting | Render / Netlify |

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

## Cloud Deployment

### Option 1: Render + Neon (Recommended)

#### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/GTDF.git
git push -u origin main
```

#### Step 2: Create a Neon Database

1. Go to [neon.tech](https://neon.tech) and sign up (free tier available)
2. Click **Create Project**
3. Configure:
   - **Project name:** `GTDF`
   - **Region:** closest to your users
   - **Postgres version:** 16 (or latest)
4. Click **Create Project**
5. Copy the **Connection String** (looks like `postgresql://user:password@ep-...neon.tech/gtdf?sslmode=require`)
   - Keep this safe — you'll need it for both Render and local testing

#### Step 3: Create a Web Service on Render

1. Go to [render.com](https://render.com) and sign up
2. Click **New → Web Service**
3. Select **Public Git Repository** and paste your GitHub repo URL
4. Configure:
   - **Name:** `gtdf-platform`
   - **Environment:** `Python 3`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn run:app`
5. Click **Create Web Service**

#### Step 4: Set Environment Variables on Render

1. In the Render dashboard, go to your web service
2. Click **Environment** in the left sidebar
3. Add these variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Your Neon connection string from Step 2 |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate a random string: `python -c "import secrets; print(secrets.token_hex(32))"` |

4. Click **Save**
5. The app will automatically redeploy and be live in 2-3 minutes

**Deployed URL:** `https://gtdf-platform.onrender.com`

> **Note:** Render's free tier spins down after 15 minutes of inactivity. The first request after idle takes ~30 seconds. Upgrade to Starter plan ($7/month) to keep it always running.

---

### Option 2: Netlify + Neon (For Static Frontends + Serverless)

Netlify is best suited for static frontends or JAMstack architectures. If you have a separate React/Vue frontend and want to host it on Netlify, follow this approach:

#### Step 1: Set Up Neon Database (same as above)

Follow **Steps 1-2** from Option 1 to create your Neon database.

#### Step 2: Deploy Backend Separately

Since Netlify isn't ideal for long-running Flask apps, deploy the Flask backend to Render (Steps 2-4 above) or another Python-friendly service like:
- [Railway.app](https://railway.app) — simple Flask deployment
- [Fly.io](https://fly.io) — global deployment
- [Heroku](https://heroku.com) — with paid dyno

#### Step 3: Deploy Frontend to Netlify (Optional)

If you have a separate static frontend (React, Vue, Next.js, etc.):

1. Push your frontend code to GitHub
2. Go to [netlify.com](https://netlify.com) → **New site from Git**
3. Select your GitHub repo
4. Configure:
   - **Build command:** `npm run build` (or your framework's command)
   - **Publish directory:** `dist` (or `build` for React)
5. Click **Deploy site**
6. In **Site Settings → Environment**, add:
   - `REACT_APP_API_URL` = your Render backend URL (e.g., `https://gtdf-platform.onrender.com`)
7. Update your frontend code to use this environment variable

```javascript
// Example: fetch to backend
const API_URL = process.env.REACT_APP_API_URL;
fetch(`${API_URL}/api/scenarios`, { /* ... */ })
```

---

### Option 3: Netlify Functions (Advanced)

If you want the entire app on Netlify, convert Flask routes to Netlify Functions:

```python
# netlify/functions/app.py
import json
from flask import Flask, request

app = Flask(__name__)

def handler(event, context):
    with app.test_client() as client:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Hello from Netlify'})
        }
```

This requires significant refactoring and isn't recommended for a full Flask app. Use **Option 1** instead.

---

## Environment Variables

| Variable | Required | Description | Example |
|---|---|---|---|
| `DATABASE_URL` | Production only | PostgreSQL connection string | `postgresql://user:pass@ep-....neon.tech/gtdf?sslmode=require` |
| `FLASK_ENV` | Recommended | Set to `production` in deployed environments | `production` |
| `SECRET_KEY` | Recommended | Flask session signing key (32+ chars, must be random) | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |

**In development:** Neither variable is needed — the app defaults to SQLite and a built-in dev secret key.

**To test production database locally:**

```bash
export DATABASE_URL="your-neon-connection-string"
python run.py
```

---

## Setting Up Neon Database Locally

If you want to use Neon for local development:

1. Copy your Neon connection string from the Neon dashboard
2. In your terminal, set the environment variable:

```bash
# Windows (PowerShell)
$env:DATABASE_URL = "postgresql://user:pass@ep-....neon.tech/gtdf?sslmode=require"

# Mac/Linux
export DATABASE_URL="postgresql://user:pass@ep-....neon.tech/gtdf?sslmode=require"
```

3. Run the app:

```bash
python run.py
```

The database will initialize and seed automatically on first run.

**Resetting Neon Database (if needed):**

To wipe all data and re-seed (be careful — this deletes production data):

```python
from app import create_app, db
from app.database.seed import seed_all

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    seed_all()
```

> **Warning:** Use this only in development. For production, manage migrations separately.

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
