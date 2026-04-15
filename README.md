# vibepin

Shop the look you saved. Find it. Match it. Wear it.

## Features

- **Find** — paste a Pinterest pin or screenshot, get real shoppable links
- **Match** — enter your Pinterest username to analyse your aesthetic and get style recommendations
- **Wear** — virtual try-on using AI

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Copy `.env.example` to `.env` and fill in your API keys
4. Run:
   ```bash
   python3.10 -m uvicorn vibepin.main:app --reload
   ```
5. Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Environment Variables

| Variable | Description |
|---|---|
| `SERPAPI_KEY` | [SerpAPI](https://serpapi.com) key for Google Images search |
| `IMGBB_KEY` | [imgbb](https://imgbb.com) key for image hosting |
| `REPLICATE_API_TOKEN` | [Replicate](https://replicate.com) token for virtual try-on |

## Stack

Python, FastAPI, CLIP, Replicate IDM-VTON, SerpAPI
