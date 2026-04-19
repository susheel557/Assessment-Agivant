from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os

from backend.agents.document_processor import process_document
from backend.agents.confidence_scorer import score_data
from backend.agents.summary_agent import generate_summary
from fastapi.middleware.cors import CORSMiddleware
# -------------------------
# APP INIT
# -------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory DB (simple for prototype)
DATABASE = []
REQUEST_ID = 1


# -------------------------
# HELPER: STATUS DECISION
# -------------------------
def decide_status(confidence):
    if confidence > 90:
        return "APPROVED"
    elif confidence > 70:
        return "AI_VERIFIED_PENDING_HUMAN"
    else:
        return "ESCALATED"


# -------------------------
# SUBMIT API
# -------------------------
@app.post("/submit")
async def submit_request(
    customer_id: str = Form(...),
    old_name: str = Form(...),
    new_name: str = Form(...),
    file: UploadFile = File(...)
):
    global REQUEST_ID

    # Save file
    file_path = f"storage/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("\n===== FILE DEBUG =====")
    print("File saved at:", file_path)
    print("File exists?", os.path.exists(file_path))
    print("======================\n")

    # -------------------------
    # PROCESS DOCUMENT
    # -------------------------
    extracted = process_document(file_path, old_name, new_name)

    # -------------------------
    # SCORING
    # -------------------------
    score = score_data(old_name, new_name, extracted)
    confidence = score["confidence"]

    # -------------------------
    # STATUS
    # -------------------------
    status = decide_status(confidence)

    # -------------------------
    # LLM SUMMARY
    # -------------------------
    summary = generate_summary(
        confidence,
        old_name,
        new_name
    )

    # -------------------------
    # STORE RESULT
    # -------------------------
    record = {
        "id": REQUEST_ID,
        "customer_id": customer_id,
        "old_name": old_name,
        "new_name": new_name,
        "confidence": confidence,
        "status": status,
        "summary": summary,
        "forgery": extracted.get("forgery", "UNKNOWN")
    }

    DATABASE.append(record)
    REQUEST_ID += 1

    # -------------------------
    # DEBUG OUTPUT
    # -------------------------
    print("\n===== FINAL RESULT =====")
    print("Extracted:", extracted)
    print("Confidence:", confidence)
    print("Status:", status)
    print("Summary:", summary)
    print("========================\n")

    return record


# -------------------------
# GET PENDING
# -------------------------
@app.get("/pending")
def get_pending():
    return [r for r in DATABASE if r["status"] == "AI_VERIFIED_PENDING_HUMAN"]


# -------------------------
# GET PROCESSED
# -------------------------
@app.get("/processed")
def get_processed():
    return [r for r in DATABASE if r["status"] != "AI_VERIFIED_PENDING_HUMAN"]


# -------------------------
# APPROVE
# -------------------------
@app.post("/approve")
def approve(id: int):
    for r in DATABASE:
        if r["id"] == id:
            r["status"] = "APPROVED"
            return {"message": "Approved"}
    return {"error": "Not found"}


# -------------------------
# REJECT
# -------------------------
@app.post("/reject")
def reject(id: int):
    for r in DATABASE:
        if r["id"] == id:
            r["status"] = "REJECTED"
            return {"message": "Rejected"}
    return {"error": "Not found"}