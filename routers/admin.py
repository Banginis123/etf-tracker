from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import SessionLocal
from models import ETF, Purchase

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


@router.get("/")
def admin_dashboard(request: Request):
    db = SessionLocal()

    etfs = db.query(ETF).all()
    purchases = db.query(Purchase).all()

    db.close()
    return templates.TemplateResponse(
        "admin/index.html",
        {
            "request": request,
            "etfs": etfs,
            "purchases": purchases
        }
    )


# -------------------------
# NEW PURCHASE
# -------------------------

@router.get("/purchase/new")
def new_purchase_form(request: Request):
    db = SessionLocal()
    etfs = db.query(ETF).all()
    db.close()

    return templates.TemplateResponse(
        "admin/new_purchase.html",
        {"request": request, "etfs": etfs}
    )


@router.post("/purchase/new")
def create_purchase(
    etf_id: int = Form(...),
    units: float = Form(...),
    price: float = Form(...)
):
    db = SessionLocal()

    purchase = Purchase(
        etf_id=etf_id,
        units=units,
        price=price
    )
    db.add(purchase)
    db.commit()

    db.close()
    return RedirectResponse("/admin", status_code=303)


# -------------------------
# EDIT PURCHASE
# -------------------------

@router.get("/purchase/{purchase_id}/edit")
def edit_purchase_form(request: Request, purchase_id: int):
    db = SessionLocal()
    purchase = db.query(Purchase).get(purchase_id)
    db.close()

    return templates.TemplateResponse(
        "admin/edit_purchase.html",
        {
            "request": request,
            "purchase": purchase
        }
    )


@router.post("/purchase/{purchase_id}/edit")
def edit_purchase(
    purchase_id: int,
    units: float = Form(...),
    price: float = Form(...)
):
    db = SessionLocal()

    purchase = db.query(Purchase).get(purchase_id)
    if purchase:
        purchase.units = units
        purchase.price = price
        db.commit()

    db.close()
    return RedirectResponse("/admin", status_code=303)


# -------------------------
# DELETE PURCHASE
# -------------------------

@router.get("/purchase/{purchase_id}/delete")
def delete_purchase(purchase_id: int):
    db = SessionLocal()

    purchase = db.query(Purchase).get(purchase_id)
    if purchase:
        db.delete(purchase)
        db.commit()

    db.close()
    return RedirectResponse("/admin", status_code=303)
