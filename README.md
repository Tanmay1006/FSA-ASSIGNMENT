# Financial Intelligence Engine — Nike vs Adidas (Streamlit)

Interactive dashboard scoring the financial health of Nike (FY2026, ended May 31, 2026)
and adidas (FY2025, ended Dec 31, 2025).

## How to run

1. Install Python 3.9+ from python.org
2. Open a terminal in this folder and run:

   pip install -r requirements.txt
   streamlit run app.py

3. Your browser opens automatically at http://localhost:8501

## Tabs
- Scoreboard — overall scores (Nike 59/C, adidas 45/D) and category comparison
- Trends — revenue, margins, and operating cash flow (3 years)
- Ratios — all 16 ratios across 5 categories
- Strengths & Risks — engine-generated flags per company
- Prediction — next-year score forecast + Altman Z-Score distress screen
- Methodology — the scoring model and category radar

Educational project — not investment advice.
