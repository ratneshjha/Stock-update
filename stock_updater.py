import os
import yfinance as yf
import pandas as pd
import json
import requests
from datetime import datetime

def get_nasdaq_universe():
    try:
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        # We add a 'User-Agent' to pretend we are a browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url, headers=headers)
        tables = pd.read_html(response.text)
        
        # Search for the correct table
        for df in tables:
            if 'Ticker' in df.columns:
                return df['Ticker'].tolist()
            if 'Symbol' in df.columns:
                return df['Symbol'].tolist()
        
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"] # Fallback
    except Exception as e:
        print(f"Fetch Error: {e}")
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"]

def evaluate_gems():
    tickers = get_nasdaq_universe()
    results = []
    
    # Scanning top 30 for speed
    for symbol in tickers[:30]: 
        try:
            clean_symbol = str(symbol).replace('.', '-')
            stock = yf.Ticker(clean_symbol)
            info = stock.info
            
            rev_growth = info.get('revenueGrowth', 0)
            roe = info.get('returnOnEquity', 0)
            pe = info.get('forwardPE', 0)
            
            # Weighted Scoring
            score = (rev_growth * 50) + (roe * 50)
            score = max(0, min(100, score))

            results.append({
                "symbol": clean_symbol,
                "name": info.get('shortName', clean_symbol),
                "price": info.get('currentPrice'),
                "score": round(score, 1),
                "metrics": {"Growth": f"{round(rev_growth*100)}%", "PE": pe},
                "tag": "High Growth" if rev_growth > 0.25 else "Value Gem",
                "reason": f"Revenue grew by {round(rev_growth*100)}% this year."
            })
        except:
            continue

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:12]

# Save to the JSON file
output_data = {
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "stocks": evaluate_gems()
}

with open('live_stocks.json', 'w') as f:
    json.dump(output_data, f, indent=4)
