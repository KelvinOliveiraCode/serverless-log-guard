"""Deteccao e mascaramento de PII.

PII detection and masking.

Varre um texto em busca de cinco categorias de dado sensivel - CPF, e-mail,
telefone BR, numero de cartao e IP IPv4 - e devolve os trechos achados ou
uma versao do texto com cada um mascarado pelo padrao da categoria. O
mascaramento mostra apenas o minimo necessario: os ultimos 3 digitos do
CPF, o dominio do e-mail, o DDD do telefone, os ultimos 4 digitos do
cartao e a rede /24 do IP.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Ordem fixa de prioridade: quem casa primeiro ocupa o trecho e as
# demais categorias nao repetem sobreposta.
ORDEM = ("cpf", "cartao", "telefone", "ip", "email")

_PADRAO_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
_PADRAO_CARTAO = re.compile(r"(?<!\d)(?:\d{4}[ -])+\d{4}(?!\d)")
_PADRAO_TELEFONE = re.compile(r"\(?\d{2}\)?[ .-]?\d{4,5}-\d{4}")
_PADRAO_IP = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)
_PADRAO_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

_PADROES = {
    "cpf": _PADRAO_CPF,
    "cartao": _PADRAO_CARTAO,
    "telefone": _PADRAO_TELEFONE,
    "ip": _PADRAO_IP,
    "email": _PADRAO_EMAIL,
}


@dataclass(frozen=True)
class AchadoPII:
    """Um trecho de PII localizado em um texto.

    A PII match found in a text.

    Attributes:
        categoria: `cpf`, `email`, `telefone`, `cartao` ou `ip`.
        trecho: O texto exato como apareceu.
        linha: A linha (1-based) dentro do texto varrido.
    """

    categoria: str
    trecho: str
    linha: int


def _digitos(trecho: str) -> str:
    """So os digitos do trecho.

    Only the digits of the match.
    """
    return re.sub(r"\D", "", trecho)


def _valido_cartao(trecho: str) -> bool:
    """Cartao precisa de 13 a 19 digitos.

    A card number needs 13 to 19 digits.
    """
    return 13 <= len(_digitos(trecho)) <= 19


def _sobrepoe(ini: int, fim: int, ocupados: list[tuple[int, int]]) -> bool:
    """Se o trecho ja foi ocupado por outra categoria.

    Whether the span overlaps an already accepted match.
    """
    return any(ini < fim_anterior and fim > inicio for inicio, fim_anterior in ocupados)


def _varrer(texto: str) -> list[tuple[int, AchadoPII]]:
    """Varre o texto e devolve (posicao, achado) em ordem.

    Scan the text and return (start position, match) in order.
    """
    bruto: list[tuple[int, int, AchadoPII]] = []
    ocupados: list[tuple[int, int]] = []
    for categoria in ORDEM:
        for achado in _PADROES[categoria].finditer(texto):
            if categoria == "cartao" and not _valido_cartao(achado.group(0)):
                continue
            ini, fim = achado.span()
            if _sobrepoe(ini, fim, ocupados):
                continue
            ocupados.append((ini, fim))
            linha = texto.count("\n", 0, ini) + 1
            bruto.append(
                (ini, fim, AchadoPII(categoria=categoria, trecho=achado.group(0),
                                     linha=linha))
            )
    bruto.sort(key=lambda item: item[0])
    return [(ini, achado) for ini, _, achado in bruto]


def detectar(texto: str) -> list[AchadoPII]:
    """Acha PII nos cinco formatos em um texto.

    Detect PII in a text across the five categories.

    Args:
        texto: O texto a varrer.

    Returns:
        Os achados, em ordem de posicao; vazio se nao ha PII.
    """
    return [achado for _, achado in _varrer(texto)]


def _mascarar(trecho: str, categoria: str) -> str:
    """Mascara um trecho pelo padrao da categoria.

    Mask a match using the category pattern.
    """
    if categoria == "email":
        dominio = trecho.split("@", 1)[1]
        return "***@" + dominio
    if categoria == "ip":
        partes = trecho.split(".")
        return ".".join(partes[:3]) + ".***"
    # cpf, telefone e cartao: trocam digitos por * mantendo o padrao.
    posicoes = [i for i, c in enumerate(trecho) if c.isdigit()]
    if categoria == "cpf":
        manter = set(posicoes[-3:])
    elif categoria == "telefone":
        manter = set(posicoes[:2])
    else:  # cartao
        manter = set(posicoes[-4:])
    return "".join(
        c if i in manter else ("*" if c.isdigit() else c)
        for i, c in enumerate(trecho)
    )


def mascarar(texto: str) -> str:
    """Devolve o texto com toda PII mascarada.

    Return the text with every PII match masked.

    Args:
        texto: O texto a limpar.

    Returns:
        O texto mascarado; igual ao original se nao ha PII.
    """
    bruto = _varrer(texto)
    if not bruto:
        return texto
    saida = texto
    for ini, achado in sorted(bruto, key=lambda item: -item[0]):
        fim = ini + len(achado.trecho)
        mascarado = _mascarar(achado.trecho, achado.categoria)
        saida = saida[:ini] + mascarado + saida[fim:]
    return saida
