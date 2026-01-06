from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import requests

from templating import templates

router = APIRouter(prefix="/admin", tags=["admin-etfs"])


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
# ETFs list (HTML)
# -------------------------
@router.get("/etfs")
def etfs_list(request: Request):
    etfs = fetch_json(request, "/admin/api/etfs")

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
    etfs = fetch_json(request, "/admin/api/etfs")
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
    base_url = str(request.base_url).rstrip("/")
    r = requests.delete(f"{base_url}/admin/api/etfs/{etf_id}")

    if r.status_code != 200:
        error_msg = "ETF cannot be deleted"

        try:
            error_msg = r.json().get("detail", error_msg)
        except Exception:
            pass

        etfs = fetch_json(request, "/admin/api/etfs")

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
