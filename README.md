# Credit Score API

REST API for credit score simulation built with FastAPI. Receives a client's financial data and returns a score from 0 to 1000, risk level, analysis factors, and recommendations.

This project is the core engine of the [Credit Score Ecosystem](https://github.com/graziramacciotti) -> a set of four connected projects demonstrating a complete data workflow.

> *Note: Variable names and API responses are in Portuguese as this project simulates the Brazilian credit scoring context.*

## Ecosystem

| Project | Description |
|---------|-------------|
| **Credit Score API** (this) | REST API with scoring logic |
| [Credit Score Analysis](https://github.com/graziramacciotti/credit-score-analysis) | EDA and predictive modeling |
| [Credit Score ETL](https://github.com/graziramacciotti/credit-score-etl) | Batch pipeline with SQLite |
| [Credit Score Dashboard](https://github.com/graziramacciotti/credit-score-dashboard) | Interactive Streamlit dashboard |

## Tech Stack

- Python 3.13
- FastAPI
- Pydantic
- Pytest

## Setup

```bash
git clone https://github.com/graziramacciotti/credit-score-api.git
cd credit-score-api
python -m venv venv

# Windows
.\venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Access the interactive docs at: http://localhost:8000/docs

## Web Interface

The project includes a visual interface for score simulation:

1. Run `INICIAR.bat` (Windows) or `python main.py`
2. Open `index.html` in your browser

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | API information |
| GET | `/health` | API status |
| POST | `/score/calcular` | Calculate credit score |
| GET | `/score/historico` | List previous queries |

## Example

**Request:**
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

**Response:**
```json
{
  "score": 870,
  "nivel_risco": "baixo",
  "mensagem": "🟢 Excelente! Perfil muito saudável.",
  "fatores_positivos": [...],
  "fatores_negativos": [...],
  "recomendacoes": [...]
}
```

## Scoring Logic

Calculation starts at a base score of 500. Each factor adds or subtracts points:

| Factor | Impact |
|--------|--------|
| Monthly income | +100 (≥R$5k), +50 (≥R$2k), -30 (below) |
| Debt-to-income ratio | +125 (<30%), +60 (<50%), -50 (<80%), -100 (≥80%) |
| Payment history | +150 (on time), +50 (minor delay), -100 (major delay), -200 (defaulted) |
| Credit history length | +75 (≥60mo), +40 (≥24mo), +10 (≥6mo), -20 (<6mo) |
| Recent inquiries | +50 (0), +20 (≤3), -20 (≤6), -50 (>6) |

Final score is clamped between 0 and 1000.

## Risk Classification

| Score | Risk Level |
|-------|------------|
| 800-1000 | 🟢 Low |
| 600-799 | 🟡 Medium |
| 400-599 | 🟠 High |
| 0-399 | 🔴 Very High |

## Tests

```bash
pytest tests/test_main.py -v
```

## Author

Grazi Ramacciotti
- [LinkedIn](https://linkedin.com/in/graziramacciotti)
- [GitHub](https://github.com/graziramacciotti)
