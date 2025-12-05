"""
API de Score de Crédito
Simula o cálculo de score de crédito baseado em fatores financeiros.
"""

from datetime import datetime
from enum import Enum
import uuid

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator


class StatusPagamento(str, Enum):
    EM_DIA = "em_dia"
    ATRASO_LEVE = "atraso_leve"
    ATRASO_GRAVE = "atraso_grave"
    INADIMPLENTE = "inadimplente"


class NivelRisco(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    MUITO_ALTO = "muito_alto"


class ClienteInput(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, examples=["Maria Silva"])
    idade: int = Field(..., ge=18, le=100, examples=[30])
    renda_mensal: float = Field(..., ge=0, examples=[5000.0])
    dividas_totais: float = Field(..., ge=0, examples=[1500.0])
    historico_pagamentos: StatusPagamento = Field(..., examples=["em_dia"])
    tempo_primeiro_credito_meses: int = Field(..., ge=0, le=600, examples=[36])
    consultas_ultimos_6_meses: int = Field(..., ge=0, le=50, examples=[2])
    quantidade_contas_bancarias: int = Field(default=1, ge=0, le=10)

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v: str) -> str:
        v = v.strip()
        if not any(c.isalpha() for c in v):
            raise ValueError("Nome deve conter letras")
        return v


class FatorAnalise(BaseModel):
    fator: str
    descricao: str
    impacto: int
    tipo: str
    recomendacao: str | None = None


class ScoreResponse(BaseModel):
    id_consulta: str
    nome_cliente: str
    score: int = Field(..., ge=0, le=1000)
    nivel_risco: NivelRisco
    mensagem: str
    fatores_positivos: list[FatorAnalise] = []
    fatores_negativos: list[FatorAnalise] = []
    recomendacoes: list[str] = []
    data_consulta: datetime


class HistoricoConsulta(BaseModel):
    id_consulta: str
    nome_cliente: str
    score: int
    nivel_risco: NivelRisco
    data_consulta: datetime


historico_consultas: list[HistoricoConsulta] = []

SCORE_BASE = 500
SCORE_MIN, SCORE_MAX = 0, 1000

CONFIG_RENDA = [
    (5000, 100, "Renda adequada", "positivo"),
    (2000, 50, "Renda estável", "positivo"),
    (0, -30, "Renda baixa", "negativo"),
]

CONFIG_HISTORICO = {
    StatusPagamento.EM_DIA: (150, "Pagamentos em dia", "positivo"),
    StatusPagamento.ATRASO_LEVE: (50, "Atrasos pontuais", "positivo"),
    StatusPagamento.ATRASO_GRAVE: (-100, "Atrasos frequentes", "negativo"),
    StatusPagamento.INADIMPLENTE: (-200, "Inadimplência ativa", "negativo"),
}

MENSAGENS_RISCO = {
    NivelRisco.BAIXO: "🟢 Excelente! Perfil de crédito muito saudável.",
    NivelRisco.MEDIO: "🟡 Bom! Seu perfil é aceitável, mas pode melhorar.",
    NivelRisco.ALTO: "🟠 Atenção! Seu perfil precisa de melhorias.",
    NivelRisco.MUITO_ALTO: "🔴 Crítico! Tome ações urgentes.",
}


def calcular_score(cliente: ClienteInput) -> tuple[int, list[FatorAnalise], list[str]]:
    score = SCORE_BASE
    fatores: list[FatorAnalise] = []
    recomendacoes: list[str] = []

    for limite, pontos, desc, tipo in CONFIG_RENDA:
        if cliente.renda_mensal >= limite:
            fatores.append(FatorAnalise(fator="Renda Mensal", descricao=desc, impacto=pontos, tipo=tipo))
            if pontos < 0:
                recomendacoes.append("💰 Busque aumentar sua renda")
            score += pontos
            break

    taxa = (cliente.dividas_totais / cliente.renda_mensal * 100) if cliente.renda_mensal > 0 else 999
    
    if taxa < 30:
        pontos, desc, tipo = 125, f"Baixo endividamento ({taxa:.0f}%)", "positivo"
    elif taxa < 50:
        pontos, desc, tipo = 60, f"Endividamento controlado ({taxa:.0f}%)", "positivo"
    elif taxa < 80:
        pontos, desc, tipo = -50, f"Endividamento elevado ({taxa:.0f}%)", "negativo"
        recomendacoes.append("📉 Priorize quitar dívidas com juros altos")
    else:
        pontos, desc, tipo = -100, f"Endividamento crítico ({taxa:.0f}%)", "negativo"
        recomendacoes.append("🚨 Procure ajuda para renegociar dívidas")
    
    fatores.append(FatorAnalise(fator="Endividamento", descricao=desc, impacto=pontos, tipo=tipo))
    score += pontos

    pontos, desc, tipo = CONFIG_HISTORICO[cliente.historico_pagamentos]
    fatores.append(FatorAnalise(fator="Histórico de Pagamentos", descricao=desc, impacto=pontos, tipo=tipo))
    if pontos < 0:
        recomendacoes.append("📅 Regularize seus pagamentos")
    score += pontos

    meses = cliente.tempo_primeiro_credito_meses
    if meses >= 60:
        pontos, desc, tipo = 75, "Histórico consolidado", "positivo"
    elif meses >= 24:
        pontos, desc, tipo = 40, "Histórico estabelecido", "positivo"
    elif meses >= 6:
        pontos, desc, tipo = 10, "Histórico em construção", "positivo"
    else:
        pontos, desc, tipo = -20, "Histórico muito recente", "negativo"
        recomendacoes.append("🕐 Mantenha contas ativas para construir histórico")
    
    fatores.append(FatorAnalise(fator="Tempo de Histórico", descricao=desc, impacto=pontos, tipo=tipo))
    score += pontos

    consultas = cliente.consultas_ultimos_6_meses
    if consultas == 0:
        pontos, desc, tipo = 50, "Sem consultas recentes", "positivo"
    elif consultas <= 3:
        pontos, desc, tipo = 20, f"Poucas consultas ({consultas})", "positivo"
    elif consultas <= 6:
        pontos, desc, tipo = -20, f"Várias consultas ({consultas})", "negativo"
        recomendacoes.append("🔍 Evite solicitar crédito em muitos lugares")
    else:
        pontos, desc, tipo = -50, f"Excesso de consultas ({consultas})", "negativo"
        recomendacoes.append("⚠️ Aguarde antes de pedir novo crédito")
    
    fatores.append(FatorAnalise(fator="Consultas Recentes", descricao=desc, impacto=pontos, tipo=tipo))
    score += pontos

    score = max(SCORE_MIN, min(SCORE_MAX, score))
    
    return score, fatores, recomendacoes


def classificar_risco(score: int) -> tuple[NivelRisco, str]:
    if score >= 800:
        nivel = NivelRisco.BAIXO
    elif score >= 600:
        nivel = NivelRisco.MEDIO
    elif score >= 400:
        nivel = NivelRisco.ALTO
    else:
        nivel = NivelRisco.MUITO_ALTO
    
    return nivel, MENSAGENS_RISCO[nivel]


app = FastAPI(
    title="API de Score de Crédito",
    description="Calcula score de crédito baseado em fatores financeiros",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Geral"])
async def raiz():
    return {
        "mensagem": "Bem-vindo à API de Score de Crédito!",
        "versao": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Geral"])
async def health():
    return {
        "status": "online",
        "consultas_realizadas": len(historico_consultas)
    }


@app.post("/score/calcular", response_model=ScoreResponse, tags=["Score"])
async def calcular(cliente: ClienteInput):
    id_consulta = str(uuid.uuid4())
    score, fatores, recomendacoes = calcular_score(cliente)
    nivel_risco, mensagem = classificar_risco(score)
    data_consulta = datetime.now()

    historico_consultas.append(HistoricoConsulta(
        id_consulta=id_consulta,
        nome_cliente=cliente.nome,
        score=score,
        nivel_risco=nivel_risco,
        data_consulta=data_consulta
    ))

    return ScoreResponse(
        id_consulta=id_consulta,
        nome_cliente=cliente.nome,
        score=score,
        nivel_risco=nivel_risco,
        mensagem=mensagem,
        fatores_positivos=[f for f in fatores if f.tipo == "positivo"],
        fatores_negativos=[f for f in fatores if f.tipo == "negativo"],
        recomendacoes=recomendacoes,
        data_consulta=data_consulta
    )


@app.get("/score/historico", response_model=list[HistoricoConsulta], tags=["Score"])
async def historico(limite: int = Query(default=10, ge=1, le=100)):
    return historico_consultas[-limite:][::-1]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
