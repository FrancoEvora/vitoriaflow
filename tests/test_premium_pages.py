from fastapi.testclient import TestClient

from app.main import app

AUTH = ("evora", "leadflow-demo")


def test_premium_pages_render():
    with TestClient(app) as client:
        for path in ["/", "/leads", "/vitoria", "/materiais", "/relatorios", "/corretores", "/empreendimentos", "/configuracoes"]:
            response = client.get(path, auth=AUTH)
            assert response.status_code == 200
            assert "Évora LeadFlow" in response.text


def test_vitoria_simulated_whatsapp_message():
    with TestClient(app) as client:
        response = client.post(
            "/api/simulate-message",
            json={"from_phone": "5516999999999", "text": "tenho um lead", "profile_name": "Lucas Andrade"},
            auth=AUTH,
        )
        assert response.status_code == 200
        assert "Lead" in response.json()["reply"] or "lead" in response.json()["reply"]
