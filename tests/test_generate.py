import pytest

import app as app_module


@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


def test_generate_returns_recommendation_and_normalized_input(client, monkeypatch):
    captured_prompts = []

    def fake_generate_recommendation(prompt):
        captured_prompts.append(prompt)
        return "Visit the museum and Sky Tower."

    monkeypatch.setattr(
        app_module,
        "generate_recommendation",
        fake_generate_recommendation,
    )

    response = client.post(
        "/generate",
        json={
            "location": " Auckland ",
            "weather": " rainy ",
            "temperature": 16,
            "places": [" Museum ", "Sky Tower"],
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "recommendation": "Visit the museum and Sky Tower.",
        "model": app_module.GROQ_MODEL,
        "input": {
            "location": "Auckland",
            "weather": "rainy",
            "temperature": 16,
            "places": ["Museum", "Sky Tower"],
        },
    }

    assert len(captured_prompts) == 1
    prompt = captured_prompts[0]
    assert "- Location: Auckland" in prompt
    assert "- Weather: rainy" in prompt
    assert f"- Temperature: 16{chr(176)}C" in prompt
    assert "- Candidate places: Museum, Sky Tower" in prompt
    assert "Avoid outdoor suggestions if the weather is poor." in prompt


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        (
            {"weather": "rainy", "temperature": 16, "places": ["Museum"]},
            "Missing required field: location",
        ),
        (
            {"location": " ", "weather": "rainy", "temperature": 16, "places": ["Museum"]},
            "Field 'location' must be a non-empty string",
        ),
        (
            {"location": "Auckland", "weather": "", "temperature": 16, "places": ["Museum"]},
            "Field 'weather' must be a non-empty string",
        ),
        (
            {
                "location": "Auckland",
                "weather": "rainy",
                "temperature": "16",
                "places": ["Museum"],
            },
            "Field 'temperature' must be a number",
        ),
        (
            {
                "location": "Auckland",
                "weather": "rainy",
                "temperature": True,
                "places": ["Museum"],
            },
            "Field 'temperature' must be a number",
        ),
        (
            {"location": "Auckland", "weather": "rainy", "temperature": 16, "places": []},
            "Field 'places' must be a non-empty array",
        ),
        (
            {"location": "Auckland", "weather": "rainy", "temperature": 16, "places": [" "]},
            "Field 'places' must contain only non-empty strings",
        ),
    ],
)
def test_generate_rejects_invalid_payloads(
    client,
    monkeypatch,
    payload,
    expected_error,
):
    def fail_if_called(prompt):
        raise AssertionError("generate_recommendation should not be called")

    monkeypatch.setattr(app_module, "generate_recommendation", fail_if_called)

    response = client.post("/generate", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": expected_error}


def test_generate_rejects_non_json_request_body(client, monkeypatch):
    def fail_if_called(prompt):
        raise AssertionError("generate_recommendation should not be called")

    monkeypatch.setattr(app_module, "generate_recommendation", fail_if_called)

    response = client.post(
        "/generate",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object"}


def test_generate_returns_service_error_response(client, monkeypatch):
    def raise_service_error(prompt):
        raise app_module.RecommendationServiceError("Groq request timed out.", 504)

    monkeypatch.setattr(app_module, "generate_recommendation", raise_service_error)

    response = client.post(
        "/generate",
        json={
            "location": "Auckland",
            "weather": "rainy",
            "temperature": 16,
            "places": ["Museum"],
        },
    )

    assert response.status_code == 504
    assert response.get_json() == {"error": "Groq request timed out."}


def test_generate_returns_generic_error_response(client, monkeypatch):
    def raise_unexpected_error(prompt):
        raise RuntimeError("boom")

    monkeypatch.setattr(app_module, "generate_recommendation", raise_unexpected_error)

    response = client.post(
        "/generate",
        json={
            "location": "Auckland",
            "weather": "rainy",
            "temperature": 16,
            "places": ["Museum"],
        },
    )

    assert response.status_code == 502
    assert response.get_json() == {"error": "Failed to generate recommendation"}
