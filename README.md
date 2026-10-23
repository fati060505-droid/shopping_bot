# Product Helper

Describe a product, its specs, or a problem ("my phone battery dies by evening"). The app finds candidates,
ranks them by your price / features / reviews priorities, and an AI advisor tells you what it would buy.
Everything runs on free tiers, with no database.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

It works immediately on demo data with no keys. Verify the core logic offline: `python -m tests.smoke_test`.

## Add your keys (`.env`)

| Key | Where to get it | Free allowance |
|---|---|---|
| `GROQ_API_KEY` | console.groq.com/keys | Free tier, rate limited |
| `SERPER_API_KEY` | serper.dev | Free credits on signup (one time) |
| `SERPAPI_API_KEY` | serpapi.com | 100 searches per month |

Add a Groq key for the AI advisor, plus one search key for live products. Check each provider's current limits.
Non-secret settings (region, models, quotas) live in `settings.env`. Set `SEARCH_COUNTRY` (us, uk, pk, in, ae...)
and `CURRENCY_SYMBOL` for your market.

## How it flows

1. Intent parser (Groq 8B): free text becomes a search query, budget and must-have specs.
2. Product source: Serper or SerpApi Google Shopping, falling back to demo data. Results are cached for an hour.
3. Ranking (plain Python): price, features and Bayesian-adjusted reviews, weighted by the sidebar sliders.
4. Advisor (Groq 70B) plus RAG: reads the ranked data and your buying-guide notes in `rag/kb/`, then gives its own opinion.

Free-quota protection: caching, a per-session search cap (`MAX_SEARCHES_PER_SESSION`), the small model for cheap steps,
and graceful fallbacks if a limit is hit.

## Customize

- Add buying guides: drop `.md` files with `## ` sections into `rag/kb/`.
- Add a data source: write `sources/yours.py` returning `list[Product]`, then register it in `sources/__init__.py`.
- CrewAI: `pip install crewai`, set `USE_CREWAI=true`. The two LLM steps then run as CrewAI agents.
- Colors: `.streamlit/config.toml` and the variables at the top of `ui/styles.py`.

## Deploy free (Streamlit Community Cloud)

1. Push this folder to a public GitHub repo. `.env` is git-ignored, so keys stay private.
2. Create the app on share.streamlit.io and point it to `app.py`.
3. In the app's Secrets panel, paste `GROQ_API_KEY = "..."` and `SERPER_API_KEY = "..."`.

## Structure

```
app.py            Streamlit UI and orchestration
config.py         loads .env and settings.env
agents/           llm.py (Groq or CrewAI), intent.py, advisor.py
sources/          serper.py, serpapi.py, mock.py, models.py
ranking/scorer.py weighted scoring
rag/              kb.py + kb/*.md buying guides
ui/               styles.py, components.py
data/             mock_products.json
tests/            smoke_test.py
```

Notes: prices and ratings come from search results and can be stale, so confirm on the store page.
Demo links are placeholders and are not real listings.
