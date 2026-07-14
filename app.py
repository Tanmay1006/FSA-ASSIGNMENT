"""
FINANCIAL INTELLIGENCE ENGINE — Nike vs Adidas
Streamlit dashboard.

Run with:
    pip install -r requirements.txt
    streamlit run app.py

Data: Nike FY2026 (year ended May 31, 2026, USD) and
adidas FY2025 (year ended Dec 31, 2025, EUR).
All cross-company comparisons use ratios and margins,
so currency differences do not distort results.
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------- Page & theme ----------------
st.set_page_config(
    page_title="FIE — Nike vs Adidas",
    page_icon="🏟️",
    layout="wide",
)

NIKE = "#D4FB4B"
ADI = "#7DD3FC"
BG = "#0D0F13"
PANEL = "#15181F"
LINE = "#262B36"
TEXT = "#F2F4F8"
DIM = "#8B93A3"
RISK = "#F87171"
OK = "#4ADE80"
AMBER = "#FACC15"
ORANGE = "#FB923C"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    h1, h2, h3, h4, p, li, span, div {{ color: {TEXT}; }}
    .dim {{ color: {DIM}; }}
    .panel {{
        background: {PANEL}; border: 1px solid {LINE};
        border-radius: 14px; padding: 18px 20px; margin-bottom: 12px;
    }}
    [data-testid="stMetricValue"] {{ color: {TEXT}; }}
    [data-testid="stMetricLabel"] {{ color: {DIM}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Model data ----------------
CATS = [
    # (category, weight %, nike score, adidas score)
    ("Profitability", 25, 58, 62),
    ("Cash Flow", 20, 45, 21),
    ("Solvency", 20, 71, 53),
    ("Liquidity", 15, 82, 31),
    ("Efficiency", 15, 52, 37),
    ("Growth & Trend", 5, 25, 85),
]
NIKE_SCORE = round(sum(w * n for _, w, n, _ in CATS) / 100)  # 59
ADI_SCORE = round(sum(w * a for _, w, _, a in CATS) / 100)   # 45


def rating(score: int):
    if score >= 80:
        return "A", "Strong", OK
    if score >= 65:
        return "B", "Good", "#A3E635"
    if score >= 50:
        return "C", "Moderate Risk", AMBER
    if score >= 35:
        return "D", "Elevated Risk", ORANGE
    return "E", "Critical Risk", RISK


YEARS = ["FY24 / 2023", "FY25 / 2024", "FY26 / 2025"]
TRENDS = {
    "Revenue (Nike $B · adidas €B)": ([51.4, 46.3, 46.4], [21.4, 23.7, 24.8], "bar"),
    "Gross margin %": ([44.6, 42.7, 42.9], [47.5, 50.8, 51.6], "line"),
    "Operating margin %": ([13.0, 8.2, 8.3], [1.3, 5.6, 8.3], "line"),
    "Operating cash flow (Nike $B · adidas €B)": ([7.4, 3.7, 3.0], [2.6, 2.9, 0.8], "bar"),
}

RATIOS = [
    ("Liquidity", [
        ("Current ratio", "1.96", "1.32", "Nike"),
        ("Quick ratio", "1.19", "0.52", "Nike"),
        ("Cash ratio", "0.72", "0.23", "Nike"),
    ]),
    ("Profitability", [
        ("Gross margin", "42.9%", "51.6%", "adidas"),
        ("Operating margin", "8.3%", "8.3%", "Even"),
        ("Net margin", "6.7%", "5.5%", "Nike"),
        ("Return on equity (ROE)", "22.1%", "23.8%", "adidas"),
        ("Return on assets (ROA)", "8.3%", "6.7%", "Nike"),
    ]),
    ("Efficiency", [
        ("Inventory turnover", "3.5x", "2.2x", "Nike"),
        ("Asset turnover", "1.24x", "1.21x", "Nike"),
        ("Cash conversion cycle", "96 days", "110 days", "Nike"),
    ]),
    ("Solvency", [
        ("Debt-to-equity (borrowings)", "0.53", "0.43", "adidas"),
        ("Liabilities-to-assets", "0.61", "0.70", "Nike"),
        ("Interest coverage", "Net interest income", "8.7x", "Nike"),
    ]),
    ("Cash Flow", [
        ("Operating CF margin", "≈6.5%*", "3.0%", "Nike"),
        ("Free cash flow", "≈$2.4B*", "≈€0.1–0.3B", "Nike"),
        ("Operating CF to borrowings", "≈0.38x*", "0.28x", "Nike"),
    ]),
]

STRENGTHS = {
    "Nike": [
        "Fortress liquidity — $9.0B cash & short-term investments, current ratio ~2x",
        "Larger scale ($46.4B revenue) and stronger returns on assets",
        "Net interest income — debt costs fully covered",
        "24 consecutive years of dividend increases",
    ],
    "adidas": [
        "Powerful momentum — operating profit up 54% to €2.06B in 2025",
        "Record gross margin of 51.6%, well above Nike's 42.9%",
        "Second straight year of double-digit currency-neutral brand growth",
        "Recovered from a 2023 net loss to €1.34B net income in two years",
    ],
}
RISKS = {
    "Nike": [
        "Revenue flat for two years; Greater China down 11%, Converse down 31%",
        "Gross margin ~9 pts below adidas; FY26 flattered by a one-off $986M tariff recovery",
        "Operating cash flow fell from $7.4B (FY24) to ≈$3.0B (FY26)",
        "Receivables up 26% while sales are flat — cash-quality warning",
    ],
    "adidas": [
        "Weak 2025 cash conversion — operating cash flow collapsed to €0.75B (2024: €2.9B)",
        "Inventories up 17% ahead of World Cup 2026 — markdown risk if demand disappoints",
        "Thin liquidity buffer — quick ratio 0.52, cash down 34% to €1.6B",
        "≈€400M tariff & currency headwind expected in 2026",
    ],
}


def base_layout(fig, height=340):
    fig.update_layout(
        paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Arial"),
        legend=dict(orientation="h", y=-0.2, font=dict(color=DIM)),
        margin=dict(l=30, r=20, t=30, b=30), height=height,
    )
    fig.update_xaxes(gridcolor=LINE, zerolinecolor=LINE, color=DIM)
    fig.update_yaxes(gridcolor=LINE, zerolinecolor=LINE, color=DIM)
    return fig


def score_dial(value, color, name):
    g, label, rcolor = rating(value)
    fig = go.Figure(go.Pie(
        values=[value, 100 - value], hole=0.72,
        marker=dict(colors=[color, LINE]),
        textinfo="none", sort=False, direction="clockwise", showlegend=False,
    ))
    fig.add_annotation(text=f"<b>{value}</b>", font=dict(size=44, color=TEXT), showarrow=False, y=0.55)
    fig.add_annotation(text=f"<b>{g} · {label}</b>", font=dict(size=15, color=rcolor), showarrow=False, y=0.30)
    fig.add_annotation(text=f"<b>{name}</b>", font=dict(size=20, color=color), showarrow=False, y=0.08)
    fig.update_layout(paper_bgcolor=BG, margin=dict(l=10, r=10, t=10, b=10), height=300)
    return fig


# ---------------- Header ----------------
st.markdown(
    f"""
    <div style='text-align:center; margin-bottom:4px;'>
      <div style='letter-spacing:5px; color:{DIM}; font-size:13px; font-weight:600;'>FINANCIAL INTELLIGENCE ENGINE</div>
      <h1 style='margin:2px 0;'>
        <span style='color:{NIKE};'>NIKE</span>
        <span style='color:{DIM}; font-size:24px;'>&nbsp;VS&nbsp;</span>
        <span style='color:{ADI};'>ADIDAS</span>
      </h1>
      <div class='dim' style='font-size:13px;'>Nike FY2026 (year ended May 31, 2026) · adidas FY2025 (year ended Dec 31, 2025)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([2, 1, 2])
with c1:
    st.plotly_chart(score_dial(NIKE_SCORE, NIKE, "NIKE"), use_container_width=True)
with c2:
    st.markdown(f"<div style='text-align:center; font-size:34px; color:{DIM}; font-weight:700; margin-top:110px;'>VS</div>", unsafe_allow_html=True)
with c3:
    st.plotly_chart(score_dial(ADI_SCORE, ADI, "ADIDAS"), use_container_width=True)

# ---------------- Tabs ----------------
tabs = st.tabs(["🏟️ Scoreboard", "📈 Trends", "📋 Ratios", "⚖️ Strengths & Risks", "🔮 Prediction", "🧮 Methodology"])

# --- Scoreboard ---
with tabs[0]:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Category scores")
        cats = [c for c, _, _, _ in CATS][::-1]
        nvals = [n for _, _, n, _ in CATS][::-1]
        avals = [a for _, _, _, a in CATS][::-1]
        fig = go.Figure()
        fig.add_bar(y=cats, x=nvals, name="Nike", orientation="h",
                    marker_color=NIKE, text=nvals, textposition="outside")
        fig.add_bar(y=cats, x=avals, name="adidas", orientation="h",
                    marker_color=ADI, text=avals, textposition="outside")
        fig.update_xaxes(range=[0, 105])
        st.plotly_chart(base_layout(fig, 420), use_container_width=True)
        st.caption("Weights: Profitability 25% · Cash Flow 20% · Solvency 20% · Liquidity 15% · Efficiency 15% · Growth & Trend 5%")
    with right:
        st.subheader("The verdict")
        st.markdown(
            f"""
            <div class='panel'>
            <p><b style='color:{NIKE};'>Nike scores {NIKE_SCORE} (C — Moderate Risk).</b>
            Its balance sheet is far sturdier — nearly twice the liquidity score and net
            interest income — but the business is stalled: revenue flat two years running,
            operating cash flow less than half of FY2024, and the FY26 profit was propped
            up by a one-off $986M tariff recovery.</p>
            <p><b style='color:{ADI};'>adidas scores {ADI_SCORE} (D — Elevated Risk).</b>
            The engine penalises its thin liquidity, weak 2025 cash conversion and heavier
            lease-loaded balance sheet — but its Growth &amp; Trend score (85 vs 25) is the
            highest in the model: margins, profits and revenue are all moving sharply upward.</p>
            <p class='dim'>One sentence: <b style='color:{TEXT};'>Nike is the stronger company
            today; adidas is the improving one</b> — and the gap is closing.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Trends ---
with tabs[1]:
    cols = st.columns(2)
    for i, (title, (nike_v, adi_v, kind)) in enumerate(TRENDS.items()):
        with cols[i % 2]:
            fig = go.Figure()
            if kind == "bar":
                fig.add_bar(x=YEARS, y=nike_v, name="Nike", marker_color=NIKE)
                fig.add_bar(x=YEARS, y=adi_v, name="adidas", marker_color=ADI)
            else:
                fig.add_scatter(x=YEARS, y=nike_v, name="Nike", mode="lines+markers+text",
                                text=nike_v, textposition="top center",
                                line=dict(color=NIKE, width=3))
                fig.add_scatter(x=YEARS, y=adi_v, name="adidas", mode="lines+markers+text",
                                text=adi_v, textposition="top center",
                                line=dict(color=ADI, width=3))
            fig.update_layout(title=dict(text=title, font=dict(size=15)))
            st.plotly_chart(base_layout(fig), use_container_width=True)
    st.caption("Nike fiscal years end May 31; adidas years end Dec 31. Currency-sensitive charts show each company in its own reporting currency; margin charts are directly comparable.")

# --- Ratios ---
with tabs[2]:
    for cat, rows in RATIOS:
        st.markdown(f"#### {cat}")
        header = f"| Ratio | <span style='color:{NIKE};'>NIKE FY26</span> | <span style='color:{ADI};'>ADIDAS FY25</span> | Edge |"
        table = [header, "|---|---|---|---|"]
        for name, n, a, edge in rows:
            table.append(f"| {name} | {n} | {a} | {edge} |")
        st.markdown("\n".join(table), unsafe_allow_html=True)
    st.caption("* Nike FY2026 cash-flow figures are estimated from disclosed cash movements (full 10-K cash-flow statement pending at time of analysis). Turnover and return ratios use averages of opening and closing balances.")

# --- Strengths & Risks ---
with tabs[3]:
    c1, c2 = st.columns(2)
    for col, co, color in ((c1, "Nike", NIKE), (c2, "adidas", ADI)):
        with col:
            st.markdown(f"<h3 style='color:{color};'>{co.upper()}</h3>", unsafe_allow_html=True)
            st.markdown(f"<b style='color:{OK};'>KEY STRENGTHS</b>", unsafe_allow_html=True)
            for s_ in STRENGTHS[co]:
                st.markdown(f"- {s_}")
            st.markdown(f"<b style='color:{RISK};'>RISK WARNINGS</b>", unsafe_allow_html=True)
            for r_ in RISKS[co]:
                st.markdown(f"- ⚠️ {r_}")

# --- Prediction ---
with tabs[4]:
    c1, c2 = st.columns(2)
    preds = [
        ("NIKE", NIKE, NIKE_SCORE, "62–66 (C → borderline B)", "≈65%", "4.6",
         "Stabilisation. Revenue roughly flat; margin recovery from tariff refunds and cost discipline lifts the score."),
        ("ADIDAS", ADI, ADI_SCORE, "55–60 (D → C)", "≈70%", "3.5",
         "Improvement. High-single-digit growth guided for 2026; cash flow normalises once the World Cup inventory build sells through."),
    ]
    for col, (co, color, now, nxt, conf, z, note) in zip((c1, c2), preds):
        with col:
            st.markdown(
                f"""
                <div class='panel'>
                <h3 style='color:{color}; letter-spacing:2px;'>{co}</h3>
                <table style='width:100%;'><tr>
                <td><div class='dim' style='font-size:11px;'>SCORE TODAY</div>
                    <div style='font-size:34px; font-weight:700;'>{now}</div></td>
                <td><div class='dim' style='font-size:11px;'>PREDICTED (NEXT FY)</div>
                    <div style='font-size:30px; font-weight:700; color:{color};'>{nxt}</div></td>
                </tr></table>
                <p style='margin-top:8px;'>{note}</p>
                <p><b>Confidence:</b> <span style='color:{color};'>{conf}</span>
                &nbsp;&nbsp; <b>Altman Z-Score:</b> <span style='color:{OK};'>{z} — Safe zone</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.info(
        "How predictions are made: a simple trend extrapolation of revenue and margins, "
        "cross-checked against management guidance (adidas: high-single-digit currency-neutral growth "
        "in 2026; Nike: continued 'Sport Offense' reset), plus the Altman Z-Score as a distress screen "
        "(Z above 2.99 = safe zone). Both firms sit safely above the threshold — the risk is about "
        "performance, not survival."
    )

# --- Methodology ---
with tabs[5]:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("The FIE scoring model")
        st.markdown(
            """
            **Step 1 — Ratio scores (0–100).** Each ratio is placed on a scale between a
            sportswear-industry *floor* (score 0) and *target* (score 100), using straight-line
            interpolation. Example: current ratio floor 0.5, target 2.5 → Nike's 1.96 scores 73,
            adidas' 1.32 scores 41.

            **Step 2 — Category scores.** Ratio scores are averaged within each of the six categories.

            **Step 3 — Weights.** Profitability 25% and Cash Flow 20% carry the most weight because,
            for mature consumer brands, margin quality and cash conversion drive value. Solvency 20%
            reflects tariff-era balance-sheet stress. Liquidity 15%; Efficiency 15% (inventory is the
            industry's classic failure point); Growth & Trend 5% captures direction of travel.

            **Step 4 — Rating.** 80–100 A Strong · 65–79 B Good · 50–64 C Moderate Risk ·
            35–49 D Elevated Risk · 0–34 E Critical Risk.
            """
        )
    with c2:
        st.subheader("Category radar")
        cats = [c for c, _, _, _ in CATS]
        fig = go.Figure()
        fig.add_scatterpolar(r=[n for _, _, n, _ in CATS] + [CATS[0][2]],
                             theta=cats + [cats[0]], fill="toself", name="Nike",
                             line=dict(color=NIKE))
        fig.add_scatterpolar(r=[a for _, _, _, a in CATS] + [CATS[0][3]],
                             theta=cats + [cats[0]], fill="toself", name="adidas",
                             line=dict(color=ADI))
        fig.update_layout(
            polar=dict(bgcolor=PANEL,
                       radialaxis=dict(range=[0, 100], color=DIM, gridcolor=LINE),
                       angularaxis=dict(color=DIM, gridcolor=LINE)),
            paper_bgcolor=PANEL, font=dict(color=TEXT),
            legend=dict(orientation="h", y=-0.1), height=380,
            margin=dict(l=40, r=40, t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"<div style='text-align:center; color:{DIM}; font-size:12px; margin-top:20px;'>"
    "Sources: Nike FY2026 Q4 earnings release (June 30, 2026) · adidas Annual Report 2025 (March 2026). "
    "Educational project — not investment advice.</div>",
    unsafe_allow_html=True,
)
