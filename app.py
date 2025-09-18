# app.py
# -*- coding: utf-8 -*-

import os, sys, importlib.util
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------- load prices_lib.py (same folder) ----------
HERE = os.path.dirname(__file__)
PRICES_LIB_PATH = os.path.join(HERE, "prices_lib.py")
spec = importlib.util.spec_from_file_location("prices_lib", PRICES_LIB_PATH)
prices_lib = importlib.util.module_from_spec(spec)
sys.modules["prices_lib"] = prices_lib
assert spec.loader is not None
spec.loader.exec_module(prices_lib)

from prices_lib import DEFAULT_EXCEL_PATH, load_prices, build_metrics_table

# ---------- Watchlist (same as your email) ----------
QUOTES = [
    'ABWEM00','AAPRD00','AAPRE00','ABWDY00','AAXAL00','AAXAM00','ABWDK00','AAPEF00','AAPEG00',
    'AANYX77','AANY105','AANYX79','AANYX78','AANYX76','AANYX80','ADIQA00','ADIAI00','ADIAA00',
    'ADIAS00','AARQUCY','PGACTCY','AAMFBCY','AARQVCY','PGAJBCY','AAMNGCY','AATGYCY','AAXFDCY',
    'POAEDCY','PJABOCY','RBc1','RBc2','HOc1','HOc2','PGACU00','AWTRA00','RVOR002','AATGZ00',
    'AUSGN00','PJABM00','AUSGL00','AATGY00','PJABO00','PGACT00','AAXTA00','AAXTD00','AAXTB00',
    'AAXTACY','AAXTDCY','AAXTBCY','AREFA00','AREFB00','AREFE00','PHAKX00','AREFD00','AREFC00',
    'ADDPG00','ADDPH00','ADDPGRV','AAMHB00','AANYX35','AAMHBRV','ADDPE00','ADDPF00','ADDPFRV',
    'AAMHBRV','AANYX33','AAPSYRV','AAVYA00','AANYX37','AAVYARV','AAUAS00','AANYX29','AAUASRV',
    'ADDPI00','ADDPJ00','ADDPIRV','ADDPK00','ADDPL00','ADDPKRV','AAVYB00','ADLAL00','AAVYBRV',
    'AAUAT00','AANYX30','AAUATRV','ADDPK00','ADDPL00','ADDPKRV','AAMHZ00','AANYX36','AAMHZRV',
    'ADDPM00','ADDPN00','AATHF00','ADIYA00','ADDPA00','ADDPB00','AAJNL00','ADIEA00','ACXPW00',
    'AANYX40','ACRQWRV','ACRQWCY','ABXPW00','AANYX41','ABRQWRV','ABRQWCY','ADXPW00','AANYX42',
    'ADRQWRV','ADRQWCY','AAXPV00','ADIJA00','AAXPVCY','AAXPU00','ADIAR00','AAXPUCY','AAXPW00',
    'ADLAA00','AAXPWCY','APPNE00','APPNF00','APPNGRV','APPNH00','APPNM00','APPNN00','APPNORV',
    'APPNP00','APPNA00','APPNB00','APPNCRV','APPND00','APPNI00','APPNJ00','APPNKRV','APPNL00',
    'TCJNC00','TCJNA00','TCJNE00','PPARH00','AANY102','PPARHRV','AAREL00','AANY101','AARELRV',
    'AAUEU00','AANY103','AAUEURV','AATHA00','ADLAI00','PJAAF00','ADILA00','PPASQ00','AANY100',
    'PPASQRV','AAXIX00','AANYX01','AAXIXRV','ARVPA00','ARVPB00','ARVPJRV','PGABD00','AANYX02',
    'PGABDRV','ARVPC00','ARVPD00','ARVPIRV','PJAAI00','ADIKA00','AATHB00','ADLAB00','AAKYJ00',
    'AANVX00','AAKYJRV','AAKYN00','AANYX89','AAKYNRV','POAAK00','AANWA00','POAAL00','ADLAF00',
    'ABWFB00','ABWFC00','ABWFD00','AGEAB00','AGEAM01','AGEAM02','ABWFT00','AAEBW00','AAEBY00',
    'GPWSD00','GPWSD01','GPWSD02','ABWFV00','PAAAJ00','AAECO00','AGEFA00','AAQZV00','PGABM00',
    'AAKOD00','AAXPM00','AAXPN00','AAWZA00','AAWZB00','AAXFQ00','AWFRC00','AWFRD00','ABNWE00',
    'ABNWG00','ABNWH00','ABNWI00','AAKUV00','AGNWC00','TCAFL00','TCAHK00','TCAHM00','PFALY00',
    'PFAMH00','PFAMA00','PFAMB00','UBMWA00','PFABX00','PFABY00','AABDV00','PFADC10','AABDX00',
    'PFADB10','PFACW10','PFACY10','PFAMI00','TCAFN00','PFAMP00','PFAMQ00','PFAMM00','AALPDSZ',
    'TCAFJ00','TCAFH00','TCAFO00','TCAFQ00','TCAFT00','TCATX00','TCAXX00','TCUWB00','TCAWX00',
    'TCAVX00','TCAUX00','TCMNA00','TCAFV00','TCAFX00','TCBRB00','TCNBB00','TCLNASZ','TCJND00',
    'TCJNB00','TCJNE00','ACDUA00','PAAAL00','PAAAI00','PAAAH00','PAAAM00','PHALA00','PHALA02',
    'MTPRA00','AASLQ00','AASLQ02','AAOAX00','AAOQQ00','TLEAA00','TLEAB00','TLPRA00','AASFD00',
    'AASFF00','AAILD00','AASDB00','PHABK00','MXEEA00','MXEAB00','PHABD00','MXPRA00','AAOQP00',
    'AAVOQ00','CEBXE00','CEBXE01','HPACQ00','MEFRB01'
]

# ---------- Streamlit config ----------
st.set_page_config(page_title="Gasoline Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
/* hide sidebar completely */
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {display:none!important;}
</style>
""", unsafe_allow_html=True)
st.title("⛽ Gasoline Dashboard")

# ---------- Load once (fixed path/sheet) ----------
with st.spinner("Loading data…"):
    data = load_prices(DEFAULT_EXCEL_PATH, 0)
df = data["df"]
mdf_full = build_metrics_table(df, quotes=QUOTES)

# ---------- Seasonal daily (no aggregation) ----------
def seasonal_daily_figure(df: pd.DataFrame, quote: str):
    g = df[df["Quote"] == quote].copy()
    if g.empty:
        return px.line()
    desc = g.get("Description", pd.Series([quote])).iloc[0] or quote
    u = (g.get("UOM", pd.Series([""])).iloc[0] or "")
    c = (g.get("Currency", pd.Series([""])).iloc[0] or "")
    units = f"{u}/{c}".strip("/")

    g["Year"] = g["Date"].dt.year
    g["BaseDate"] = pd.to_datetime(g["Date"].dt.strftime("2000-%m-%d"))

    fig = px.line(g, x="BaseDate", y="Value", color="Year", title=f"{desc} ({units})", markers=False)
    fig.update_xaxes(
        tickvals=pd.date_range("2000-01-01", "2000-12-31", freq="MS"),
        tickformat="%b",
        range=[pd.Timestamp("2000-01-01"), pd.Timestamp("2000-12-31")]
    )
    for tr in fig.data:
        tr.update(mode="lines", line={"width": 2})
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                      margin=dict(l=10, r=10, t=60, b=10), height=420)
    return fig

# ---------- Tabs ----------
tab_heatmap, tab_seasonals = st.tabs(["🔥 Heatmap", "📈 Seasonals (daily, by year)"])

# ================== Tab 1 : Heatmap ==================
with tab_heatmap:
    search = st.text_input("🔎 Search by description", value="", placeholder="e.g., Gasoline NWE").strip().lower()
    mdf = mdf_full[mdf_full["Description"].str.lower().str.contains(search)] if search else mdf_full

    # --- Zoom control (drives sizes & margins) ---
    zoom = st.slider("Zoom", min_value=1.0, max_value=2.0, value=1.35, step=0.05)
    FONT_SIZE   = int(12 * zoom)
    TEXT_SIZE   = int(10 * zoom)
    GRID_W      = max(1, int(1 * zoom))
    ROW_H       = int(22 * zoom)
    HEADER_PAD  = int(6 * zoom)
    HEADER_FS   = int(14 * zoom)
    RIGHT_MARGIN = int(20 * zoom)

    # display columns: Last (neutral) + deltas (colored)
    all_cols = [c for c in ["Last", "Δ1d", "Δ7d", "MoM", "YTD %"] if c in mdf.columns]
    delta_cols = [c for c in ["Δ1d", "Δ7d", "MoM", "YTD %"] if c in mdf.columns]

    if mdf.empty or len(all_cols) == 0 or len(delta_cols) == 0:
        st.info("No series/columns available for the heatmap.")
    else:
        RAW_ALL = mdf[all_cols].astype(float).to_numpy()
        TXT_ALL = np.where(np.isfinite(RAW_ALL), np.vectorize(lambda x: f"{x:,.2f}")(RAW_ALL), "–")

        RAW_DELTA = mdf[delta_cols].astype(float).to_numpy()
        row_mask = np.isfinite(RAW_DELTA).any(axis=1)
        RAW_ALL, TXT_ALL, RAW_DELTA = RAW_ALL[row_mask], TXT_ALL[row_mask], RAW_DELTA[row_mask]
        mdf_shown = mdf[row_mask]

        if mdf_shown.empty:
            st.info("After filtering, no rows have values for Δ1d/Δ7d/MoM/YTD%.")
        else:
            y_labels = mdf_shown["Description"].tolist()
            n_rows = RAW_ALL.shape[0]
            n_all = len(all_cols)
            n_delta = len(delta_cols)

            # ---------- DYNAMIC LEFT MARGIN (prevents truncation) ----------
            # rough character width in pixels for the current font size
            char_px = 0.62 * FONT_SIZE  # 0.6–0.65 is a good rule of thumb
            max_len = max(len(s) for s in y_labels) if y_labels else 30
            LEFT_MARGIN = int(max(260, char_px * max_len + 40) * 1.0)  # +40 padding
            # (you can clamp with min(..., 1100) if needed)
            # ---------------------------------------------------------------

            x_all = list(range(n_all))
            x_delta = list(range(1, n_all))  # 0 is 'Last'

            # robust color scaling for deltas
            Z_DELTA = RAW_DELTA.copy()
            for j in range(n_delta):
                col = Z_DELTA[:, j]
                vmax = np.nanpercentile(np.abs(col), 95)
                if not np.isfinite(vmax) or vmax == 0:
                    vmax = np.nanmax(np.abs(col)) if np.isfinite(np.nanmax(np.abs(col))) and np.nanmax(np.abs(col)) != 0 else 1.0
                Z_DELTA[:, j] = np.clip(col / vmax, -1.0, 1.0)

            colorscale = [
                [0.00, "#9b000f"],
                [0.45, "#ffdede"],
                [0.50, "#ffffff"],
                [0.55, "#e0ffe0"],
                [1.00, "#0a7a0a"],
            ]

            fig = go.Figure()

            # light gray for missing values (all cols)
            missing_mask_all = ~np.isfinite(RAW_ALL)
            if missing_mask_all.any():
                fig.add_trace(go.Heatmap(
                    z=np.where(missing_mask_all, 0.0, np.nan),
                    x=x_all, y=y_labels,
                    colorscale=[[0, "#f0f0f0"], [1, "#f0f0f0"]],
                    showscale=False, xgap=1, ygap=1, hoverinfo="skip"
                ))

            # neutral 'Last' column + text
            last_vals = RAW_ALL[:, [0]]
            last_txt  = TXT_ALL[:, [0]]
            fig.add_trace(go.Heatmap(
                z=np.zeros_like(last_vals),
                x=[0], y=y_labels,
                colorscale=[[0, "#ffffff"], [1, "#ffffff"]],
                showscale=False, xgap=1, ygap=1,
                text=last_txt, texttemplate="%{text}",
                textfont={"size": TEXT_SIZE, "color": "#111"},
                customdata=last_vals,
                hovertemplate="<b>%{y}</b><br>Last: %{customdata:.4f}<extra></extra>"
            ))

            # colored deltas with values
            delta_txt = TXT_ALL[:, 1:]
            fig.add_trace(go.Heatmap(
                z=Z_DELTA,
                x=x_delta, y=y_labels,
                colorscale=colorscale, zmin=-1, zmax=1, zmid=0,
                showscale=False, xgap=1, ygap=1,
                text=delta_txt, texttemplate="%{text}",
                textfont={"size": TEXT_SIZE},
                customdata=RAW_DELTA,
                hovertemplate="<b>%{y}</b><br>%{meta}: %{customdata:.4f}<extra></extra>",
                meta=np.tile(np.array(delta_cols), (n_rows, 1))
            ))

            # grid lines
            shapes = []
            for i in range(n_all + 1):
                x0 = i - 0.5
                shapes.append(dict(type="line", xref="x", yref="y",
                                   x0=x0, x1=x0, y0=-0.5, y1=n_rows - 0.5,
                                   line=dict(color="black", width=GRID_W)))
            for j in range(n_rows + 1):
                y0 = j - 0.5
                shapes.append(dict(type="line", xref="x", yref="y",
                                   x0=-0.5, x1=n_all - 0.5, y0=y0, y1=y0,
                                   line=dict(color="black", width=GRID_W)))
            fig.update_layout(shapes=shapes)

            # lock margins (no automargin → we control the space)
            fig.update_xaxes(showticklabels=False, range=[-0.5, n_all - 0.5])
            fig.update_yaxes(automargin=False, tickfont=dict(size=FONT_SIZE))
            fig.update_layout(
                margin=dict(l=LEFT_MARGIN, r=RIGHT_MARGIN, t=10, b=10),
                font=dict(size=FONT_SIZE),
                height=max(int(650 * zoom), ROW_H * n_rows)
            )

            # sticky header aligned with plot area
            st.markdown(
                f"""
                <style>
                  .sticky-heat-header {{
                      position: sticky; top: 0; z-index: 1000;
                      background: #ffffff; border-bottom: 1px solid #000;
                      padding: {HEADER_PAD}px 8px; padding-right: {RIGHT_MARGIN}px;
                  }}
                  .sticky-heat-grid {{
                      display: grid;
                      grid-template-columns: {LEFT_MARGIN}px repeat({n_all}, 1fr);
                      gap: 0px;
                  }}
                  .sticky-heat-cell {{
                      text-align: center; font-weight: 700; color: #111827;
                      font-size: {HEADER_FS}px;
                  }}
                </style>
                <div class="sticky-heat-header">
                  <div class="sticky-heat-grid">
                    <div></div>
                    {''.join(f'<div class="sticky-heat-cell">{c}</div>' for c in all_cols)}
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.plotly_chart(fig, use_container_width=True)

            valid = int(np.isfinite(RAW_DELTA).sum()); total = int(RAW_DELTA.size)
            counts = {c: int(np.isfinite(RAW_DELTA[:, j]).sum()) for j, c in enumerate(delta_cols)}
            st.caption(f"Valid delta cells: **{valid}/{total}** — per column: {counts}. Grey = not enough history.")


# ================== Tab 2 : Seasonals (daily, by year) ==================
with tab_seasonals:
    q = st.text_input("🔎 Search by description (seasonals)", value="", placeholder="e.g., Barges Crack").strip().lower()
    cols_per_row = st.slider("Charts per row", 1, 4, 3)

    mdf2 = mdf_full[mdf_full["Description"].str.lower().str.contains(q)] if q else mdf_full
    if mdf2.empty:
        st.info("No series match your search.")
    else:
        q_list = mdf2.index.tolist()
        desc_map = mdf2["Description"].to_dict()
        n = len(q_list)
        rows = (n + cols_per_row - 1) // cols_per_row

        for r in range(rows):
            cols = st.columns(cols_per_row, gap="large")
            for c in range(cols_per_row):
                i = r * cols_per_row + c
                if i >= n: break
                quote = q_list[i]
                with cols[c]:
                    st.markdown(f"**{desc_map.get(quote, quote)}**")
                    st.plotly_chart(seasonal_daily_figure(df, quote), use_container_width=True)
