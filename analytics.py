"""
Data Processing & Analytics Engine
Food Price Volatility Analysis System (India)
Handles: cleaning, feature engineering, volatility, anomaly detection, aggregations
"""

import pandas as pd
import numpy as np
from scipy import stats
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../food_prices.csv")

# ─────────────────────────────────────────────
# 1. LOAD & PREPROCESS
# ─────────────────────────────────────────────

def load_and_preprocess(path: str = DATA_PATH) -> pd.DataFrame:
    """Load raw CSV and apply full preprocessing pipeline"""
    df = pd.read_csv(path)

    # --- Rename columns ---
    df = df.rename(columns={
        "Market":       "city",
        "Commodity":    "commodity",
        "Arrival_Date": "date",
        "Modal_Price":  "price",
    })

    # --- Handle nulls ---
    df = df.dropna(subset=["date", "price", "city", "commodity"])
    df["Min_Price"] = pd.to_numeric(df["Min_Price"], errors="coerce").fillna(df["price"])
    df["Max_Price"] = pd.to_numeric(df["Max_Price"], errors="coerce").fillna(df["price"])
    df["price"]     = pd.to_numeric(df["price"],     errors="coerce")
    df = df.dropna(subset=["price"])
    df = df[df["price"] > 0]

    # --- Date conversion ---
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # --- Feature Engineering ---
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"]   = df["date"].dt.day
    df["avg_price"] = (df["Min_Price"] + df["Max_Price"] + df["price"]) / 3
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

    df = df.sort_values("date").reset_index(drop=True)
    return df


# ─────────────────────────────────────────────
# 2. FILTERS
# ─────────────────────────────────────────────

def filter_df(df, commodity=None, city=None, start_date=None, end_date=None):
    """Apply UI filters to dataframe (Fixed Version)"""
    
    # 1. Filter Commodity
    if commodity is not None:
        # Check if it's a list/tuple/Index/Array (multi-select)
        if not isinstance(commodity, (str, bytes)):
            try:
                c_list = list(commodity)
                if c_list:
                    df = df[df["commodity"].isin(c_list)]
            except:
                pass
        # Handle scalar string case
        elif isinstance(commodity, str) and commodity != "All":
            df = df[df["commodity"] == commodity]

    # 2. Filter City
    if city is not None:
        if isinstance(city, str):
            if city != "All":
                df = df[df["city"] == city]
        else:
            try:
                ct_list = list(city)
                if ct_list:
                    df = df[df["city"].isin(ct_list)]
            except:
                pass

    # 3. Filter Date
    if start_date:
        df = df[df["date"] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df["date"] <= pd.Timestamp(end_date)]

    return df


# ─────────────────────────────────────────────
# 3. TIME SERIES & MOVING AVERAGES
# ─────────────────────────────────────────────

def get_price_trend(df, freq="M"):
    """Aggregate price by time frequency: D/W/M/Y"""
    freq_map = {"D": "date", "W": "date", "M": "year_month", "Y": "year"}
    if freq == "M":
        trend = df.groupby("year_month")["price"].mean().reset_index()
        trend.columns = ["period", "avg_price"]
        trend["period"] = pd.PeriodIndex(trend["period"], freq="M").to_timestamp()
    elif freq == "Y":
        trend = df.groupby("year")["price"].mean().reset_index()
        trend.columns = ["period", "avg_price"]
    elif freq == "D":
        trend = df.groupby("date")["price"].mean().reset_index()
        trend.columns = ["period", "avg_price"]
    else:
        trend = df.groupby("year_month")["price"].mean().reset_index()
        trend.columns = ["period", "avg_price"]
        trend["period"] = pd.PeriodIndex(trend["period"], freq="M").to_timestamp()

    trend = trend.sort_values("period")
    if len(trend) >= 7:
        trend["ma7"]  = trend["avg_price"].rolling(7,  min_periods=1).mean()
    if len(trend) >= 30:
        trend["ma30"] = trend["avg_price"].rolling(30, min_periods=1).mean()
    return trend


# ─────────────────────────────────────────────
# 4. VOLATILITY ANALYSIS
# ─────────────────────────────────────────────

def compute_volatility(df, group_by="commodity"):
    """Compute price volatility (std dev, CV) grouped by commodity or city"""
    vol = df.groupby(group_by)["price"].agg(
        mean_price="mean",
        std_dev="std",
        min_price="min",
        max_price="max",
        count="count"
    ).reset_index()
    vol["cv"] = (vol["std_dev"] / vol["mean_price"] * 100).round(2)   # Coefficient of Variation %
    vol["price_range"] = vol["max_price"] - vol["min_price"]
    vol = vol.sort_values("cv", ascending=False).reset_index(drop=True)
    return vol


# ─────────────────────────────────────────────
# 5. ANOMALY DETECTION (Z-SCORE)
# ─────────────────────────────────────────────

def detect_anomalies(df, z_threshold=2.0):
    """
    Z-score anomaly detection per commodity+city pair
    z = (price - mean) / stddev; mark spike where |z| > threshold
    """
    df = df.copy()
    if df.empty:
        return df, pd.DataFrame()

    groups = df.groupby(["commodity", "city"])["price"]

    df["mean_ref"]   = groups.transform("mean")
    df["std_ref"]    = groups.transform("std").fillna(1)
    df["z_score"]    = (df["price"] - df["mean_ref"]) / df["std_ref"]
    df["is_anomaly"] = df["z_score"].abs() > z_threshold
    
    df["spike_type"] = np.where(df["z_score"] > z_threshold, "Price Spike 🔺",
                       np.where(df["z_score"] < -z_threshold, "Price Drop 🔻", "Normal"))
    
    anomalies = df[df["is_anomaly"]].sort_values("z_score", key=abs, ascending=False)
    return df, anomalies


# ─────────────────────────────────────────────
# 6. SEASONAL TRENDS
# ─────────────────────────────────────────────

def get_seasonal_trends(df):
    """Month-wise average price aggregation"""
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seasonal = df.groupby(["month", "month_name"])["price"].mean().reset_index()
    seasonal.columns = ["month_num", "month", "avg_price"]
    seasonal = seasonal.sort_values("month_num")
    return seasonal


def get_commodity_seasonal(df):
    """Commodity-wise monthly heatmap data"""
    pivot = df.pivot_table(
        index="commodity",
        columns="month",
        values="price",
        aggfunc="mean"
    )
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot.columns)]
    return pivot


# ─────────────────────────────────────────────
# 7. CITY COMPARISON
# ─────────────────────────────────────────────

def city_comparison(df):
    """City-wise price stats"""
    comp = df.groupby("city")["price"].agg(
        avg_price="mean",
        std_dev="std",
        min_price="min",
        max_price="max",
        records="count"
    ).reset_index()
    comp["cv"] = (comp["std_dev"] / comp["avg_price"] * 100).round(2)
    comp = comp.sort_values("avg_price", ascending=False).reset_index(drop=True)
    return comp


# ─────────────────────────────────────────────
# 8. SUMMARY INSIGHTS (KPI Cards)
# ─────────────────────────────────────────────

def get_insights(df, anomalies_df):
    """Compute top-level KPI insights"""
    vol = compute_volatility(df, "commodity")
    city_vol = compute_volatility(df, "city")

    most_volatile_commodity = vol.iloc[0]["commodity"]  if len(vol) else "N/A"
    most_volatile_cv        = vol.iloc[0]["cv"]          if len(vol) else 0

    city_high_fluc = city_vol.iloc[0]["city"] if len(city_vol) else "N/A"
    city_high_cv   = city_vol.iloc[0]["cv"]   if len(city_vol) else 0

    if not anomalies_df.empty:
        top_spike = anomalies_df.sort_values("z_score", ascending=False).iloc[0]
        spike_info = {
            "commodity": top_spike["commodity"],
            "city":      top_spike["city"],
            "price":     round(top_spike["price"], 2),
            "z_score":   round(top_spike["z_score"], 2),
            "date":      str(top_spike["date"].date()),
        }
    else:
        spike_info = {}

    return {
        "total_records":          len(df),
        "total_commodities":      df["commodity"].nunique(),
        "total_cities":           df["city"].nunique(),
        "avg_price":              round(df["price"].mean(), 2),
        "most_volatile_commodity":most_volatile_commodity,
        "most_volatile_cv":       round(most_volatile_cv, 2),
        "city_highest_fluctuation":city_high_fluc,
        "city_fluctuation_cv":    round(city_high_cv, 2),
        "total_anomalies":        len(anomalies_df),
        "top_spike":              spike_info,
    }
