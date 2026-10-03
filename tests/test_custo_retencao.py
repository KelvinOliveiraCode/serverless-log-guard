"""Testes de custo e retencao.

Cost and retention tests.

O custo tem um numero que nao pode mudar sem motivo: 0.52 para os 20 eventos
nos parametros padrao, com a aritmetica aberta no modulo. A retencao tem cinco
decisoes de fronteira que nao podem inverter: auditoria nunca cai, debug cai
cedo, info cai no dia 31 e nao no 30.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from slsguard import custo, retencao
from slsguard.evento import carregar, normalizar

RAIZ = Path(__file__).resolve().parent.parent
JSONL = RAIZ / "dados" / "eventos-sinteticos.jsonl"
POLITICA = RAIZ / "dados" / "politica-retencao.yaml"


@pytest.fixture(scope="module")
def eventos():
    return carregar(JSONL)


@pytest.fixture(scope="module")
def politica():
    return retencao.carregar_politica(POLITICA)


def _evento(nivel: str):
    return normalizar({"id": "x", "tipo": "t", "mensagem": "m", "nivel": nivel})


class TestCusto:
    """O modelo de custo."""

    def test_total_manual(self, eventos) -> None:
        resultado = custo.calcular(eventos, 120.0, 0.5)
        assert resultado.total == pytest.approx(0.52, abs=0.0001)
        assert resultado.execucoes == 20

    def test_zero_eventos(self) -> None:
        assert custo.calcular([], 120.0, 0.5).total == 0.0

    def test_por_tipo_soma_a_parte_fixa(self, eventos) -> None:
        # Por decisao documentada no modulo: por tipo entra so a parte fixa,
        # porque duracao e memoria sao parametros do lote. A soma tem de bater
        # com 20 vezes a base, nem mais nem menos.
        por_tipo = custo.custo_por_tipo(eventos)
        assert sum(por_tipo.values()) == pytest.approx(20 * 0.02)

    def test_duracao_zero_so_base(self, eventos) -> None:
        resultado = custo.calcular(eventos, 0.0, 0.5)
        assert resultado.total == pytest.approx(20 * 0.02)


class TestRetencao:
    """As cinco decisoes de fronteira."""

    def test_auditoria_nunca_cai(self, politica) -> None:
        assert retencao.deve_manter(_evento("auditoria"), 9999, politica) is True

    def test_debug_cai_cedo(self, politica) -> None:
        assert retencao.deve_manter(_evento("debug"), 8, politica) is False
        assert retencao.deve_manter(_evento("debug"), 7, politica) is True

    def test_info_na_fronteira(self, politica) -> None:
        assert retencao.deve_manter(_evento("info"), 30, politica) is True
        assert retencao.deve_manter(_evento("info"), 31, politica) is False

    def test_erro_no_prazo(self, politica) -> None:
        assert retencao.deve_manter(_evento("erro"), 90, politica) is True
        assert retencao.deve_manter(_evento("erro"), 91, politica) is False

    def test_politica_carrega_prazos(self, politica) -> None:
        dias, nunca = politica
        assert dias == {"debug": 7, "info": 30, "erro": 90, "auditoria": 365}
        assert "auditoria" in nunca