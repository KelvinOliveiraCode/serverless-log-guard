"""Testes de PII e do handler.

PII and handler tests.

A PII tem dois lados e os dois precisam estar certos: achar o que esta la e
nao acusar o que nao esta. Um detector que acha as 5 categorias e mais 10
falsos positivos e pior do que um que acha 4 - porque o time aprende que o
relatorio mente e para de ler.

O handler tem uma ordem que nao pode inverter: mascarar antes de reter. Se a
retencao viesse primeiro, o conteudo guardado teria PII, e apagar depois nao
apaga o que ja foi escrito no disco.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from slsguard import handler, pii, retencao
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


class TestCincoCategorias:
    """As 5 plantadas, cada uma no seu evento."""

    def test_todas_as_categorias(self, eventos) -> None:
        categorias = set()
        for evento in eventos:
            for texto in evento.textos():
                categorias.update(a.categoria for a in pii.detectar(texto))
        assert categorias == {"cpf", "email", "telefone", "cartao", "ip"}

    def test_cada_uma_no_evento_certo(self, eventos) -> None:
        por_evento = {}
        for evento in eventos:
            for texto in evento.textos():
                for achado in pii.detectar(texto):
                    por_evento.setdefault(evento.id, set()).add(achado.categoria)
        assert por_evento["evt-001"] == {"email"}
        assert por_evento["evt-003"] == {"cartao"}
        assert por_evento["evt-004"] == {"cpf"}
        assert por_evento["evt-005"] == {"telefone"}
        assert por_evento["evt-015"] == {"ip"}

    def test_so_cinco_eventos_tem_pii(self, eventos) -> None:
        com_pii = [
            evento.id for evento in eventos
            if any(pii.detectar(t) for t in evento.textos())
        ]
        assert sorted(com_pii) == [
            "evt-001", "evt-003", "evt-004", "evt-005", "evt-015",
        ]


class TestMascarar:
    """O mascaramento por tipo."""

    def test_cpf_mostra_so_fim(self) -> None:
        assert "123.456.789" not in pii.mascarar("CPF 123.456.789-00")

    def test_email_mostra_so_dominio(self) -> None:
        mascarado = pii.mascarar("contato cliente.teste@example.invalid")
        assert "cliente.teste" not in mascarado
        assert "example.invalid" in mascarado

    def test_texto_limpo_igual(self) -> None:
        texto = "pedido 1042 criado para entrega"
        assert pii.mascarar(texto) == texto

    def test_detectar_vazio_em_texto_limpo(self) -> None:
        assert pii.detectar("pedido 1042 criado para entrega") == []


class TestHandler:
    """A ordem: mascarar antes de reter."""

    def test_conta_pii_e_retidos(self, eventos, politica) -> None:
        resultado = handler.executar(eventos, politica)
        assert resultado.com_pii == 5
        assert len(resultado.eventos) == 20
        assert resultado.descartados == 0

    def test_retencao_descarta_debug_velho(self, eventos, politica) -> None:
        resultado = handler.executar(eventos, politica, idade_dias=8)
        assert resultado.descartados == 4

    def test_mascarado_nao_tem_pii(self, eventos, politica) -> None:
        resultado = handler.executar(eventos, politica)
        for evento in resultado.eventos:
            for texto in evento.textos():
                assert pii.detectar(texto) == [], texto

    def test_custo_do_lote(self, eventos, politica) -> None:
        resultado = handler.executar(eventos, politica)
        assert resultado.custo_total == pytest.approx(0.52, abs=0.0001)