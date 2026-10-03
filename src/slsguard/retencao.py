"""Politica de retencao por nivel.

Retention policy per event level.

Cada nivel de evento tem um prazo de retencao em dias. Este modulo decide,
para um evento de uma idade dada, se ele ainda deve ser mantido. Niveis em
`nunca_descartar` sao mantidos mesmo vencidos: auditoria e prova, e prova
nao pode virar lixo por rotina.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .evento import Evento


class ErroDePolitica(Exception):
    """A politica de retencao nao pode ser lida.

    The retention policy cannot be loaded.
    """


def carregar_politica(caminho: str | Path) -> tuple[dict[str, int], list[str]]:
    """Le a politica de retencao em YAML.

    Load the retention policy from a YAML file.

    O arquivo tem duas chaves: `retencao` (mapa nivel -> dias) e
    `nunca_descartar` (lista de niveis mantidos mesmo vencidos).

    Args:
        caminho: O arquivo YAML da politica.

    Returns:
        Um par: dict nivel -> dias de retencao, e a lista de niveis que
        nunca sao descartados.

    Raises:
        ErroDePolitica: Se o arquivo nao existir, for YAML invalido ou
            estiver com estrutura errada.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroDePolitica(f"arquivo nao encontrado: {caminho}")
    try:
        texto = caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError as erro:
        raise ErroDePolitica(f"{caminho}: nao decodifica como UTF-8 ({erro})") from None
    try:
        bruto: Any = yaml.safe_load(texto)
    except yaml.YAMLError as erro:
        raise ErroDePolitica(f"{caminho}: YAML invalido ({erro})") from None
    if not isinstance(bruto, dict):
        raise ErroDePolitica(f"{caminho}: politica nao e um mapa")

    retencao = bruto.get("retencao", {})
    if not isinstance(retencao, dict):
        raise ErroDePolitica(f"{caminho}: `retencao` nao e um mapa")
    dias: dict[str, int] = {}
    for nivel, valor in retencao.items():
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ErroDePolitica(
                f"{caminho}: prazo de {nivel!r} deve ser inteiro de dias >= 0"
            )
        dias[str(nivel).strip().lower()] = valor

    nunca = bruto.get("nunca_descartar", [])
    if not isinstance(nunca, list):
        raise ErroDePolitica(f"{caminho}: `nunca_descartar` deve ser uma lista")
    nunca_lista = [str(n).strip().lower() for n in nunca]
    return dias, nunca_lista


def deve_manter(
    evento: Evento,
    idade_dias: int | float,
    politica: tuple[dict[str, int], list[str]],
) -> bool:
    """Decide se o evento ainda deve ser mantido.

    Decide whether the event must still be kept.

    Regra: nivel em `nunca_descartar` sempre e mantido; senao, o evento e
    mantido se a idade for menor ou igual ao prazo do nivel.

    Args:
        evento: O evento canonico, com o campo `nivel`.
        idade_dias: A idade do evento, em dias.
        politica: O par (nivel -> dias, nunca_descartar) devolvido por
            carregar_politica.

    Returns:
        True se mantem; False se descarta.
    """
    dias, nunca_descartar = politica
    if evento.nivel in nunca_descartar:
        return True
    prazo = dias.get(evento.nivel)
    if prazo is None:
        return False
    return idade_dias <= prazo
