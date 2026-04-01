import os
import yfinance as yf
import pandas as pd
import json
import requests
from datetime import datetime

def get_market_universe():
    """Scrapes 600+ stocks to find the best 20 hidden gems."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    tickers = []
    try:
        # Pulling Nasdaq 100
        n_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        n_resp = requests.get(n_url, headers=headers)
        tickers += pd.read_html(n_resp.text)[4]['Ticker'].tolist()
        
        # Pulling S&P 500 for a wider search area
        s_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        s_resp = requests.get(s_url, headers=headers)
        tickers += pd.read_html(s_resp.text)[0]['Symbol'].tolist()
        
        return list(set(tickers)) # Remove duplicates
    except Exception as e:
        print(f"Fetch Error: {e}")
        return ["AAPL", "MSFT", "NVDA"] # Minimal fallback

def evaluate_hidden_gems():
    universe = get_market_universe()
    gems = []

    print(f"🔍 Screening {len(universe)} stocks for Hidden Gems...")

    for symbol in universe:
        try:
            clean_symbol = str(symbol).replace('.', '-')
            stock = yf.Ticker(clean_symbol)
            info = stock.info
            
            # --- THE "HIDDEN GEM" FILTERS ---
            price = info.get('currentPrice', 1000)
            mkt_cap = info.get('marketCap', 0)
            peg = info.get('pegRatio', 5)
            roe = info.get('returnOnEquity', 0)
            pe = info.get('forwardPE', 100)

            # Logic: Price < $50 AND Market Cap > $5B
            if price < 50 and mkt_cap > 5000000000:
                
                # Scoring for "Hidden Value" (Higher ROE + Lower PEG)
                # We reward stocks where Growth > Price
                score = (roe * 250) + ((2 - peg) * 20)
                
                # Bonus if P/E is under 15 (Classic Value)
                if 0 < pe < 15: score += 15
                
                score = max(40, min(98.5, score))

                gems.append({
                    "symbol": clean_symbol,
                    "name": info.get('shortName', clean_symbol),
                    "price": price,
                    "score": round(score, 1),
                    "metrics": {
                        "PEG": peg if peg else "N/A",
                        "ROE": f"{round(roe*100)}%",
                        "PE": round(pe, 1) if pe else "N/A"
                    },
                    "tag": "Hidden Value" if pe < 18 else "Growth Gem",
                    "reason": f"Market Cap: ${round(mkt_cap/1e9, 1)}B | PEG: {peg}"
                })
        except: continue

    # Sort by score and take the Top 20
    gems.sort(key=lambda x: x['score'], reverse=True)
    return gems[:20]

if __name__ == "__main__":
    final_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stocks": evaluate_hidden_gems()
    }
    with open('live_stocks.json', 'w') as f:
        json.dump(final_data, f, indent=4)
