import pytest
from fastapi.testclient import TestClient
from main import app, historico_consultas

client = TestClient(app)


@pytest.fixture
def cliente_bom():
    return {
        "nome": "Maria Santos",
        "idade": 35,
        "renda_mensal": 8000.00,
        "dividas_totais": 1500.00,
        "historico_pagamentos": "em_dia",
        "tempo_primeiro_credito_meses": 72,
        "consultas_ultimos_6_meses": 1,
        "quantidade_contas_bancarias": 2
    }


@pytest.fixture
def cliente_ruim():
    return {
        "nome": "João Devedor",
        "idade": 25,
        "renda_mensal": 1500.00,
        "dividas_totais": 5000.00,
        "historico_pagamentos": "inadimplente",
        "tempo_primeiro_credito_meses": 3,
        "consultas_ultimos_6_meses": 10,
        "quantidade_contas_bancarias": 1
    }


@pytest.fixture(autouse=True)
def limpar_historico():
    historico_consultas.clear()
    yield
    historico_consultas.clear()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensagem" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_calcular_score_cliente_bom(cliente_bom):
    response = client.post("/score/calcular", json=cliente_bom)
    data = response.json()
    
    assert response.status_code == 200
    assert data["score"] >= 700
    assert data["nivel_risco"] == "baixo"


def test_calcular_score_cliente_ruim(cliente_ruim):
    response = client.post("/score/calcular", json=cliente_ruim)
    data = response.json()
    
    assert response.status_code == 200
    assert data["score"] < 500
    assert data["nivel_risco"] in ["alto", "muito_alto"]


def test_validacao_idade_invalida(cliente_bom):
    cliente_bom["idade"] = 17
    response = client.post("/score/calcular", json=cliente_bom)
    assert response.status_code == 422


def test_historico(cliente_bom):
    client.post("/score/calcular", json=cliente_bom)
    response = client.get("/score/historico")
    assert response.status_code == 200
    assert len(response.json()) == 1