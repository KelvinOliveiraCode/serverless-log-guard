"""Gera os eventos sinteticos de forma deterministica.

Generate the synthetic events deterministically.

Vinte eventos, um por linha JSON. As 5 categorias de PII plantadas estao
documentadas aqui e nao escondidas: o criterio de aceite e que o detector as
ache e mascare, e PII que ninguem sabe onde esta nao e criterio, e loteria.

## PII ficticia, mas valida em formato

Cada valor plantado passa no formato mas nao e real: CPF com digito
verificador invalido, e-mail em dominio .invalid, telefone com DDD e prefixo
reservados, cartao com o numero padrao de teste da industria (reconhecivel
como teste por qualquer validador), IP em faixa RFC 1918 ou de documentacao.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "dados" / "eventos-sinteticos.jsonl"
SEMENTE = 20261003

# As 5 categorias plantadas, com o evento que carrega cada uma.
PII = {
    "cpf": "123.456.789-00",
    "email": "cliente.teste@example.invalid",
    "telefone": "(11) 90000-0000",
    "cartao": "4111-1111-1111-1111",
    "ip": "192.168.99.77",
}

EVENTOS = [
    ("evt-001", "login", "info", "usuario cliente.teste@example.invalid entrou no portal"),
    ("evt-002", "pedido", "info", "pedido 1042 criado para entrega"),
    ("evt-003", "pagamento", "info", "cartao 4111-1111-1111-1111 aprovado na operadora de teste"),
    ("evt-004", "cadastro", "info", "novo cadastro com CPF 123.456.789-00 validado no formato"),
    ("evt-005", "suporte", "debug", "ticket aberto pelo telefone (11) 90000-0000"),
    ("evt-006", "monitor", "debug", "latencia p95 em 120ms no ultimo minuto"),
    ("evt-007", "pedido", "erro", "falha ao reservar estoque do pedido 1043"),
    ("evt-008", "login", "info", "sessao expirada por inatividade"),
    ("evt-009", "pagamento", "erro", "operadora recusou a transacao, sem motivo detalhado"),
    ("evt-010", "auditoria", "auditoria", "acesso administrativo ao painel de cobranca"),
    ("evt-011", "cadastro", "info", "endereco atualizado sem documento anexo"),
    ("evt-012", "monitor", "debug", "uso de CPU em 41% no agregador"),
    ("evt-013", "suporte", "info", "retorno de chamada agendado para amanha"),
    ("evt-014", "pedido", "info", "pedido 1044 separado no deposito"),
    ("evt-015", "login", "erro", "tres tentativas falhas seguidas do IP 192.168.99.77"),
    ("evt-016", "pagamento", "info", "estorno solicitado para o pedido 1042"),
    ("evt-017", "monitor", "info", "disco em 62% no no de registros"),
    ("evt-018", "auditoria", "auditoria", "exportacao de relatorio mensal concluida"),
    ("evt-019", "suporte", "debug", "anexo recebido e encaminhado ao nivel 2"),
    ("evt-020", "pedido", "erro", "timeout no calculo de frete do pedido 1045"),
]


def principal() -> int:
    """Gera o JSONL.

    Generate the JSONL.

    Returns:
        Sempre 0.
    """
    rng = random.Random(SEMENTE)
    ordem = list(range(len(EVENTOS)))
    rng.shuffle(ordem)
    linhas = []
    for indice in ordem:
        eid, tipo, nivel, mensagem = EVENTOS[indice]
        linhas.append(
            json.dumps(
                {"id": eid, "tipo": tipo, "nivel": nivel, "mensagem": mensagem},
                ensure_ascii=True,
            )
        )
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(f"eventos gravados em {DESTINO.relative_to(RAIZ)}: {len(linhas)}")
    print("PII plantada: cpf, email, telefone, cartao, ip")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())