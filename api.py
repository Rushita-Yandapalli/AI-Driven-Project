"""
backend/api.py
─────────────
FastAPI REST API — Food Price Volatility Analysis System
Run: uvicorn backend.api:app --reload --port 8000

Endpoints:
  GET /prices          → paginated price records
  GET /trends          → price trend over time
  GET /volatility      → commodity/city volatility stats
  GET /anomalies       → detected price spikes/drops
  GET /cities          → city list and stats
  GET /city-comparison → city-wise aggregated comparison
  GET /seasonal        → month-wise seasonal data
  GET /health          → health check
"""

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from typing import Optional
import pandas as pd

# ── Try FastAPI; fall back gracefully if not installed ────────
try:
    from fastapi import FastAPI, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[API] FastAPI not installed. Run: pip install fastapi uvicorn")

from analytics import (
    load_and_preprocess, filter_df, get_price_trend,
    compute_volatility, detect_anomalies, get_seasonal_trends,
    city_comparison, get_insights,
)

# ── Load data once at startup ─────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "../food_prices.csv")
_df_cache: Optional[pd.DataFrame] = None

def get_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = load_and_preprocess(DATA_PATH)
    return _df_cache


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title       = "Food Price Volatility API",
        description = "Agricultural commodity price analytics for India (Agmarknet)",
        version     = "1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
    )

    # ── /health ───────────────────────────────────────────────
    @app.get("/health")
    def health():
        return {"status": "ok", "records": len(get_df())}

    # ── /prices ───────────────────────────────────────────────
    @app.get("/prices")
    def get_prices(
        commodity : Optional[str] = Query(None),
        city      : Optional[str] = Query(None),
        start_date: Optional[str] = Query(None),
        end_date  : Optional[str] = Query(None),
        page      : int           = Query(1, ge=1),
        page_size : int           = Query(100, le=1000),
    ):
        df = filter_df(get_df(), commodity, city, start_date, end_date)
        total    = len(df)
        start_i  = (page - 1) * page_size
        end_i    = start_i + page_size
        page_df  = df[["date","commodity","city","price","Min_Price","Max_Price","avg_price"]].iloc[start_i:end_i]
        page_df["date"] = page_df["date"].astype(str)
        return {"total": total, "page": page, "page_size": page_size, "data": page_df.to_dict(orient="records")}

    # ── /trends ───────────────────────────────────────────────
    @app.get("/trends")
    def get_trends(
        commodity : Optional[str] = Query(None),
        city      : Optional[str] = Query(None),
        start_date: Optional[str] = Query(None),
        end_date  : Optional[str] = Query(None),
        freq      : str           = Query("M", regex="^(D|M|Y)$"),
    ):
        df    = filter_df(get_df(), commodity, city, start_date, end_date)
        trend = get_price_trend(df, freq)
        trend["period"] = trend["period"].astype(str)
        return trend.fillna(0).to_dict(orient="records")

    # ── /volatility ───────────────────────────────────────────
    @app.get("/volatility")
    def get_volatility(
        group_by  : str           = Query("commodity", regex="^(commodity|city)$"),
        commodity : Optional[str] = Query(None),
        city      : Optional[str] = Query(None),
    ):
        df  = filter_df(get_df(), commodity, city)
        vol = compute_volatility(df, group_by)
        return vol.fillna(0).to_dict(orient="records")

    # ── /anomalies ────────────────────────────────────────────
    @app.get("/anomalies")
    def get_anomalies(
        commodity   : Optional[str] = Query(None),
        city        : Optional[str] = Query(None),
        z_threshold : float         = Query(2.0),
        limit       : int           = Query(200),
    ):
        df = filter_df(get_df(), commodity, city)
        _, anomalies = detect_anomalies(df, z_threshold)
        anomalies = anomalies.sort_values("z_score", key=abs, ascending=False).head(limit)
        anomalies["date"] = anomalies["date"].astype(str)
        cols = ["date","commodity","city","price","z_score","spike_type"]
        return anomalies[cols].fillna(0).to_dict(orient="records")

    # ── /cities ───────────────────────────────────────────────
    @app.get("/cities")
    def get_cities():
        df = get_df()
        return sorted(df["city"].unique().tolist())

    # ── /city-comparison ──────────────────────────────────────
    @app.get("/city-comparison")
    def get_city_comparison(commodity: Optional[str] = Query(None)):
        df   = filter_df(get_df(), commodity=commodity)
        comp = city_comparison(df)
        return comp.fillna(0).to_dict(orient="records")

    # ── /seasonal ─────────────────────────────────────────────
    @app.get("/seasonal")
    def get_seasonal(commodity: Optional[str] = Query(None)):
        df       = filter_df(get_df(), commodity=commodity)
        seasonal = get_seasonal_trends(df)
        return seasonal.to_dict(orient="records")

else:
    print("[API] FastAPI not available. Install with: pip install fastapi uvicorn")
