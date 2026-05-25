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
