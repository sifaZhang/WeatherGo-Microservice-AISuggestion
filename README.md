# WeatherGo-Microservice-AISuggestion

Flask microservice for generating local activity recommendations from weather
conditions, temperature, and candidate places. The service calls Groq using the
`llama-3.1-8b-instant` model.

## Requirements

- Python 3.12
- `pip`
- Groq API key for live `/generate` requests
- Docker, optional

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The application loads `GROQ_API_KEY` from the environment at runtime. Do not
commit `.env` or hard-code the API key in the repository.

Run the service:

```bash
python app.py
```

By default the service runs at `http://localhost:5001`.

## Test Locally

Run the test suite:

```bash
pytest
```

The tests mock recommendation generation, so they do not require a valid
`GROQ_API_KEY` and do not call the live Groq API.

To manually check the running service:

```bash
curl http://localhost:5001/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Docker

Build the image:

```bash
docker build -t weathergo-ai-suggestion .
```

Run the container on port 5001:

```bash
docker run --env-file .env -p 5001:5001 weathergo-ai-suggestion
```

Then open `http://localhost:5001/health` or call the API with `curl`.

## API

### `GET /`

Basic smoke test endpoint.

Successful response:

```text
API Works!
```

### `GET /health`

```http
GET /health
```

Successful response:

```json
{
  "status": "ok"
}
```

### `POST /generate`

```http
POST /generate
Content-Type: application/json
```

Request body:

```json
{
  "location": "Auckland",
  "weather": "rainy",
  "temperature": 16,
  "places": ["Auckland War Memorial Museum", "Sky Tower", "Cornwall Park"]
}
```

Example `curl` request:

```bash
curl -X POST http://localhost:5001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Auckland",
    "weather": "rainy",
    "temperature": 16,
    "places": ["Auckland War Memorial Museum", "Sky Tower", "Cornwall Park"]
  }'
```

Successful response:

```json
{
  "recommendation": "Visit Auckland War Memorial Museum or Sky Tower, since they are indoor-friendly options for rainy weather.",
  "model": "llama-3.1-8b-instant",
  "input": {
    "location": "Auckland",
    "weather": "rainy",
    "temperature": 16,
    "places": ["Auckland War Memorial Museum", "Sky Tower", "Cornwall Park"]
  }
}
```

Error response:

```json
{
  "error": "Missing required field: weather"
}
```

Groq-related errors are returned as JSON instead of crashing the service:

```json
{
  "error": "Groq request timed out. Please try again later."
}
```

Common Groq error status codes:

- `429`: Groq rate limit exceeded
- `502`: Groq service returned an error or an empty recommendation
- `503`: Unable to connect to Groq
- `504`: Groq request timed out

## Project Structure

```text
.
├── app.py
├── Dockerfile
├── README.md
├── requirements.txt
└── tests/
    ├── conftest.py
    └── test_generate.py
```
