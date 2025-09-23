# 🏀 Swish Report

Swish Report is a full-stack web app for **basketball player analysis** across **High School, College, and NBA** levels. It aggregates data, generates AI scouting reports, and lets users build/comparing lineups—wrapped in a modern, scalable stack.

---

# Tech Stack

- **Frontend:** React + Next.js (TypeScript)
- **Backend:** Python + FastAPI
  - Playwright (web scraping)
  - OpenAI + Gemini (LLM integrations)
  - OpenCV (generating highlight reels and basketball player scouting videos)
- **Database:** MySQL (relational modeling)
- **Infrastructure:** Docker (containerization)

---

# Features

- **AI scouting reports** for players at HS/College/NBA (OpenAI & Gemini powered)
- **AI generated highlight reels** for players at every level of basketball (OpenCV & Gemini powered)
- **Player pages:** Scouting reports, player related content and highlight reels, and forums to discuss player skillset and potential
- **Auth:** Email/password + Google OAuth signup and login
- **Lineup builder game** with interactive team composition and lineup analysis
- **Community:** Compare lineups, post takes/hot-takes, discuss player scouting analysis

---

# Roadmap (Future Development)

- Expand scraping coverage for **college players** and **international players**
- Deeper **personalization** and richer **community features** (follows, votes, badges)
- More **interactive games** (salary cap drafts, scenario simulators, p)
- Deploy backend and database for the application on a cloud service like **AWS**, **GCP**, or **Azure**

---

# Architecture

- **Next.js (app or pages router)** serves the UI + API proxy where needed
- **FastAPI** exposes REST endpoints for player search, reports, lineups, and community
- **MySQL** stores player master data and metadata, evaluations, sources, users, and community content
- **Playwright** scrapers feed normalized data into MySQL via ETL jobs
- **LLM layer** (OpenAI/Gemini) summarizes scouting text and produces structured insights
- **Docker** standardizes local/dev/prod environments

