
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

import os
from dotenv import load_dotenv
from supabase import create_client
from postgrest.exceptions import APIError
from classifier import predict_category
from duplicate_detector import find_duplicate_complaint

# Load environment variables from backend/.env
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise RuntimeError(
        "Missing SUPABASE_URL or SUPABASE_KEY in the backend .env file."
    )

# Connect to Supabase
supabase = create_client(supabase_url, supabase_key)

# Safe diagnostic information; never print the key
print("Supabase URL loaded:", supabase_url)
print(
    "Supabase key type:",
    "publishable"
    if supabase_key.startswith("sb_publishable_")
    else "other"
)

app = FastAPI(title="Smart Complaint Router API")


class Complaint(BaseModel):
    description: str
    category: Optional[str] = None
    location: str


# Allow the local Next.js frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Smart Complaint Router backend is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/complaints")
def submit_complaint(complaint: Complaint):
    # 1. Automatically determine the category using the ML classifier
    predicted_category = predict_category(complaint.description)

    # 2. Query recent existing complaints to check for duplicates before inserting
    try:
        recent_query = (
            supabase.table("complaints")
            .select("description")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
    except APIError as query_error:
        print("Supabase error querying candidate duplicates:", query_error.message)
        print("Supabase error code:", query_error.code)
        print("Supabase error details:", query_error.details)
        print("Supabase error hint:", query_error.hint)

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to check for duplicate complaints due to a database error.",
                "code": query_error.code,
                "details": query_error.details,
                "hint": query_error.hint,
            },
        )
    except Exception as query_exc:
        print("Unexpected error querying candidate duplicates:", str(query_exc))
        raise HTTPException(
            status_code=500,
            detail="Failed to check for duplicate complaints due to an unexpected error.",
        )

    # Extract descriptions safely from candidate query
    candidate_records = recent_query.data if recent_query.data is not None else []
    existing_descriptions = [
        row["description"]
        for row in candidate_records
        if isinstance(row, dict) and row.get("description")
    ]

    # 3. Evaluate duplicate similarity (default threshold = 0.65)
    duplicate_result = find_duplicate_complaint(
        complaint.description,
        existing_descriptions,
    )

    # 4. Insert the new complaint into Supabase (never reject or merge)
    try:
        result = (
            supabase.table("complaints")
            .insert({
                "description": complaint.description,
                "category": predicted_category,
                "location": complaint.location,
                "status": "Pending",
            })
            .execute()
        )

        # Confirm that Supabase returned the saved row
        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Supabase returned no saved complaint."
            )

        return {
            "message": "Complaint saved successfully!",
            "predicted_category": predicted_category,
            "duplicate_detection": {
                "is_duplicate": duplicate_result["is_duplicate"],
                "similarity_score": duplicate_result["similarity_score"],
            },
            "complaint": result.data[0],
        }

    except APIError as error:
        # Print diagnostic details in the backend terminal
        print("Supabase error:", error.message)
        print("Supabase error code:", error.code)
        print("Supabase error details:", error.details)
        print("Supabase error hint:", error.hint)

        raise HTTPException(
            status_code=500,
            detail={
                "message": error.message,
                "code": error.code,
                "details": error.details,
                "hint": error.hint,
            },
        )
