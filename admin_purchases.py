from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from templating import templates
from database import SessionLocal
from models import Purchase, ETF

router = APIRouter(prefix="/admin", tags=["admin-purchases"])


@router.get("/__ping")
def ping():
    return {"ok": True}


# =========================================================
# DB helpers (vietoj HTTP į localhost)
# =========================================================
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def get_etfs():
    db = get_db()
    return db.query(ETF).all()


def get_purchases():
    db = get_db()
    return db.query(Purchase).all()


def get_purchase(purchase_id: int):
    db = get_db()
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


def delete_purchase_db(purchase_id: int):
    db = get_db()
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    db.delete(purchase)
    db.commit()


# -------------------------
# Purchases list (HTML)
# -------------------------
@router.get("/purchases")
def purchases_list(request: Request):
    purchases = get_purchases()
    etfs = get_etfs()

    etf_map = {e.id: e.ticker for e in etfs}

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
    etfs = get_etfs()

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
    purchase = get_purchase(purchase_id)
    etfs = get_etfs()

    return templates.TemplateResponse(
        "admin/purchase_form.html",
        {
            "request": request,
            "etfs": etfs,
            "purchase": purchase,
            "action": f"/admin/api/purchases/{purchase_id}",
            "method": "post",
        },
    )


# -------------------------
# Delete purchase (POST)
# -------------------------
@router.post("/purchases/{purchase_id}/delete")
def delete_purchase_post(purchase_id: int):
    delete_purchase_db(purchase_id)
    return RedirectResponse("/admin/purchases", status_code=303)


# -------------------------
# Delete purchase (GET fallback – admin UI)
# -------------------------
@router.get("/purchases/{purchase_id}/delete")
def delete_purchase_get(purchase_id: int):
    delete_purchase_db(purchase_id)
    return RedirectResponse("/admin/purchases", status_code=303)
