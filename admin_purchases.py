from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import requests

from templating import templates

router = APIRouter(prefix="/admin", tags=["admin-purchases"])


@router.get("/__ping")
def ping():
    return {"ok": True}


def fetch_json(request: Request, path: str):
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}{path}"

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
    purchases = fetch_json(request, "/admin/api/purchases")
    etfs = fetch_json(request, "/admin/api/etfs")

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
    etfs = fetch_json(request, "/admin/api/etfs")

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
    purchase = fetch_json(request, f"/admin/api/purchases/{purchase_id}")
    etfs = fetch_json(request, "/admin/api/etfs")

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
def delete_purchase_post(purchase_id: int, request: Request):
    base_url = str(request.base_url).rstrip("/")
    r = requests.delete(f"{base_url}/admin/api/purchases/{purchase_id}")

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)

    return RedirectResponse("/admin/purchases", status_code=303)


# -------------------------
# Delete purchase (GET fallback – admin UI)
# -------------------------
@router.get("/purchases/{purchase_id}/delete")
def delete_purchase_get(purchase_id: int, request: Request):
    base_url = str(request.base_url).rstrip("/")
    r = requests.delete(f"{base_url}/admin/api/purchases/{purchase_id}")

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)

    return RedirectResponse("/admin/purchases", status_code=303)
