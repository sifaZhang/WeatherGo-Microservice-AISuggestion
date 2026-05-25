# WeatherGo-Microservice-AISuggestion

## Setup

Create a local `.env` file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The application loads `GROQ_API_KEY` from the environment at runtime. Do not
commit `.env` or hard-code the API key in the repository.

Install dependencies and run the service:

```bash
pip install -r requirements.txt
python app.py
```

## API

### Health Check

```http
GET /health
```

Successful response:

```json
{
  "status": "ok"
}
```

### Generate Recommendation

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
