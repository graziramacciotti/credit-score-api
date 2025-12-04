# API de Score de Crédito

API REST para cálculo de score de crédito desenvolvida com FastAPI.

**Projeto desenvolvido para aprendizado**

---

## Tecnologias

- Python 3.13
- FastAPI
- Pydantic
- Pytest

---

## Instalação

```bash

git clone https://github.com/graziramacciotti/credit-score-api.git
cd credit-score-api

python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Execução

```bash
python main.py
```

Acesse: http://localhost:8000/docs

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Status da API |
| POST | `/score/calcular` | Calcular score de crédito |
| GET | `/score/historico` | Listar consultas realizadas |

---

## Exemplo de Uso

**Requisição:**
```json
{
  "nome": "Maria Silva",
  "idade": 30,
  "renda_mensal": 5000.00,
  "dividas_totais": 1500.00,
  "historico_pagamentos": "em_dia",
  "tempo_primeiro_credito_meses": 36,
  "consultas_ultimos_6_meses": 2,
  "quantidade_contas_bancarias": 2
}
```

**Resposta:**
```json
{
  "score": 870,
  "nivel_risco": "baixo",
  "mensagem": "🟢 Excelente! Perfil muito saudável."
}
```

---

## Como o Score é Calculado

| Fator | Peso |
|-------|------|
| Histórico de Pagamentos | 30% |
| Taxa de Endividamento | 25% |
| Renda Mensal | 20% |
| Tempo de Histórico | 15% |
| Consultas Recentes | 10% |

---

## Classificação de Risco

| Score | Risco |
|-------|-------|
| 800-1000 | 🟢 Baixo |
| 600-799 | 🟡 Médio |
| 400-599 | 🟠 Alto |
| 0-399 | 🔴 Muito Alto |

---

## Executar Testes

```bash
pytest tests/test_main.py -v
```

---


**Grazi Ramacciotti**

---

