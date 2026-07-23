import os
import httpx
import streamlit as st
from typing import Any

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _get_headers() -> dict:
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE_URL, timeout=30.0, headers=_get_headers())


def get_health() -> dict:
    with _get_client() as client:
        response = client.get("/health")
        return response.json()


# --- Auth ---

def login(email: str, password: str) -> dict:
    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        response = client.post("/api/auth/login", json={"email": email, "password": password})
        if response.status_code == 401:
            raise Exception("Invalid email or password")
        response.raise_for_status()
        return response.json()


def signup(email: str, password: str, full_name: str) -> dict:
    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        response = client.post("/api/auth/signup", json={"email": email, "password": password, "full_name": full_name})
        response.raise_for_status()
        return response.json()


def refresh_token() -> dict | None:
    refresh = st.session_state.get("refresh_token")
    if not refresh:
        return None
    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        response = client.post("/api/auth/refresh", json={"refresh_token": refresh})
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.refresh_token = data["refresh_token"]
            st.session_state.user = data["user"]
            return data
    return None


def get_me() -> dict | None:
    try:
        with _get_client() as client:
            response = client.get("/api/auth/me")
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None


# --- Leads ---

def list_leads(
    status: str | None = None,
    campaign_id: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    params = {"page": page, "page_size": page_size}
    if status:
        params["status"] = status
    if campaign_id:
        params["campaign_id"] = campaign_id
    if search:
        params["search"] = search
    with _get_client() as client:
        response = client.get("/api/leads", params=params)
        return response.json()


def get_lead(lead_id: str) -> dict:
    with _get_client() as client:
        response = client.get(f"/api/leads/{lead_id}")
        return response.json()


def create_lead(name: str, phone: str, language: str = "urdu") -> dict:
    payload = {"name": name, "phone": phone, "language": language}
    with _get_client() as client:
        response = client.post("/api/leads", json=payload)
        return response.json()


def bulk_upload_leads(file_bytes: bytes, filename: str, campaign_id: str | None = None) -> dict:
    with _get_client() as client:
        files = {"file": (filename, file_bytes, "text/csv")}
        params = {}
        if campaign_id:
            params["campaign_id"] = campaign_id
        response = client.post("/api/leads/bulk-upload", files=files, params=params)
        return response.json()


def update_lead(lead_id: str, data: dict) -> dict:
    with _get_client() as client:
        response = client.patch(f"/api/leads/{lead_id}", json=data)
        return response.json()


def delete_lead(lead_id: str) -> bool:
    with _get_client() as client:
        response = client.delete(f"/api/leads/{lead_id}")
        return response.status_code == 204


# --- Campaigns ---

def list_campaigns(status: str | None = None, page: int = 1, page_size: int = 50) -> dict:
    params = {"page": page, "page_size": page_size}
    if status:
        params["status"] = status
    with _get_client() as client:
        response = client.get("/api/campaigns", params=params)
        return response.json()


def get_campaign(campaign_id: str) -> dict:
    with _get_client() as client:
        response = client.get(f"/api/campaigns/{campaign_id}")
        return response.json()


def create_campaign(
    name: str, script_template: str, greeting: str | None = None, closing: str | None = None
) -> dict:
    payload = {
        "name": name,
        "script_template": script_template,
        "greeting_message": greeting,
        "closing_message": closing,
    }
    with _get_client() as client:
        response = client.post("/api/campaigns", json=payload)
        return response.json()


def update_campaign(campaign_id: str, data: dict) -> dict:
    with _get_client() as client:
        response = client.patch(f"/api/campaigns/{campaign_id}", json=data)
        return response.json()


def start_campaign(campaign_id: str) -> dict:
    with _get_client() as client:
        response = client.post(f"/api/campaigns/{campaign_id}/start")
        return response.json()


def pause_campaign(campaign_id: str) -> dict:
    with _get_client() as client:
        response = client.post(f"/api/campaigns/{campaign_id}/pause")
        return response.json()


def delete_campaign(campaign_id: str) -> bool:
    with _get_client() as client:
        response = client.delete(f"/api/campaigns/{campaign_id}")
        return response.status_code == 204


# --- Calls ---

def initiate_call(lead_id: str, campaign_id: str | None = None) -> dict:
    params = {"lead_id": lead_id}
    if campaign_id:
        params["campaign_id"] = campaign_id
    with _get_client() as client:
        response = client.post("/api/calls/initiate", params=params)
        return response.json()


def get_call_history(
    lead_id: str | None = None,
    campaign_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    params = {"page": page, "page_size": page_size}
    if lead_id:
        params["lead_id"] = lead_id
    if campaign_id:
        params["campaign_id"] = campaign_id
    if status:
        params["status"] = status
    with _get_client() as client:
        response = client.get("/api/calls/history", params=params)
        return response.json()


# --- Analytics ---

def get_dashboard(days: int = 7) -> dict:
    with _get_client() as client:
        response = client.get("/api/analytics/dashboard", params={"days": days})
        return response.json()


def get_campaign_analytics() -> dict:
    with _get_client() as client:
        response = client.get("/api/analytics/campaigns")
        return response.json()
