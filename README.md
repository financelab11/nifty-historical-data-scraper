# Nifty Historical Data Strategy Hub

This project is a comprehensive analysis platform for the Indian equity market, providing 20.6 years of high-fidelity historical data (starting from 1 April 2005) for the entire Nifty ecosystem.

## Features

- **Official Data Source:** All data is scraped directly from [niftyindices.com](https://www.niftyindices.com/reports/historical-data), ensuring institutional-grade accuracy.
- **Comprehensive Coverage:**
  - **Market Benchmarks:** Nifty 50, Nifty Next 50, Nifty 500, Nifty Total Market.
  - **Mid & Small Cap:** Nifty Midcap 150, Nifty Smallcap 250, Nifty Smallcap 500, Nifty Microcap 250.
  - **Factor Indices:** Momentum 50, Quality 50, Value 50, Low Volatility 50.
- **Deep Historical Insights:** Data spans over 20 years, capturing multiple market cycles.
- **Real-time Analysis:** Interactive charts and CAGR calculations for performance benchmarking.

## Getting Started

### Prerequisites

- [Supabase](https://supabase.com) project for data storage.
- Python 3.10+ with `nsepython` and `pandas`.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/financelab11/nifty-historical-data-scraper.git
   ```

2. Install dependencies:
   ```bash
   bun install
   # or npm install
   ```

3. Configure environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. Populate the database (optional, if you want to re-scrape):
   ```bash
   python fetch_all_indices.py
   python upload_to_supabase.py
   ```

5. Start the development server:
   ```bash
   bun dev
   ```

## Tech Stack

- **Frontend:** Next.js, Tailwind CSS, Recharts, Framer Motion.
- **Backend/Database:** Supabase.
- **Data Pipeline:** Python (nsepython, pandas).

## License

MIT
