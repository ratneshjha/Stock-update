import os
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def get_nasdaq_universe():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    return pd.read_html(url)[4]['Ticker'].tolist()

def evaluate_gems():
    tickers = get_nasdaq_universe()
    results = []

    for symbol in tickers[:40]: # Scanning top 40 for speed & reliability
        try:
            stock = yf.Ticker(symbol.replace('.', '-'))
            info = stock.info
            
            # --- EVALUATION CRITERIA ---
            # 1. Growth: Revenue & Earnings
            rev_growth = info.get('revenueGrowth', 0)
            # 2. Valuation: PEG & PE
            peg = info.get('pegRatio', 2)
            # 3. Health: ROE & Debt
            roe = info.get('returnOnEquity', 0)
            # 4. Sentiment: Analyst Score (1=Buy, 5=Sell)
            rating = info.get('recommendationMean', 3)

            # --- THE "GEM" SCORE (0-100) ---
            score = (rev_growth * 40) + (roe * 30) + ((2 - peg) * 10) + ((5 - rating) * 5)
            score = max(0, min(100, score)) # Keep between 0-100

            results.append({
                "symbol": symbol,
                "name": info.get('shortName', symbol),
                "price": info.get('currentPrice'),
                "score": round(score, 1),
                "growth": f"{round(rev_growth * 100, 1)}%",
                "tag": "🔥 High Growth" if rev_growth > 0.25 else "💎 Value Gem",
                "reason": f"Strong ROE of {round(roe*100)}% and Analyst Rating of {rating}"
            })
        except: continue

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:12]

# Save for the website
data = {"last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "stocks": evaluate_gems()}
with open('live_stocks.json', 'w') as f:
    json.dump(data, f, indent=4)