"""A linha de comando do slsguard.

The slsguard command line.

Um comando: `executar` le o JSONL, aplica a politica e imprime o resumo com
o custo. O codigo de saida e 1 quando algum evento tinha PII - nao porque PII
e erro, mas porque um lote com dado sensivel merece um olhar antes de seguir.
"""

from __future__ import annotations

import argparse
import sys

from . import handler as modulo_handler
from . import retencao as modulo_retencao
from .evento import carregar

SAIDA_OK = 0
SAIDA_PII = 1
SAIDA_ERRO = 2


def _constroi_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos.

    Build the argument parser.

    Returns:
        O parser pronto.
    """
    parser = argparse.ArgumentParser(
        prog="slsguard",
        description=(
            "Funcao serverless simulada localmente. / "
            "Locally simulated serverless function."
        ),
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_exe = sub.add_parser("executar", help="processa o arquivo de eventos")
    p_exe.add_argument("eventos", help="o JSONL de eventos")
    p_exe.add_argument("--politica", required=True)
    p_exe.add_argument("--idade", type=int, default=0)
    p_exe.add_argument("--duracao", type=float, default=120.0)
    p_exe.add_argument("--memoria", type=float, default=0.5)

    return parser


def main(argv: list[str] | None = None) -> int:
    """O ponto de entrada.

    The entry point.

    Args:
        argv: Os argumentos, sem `argv[0]`.

    Returns:
        O codigo de saida.
    """
    parser = _constroi_parser()
    argumentos = parser.parse_args(argv)

    try:
        eventos = carregar(argumentos.eventos)
        politica = modulo_retencao.carregar_politica(argumentos.politica)
    except Exception as erro:
        print(f"erro de entrada: {erro}", file=sys.stderr)
        return SAIDA_ERRO

    resultado = modulo_handler.executar(
        eventos,
        politica,
        idade_dias=argumentos.idade,
        duracao_ms=argumentos.duracao,
        memoria_gb=argumentos.memoria,
    )
    print(f"eventos processados: {len(eventos)}")
    print(f"eventos retidos: {len(resultado.eventos)}")
    print(f"descartados pela retencao: {resultado.descartados}")
    print(f"eventos com PII mascarada: {resultado.com_pii}")
    print(f"custo estimado: {resultado.custo_total:.4f}")
    return SAIDA_PII if resultado.com_pii else SAIDA_OK


if __name__ == "__main__":
    main()