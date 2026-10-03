"""Modelo de custo por execucao, duracao e memoria.

Cost model by execution count, duration, and memory.

Cada evento normalizado conta como uma execucao. O custo de cada execucao
e a parte fixa (base) mais a parte variavel (duracao em ms vezes preco por
ms vezes memoria em GB). Os precos sao constantes ficticias, documentadas.
"""

from __future__ import annotations

from dataclasses import dataclass

from .evento import Evento

# Precos ficticios documentados.
# Documented fictitious prices.
BASE_POR_EXECUCAO = 0.02  # Parte fixa por evento (BRL).
PRECO_POR_MS = 0.0001  # Parte variavel por milissegundo (BRL/ms/GB).


@dataclass(frozen=True)
class Custo:
    """Resultado do calculo de custo de um lote.

    Cost result for a batch.
    """

    execucoes: int
    duracao_ms_total: int
    memoria_gb: float
    total: float


def calcular(eventos: list[Evento], duracao_ms: int, memoria_gb: float) -> Custo:
    """Calcula o custo de um lote de eventos.

    Compute the cost of an event batch.

    Custo por execucao:
        base_por_execucao + duracao_ms * preco_por_ms * memoria_gb

    Calculo manual esperado (gate final):
        20 eventos * base 0.02 + 20 * 120ms * 0.0001 * 0.5GB
        = 0.40 + 0.12
        = 0.52

    Lote com zero eventos custa zero.

    Args:
        eventos: Os eventos normalizados; cada um e uma execucao.
        duracao_ms: A duracao em ms de cada execucao.
        memoria_gb: A memoria em GB de cada execucao.

    Returns:
        O custo do lote.
    """
    n = len(eventos)
    if n == 0:
        return Custo(execucoes=0, duracao_ms_total=0, memoria_gb=0.0, total=0.0)
    total = n * BASE_POR_EXECUCAO + n * duracao_ms * PRECO_POR_MS * memoria_gb
    return Custo(
        execucoes=n,
        duracao_ms_total=n * duracao_ms,
        memoria_gb=memoria_gb,
        total=total,
    )


def custo_por_tipo(eventos: list[Evento]) -> dict[str, float]:
    """Agrupa o total por tipo de evento.

    Group the total by event type.

    Entra so a parte fixa, porque duracao e memoria sao parametros do lote
    em `calcular`: cada evento custa BASE_POR_EXECUCAO. Lote vazio vira
    mapa vazio.

    Args:
        eventos: Os eventos normalizados.

    Returns:
        O total por tipo, como {"login": 0.4}.
    """
    totais: dict[str, float] = {}
    for evento in eventos:
        totais[evento.tipo] = totais.get(evento.tipo, 0.0) + BASE_POR_EXECUCAO
    return totais
