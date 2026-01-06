from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import requests

from templating import templates

router = APIRouter(prefix="/admin", tags=["admin-etfs"])

API_BASE = "/admin/api"


def fetch_json(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"API error {r.status_code}: {r.text}"
        )
    return r.json()


# -------------------------
# ETFs list (HTML)
# -------------------------
@router.get("/etfs")
def etfs_list(request: Request):
    etfs = fetch_json(f"{API_BASE}/etfs")

    return templates.TemplateResponse(
        "admin/etfs.html",
        {
            "request": request,
            "etfs": etfs,
            "error": None,
        },
    )


# -------------------------
# New ETF form
# -------------------------
@router.get("/etfs/new")
def new_etf_form(request: Request):
    return templates.TemplateResponse(
        "admin/etf_form.html",
        {
            "request": request,
            "etf": None,
            "action": "/admin/api/etfs",
        },
    )


# -------------------------
# Edit ETF form
# -------------------------
@router.get("/etfs/{etf_id}/edit")
def edit_etf_form(etf_id: int, request: Request):
    etfs = fetch_json(f"{API_BASE}/etfs")
    etf = next((e for e in etfs if e["id"] == etf_id), None)

    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")

    return templates.TemplateResponse(
        "admin/etf_form.html",
        {
            "request": request,
            "etf": etf,
            "action": f"/admin/api/etfs/{etf_id}",
        },
    )


# -------------------------
# Delete ETF (POST wrapper)
# -------------------------
@router.post("/etfs/{etf_id}/delete")
def delete_etf(etf_id: int, request: Request):
    r = requests.delete(f"{API_BASE}/etfs/{etf_id}")

    if r.status_code != 200:
        error_msg = "ETF cannot be deleted"

        try:
            error_msg = r.json().get("detail", error_msg)
        except Exception:
            pass

        etfs = fetch_json(f"{API_BASE}/etfs")

        return templates.TemplateResponse(
            "admin/etfs.html",
            {
                "request": request,
                "etfs": etfs,
                "error": error_msg,
            },
            status_code=400,
        )

    return RedirectResponse("/admin/etfs", status_code=303)
