from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import requests

from templating import templates

router = APIRouter(prefix="/admin", tags=["admin-purchases"])

API_BASE = "http://127.0.0.1:8000/admin/api"


@router.get("/__ping")
def ping():
    return {"ok": True}


def fetch_json(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"API error {r.status_code}: {r.text}"
        )
    return r.json()


# -------------------------
# Purchases list (HTML)
# -------------------------
@router.get("/purchases")
def purchases_list(request: Request):
    purchases = fetch_json(f"{API_BASE}/purchases")
    etfs = fetch_json(f"{API_BASE}/etfs")

    etf_map = {e["id"]: e["ticker"] for e in etfs}

    return templates.TemplateResponse(
        "admin/purchases.html",
        {
            "request": request,
            "purchases": purchases,
            "etf_map": etf_map,
        },
    )


# -------------------------
# New purchase form
# -------------------------
@router.get("/purchases/new")
def new_purchase_form(request: Request):
    etfs = fetch_json(f"{API_BASE}/etfs")

    return templates.TemplateResponse(
        "admin/purchase_form.html",
        {
            "request": request,
            "etfs": etfs,
            "purchase": None,
            "action": "/admin/api/purchases",
            "method": "post",
        },
    )


# -------------------------
# Edit purchase form
# -------------------------
@router.get("/purchases/{purchase_id}/edit")
def edit_purchase_form(purchase_id: int, request: Request):
    purchase = fetch_json(f"{API_BASE}/purchases/{purchase_id}")
    etfs = fetch_json(f"{API_BASE}/etfs")

    return templates.TemplateResponse(
        "admin/purchase_form.html",
        {
            "request": request,
            "etfs": etfs,
            "purchase": purchase,
            "action": f"/admin/api/purchases/{purchase_id}",
            "method": "put",
        },
    )


# -------------------------
# Delete purchase (POST)
# -------------------------
@router.post("/purchases/{purchase_id}/delete")
def delete_purchase_post(purchase_id: int):
    r = requests.delete(f"{API_BASE}/purchases/{purchase_id}")

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)

    return RedirectResponse("/admin/purchases", status_code=303)


# -------------------------
# Delete purchase (GET fallback – admin UI)
# -------------------------
@router.get("/purchases/{purchase_id}/delete")
def delete_purchase_get(purchase_id: int):
    r = requests.delete(f"{API_BASE}/purchases/{purchase_id}")

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)

    return RedirectResponse("/admin/purchases", status_code=303)
