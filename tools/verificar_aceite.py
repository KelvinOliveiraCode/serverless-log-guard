"""Prova de aceite do slsguard.

slsguard acceptance proof.

O criterio de aceite tem duas metades:

1. **As 5 categorias de PII plantadas sao detectadas e mascaradas.** Uma a
   menos e um detector cego; uma a mais (falso positivo) e um relatorio que
   mente. Os dois lados sao verificados.
2. **O custo estimado bate com o calculo manual.** 20 eventos a base 0.02
   mais 20 vezes 120ms a 0.0001 por 0.5GB: 0.52. O numero esta aberto no
   modulo, e o teste trava o numero.

O script verifica ainda que o mascarado nao tem PII residual, porque
detectar e mascarar sao duas operacoes e a segunda pode falhar sozinha.
"""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from slsguard import handler as modulo_handler  # noqa: E402
from slsguard import pii as modulo_pii  # noqa: E402
from slsguard import retencao as modulo_retencao  # noqa: E402
from slsguard.cli import main as cli_main  # noqa: E402
from slsguard.evento import carregar  # noqa: E402

JSONL = RAIZ / "dados" / "eventos-sinteticos.jsonl"
POLITICA = RAIZ / "dados" / "politica-retencao.yaml"

ESPERADAS = {
    "evt-001": "email",
    "evt-003": "cartao",
    "evt-004": "cpf",
    "evt-005": "telefone",
    "evt-015": "ip",
}
CUSTO_ESPERADO = 0.52


class Falha(Exception):
    """Uma condicao de aceite nao foi satisfeita."""


def checar(condicao: bool, mensagem: str) -> None:
    """Falha se a condicao e falsa.

    Args:
        condicao: A condicao.
        mensagem: O que deu errado.

    Raises:
        Falha: Se a condicao for falsa.
    """
    if not condicao:
        raise Falha(mensagem)


def principal() -> int:
    """Roda a prova de aceite.

    Returns:
        0 se tudo passar, 1 se alguma condicao falhar.
    """
    try:
        eventos = carregar(JSONL)
        politica = modulo_retencao.carregar_politica(POLITICA)
        print(f"1) {len(eventos)} eventos carregados")

        por_evento: dict[str, set[str]] = {}
        for evento in eventos:
            for texto in evento.textos():
                for achado in modulo_pii.detectar(texto):
                    por_evento.setdefault(evento.id, set()).add(achado.categoria)
        for eid, categoria in sorted(ESPERADAS.items()):
            checar(
                por_evento.get(eid) == {categoria},
                f"{eid}: esperado {{{categoria}}}, veio {por_evento.get(eid)}",
            )
        checar(
            set(por_evento) == set(ESPERADAS),
            f"eventos com PII alem dos plantados: "
            f"{sorted(set(por_evento) - set(ESPERADAS))}",
        )
        print("2) as 5 categorias detectadas nos 5 eventos, sem falso positivo")

        resultado = modulo_handler.executar(eventos, politica)
        for evento in resultado.eventos:
            for texto in evento.textos():
                checar(
                    modulo_pii.detectar(texto) == [],
                    f"PII residual apos mascarar em {evento.id}: {texto}",
                )
        print("3) mascarado sem PII residual")

        checar(
            abs(resultado.custo_total - CUSTO_ESPERADO) < 0.0001,
            f"custo {resultado.custo_total:.4f} difere do manual {CUSTO_ESPERADO}",
        )
        print(f"4) custo {resultado.custo_total:.4f} bate com o calculo manual")

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            codigo = cli_main(
                ["executar", str(JSONL), "--politica", str(POLITICA)]
            )
        checar(codigo == 1, f"o CLI deveria sair com 1 (ha PII), saiu com {codigo}")
        print("5) o CLI sinaliza lote com PII com saida 1")
    except Falha as erro:
        print("\nACEITE FALHOU:")
        print(f"  - {erro}")
        return 1

    print("\nok: 5 PIIs detectadas e mascaradas, custo confere, CLI sinaliza")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())