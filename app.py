import flask

app = flask.Flask(__name__)


@app.route('/')
def index():
    return 'API Works!'


@app.route('/health')
def health():
    return flask.jsonify({"status": "ok"}), 200


def validate_generate_payload(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    required_fields = ["location", "weather", "temperature", "places"]
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"

    if not isinstance(data["location"], str) or not data["location"].strip():
        return "Field 'location' must be a non-empty string"

    if not isinstance(data["weather"], str) or not data["weather"].strip():
        return "Field 'weather' must be a non-empty string"

    if not isinstance(data["temperature"], (int, float)):
        return "Field 'temperature' must be a number"

    if isinstance(data["temperature"], bool):
        return "Field 'temperature' must be a number"

    if not isinstance(data["places"], list) or not data["places"]:
        return "Field 'places' must be a non-empty array"

    for place in data["places"]:
        if not isinstance(place, str) or not place.strip():
            return "Field 'places' must contain only non-empty strings"

    return None


def build_prompt(location, weather, temperature, places):
    place_list = ", ".join(place.strip() for place in places)

    return (
        "You are a local activity recommendation assistant.\n\n"
        "User context:\n"
        f"- Location: {location.strip()}\n"
        f"- Weather: {weather.strip()}\n"
        f"- Temperature: {temperature}°C\n"
        f"- Candidate places: {place_list}\n\n"
        "Task:\n"
        "Recommend suitable places or activities based on the weather and temperature.\n"
        "Avoid outdoor suggestions if the weather is poor.\n"
        "Return concise, practical suggestions."
    )


@app.route('/generate', methods=['POST'])
def generate():
    data = flask.request.get_json(silent=True)
    error = validate_generate_payload(data)

    if error:
        return flask.jsonify({"error": error}), 400

    prompt = build_prompt(
        data["location"],
        data["weather"],
        data["temperature"],
        data["places"],
    )

    return flask.jsonify({
        "prompt": prompt,
        "input": {
            "location": data["location"].strip(),
            "weather": data["weather"].strip(),
            "temperature": data["temperature"],
            "places": [place.strip() for place in data["places"]],
        },
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
