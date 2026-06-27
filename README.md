# API Usage Tracker Dashboard 📊

## Problem We're Solving
- Companies give API keys to employees
- Some employees share keys with friends/relatives
- Friends use it for personal projects informally
- Company gets surprise bills at end of month
- No way to know WHO caused the extra usage

## Our Solution
- Every API call gets logged automatically
- Dashboard shows who used what and when
- Manager can see unusual patterns instantly
- Warning alerts when spending limit approached
- Security alerts for unauthorized access

## How It Works — 4 Components

### Component 1 — API Key Manager (api_keys.json)
- Assigns unique keys to each employee
- Each key linked to name, department, monthly limit
- Example: "emp001" → Rahul Sharma, Engineering, $10 limit

### Component 2 — Usage Logger (logger.py)
- Every API call gets logged automatically
- Tracks: who called, when, tokens used, cost
- Flags unknown keys as security threat
- Saves everything to usage_logs.csv

### Component 3 — Database (usage_logs.csv)
- Stores all logs permanently
- Pandas reads and analyses the data
- Never overwrites — always appends new data

### Component 4 — Streamlit Dashboard (main.py)
- 5 page clean dashboard with green theme
- Page 1 — Home: total calls, cost, warnings
- Page 2 — Employee Usage: individual details
- Page 3 — Leaderboard: neutral usage ranking
- Page 4 — Security Alerts: unauthorized access
- Page 5 — Analytics: charts and visualizations

## Features
- ✅ Real time usage tracking
- ✅ Day / Week / Month filters
- ✅ Spending limit warnings at 80%
- ✅ Security alerts for unknown API keys
- ✅ Department wise cost breakdown
- ✅ Individual employee call history
- ✅ 4 interactive charts

## Tech Stack
- Python
- Pandas
- Streamlit
- Plotly
- JSON + CSV

## Setup
1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Add employees to api_keys.json
4. Run dashboard:
   python -m streamlit run main.py

## Project Structure
api-usage-tracker/
├── api_keys.json      # Employee database
├── logger.py          # API call logger
├── main.py            # Streamlit dashboard
├── usage_logs.csv     # Usage data storage
├── requirements.txt   # Dependencies
├── README.md          # Documentation
└── .env               # API keys (not pushed to GitHub)

## Future Improvements
- PostgreSQL database instead of CSV
- Real time webhooks for instant alerts
- Email notifications when limit exceeded
- OAuth2 authentication with company Google account
- IP whitelisting for extra security
- Cloud deployment on AWS/GCP









