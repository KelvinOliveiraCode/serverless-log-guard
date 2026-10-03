"""Normalizacao de evento.

Event normalization.

A funcao serverless recebe JSON de formatos diferentes e precisa de uma forma
canonica antes de qualquer politica. Este modulo e essa forma: todo evento
vira um `Evento` com os mesmos campos, e o resto do pipeline nunca ve o JSON
cru.

## Por que normalizar antes de filtrar

PII escondida em campo com nome diferente e PII nao encontrada. Um `cpf` no
campo `documento` e o mesmo dado que no campo `cpf`, e um detector que so
olha campo conhecido perde o primeiro. Normalizar nao resolve isso sozinho -
o detector varre valores, nao chaves - mas garante que o resto do pipeline
leia o evento da mesma forma independente da origem.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ErroDeEvento(Exception):
    """O evento nao pode ser normalizado.

    The event cannot be normalized.
    """


@dataclass(frozen=True)
class Evento:
    """Um evento canonico.

    A canonical event.

    Attributes:
        id: Identificador unico no lote.
        tipo: O tipo, como `pedido` ou `login`.
        nivel: `debug`, `info`, `erro` ou `auditoria`.
        mensagem: O texto principal.
        campos: O resto dos campos, preservados.
        linha: A linha no JSONL, para o erro apontar o lugar.
    """

    id: str
    tipo: str
    nivel: str
    mensagem: str
    campos: dict[str, Any] = field(default_factory=dict)
    linha: int = 0

    def textos(self) -> list[str]:
        """Todos os textos do evento para varredura de PII.

        All event texts for PII scanning.

        Returns:
            A mensagem mais cada valor de texto dos campos.
        """
        textos = [self.mensagem]
        for valor in self.campos.values():
            if isinstance(valor, str):
                textos.append(valor)
        return textos


NIVEIS = ("debug", "info", "erro", "auditoria")


def normalizar(bruto: dict[str, Any], linha: int = 0) -> Evento:
    """Converte um mapa em evento canonico.

    Convert a map into a canonical event.

    Args:
        bruto: O mapa do JSON.
        linha: A linha no arquivo.

    Returns:
        O evento normalizado.

    Raises:
        ErroDeEvento: Se faltar campo obrigatorio ou o nivel for desconhecido.
    """
    if not isinstance(bruto, dict):
        raise ErroDeEvento(f"linha {linha}: evento nao e um mapa")
    for campo in ("id", "tipo", "mensagem"):
        if not str(bruto.get(campo, "")).strip():
            raise ErroDeEvento(f"linha {linha}: campo {campo!r} obrigatorio")
    nivel = str(bruto.get("nivel", "info")).strip().lower()
    if nivel not in NIVEIS:
        raise ErroDeEvento(f"linha {linha}: nivel {nivel!r} desconhecido")
    extras = {
        chave: valor
        for chave, valor in bruto.items()
        if chave not in ("id", "tipo", "nivel", "mensagem")
    }
    return Evento(
        id=str(bruto["id"]),
        tipo=str(bruto["tipo"]),
        nivel=nivel,
        mensagem=str(bruto["mensagem"]),
        campos=extras,
        linha=linha,
    )


def carregar(caminho: str | Path) -> list[Evento]:
    """Le um JSONL de eventos.

    Read a JSONL event file.

    Args:
        caminho: O arquivo, uma linha JSON por evento.

    Returns:
        Os eventos normalizados, na ordem do arquivo.

    Raises:
        ErroDeEvento: Se o arquivo nao existir ou alguma linha for invalida.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroDeEvento(f"arquivo nao encontrado: {caminho}")
    eventos: list[Evento] = []
    try:
        texto = caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError as erro:
        raise ErroDeEvento(f"{caminho}: nao decodifica como UTF-8 ({erro})") from None
    for numero, linha in enumerate(texto.splitlines(), start=1):
        if not linha.strip():
            continue
        try:
            bruto = json.loads(linha)
        except json.JSONDecodeError as erro:
            raise ErroDeEvento(f"linha {numero}: JSON invalido ({erro})") from None
        eventos.append(normalizar(bruto, linha=numero))
    if not eventos:
        raise ErroDeEvento(f"{caminho}: nenhum evento valido")
    return eventos