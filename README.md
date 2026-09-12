# AI Travel Planning Assistant

A small Singapore-focused travel assistant built around RAG and MCP tools.

## What it does

- Answers Singapore travel questions from a local knowledge base.
- Uses retrieval to ground destination facts and provides source links.
- Calls an MCP weather tool for current forecasts.
- Calls an MCP currency tool for live conversion.
- Combines retrieved travel information and both tools for weather-aware planning.
- Keeps conversation context in the Streamlit session.

## Project layout

```text
app/                Streamlit app, RAG pipeline and MCP client
mcp/                MCP server with weather + currency tools
data/kb/            Travel knowledge base
tests/              Small routing tests
.github/workflows/  CI
```

## Request flow

1. The Streamlit app receives a user message.
2. The request is checked for weather and currency intents.
3. Relevant Singapore documents are retrieved from Chroma using HuggingFace embeddings.
4. MCP tools are called when the question needs live weather or exchange rates.
5. The final answer is generated using the retrieved context, tool results and recent conversation history.

Stable destination facts come from the KB. Time-sensitive weather and currency values come from the MCP tools.

## Knowledge base

The initial KB contains short, source-linked notes based on:

- Visit Singapore — https://www.visitsingapore.com/
- Visit Singapore trip planning — https://www.visitsingapore.com/mice/en/tools-and-resources/plan-your-trip/
- Wikivoyage Singapore — https://en.wikivoyage.org/wiki/Singapore

The notes are intentionally compact instead of copying large sections of the source sites.

## MCP tools

`mcp/travel_mcp_server.py` exposes:

- `get_weather_forecast(location, days)` — Open-Meteo geocoding + forecast.
- `convert_currency(amount, from_currency, to_currency)` — Frankfurter latest exchange rate.

The client uses `langchain-mcp-adapters` over stdio so the assistant can invoke the same tools from the application.

## Run locally

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in `.env`, then build the local vector store:

```bash
python -m app.ingest
```

Start the app:

```bash
streamlit run app/main.py
```

## Demo questions

1. What are the must-visit attractions in Singapore?
2. Which neighbourhoods are good for a cultural experience?
3. What is the weather forecast for Singapore for the next 3 days?
4. Convert INR 60,000 to SGD.
5. I have INR 60,000. Plan a three-day Singapore trip and adjust outdoor activities if rain is expected.
6. Make it suitable for two adults and one child, with more indoor activities.

The last question uses the context from the previous turns.

## Notes

The assistant is intentionally limited to travel planning. It does not perform bookings, payments, reservations or route navigation.
