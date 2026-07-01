from app.services.vitoria import parse_objective, parse_yes_no


def test_parse_objective():
    assert parse_objective("quero investir") == "investimento"
    assert parse_objective("construir daqui dois anos") == "construção futura"
    assert parse_objective("morar com a família") == "moradia"


def test_parse_yes_no():
    assert parse_yes_no("sim, já conhece") is True
    assert parse_yes_no("não") is False
