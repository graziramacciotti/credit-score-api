"""Testes da API de Score de Crédito"""

import pytest
from fastapi.testclient import TestClient
from main import app, historico_consultas

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpar():
    historico_consultas.clear()
    yield
    historico_consultas.clear()


@pytest.fixture
def cliente_bom():
    return {
        "nome": "Maria Silva",
        "idade": 35,
        "renda_mensal": 8000,
        "dividas_totais": 1500,
        "historico_pagamentos": "em_dia",
        "tempo_primeiro_credito_meses": 72,
        "consultas_ultimos_6_meses": 1
    }


@pytest.fixture
def cliente_ruim():
    return {
        "nome": "João Teste",
        "idade": 22,
        "renda_mensal": 1500,
        "dividas_totais": 5000,
        "historico_pagamentos": "inadimplente",
        "tempo_primeiro_credito_meses": 3,
        "consultas_ultimos_6_meses": 10
    }


def test_raiz():
    r = client.get("/")
    assert r.status_code == 200
    assert "mensagem" in r.json()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "online"


def test_score_cliente_bom(cliente_bom):
    r = client.post("/score/calcular", json=cliente_bom)
    data = r.json()
    assert r.status_code == 200
    assert data["score"] >= 700
    assert data["nivel_risco"] == "baixo"


def test_score_cliente_ruim(cliente_ruim):
    r = client.post("/score/calcular", json=cliente_ruim)
    data = r.json()
    assert r.status_code == 200
    assert data["score"] < 400
    assert data["nivel_risco"] in ["alto", "muito_alto"]


def test_idade_invalida(cliente_bom):
    cliente_bom["idade"] = 17
    r = client.post("/score/calcular", json=cliente_bom)
    assert r.status_code == 422


def test_nome_curto(cliente_bom):
    cliente_bom["nome"] = "AB"
    r = client.post("/score/calcular", json=cliente_bom)
    assert r.status_code == 422


def test_renda_negativa(cliente_bom):
    cliente_bom["renda_mensal"] = -100
    r = client.post("/score/calcular", json=cliente_bom)
    assert r.status_code == 422


def test_historico_vazio():
    r = client.get("/score/historico")
    assert r.status_code == 200
    assert r.json() == []


def test_historico_com_consulta(cliente_bom):
    client.post("/score/calcular", json=cliente_bom)
    r = client.get("/score/historico")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_score_maximo():
    cliente = {
        "nome": "Perfeito",
        "idade": 40,
        "renda_mensal": 20000,
        "dividas_totais": 0,
        "historico_pagamentos": "em_dia",
        "tempo_primeiro_credito_meses": 120,
        "consultas_ultimos_6_meses": 0
    }
    r = client.post("/score/calcular", json=cliente)
    assert r.json()["score"] <= 1000


def test_score_minimo():
    cliente = {
        "nome": "Critico",
        "idade": 18,
        "renda_mensal": 100,
        "dividas_totais": 50000,
        "historico_pagamentos": "inadimplente",
        "tempo_primeiro_credito_meses": 0,
        "consultas_ultimos_6_meses": 50
    }
    r = client.post("/score/calcular", json=cliente)
    assert r.json()["score"] >= 0
