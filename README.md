# TalentIQ — AI-Powered Recruitment Intelligence

TalentIQ is an enterprise-style AI/ML recruitment and resume screening platform.
It automates resume intake, text extraction, NLP preprocessing, TF-IDF + TruncatedSVD
feature representation, cosine-similarity match scoring, job-category classification,
applicant ranking, full lifecycle application tracking with an audit trail, recruitment
analytics, an AI recruitment assistant ("Talia"), and a CLI demonstration tool.

The product identity ("TalentIQ: AI-Powered Recruitment Intelligence") is original and
contains no government or third-party imagery or claims.

---

## Architecture

```
React + TypeScript (Vite, Tailwind)  ──REST/JSON, JWT──▶  Flask API (blueprints)
                                                              │
                                             ┌────────────────┴────────────────┐
                                             ▼                                 ▼
                                  ML Engine (TF-IDF + SVD +           SQLAlchemy ORM
                                  cosine similarity + LogReg)          (MySQL / SQLite)
```

- **Backend**: Flask, SQLAlchemy (MySQL via PyMySQL, with automatic SQLite fallback),
  Flask-JWT-Extended, scikit-learn, PyMuPDF/pypdf, ReportLab.
- **Frontend**: Vite + React + TypeScript + Tailwind CSS, Recharts, lucide-react.
- **ML pipeline**: text cleaning → TF-IDF (unigrams+bigrams) → TruncatedSVD → L2
  normalization → cosine similarity, blended with rule-based skill/experience/education
  sub-scores into a single overall match percentage. A Logistic Regression model
  (trained on synthetic labeled data) predicts job category, with a keyword-based
  fallback ("Demo ML mode") so the app never crashes if models haven't been trained yet.

---

## Quick start

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

cp ../.env.example .env     # edit as needed; MySQL vars optional — SQLite fallback is automatic

# (Optional but recommended) train the classifier + persist vectorizer/SVD:
python -m ml.train_models

# Run the API (auto-creates schema + seeds demo data on first run):
python app.py
```

The API starts on **http://localhost:5000**. On first boot, if the database is empty,
it is automatically seeded with:
- 3 demo accounts: `admin@talentiq.ai` / `recruiter@talentiq.ai` / `candidate@talentiq.ai`
  (all password `Admin@123` / `Recruiter@123` / `Candidate@123` respectively)
- 10 job positions, 25 candidates (with generated PDF resumes), 40 applications with
  full audit history.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens on **http://localhost:5173**, proxying `/api` to the backend on port 5000.

### 3. Database flexibility

Set `DB_ENGINE=mysql` in `.env` with `MYSQL_HOST/USER/PASSWORD/DATABASE` to use MySQL.
If those credentials are missing or MySQL is unreachable at boot, TalentIQ automatically
falls back to a local SQLite file (`backend/talentiq.db`) — zero configuration required.

### 4. ML pipeline fallback

If `ml/train_models.py` has never been run, the scoring/classification pipeline operates
in **Demo ML mode**: it fits TF-IDF + SVD on-the-fly per request and uses a keyword-voting
classifier. Once trained models are present in `ml/saved_models/`, the pipeline
automatically switches to using them for consistent, faster scoring.

---

## CLI demonstration tool

```bash
cd backend
python cli/resume_demo.py --email candidate@talentiq.ai --resume /path/to/resume.pdf
```

Prints the 6-step pipeline progress, predicted job category, and a ranked table of
match scores against every open position.

---

## Running tests

```bash
cd backend
python -m unittest discover tests
```

Covers ML scoring bounds, the classifier, PDF-parsing error handling, auth, the full
position → application → status-update → audit-history flow, and chatbot fallback.

```bash
cd frontend
npm run build   # verifies zero TypeScript errors and a clean production bundle
```

---

## Deploying a live demo link (Render + Vercel)

Vercel alone can't host this app — it runs serverless functions, and this backend is a
stateful Flask + SQLAlchemy + ML service that needs a persistent process. The working
split is: **backend on Render, frontend on Vercel**, connected via a rewrite so it all
looks like one URL to your team.

### 1. Push this folder to a GitHub repo
Create a new repo and push the contents of this project (unzip it first, `git init`,
`git add .`, `git commit`, push to `origin`).

### 2. Backend → Render.com
1. Go to [render.com](https://render.com) → **New → Blueprint** → connect your repo.
2. Render will detect `render.yaml` at the repo root and configure the service
   automatically (installs requirements, trains the ML models, starts gunicorn).
3. Click **Apply** and wait for the first deploy (~2–3 min). Copy the resulting URL,
   e.g. `https://talentiq-backend.onrender.com`.
4. Visit `https://talentiq-backend.onrender.com/api/health` to confirm it's live —
   it should return `{"status": "ok", ...}`. First boot auto-seeds demo data.

> Free-tier note: Render's free web services spin down after inactivity and use an
> ephemeral disk, so the SQLite demo data resets after a period of idleness or a
> redeploy. That's fine for a live walkthrough; for anything longer-lived, add a
> paid persistent disk or switch `DB_ENGINE` to a managed MySQL/Postgres instance.

### 3. Frontend → Vercel
1. Edit `frontend/vercel.json` and replace `YOUR-RENDER-BACKEND-URL` with the Render
   URL from step 2.
2. Go to [vercel.com](https://vercel.com) → **Add New → Project** → import the same repo,
   set **Root Directory** to `frontend`.
3. Vercel auto-detects the Vite build (`npm run build`, output `dist`) from `vercel.json`.
   Click **Deploy**.
4. You'll get a URL like `https://talentiq.vercel.app` — that's the link to share with
   your team. The `/api/*` rewrite forwards requests to your Render backend, so there's
   no CORS setup needed and everything behaves as one app.

### 4. Sanity check
Open the Vercel URL, click a demo account button on the login screen (Admin / HR /
Candidate) — if the dashboard loads with data, you're good to share the link.

---

## Project layout

```
talentiq/
├── backend/
│   ├── app.py                 Flask application factory
│   ├── config.py              MySQL→SQLite fallback config
│   ├── models/                SQLAlchemy models (User, CandidateProfile, JobPosition,
│   │                          Application, ApplicationHistory)
│   ├── ml/                     preprocessing, vectorizer (TF-IDF+SVD), similarity
│   │                          (cosine scoring), classifier, pipeline, train_models
│   ├── utils/                  pdf_parser, auth (JWT + role_required)
│   ├── services/                resume_service, ranking_service, chatbot_service
│   │                            ("Talia"), report_service (PDF/CSV via ReportLab)
│   ├── routes/                  auth, candidates, positions, applications, screening,
│   │                            analytics, chatbot, reports
│   ├── database/                seed.py (synthetic data + generated PDF resumes)
│   ├── cli/resume_demo.py       terminal demonstration tool
│   └── tests/                   automated test suite
├── frontend/
│   └── src/
│       ├── pages/                13 pages (Landing, Login/Register, Dashboard,
│       │                        Candidates(+Profile), Screening, Positions(+Detail),
│       │                        Applications, Analytics, AiAssistant, Reports,
│       │                        UserManagement, Settings)
│       ├── components/           Sidebar, Header, ui primitives (Card, ScoreBar,
│       │                        MatchGauge, StatusBadge, SkillChip, KPICard)
│       ├── layouts/MainLayout.tsx
│       ├── context/AuthContext.tsx
│       └── api/client.ts         axios instance with JWT interceptor
├── database/
│   ├── schema.sql               reference MySQL DDL
│   └── sample_data/resumes/     generated sample PDF resumes (created on seed)
├── docker-compose.yml
└── .env.example
```
