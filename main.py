"""
=============================================================================
API de Análise de Score de Crédito - PYTHON 3.13
=============================================================================
"""

from datetime import datetime
from enum import Enum          
from typing import Optional    
import uuid    

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

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
    nome: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome completo do cliente",
        examples=["João Vitor Dias"]
    )

    idade: int = Field(
        ...,
        ge=18,
        le=100,
        description="Idade do cliente em anos",
        examples=[35]
    )

    renda_mensal: float = Field(
        ...,
        ge=0,
        multiple_of=0.01,
        description="Renda mensal do cliente em R$",
        examples=[5000.00]
    )

    dividas_totais: float = Field(
        ...,
        ge=0,
        description="Total de dívidas do cliente em R$",
        examples=[2000.00]
    )

    historico_pagamentos: StatusPagamento = Field(
        ...,
        description="Status do histórico de pagamentos",
        examples=[StatusPagamento.EM_DIA]
    )

    tempo_primeiro_credito_meses: int = Field(
        ...,
        ge=0,
        le=600, 
        description="Tempo desde o primeiro crédito em meses",
        examples=[36]
    )

    consultas_ultimos_6_meses: int = Field(
        ...,
        ge=0,
        le=50,
        description="Consultas ao crédito nos últimos 6 meses",
        examples=[2]
    )

    quantidade_contas_bancarias: int = Field(
        default=1, 
        ge=0,
        le=10,
        description="Número de contas bancárias ativas",
        examples=[2]
    )

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()  
        if not any(char.isalpha() for char in valor):
            raise ValueError("O nome deve conter pelo menos uma letra")
        return valor
    
class FatorAnalise(BaseModel):
    fator: str = Field(..., description="Nome do fator")
    descricao: str = Field(..., description="Descrição do impacto")
    impacto: int = Field(..., description="Pontos +/-")
    tipo: str = Field(..., description="'positivo' ou 'negativo'")
    recomendacao: str | None = Field(default=None)  

class ScoreResponse(BaseModel):
    id_consulta: str
    nome_cliente: str
    score: int = Field(..., ge=0, le=1000)
    nivel_risco: NivelRisco
    mensagem: str
    fatores_positivos: list[FatorAnalise] = Field(default_factory=list)
    fatores_negativos: list[FatorAnalise] = Field(default_factory=list)
    recomendacoes: list[str] = Field(default_factory=list)
    data_consulta: datetime

class HistoricoConsulta(BaseModel):
    id_consulta: str = Field(..., description="Identificador único")
    nome_cliente: str = Field(..., description="Nome do cliente")
    score: int = Field(..., description="Score calculado")
    nivel_risco: NivelRisco = Field(..., description="Nível de risco")
    data_consulta: datetime = Field(..., description="Data da consulta")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Data/hora atual")
    total_consultas: int = Field(..., description="Total de consultas")
    versao: str = Field(..., description="Versão da API")

class InfoResponse(BaseModel):
    mensagem: str = Field(..., description="Mensagem de boas-vindas")
    versao: str = Field(..., description="Versão da API")
    documentacao: str = Field(..., description="Link para docs")
    endpoints: dict[str, str] = Field(..., description="Endpoints disponíveis")

historico_consultas: list[HistoricoConsulta] = []

API_VERSAO = "1.0.0"
SCORE_BASE = 500      
SCORE_MINIMO = 0
SCORE_MAXIMO = 1000

LIMITE_RISCO_BAIXO = 800   
LIMITE_RISCO_MEDIO = 600   
LIMITE_RISCO_ALTO = 400 

def calcular_score(cliente: ClienteInput) -> tuple[int, list[FatorAnalise], list[str]]:
    score = SCORE_BASE
    fatores: list[FatorAnalise] = []
    recomendacoes: list[str] = []

    # =========================================
    # FATOR 1: RENDA MENSAL (peso 20%)
    # =========================================

    if cliente.renda_mensal >= 5000:
        # Renda alta: ganha 100 pontos
        pontos_renda = 100
        fatores.append(FatorAnalise(
            fator="Renda Mensal",
            descricao="Renda mensal adequada",
            impacto=pontos_renda,
            tipo="positivo"
        ))
    elif cliente.renda_mensal >= 2000:
        # Renda média: ganha 50 pontos
        pontos_renda = 50
        fatores.append(FatorAnalise(
            fator="Renda Mensal",
            descricao="Renda mensal estável",
            impacto=pontos_renda,
            tipo="positivo"
        ))
    else:
        # Renda baixa: perde 30 pontos
        pontos_renda = -30
        fatores.append(FatorAnalise(
            fator="Renda Mensal",
            descricao="Renda mensal baixa",
            impacto=pontos_renda,
            tipo="negativo",
            recomendacao="Considere buscar fontes adicionais de renda"
        ))
        recomendacoes.append("Busque aumentar sua renda mensal")
    
    score += pontos_renda
    
    # =========================================
    # FATOR 2: TAXA DE ENDIVIDAMENTO (peso 25%)
    # =========================================
    
    if cliente.renda_mensal > 0:
        taxa_endividamento = (cliente.dividas_totais / cliente.renda_mensal) * 100
    else:
        taxa_endividamento = 999
    
    if taxa_endividamento < 30:
        pontos_divida = 125
        fatores.append(FatorAnalise(
            fator="Taxa de Endividamento",
            descricao=f"Baixo nível ({taxa_endividamento:.1f}%)",
            impacto=pontos_divida,
            tipo="positivo"
        ))
    elif taxa_endividamento < 50:
        pontos_divida = 60
        fatores.append(FatorAnalise(
            fator="Taxa de Endividamento",
            descricao=f"Controlado ({taxa_endividamento:.1f}%)",
            impacto=pontos_divida,
            tipo="positivo"
        ))
    elif taxa_endividamento < 80:
        pontos_divida = -50
        fatores.append(FatorAnalise(
            fator="Taxa de Endividamento",
            descricao=f"Elevado ({taxa_endividamento:.1f}%)",
            impacto=pontos_divida,
            tipo="negativo",
            recomendacao="Reduza suas dívidas"
        ))
        recomendacoes.append("Priorize quitar dívidas com juros altos")
    else:
        pontos_divida = -100
        fatores.append(FatorAnalise(
            fator="Taxa de Endividamento",
            descricao=f"Crítico ({taxa_endividamento:.1f}%)",
            impacto=pontos_divida,
            tipo="negativo",
            recomendacao="Situação urgente!"
        ))
        recomendacoes.append("Procure um especialista em finanças")
    
    score += pontos_divida

    # =========================================
    # FATOR 3: HISTÓRICO DE PAGAMENTOS (peso 30%)
    # =========================================

    if cliente.historico_pagamentos == StatusPagamento.EM_DIA:
        pontos_historico = 150  
        fatores.append(FatorAnalise(
            fator="Histórico de Pagamentos",
            descricao="Pagamentos em dia",
            impacto=pontos_historico,
            tipo="positivo"
        ))
    elif cliente.historico_pagamentos == StatusPagamento.ATRASO_LEVE:
        pontos_historico = 50
        fatores.append(FatorAnalise(
            fator="Histórico de Pagamentos",
            descricao="Alguns atrasos pontuais",
            impacto=pontos_historico,
            tipo="positivo",
            recomendacao="Evite atrasos"
        ))
        recomendacoes.append("Configure débito automático")
    elif cliente.historico_pagamentos == StatusPagamento.ATRASO_GRAVE:
        pontos_historico = -100
        fatores.append(FatorAnalise(
            fator="Histórico de Pagamentos",
            descricao="Atrasos frequentes",
            impacto=pontos_historico,
            tipo="negativo",
            recomendacao="Regularize os pagamentos"
        ))
        recomendacoes.append("Negocie pagamentos atrasados")
    else:  
        pontos_historico = -200  
        fatores.append(FatorAnalise(
            fator="Histórico de Pagamentos",
            descricao="Inadimplência ativa",
            impacto=pontos_historico,
            tipo="negativo",
            recomendacao="URGENTE: Regularize!"
        ))
        recomendacoes.append("URGENTE: Procure o Serasa Limpa Nome")
    
    score += pontos_historico
    
    # =========================================
    # FATOR 4: TEMPO DE HISTÓRICO (peso 15%)
    # =========================================
    
    meses = cliente.tempo_primeiro_credito_meses
    
    if meses >= 60: 
        pontos_tempo = 75
        descricao = "Histórico longo e consolidado"
    elif meses >= 24:  
        pontos_tempo = 40
        descricao = "Histórico estabelecido"
    elif meses >= 6:  
        pontos_tempo = 10
        descricao = "Histórico em construção"
    else:  
        pontos_tempo = -20
        descricao = "Histórico muito recente"
        recomendacoes.append("Mantenha contas ativas para construir histórico")
    
    fatores.append(FatorAnalise(
        fator="Tempo de Histórico",
        descricao=descricao,
        impacto=pontos_tempo,
        tipo="positivo" if pontos_tempo > 0 else "negativo"
    ))
    
    score += pontos_tempo
    
    # =========================================
    # FATOR 5: CONSULTAS RECENTES (peso 10%)
    # =========================================
    
    consultas = cliente.consultas_ultimos_6_meses
    
    if consultas == 0:
        pontos_consultas = 50
        descricao = "Sem consultas recentes"
    elif consultas <= 3:
        pontos_consultas = 20
        descricao = f"Poucas consultas ({consultas})"
    elif consultas <= 6:
        pontos_consultas = -20
        descricao = f"Múltiplas consultas ({consultas})"
        recomendacoes.append("Evite solicitar crédito em muitos lugares")
    else:
        pontos_consultas = -50
        descricao = f"Excesso de consultas ({consultas})"
        recomendacoes.append("Aguarde antes de pedir novo crédito")
    
    fatores.append(FatorAnalise(
        fator="Consultas Recentes",
        descricao=descricao,
        impacto=pontos_consultas,
        tipo="positivo" if pontos_consultas > 0 else "negativo"
    ))
    
    score += pontos_consultas
    
    score = max(SCORE_MINIMO, min(SCORE_MAXIMO, score))
    
    return score, fatores, recomendacoes

def classificar_risco(score: int) -> tuple[NivelRisco, str]:    
    if score >= 800:
        return (
            NivelRisco.BAIXO,
            "🟢 Excelente! Perfil muito saudável."
        )
    elif score >= 600:
        return (
            NivelRisco.MEDIO,
            "🟡 Bom! Há espaço para melhorias."
        )
    elif score >= 400:
        return (
            NivelRisco.ALTO,
            "🟠 Atenção! Precisa de melhorias."
        )
    else:
        return (
            NivelRisco.MUITO_ALTO,
            "🔴 Crítico! Ações urgentes necessárias."
        )

app = FastAPI(
    title="API de Score de Crédito",
    description="API para análise de score de crédito",
    version=API_VERSAO,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/", response_model=InfoResponse, tags=["Geral"])
async def raiz() -> InfoResponse:
    return InfoResponse(
        mensagem="Bem-vindo à API de Score de Crédito!",
        versao=API_VERSAO,
        documentacao="/docs",
        endpoints={
            "calcular_score": "POST /score/calcular",
            "historico": "GET /score/historico",
            "health_check": "GET /health"
        }
    )

@app.get("/health", response_model=HealthResponse, tags=["Geral"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        total_consultas=len(historico_consultas),
        versao=API_VERSAO
    )


@app.post("/score/calcular", response_model=ScoreResponse, tags=["Score"])
async def calcular_score_endpoint(cliente: ClienteInput) -> ScoreResponse:
    try:
        id_consulta = str(uuid.uuid4())
        score, fatores, recomendacoes = calcular_score(cliente)
        nivel_risco, mensagem = classificar_risco(score)
        
        fatores_positivos = [f for f in fatores if f.tipo == "positivo"]
        fatores_negativos = [f for f in fatores if f.tipo == "negativo"]
        
        data_consulta = datetime.now()
        
        historico_consultas.append(
            HistoricoConsulta(
                id_consulta=id_consulta,
                nome_cliente=cliente.nome,
                score=score,
                nivel_risco=nivel_risco,
                data_consulta=data_consulta
            )
        )
        
        return ScoreResponse(
            id_consulta=id_consulta,
            nome_cliente=cliente.nome,
            score=score,
            nivel_risco=nivel_risco,
            mensagem=mensagem,
            fatores_positivos=fatores_positivos,
            fatores_negativos=fatores_negativos,
            recomendacoes=recomendacoes,
            data_consulta=data_consulta
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/score/historico", response_model=list[HistoricoConsulta], tags=["Score"])
async def listar_historico(
    limite: int = Query(default=10, ge=1, le=100)
) -> list[HistoricoConsulta]:
    return historico_consultas[-limite:][::-1]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)