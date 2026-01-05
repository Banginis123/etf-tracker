from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class ETF(Base):
    __tablename__ = "etfs"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, nullable=False, index=True)

    ath_price = Column(Float, nullable=True)
    drop_threshold = Column(Float, default=5.0, nullable=False)
    ath_alert_sent = Column(Boolean, default=False, nullable=False)
    manual_reset_at = Column(DateTime, nullable=True)

    purchases = relationship(
        "Purchase",
        back_populates="etf",
        cascade="all, delete-orphan",
    )

    alerts = relationship(
        "Alert",
        back_populates="etf",
        cascade="all, delete-orphan",
    )


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey("etfs.id"), nullable=False)

    units = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    purchased_at = Column(DateTime, nullable=True)
    currency = Column(String, nullable=True)
    comment = Column(String, nullable=True)

    etf = relationship(
        "ETF",
        back_populates="purchases",
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey("etfs.id"), nullable=False)

    price = Column(Float, nullable=False)

    purchased_at = Column(DateTime, nullable=True)
    currency = Column(String, nullable=True)
    comment = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    etf = relationship(
        "ETF",
        back_populates="alerts",
    )


# ✅ NAUJA LENTELĖ YTD
class PortfolioYTD(Base):
    __tablename__ = "portfolio_ytd"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, unique=True, nullable=False)
    start_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
