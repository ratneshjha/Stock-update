import os
import yfinance as yf
import pandas as pd
import json
import requests
from datetime import datetime

def get_nasdaq_universe():
    try:
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        # Identify as a browser to avoid 403 Forbidden Error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        tables = pd.read_html(response.text)
        
        # Search for the correct table with Tickers
        for df in tables:
            if 'Ticker' in df.columns:
                return df['Ticker'].tolist()
        
        # Fallback list if scraping fails
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "COST", "NFLX", "AMD", "PEP"]
    except Exception as e:
        print(f"Fetch Error: {e}")
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "COST", "NFLX", "AMD", "PEP"]

def evaluate_gems():
    tickers = get_nasdaq_universe()
    results = []
    
    # Scanning top 35 for best balance of speed/results
    for symbol in tickers[:35]: 
        try:
            clean_symbol = str(symbol).replace('.', '-')
            stock = yf.Ticker(clean_symbol)
            info = stock.info
            
            # --- EVALUATION CRITERIA ---
            rev_growth = info.get('revenueGrowth', 0)
            roe = info.get('returnOnEquity', 0)
            pe = info.get('forwardPE', 0)
            peg = info.get('pegRatio', 1.5)
            rating = info.get('recommendationMean', 3) # 1=Buy, 5=Sell

            # --- THE "GEM" SCORE (0-100) ---
            # Weighting: Growth (40%), ROE (30%), Valuation (20%), Sentiment (10%)
            score = (rev_growth * 400) + (roe * 300) + ((2 - peg) * 10) + ((5 - rating) * 2)
            score = max(0, min(100, score))

            results.append({
                "symbol": clean_symbol,
                "name": info.get('shortName', clean_symbol),
                "price": info.get('currentPrice'),
                "score": round(score, 1),
                "metrics": {
                    "Growth": f"{round(rev_growth * 100, 1)}%",
                    "PE": round(pe, 1),
                    "ROE": f"{round(roe * 100, 1)}%"
                },
                "tag": "🔥 Momentum" if rev_growth > 0.25 else "💎 Value Gem",
                "reason": f"Revenue Growth: {round(rev_growth*100)}% | ROE: {round(roe*100)}%"
            })
        except:
            continue

    # Sort by score and take Top 12
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:12]

# Main execution
if __name__ == "__main__":
    final_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stocks": evaluate_gems()
    }

    with open('live_stocks.json', 'w') as f:
        json.dump(final_data, f, indent=4)
    print("Successfully updated live_stocks.json")
