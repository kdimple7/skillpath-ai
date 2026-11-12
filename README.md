# SkillPath AI

**Discover Your Skills. Unlock Your Potential.**

A responsive Python → AI/ML learning-path MVP. It includes an interactive landing page, four-step onboarding, topic confidence survey, adaptive 15-question assessment, evidence-based report, a practical challenge prompt, roadmap milestones, and progress history.

## Run the demo

Open `index.html` in a modern browser. The frontend has no build step and stores demo profile, assessment answers, and roadmap completion in that browser's local storage. “Reset demo data” clears it. The landing preview is explicitly labeled as an example; the authenticated-style dashboard only displays scores after a completed assessment.

## Publish the demo with GitHub Pages

This repository includes `.github/workflows/pages.yml`. Push the project to a GitHub repository using the `main` branch, then:

1. Open the repository’s **Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. Open **Actions** and allow the Pages workflow if GitHub asks.
4. Wait for **Deploy SkillPath AI demo to GitHub Pages** to finish. The workflow summary shows the published address, usually `https://YOUR-USERNAME.github.io/REPOSITORY-NAME/`.

Later pushes to `main` redeploy the static frontend. GitHub Pages only hosts the browser demo; it does not run the FastAPI backend. Demo data stays in each visitor’s browser and is not shared between devices.

## Run the API

Python 3.10+ is recommended.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The development API defaults to a local SQLite file. Set `DATABASE_URL` for PostgreSQL. Interactive API docs are available at `/docs`. Send `X-User-Id` with API requests for local multi-user ownership partitioning. This header is a development convenience, **not authentication**. Before deployment, replace it with a verified Supabase Auth/JWT subject, enable database row-level security, add rate limiting, audit logging, migrations, backups, and HTTPS. Never expose service keys in the browser.

## What is functional

- Assessment answer correctness, topic aggregation, and scores are deterministic.
- The browser assessment saves after every response and never repeats a question in one attempt.
- Confidence ratings remain separate from technical scores.
- Topic estimates show “Not enough evidence” when unanswered.
- Roadmap progress is persisted locally in the frontend.
- API profile, assessment, answer, completion, progress, and milestone endpoints persist records in SQLite/PostgreSQL.

## MVP boundaries

- Browser demo authentication is not configured; use only non-sensitive demo data.
- The API is a starter and is not wired to the static frontend yet.
- The code challenge editor is a prompt and draft review only. It does not execute or score submitted code. A sandboxed judge service is required before practical scores can affect the combined score.
- AI-generated insights are not enabled; reports use deterministic descriptions of observed answers. No API key is required.
- Google sign-in, password recovery, full account management, notifications, and GitHub Proof of Skill are future integrations.
- PostgreSQL production schema is in `backend/schema.sql`; API startup currently uses SQLAlchemy `create_all`, so add Alembic migrations before production.

## Deploying

Serve the static frontend from Vercel or any static host. Deploy the FastAPI service to a managed Python host with a managed PostgreSQL database. Set `DATABASE_URL` and a precise `CORS_ORIGINS` list. Configure auth at the API and enforce user ownership in all queries before making the service public. Never run user-submitted Python in the API process; connect a separately isolated execution service if the challenge is enabled.

## Structure

```text
index.html          Static frontend entry
styles.css          Responsive design system and views
app.js              Demo workflows, question bank, scoring, local progress
backend/main.py     FastAPI development API and deterministic assessment logic
backend/schema.sql  PostgreSQL relational schema
backend/requirements.txt
```

