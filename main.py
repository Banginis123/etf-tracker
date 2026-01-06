from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# DB
from database import engine, Base

# Routers
from admin_ui import router as admin_router
from admin_alerts import router as admin_alerts_router
from admin_api import router as admin_api_router
from admin_purchases import router as admin_purchases_router
from admin_etfs import router as admin_etfs_router
from admin_portfolio_api import router as admin_portfolio_api_router
from portfolio import router as portfolio_router

# Scheduler
from scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔧 SUKURIAMOS VISOS LENTELĖS (jei jų nėra)
    Base.metadata.create_all(bind=engine)

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(portfolio_router)
app.include_router(admin_router)
app.include_router(admin_alerts_router)
app.include_router(admin_api_router)
app.include_router(admin_purchases_router)
app.include_router(admin_etfs_router)
app.include_router(admin_portfolio_api_router)
