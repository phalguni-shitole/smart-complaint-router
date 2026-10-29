# Smart Complaint Router

An AI-powered civic complaint management system that classifies citizens' complaints into relevant departments and identifies potentially similar complaints.

## Overview

Smart Complaint Router helps organize civic complaints such as potholes, water supply problems, electricity issues, garbage collection, and broken streetlights.

The system uses Natural Language Processing (NLP) and machine learning to predict a complaint category. It also compares new complaints with recent submissions to flag possible duplicates.

**Project status:** In Development

## Problem Statement

Civic complaints may be submitted using different words even when they describe similar problems. Manually sorting complaints can take time and may lead to inconsistent categorization.

Smart Complaint Router aims to make complaint classification more consistent and highlight potentially repeated complaints for further review.

## Key Features

- **Automatic complaint classification:** Predicts one of five categories.
- **Uncertainty handling:** Returns `Uncertain` when the model does not have sufficient confidence.
- **Duplicate detection:** Uses text similarity to flag potentially similar recent complaints.
- **Complaint submission:** Stores submitted complaints in Supabase when the backend and database are configured correctly.
- **API documentation:** FastAPI provides interactive API documentation for testing endpoints.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Text classification | scikit-learn, TF-IDF, Logistic Regression |
| Duplicate detection | TF-IDF, cosine similarity |
| Database | Supabase PostgreSQL |
| Development tools | VS Code, Google Antigravity, Git |

## How It Works

1. A user enters a civic complaint in the frontend.
2. The frontend sends the complaint to the FastAPI backend.
3. The classifier processes the text using TF-IDF features and Logistic Regression.
4. The system predicts a department category or returns `Uncertain`.
5. The backend compares the complaint with recent complaint descriptions to estimate text similarity.
6. A possible duplicate is flagged when the similarity score meets the configured threshold.
7. The complaint is submitted to Supabase, and the frontend can display a warning if a possible duplicate was detected.

**Important:** A similarity warning does not prove that two complaints describe the same real-world incident.

## Complaint Categories

The current classifier supports:

- Roads
- Water Supply
- Electricity
- Garbage
- Streetlights

## Machine Learning Evaluation

The project currently uses a curated dataset of **125 complaint examples**, with 25 examples per category.

The classifier was evaluated using five-fold stratified cross-validation.

| Evaluation metric | Current result |
|---|---:|
| Mean cross-validation accuracy | 88.8% |
| Standard deviation | ±3.35 percentage points |
| Pooled cross-validation accuracy | 88.8% |

These results describe performance on the current curated dataset. They do not guarantee the same accuracy on real-world complaints. The dataset is small and requires broader, more representative testing.

## Duplicate Detection

The duplicate detector uses TF-IDF text vectors and cosine similarity to estimate how closely a new complaint resembles existing complaints.

- Default similarity threshold: `0.65`
- The backend checks up to the 50 most recent complaint descriptions.
- A complaint can still be recorded even when a possible duplicate is flagged.

The current comparison is based on text, not verified incident identity. Location, date, time, and other contextual details could improve duplicate detection in a future version.

## Project Structure

```text
smart-complaint-router/
├── README.md
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       └── submit/
│   ├── package.json
│   └── ...
└── backend/
    ├── main.py
    ├── classifier.py
    ├── duplicate_detector.py
    ├── evaluate.py
    ├── test_duplicate_detector.py
    ├── requirements.txt
    ├── .gitignore
    └── data/
        └── complaints.csv
```

Local environment files and generated folders are intentionally omitted from this overview.

## Run Locally

### Prerequisites

- Python installed
- Node.js and npm installed
- A configured Supabase project
- The required Supabase environment variables

### 1. Start the backend

Open a terminal in the `backend` directory.

Activate the existing virtual environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

Ensure the local `backend/.env` file contains your own Supabase credentials:

```text
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
```

Replace the example values locally. **Never publish your real credentials or commit your `.env` file.**

Start the backend:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Useful backend URLs:

- Health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

### 2. Start the frontend

Open a second terminal in the `frontend` directory:

```powershell
npm install
npm run dev
```

Open the complaint submission page:

http://localhost:3000/submit

The frontend must be configured to call the running backend. Database-backed submission also requires a correctly configured Supabase project and the expected database schema.

## Current Limitations

- The training dataset is small and curated.
- Classification performance has not been established on a large real-world dataset.
- Duplicate detection relies on text similarity and checks only recent submissions.
- Similarity does not establish that complaints refer to the same incident.
- Full live database integration and production deployment still require verification.
- Production deployment requires the frontend to use the deployed backend URL and the backend to have correctly configured environment variables and CORS settings.

## Future Improvements

- Expand and validate the training dataset with more representative complaint examples.
- Improve duplicate detection using location and incident timing.
- Test the model on unseen, real-world complaints.
- Add more categories and support for additional languages.
- Deploy the frontend and backend and verify the complete application end to end.

## Project Goal

The goal is to develop a practical AI/ML portfolio project that demonstrates text classification, similarity detection, API development, database integration, and responsible handling of uncertain predictions.
