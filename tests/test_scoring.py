from app.services.scoring import score_lead


def test_hot_investor_score():
    result = score_lead(
        {
            "objective": "investir",
            "purchase_timeline": "decidir esse mês",
            "budget_entry": "30 mil de entrada",
            "budget_installment": "parcela até 1800",
            "knows_development": True,
            "source": "indicação",
            "main_objection": "segurança do investimento",
        }
    )
    assert result.score >= 75
    assert result.temperature == "quente"


def test_cold_unqualified_score():
    result = score_lead({"objective": "não sei", "purchase_timeline": "sem pressa"})
    assert result.temperature == "frio"
