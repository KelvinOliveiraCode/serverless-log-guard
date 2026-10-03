"""Gera o exemplo de relatorio a partir da saida real.

Generate the report example from the real output.

O exemplo vai para o repositorio para ser lido sem instalar nada, entao ele
precisa ser a saida de verdade e nao uma transcricao. Gerar via `>` do
PowerShell grava UTF-16 com BOM, que quebra o determinismo e o diff - por
isso a geracao passa por aqui, com UTF-8 sem BOM garantido.
"""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from slsguard.cli import main as cli_main  # noqa: E402

DESTINO = RAIZ / "exemplos" / "relatorio-custo.txt"


def principal() -> int:
    """Regera o exemplo e grava no destino.

    Regenerate the example and write it to the destination.

    Returns:
        Sempre 0. O CLI sai com 1 havendo PII, o que e esperado.
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        cli_main(
            [
                "executar",
                "dados/eventos-sinteticos.jsonl",
                "--politica",
                "dados/politica-retencao.yaml",
                "--idade",
                "0",
            ]
        )
    DESTINO.write_text(buffer.getvalue(), encoding="utf-8", newline="\n")
    print(f"exemplo gravado em {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())