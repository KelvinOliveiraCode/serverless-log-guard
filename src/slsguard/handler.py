"""A funcao: recebe evento, normaliza, filtra, retem, custa.

The function: receive event, normalize, filter, retain, cost.

Este modulo e o orquestrador do pipeline, e ele nao decide nada sozinho: cada
etapa pertence ao modulo dono. O handler so garante a ordem - normalizar,
detectar PII, mascarar, aplicar retencao, somar custo - e que a saida de uma
etapa e a entrada da proxima.

## Por que mascarar antes de reter

A ordem nao e arbitraria. Se a retencao viesse antes do mascaramento, o
conteudo guardado teria PII, e apagar depois nao apaga o que ja foi escrito
no disco. Mascarar primeiro significa que o que fica retido ja esta limpo - e
o que foi descartado nunca existiu com dado sensivel.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import custo as modulo_custo
from . import pii as modulo_pii
from . import retencao as modulo_retencao
from .evento import Evento


@dataclass(frozen=True)
class Resultado:
    """O processamento de um lote.

    A batch's processing.

    Attributes:
        eventos: Os eventos mascarados e retidos.
        descartados: Quantos a retencao removeu.
        com_pii: Quantos tinham PII antes de mascarar.
        custo_total: O custo estimado do lote.
    """

    eventos: tuple[Evento, ...] = ()
    descartados: int = 0
    com_pii: int = 0
    custo_total: float = 0.0


def executar(
    eventos: list[Evento],
    politica: dict,
    idade_dias: int = 0,
    duracao_ms: float = 120.0,
    memoria_gb: float = 0.5,
) -> Resultado:
    """Processa um lote de eventos.

    Process a batch of events.

    Args:
        eventos: Os eventos normalizados.
        politica: A politica de retencao carregada.
        idade_dias: A idade simulada dos eventos.
        duracao_ms: Duracao media por execucao.
        memoria_gb: Memoria alocada.

    Returns:
        O resultado com eventos mascarados, contagens e custo.
    """
    mascarados: list[Evento] = []
    com_pii = 0
    descartados = 0

    for evento in eventos:
        textos = evento.textos()
        achou = any(modulo_pii.detectar(texto) for texto in textos)
        if achou:
            com_pii += 1
        limpo = Evento(
            id=evento.id,
            tipo=evento.tipo,
            nivel=evento.nivel,
            mensagem=modulo_pii.mascarar(evento.mensagem),
            campos={
                chave: (
                    modulo_pii.mascarar(valor)
                    if isinstance(valor, str)
                    else valor
                )
                for chave, valor in evento.campos.items()
            },
            linha=evento.linha,
        )
        if not modulo_retencao.deve_manter(limpo, idade_dias, politica):
            descartados += 1
            continue
        mascarados.append(limpo)

    custo = modulo_custo.calcular(mascarados, duracao_ms, memoria_gb)
    return Resultado(
        eventos=tuple(mascarados),
        descartados=descartados,
        com_pii=com_pii,
        custo_total=custo.total,
    )
