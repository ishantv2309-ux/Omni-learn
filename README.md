# OmniLearn — All-in-One Student Learning Hub

OmniLearn is a unified, single-search educational engine designed to eliminate tab-switching and fragmented web research for students. Searching for any academic topic dynamically aggregates and displays concept summaries, difficulty levels, handwritten study notes, curated YouTube tutorials, web resources, previous year exam questions (PYQs), and AI-generated learning roadmaps.

## Architecture

This project is built using:
- **Backend API**: FastAPI (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **Object Storage**: Local file uploads with OCR text indexing
- **Frontend Dashboard**: Responsive single-page application using Tailwind CSS and Chart.js

---

## Getting Started

### 1. Prerequisites
- **Python 3.14+** (already installed on this machine)

### 2. Set Up Virtual Environment & Dependencies
In the project directory, run:
```bash
# Set up virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
We have created a database seeder script to populate default notes and PYQs.
```bash
python3 -m backend.seed
```
This generates the SQLite database `omnilearn.db` and copies sample notes to `./storage/notes/`.

### 4. Running the Application
To run the server locally:
```bash
python3 main.py
```
Open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

---

## Environment Configuration

To use real external APIs (Gemini, YouTube Search, Google Custom Search), copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in the following credentials:
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/) for summarization and PDF OCR extraction.
- `YOUTUBE_API_KEY`: YouTube Data API v3 key from Google Cloud Console.
- `GOOGLE_SEARCH_CX` & `GOOGLE_SEARCH_KEY`: Google Custom Search Engine ID and API key.

### Mock Mode Fallback
If any of these API keys are missing, OmniLearn **automatically falls back to Mock Mode** for that service, serving realistic academic summaries, curated videos, and search outcomes. This ensures the app is fully functional right away without configuring API accounts.

---

## Verification & Testing

To run automated unit tests:
```bash
python3 -m pytest tests/test_app.py
```
