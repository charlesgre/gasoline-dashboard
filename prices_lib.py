# prices_lib.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functools import lru_cache
from typing import List, Dict, Tuple, Union

# ---- Chemin par défaut (relatif à ton projet) ----
DEFAULT_EXCEL_PATH = r".\Prices\Gasoline prices.xlsx"

# Souplesse sur les noms de colonnes
DATE_CAND = ["date", "pricing date", "obs_date", "timestamp"]
QUOTE_CAND = ["quote", "ric", "symbol", "ticker", "series"]
VALUE_CAND = ["value", "price", "close", "last", "px", "settle"]
DESC_CAND  = ["description", "name", "label", "title"]
UOM_CAND   = ["uom", "unit", "units"]
CURR_CAND  = ["currency", "ccy", "curr", "cur"]

# ---------- Helpers ----------
def _find_col(df: pd.DataFrame, candidates: List[str]) -> Union[str, None]:
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    for col in df.columns:
        if any(cand.lower() in str(col).lower() for cand in candidates):
            return col
    return None

# ---------- Chargement & prépa ----------
@lru_cache(maxsize=4)
def load_prices(excel_path: str = DEFAULT_EXCEL_PATH, sheet: Union[int, str] = 0) -> Dict[str, pd.DataFrame]:
    """Charge l'Excel et retourne {'df': dataframe nettoyé}."""
    df0 = pd.read_excel(excel_path, sheet_name=sheet, engine="openpyxl")
    dcol = _find_col(df0, DATE_CAND)
    qcol = _find_col(df0, QUOTE_CAND)
    vcol = _find_col(df0, VALUE_CAND)
    xcol = _find_col(df0, DESC_CAND)
    ucol = _find_col(df0, UOM_CAND)
    ccol = _find_col(df0, CURR_CAND)
    if not (dcol and qcol and vcol):
        raise ValueError(f"Colonnes essentielles introuvables. Colonnes dispo: {list(df0.columns)}")

    df = df0.copy()
    df[dcol] = pd.to_datetime(df[dcol], errors="coerce")
    df = df.dropna(subset=[dcol])
    df[vcol] = pd.to_numeric(df[vcol], errors="coerce")
    df = df.dropna(subset=[vcol])

    df = df.rename(columns={
        dcol: "Date",
        qcol: "Quote",
        vcol: "Value",
        (xcol or "Description"): "Description",
        (ucol or "UOM"): "UOM",
        (ccol or "Currency"): "Currency",
    })

    for col in ["Description", "UOM", "Currency"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["Date", "Quote", "Value", "Description", "UOM", "Currency"]].sort_values(["Quote", "Date"])
    return {"df": df}

# ---------- Métriques ----------
def compute_metrics(series: pd.Series) -> Dict[str, float]:
    s = series.dropna().sort_index()
    out: Dict[str, float] = {}
    if s.empty:
        return out
    last = float(s.iloc[-1]); out["Last"] = last

    def delta(days: int) -> float:
        prev = s[s.index <= (s.index[-1] - pd.Timedelta(days=days))]
        return last - float(prev.iloc[-1]) if len(prev) > 0 else np.nan

    out["Δ1d"] = delta(1)
    out["Δ7d"] = delta(7)
    out["MoM"]  = delta(30)

    cur_year = s.index[-1].year
    s_y = s[s.index.year == cur_year]
    out["YTD %"] = ((last / float(s_y.iloc[0])) - 1.0) * 100.0 if not s_y.empty and float(s_y.iloc[0]) != 0 else np.nan

    sep = s[s.index.month == 9]
    out["Avg Sep"] = float(sep.mean()) if not sep.empty else np.nan

    anchor = s.index[-1]
    mask = (s.index.month < anchor.month) | ((s.index.month == anchor.month) & (s.index.day <= anchor.day))
    s_masked = s[mask]
    out["Avg YTD"] = float(s_masked.groupby(s_masked.index.year).mean().mean()) if not s_masked.empty else np.nan

    cutoff = s.index[-1] - pd.Timedelta(days=365)
    s52 = s[s.index >= cutoff]
    if len(s52) >= 2:
        vmin, vmax = float(s52.min()), float(s52.max())
        out["Pct 52w"] = ((last - vmin) / (vmax - vmin) * 100.0) if vmax > vmin else np.nan
        std = float(s52.std(ddof=0))
        out["Z-score"] = ((last - float(s52.mean())) / std) if std != 0 else np.nan
    else:
        out["Pct 52w"] = np.nan
        out["Z-score"] = np.nan
    return out

def build_metrics_table(df: pd.DataFrame, quotes: Union[List[str], None] = None) -> pd.DataFrame:
    if quotes:
        df = df[df["Quote"].isin(quotes)]
    rows = []
    for q, g in df.groupby("Quote"):
        s = pd.Series(g["Value"].values, index=pd.DatetimeIndex(g["Date"].values))
        m = compute_metrics(s)
        desc = g["Description"].iloc[0] if "Description" in g.columns else q
        uom  = g["UOM"].iloc[0] if "UOM" in g.columns else ""
        cur  = g["Currency"].iloc[0] if "Currency" in g.columns else ""
        rows.append({
            "Quote": q,
            "Description": desc,
            "Units": f"{uom}/{cur}".strip("/"),
            **m
        })
    mdf = pd.DataFrame(rows).set_index("Quote").sort_index()
    return mdf

# ---------- Figures ----------
def heatmap_figure(mdf: pd.DataFrame, metrics_cols: List[str]) -> go.Figure:
    data = mdf[metrics_cols].copy()
    z = (data - data.mean()) / data.std(ddof=0)
    fig = px.imshow(
        z.values,
        x=metrics_cols,
        y=mdf["Description"],
        color_continuous_scale="RdYlGn",
        aspect="auto",
        origin="lower",
    )
    fig.update_layout(
        coloraxis_reversescale=True,
        margin=dict(l=0, r=0, t=20, b=0),
        height=max(320, 18 * len(mdf))
    )
    return fig

def seasonal_figure(df: pd.DataFrame, quote: str, by: str = "mean") -> go.Figure:
    g = df[df["Quote"] == quote].copy()
    if g.empty:
        return go.Figure()
    desc = g["Description"].iloc[0] if "Description" in g.columns else quote
    units = ""
    if "UOM" in g.columns or "Currency" in g.columns:
        u, c = g["UOM"].iloc[0], g["Currency"].iloc[0]
        units = f"{u}/{c}".strip("/")
    g["Year"] = g["Date"].dt.year
    g["Month"] = g["Date"].dt.month
    agg = g.groupby(["Year","Month"])["Value"].median().reset_index() if by=="median" \
          else g.groupby(["Year","Month"])["Value"].mean().reset_index()
    fig = px.line(agg, x="Month", y="Value", color="Year", title=f"{desc} ({units})")
    fig.update_xaxes(tickmode="array", tickvals=list(range(1,13)),
                     ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                      margin=dict(l=10,r=10,t=60,b=10), height=380)
    return fig
