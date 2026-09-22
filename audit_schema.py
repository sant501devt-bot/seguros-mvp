from pydantic import BaseModel, Field
from typing import List

class Cobertura(BaseModel):
    tipo_amparo: str
    monto_cubierto: float
    estado: str

class Riesgo(BaseModel):
    nivel_riesgo: str = Field(description="ALTO, MEDIO o BAJO")
    hallazgo: str
    recomendacion: str

# Esquema Principal que devuelve la IA
class ResultadoAuditoria(BaseModel):
    numero_poliza: str
    aseguradora: str
    vigencia_inicio: str
    vigencia_fin: str
    coberturas: List[Cobertura]
    matriz_riesgos: List[Riesgo]
    score_salud: int = Field(description="Puntuación de 0 a 100")
    observaciones: str = Field(
        default="",
        description="Resumen breve en lenguaje humano de los hallazgos más importantes"
    )


# --- Banderas priorizadas ---
# Prioridad la calcula PYTHON, no la IA -- así es consistente siempre,
# sin depender de que el modelo "adivine" un número.
PESO_RIESGO = {"ALTO": 100, "MEDIO": 25, "BAJO": 5}

def calcular_prioridad(resultado: ResultadoAuditoria) -> int:
    puntaje_riesgos = sum(
        PESO_RIESGO.get(r.nivel_riesgo.upper(), 0) for r in resultado.matriz_riesgos
    )
    penalizacion_score = max(0, 100 - resultado.score_salud)
    return puntaje_riesgos + penalizacion_score


def nivel_urgencia(prioridad: int) -> str:
    if prioridad >= 150:
        return "URGENTE"
    elif prioridad >= 60:
        return "REVISAR PRONTO"
    else:
        return "NORMAL"