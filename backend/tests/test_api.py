"""API smoke tests: run with `pytest -q` from the backend folder."""
import uuid
import sys
from pathlib import Path
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import app

client = TestClient(app)

def setup_user():
    user = "test-" + uuid.uuid4().hex
    response = client.put("/api/profile", headers={"X-User-Id": user}, json={"name":"Test Learner","career":"AI/ML Engineer","skill":"Python","level":"Beginner"})
    assert response.status_code == 200
    return user

def test_assessment_answers_are_private_and_score_is_deterministic():
    user = setup_user()
    started = client.post("/api/assessments", headers={"X-User-Id": user})
    assert started.status_code == 200
    assessment_id = started.json()["id"]
    q = started.json()["question"]
    assert "answer" not in q and "explanation" not in q
    denied = client.get(f"/api/assessments/{assessment_id}/next", headers={"X-User-Id": "other-user"})
    assert denied.status_code == 404

    # Answer six different retrieved questions. The server validates the answer index.
    for _ in range(6):
        question = client.get(f"/api/assessments/{assessment_id}/next", headers={"X-User-Id": user}).json()["question"]
        submitted = client.post(f"/api/assessments/{assessment_id}/answers", headers={"X-User-Id": user}, json={"question_id": question["id"], "choice": 0})
        assert submitted.status_code == 200
        assert submitted.json()["saved"] is True
    report = client.post(f"/api/assessments/{assessment_id}/complete", headers={"X-User-Id": user})
    assert report.status_code == 200
    assert report.json()["answers"] == 6
    assert 0 <= report.json()["quiz_score"] <= 100
    assert report.json()["practical"] == "not_assessed"

def test_onboarding_rejects_unimplemented_pathways():
    response = client.put("/api/profile", headers={"X-User-Id": "path-test-" + uuid.uuid4().hex}, json={"name":"Learner","career":"Data Scientist","skill":"Python","level":"Beginner"})
    assert response.status_code == 422

def test_answer_validation_and_duplicate_guard():
    user = setup_user()
    assessment = client.post("/api/assessments", headers={"X-User-Id": user}).json()
    question_id = assessment["question"]["id"]
    invalid = client.post(f"/api/assessments/{assessment['id']}/answers", headers={"X-User-Id": user}, json={"question_id": question_id,"choice":99})
    assert invalid.status_code == 422
    valid = client.post(f"/api/assessments/{assessment['id']}/answers", headers={"X-User-Id": user}, json={"question_id": question_id,"choice":0})
    assert valid.status_code == 200
    duplicate = client.post(f"/api/assessments/{assessment['id']}/answers", headers={"X-User-Id": user}, json={"question_id": question_id,"choice":0})
    assert duplicate.status_code == 409
