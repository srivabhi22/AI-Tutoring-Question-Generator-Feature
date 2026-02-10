from fastapi.testclient import TestClient

from interfaces import api


class FakePipeline:
    def run(self, request: api.GenerateRequest) -> api.GenerateResponse:
        return api.GenerateResponse(
            questions={"mcq": []},
            solutions={"mcq": []},
            evaluation={"overall_feedback": "ok", "mcq": [], "short_answer": [], "long_answer": []},
            diagnostics={"events": [], "fallbacks": [], "retries": {}, "timings_ms": {}},
        )


def test_health_endpoint():
    client = TestClient(api.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_endpoint(monkeypatch):
    def fake_get_pipeline():
        return FakePipeline()

    api.app.dependency_overrides[api.get_pipeline] = fake_get_pipeline
    client = TestClient(api.app)

    files = {"image": ("test.png", b"fake", "image/png")}
    data = {"class": "11", "board": "CBSE", "target_exam": "NEET"}
    response = client.post("/generate", data=data, files=files)
    assert response.status_code == 200
    body = response.json()
    assert "questions" in body
    assert "solutions" in body
    assert "evaluation" in body
    assert "diagnostics" in body

    api.app.dependency_overrides = {}
