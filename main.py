from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import json
import os
import re
from datetime import datetime, timezone

app = FastAPI(
    title="ALFA X OSINT API",
    description="Authorized OSINT research and cybersecurity training API",
    version="1.0.0"
)

DATA_FILE = "data.json"


# ============================================================
# DATABASE
# ============================================================

def load_database():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# UTILITY
# ============================================================

def timestamp():
    return datetime.now(timezone.utc).isoformat()


def clean(value: str) -> str:
    return value.strip()


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "success": True,
        "name": "ALFA X OSINT API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": timestamp()
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "success": True,
        "status": "healthy",
        "timestamp": timestamp()
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/v1/info")
def api_info():
    return {
        "success": True,
        "api": "ALFA X OSINT API",
        "version": "1.0.0",
        "endpoints": [
            "/v1/phone",
            "/v1/email",
            "/v1/name",
            "/v1/username",
            "/v1/search"
        ]
    }


# ============================================================
# PHONE LOOKUP
# ============================================================

@app.get("/v1/phone")
def phone_lookup(
    phone: str = Query(..., min_length=5, max_length=30)
):
    phone = normalize_phone(phone)

    if not phone:
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number"
        )

    database = load_database()

    results = []

    for record in database:
        record_phone = normalize_phone(
            str(record.get("phone", ""))
        )

        if record_phone == phone:
            results.append(record)

    return {
        "success": True,
        "query_type": "phone",
        "query": phone,
        "count": len(results),
        "results": results,
        "timestamp": timestamp()
    }


# ============================================================
# EMAIL LOOKUP
# ============================================================

@app.get("/v1/email")
def email_lookup(
    email: str = Query(..., min_length=5, max_length=150)
):
    email = clean(email).lower()

    if "@" not in email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address"
        )

    database = load_database()

    results = []

    for record in database:
        record_email = str(
            record.get("email", "")
        ).lower()

        if record_email == email:
            results.append(record)

    return {
        "success": True,
        "query_type": "email",
        "query": email,
        "count": len(results),
        "results": results,
        "timestamp": timestamp()
    }


# ============================================================
# NAME LOOKUP
# ============================================================

@app.get("/v1/name")
def name_lookup(
    name: str = Query(..., min_length=2, max_length=100)
):
    name = clean(name).lower()

    database = load_database()

    results = []

    for record in database:
        record_name = str(
            record.get("name", "")
        ).lower()

        if name in record_name:
            results.append(record)

    return {
        "success": True,
        "query_type": "name",
        "query": name,
        "count": len(results),
        "results": results,
        "timestamp": timestamp()
    }


# ============================================================
# USERNAME LOOKUP
# ============================================================

@app.get("/v1/username")
def username_lookup(
    username: str = Query(..., min_length=2, max_length=100)
):
    username = clean(username).lstrip("@").lower()

    database = load_database()

    results = []

    for record in database:
        record_username = str(
            record.get("username", "")
        ).lstrip("@").lower()

        if record_username == username:
            results.append(record)

    return {
        "success": True,
        "query_type": "username",
        "query": username,
        "count": len(results),
        "results": results,
        "timestamp": timestamp()
    }


# ============================================================
# ALL-IN-ONE SEARCH
# ============================================================

@app.get("/v1/search")
def search(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None
):
    if not any([
        name,
        phone,
        email,
        username
    ]):
        raise HTTPException(
            status_code=400,
            detail="Provide at least one search parameter"
        )

    database = load_database()

    results = []

    normalized_phone = (
        normalize_phone(phone)
        if phone else None
    )

    normalized_email = (
        email.strip().lower()
        if email else None
    )

    normalized_name = (
        name.strip().lower()
        if name else None
    )

    normalized_username = (
        username.strip().lstrip("@").lower()
        if username else None
    )

    for record in database:

        if normalized_name:
            record_name = str(
                record.get("name", "")
            ).lower()

            if normalized_name not in record_name:
                continue

        if normalized_phone:
            record_phone = normalize_phone(
                str(record.get("phone", ""))
            )

            if normalized_phone != record_phone:
                continue

        if normalized_email:
            record_email = str(
                record.get("email", "")
            ).lower()

            if normalized_email != record_email:
                continue

        if normalized_username:
            record_username = str(
                record.get("username", "")
            ).lstrip("@").lower()

            if normalized_username != record_username:
                continue

        results.append(record)

    return {
        "success": True,
        "query_type": "search",
        "count": len(results),
        "results": results,
        "timestamp": timestamp()
    }


# ============================================================
# 404 HANDLER STYLE RESPONSE
# ============================================================

@app.get("/v1/status")
def status():
    database = load_database()

    return {
        "success": True,
        "api": "ALFA X OSINT API",
        "status": "operational",
        "records_available": len(database),
        "timestamp": timestamp()
  }
