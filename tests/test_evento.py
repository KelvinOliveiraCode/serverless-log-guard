"""Testes do evento e do contrato.

Event and contract tests.

O evento e o contrato: handler, PII, retencao e custo consomem o que este
modulo produz. Um campo obrigatorio que passa vazio aqui vira `KeyError` la -
e o teste que pega isso e aqui, nao la.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from slsguard.evento import (
    NIVEIS,
    ErroDeEvento,
    carregar,
    normalizar,
)

RAIZ = Path(__file__).resolve().parent.parent
JSONL = RAIZ / "dados" / "eventos-sinteticos.jsonl"


class TestArquivoReal:
    """Os 20 eventos carregam."""

    def test_carrega_20(self) -> None:
        assert len(carregar(JSONL)) == 20

    def test_quatro_niveis(self) -> None:
        assert {e.nivel for e in carregar(JSONL)} == set(NIVEIS)

    def test_ids_unicos(self) -> None:
        eventos = carregar(JSONL)
        assert len({e.id for e in eventos}) == 20


class TestNormalizar:
    """A normalizacao."""

    def test_campos_extras_preservados(self) -> None:
        evento = normalizar(
            {"id": "x", "tipo": "t", "mensagem": "m", "extra": "e"}, linha=1
        )
        assert evento.campos == {"extra": "e"}
        assert evento.linha == 1

    def test_nivel_padrao_info(self) -> None:
        assert normalizar({"id": "x", "tipo": "t", "mensagem": "m"}).nivel == "info"

    def test_nivel_desconhecido(self) -> None:
        with pytest.raises(ErroDeEvento):
            normalizar({"id": "x", "tipo": "t", "mensagem": "m", "nivel": "x"})

    def test_campo_obrigatorio_vazio(self) -> None:
        with pytest.raises(ErroDeEvento):
            normalizar({"id": " ", "tipo": "t", "mensagem": "m"})

    def test_nao_mapa(self) -> None:
        with pytest.raises(ErroDeEvento):
            normalizar(["x"], linha=3)  # type: ignore[arg-type]

    def test_textos_varre_mensagem_e_campos(self) -> None:
        evento = normalizar(
            {"id": "x", "tipo": "t", "mensagem": "m", "doc": "d", "n": 1}
        )
        assert evento.textos() == ["m", "d"]


class TestArquivo:
    """A leitura do JSONL."""

    def test_inexistente(self, tmp_path: Path) -> None:
        with pytest.raises(ErroDeEvento):
            carregar(tmp_path / "nao-existe.jsonl")

    def test_linha_invalida(self, tmp_path: Path) -> None:
        arquivo = tmp_path / "x.jsonl"
        arquivo.write_text('{"id": "a"}\n', encoding="utf-8")
        with pytest.raises(ErroDeEvento):
            carregar(arquivo)

    def test_json_quebrado(self, tmp_path: Path) -> None:
        arquivo = tmp_path / "x.jsonl"
        arquivo.write_text('{"id":\n', encoding="utf-8")
        with pytest.raises(ErroDeEvento):
            carregar(arquivo)

    def test_vazio(self, tmp_path: Path) -> None:
        arquivo = tmp_path / "x.jsonl"
        arquivo.write_text("\n", encoding="utf-8")
        with pytest.raises(ErroDeEvento):
            carregar(arquivo)