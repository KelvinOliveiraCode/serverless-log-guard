# serverless-log-guard

[English](README.en.md) · **Português (Brasil)**

[![Python 3](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](#) [![PyYAML](https://img.shields.io/badge/PyYAML-%C3%BAnica%20dep-3776AB?style=flat-square)](#) [![pytest](https://img.shields.io/badge/pytest-33%20testes-0A9EDC?style=flat-square&logo=pytest)](#) [![MIT License](https://img.shields.io/badge/License-MIT-f4c430?style=flat-square)](LICENSE)

## O que é

**Guardião de logs serverless**: normaliza eventos estruturados (carga), detecta PII (cartão de crédito, CPF) via regex com mascaramento, aplica política de retenção (dias por tipo), calcula custo por evento (duração × memória) e simula um handler de execução. É um laboratório educacional de segurança e compliance em funções serverless.

## Status

Laboratório educacional funcional e testado (33 testes).

## Funcionalidades

- **Evento** (`evento.py`): `normalizar`, `carregar` (estruturado).
- **PII** (`pii.py`): `detectar(texto)` → `AchadoPII` (digitos, car tao, CPF), `mascarar` (cobre com ***). `_sobrepoe` gerencia overlaps.
- **Retenção** (`retencao.py`): `carregar_politica` (YAML), `deve_manter` por tipo + dias.
- **Custo** (`custo.py`): `calcular` (eventos, duração, memória), `custo_por_tipo`.
- **Handler** (`handler.py`): `executar` → `Resultado`.
- **CLI** (`slsguard`).

## Arquitetura

Pacote `slsguard` com `evento` (carga), `pii` (detecção+máscara), `retencao` (política), `custo` (finanças), `handler` (simulação).

## Stack

- Python ≥ 3.10, PyYAML ≥ 6.0
- pytest (dev)

## Estrutura

```
serverless-log-guard/
├── src/slsguard/    # evento · pii · retencao · custo · handler · cli
├── tests/           # 33 testes
└── LICENSE          # MIT
```

## Pré-requisitos e instalação

```bash
pip install -e .
```

## Como executar

```bash
slsguard dados/
```

## Testes e qualidade

```bash
PYTHONPATH=src python -m pytest tests/   # 33 passed
```

## Decisões técnicas

- PII por regex (simples e transparente); cobertura básica de cartão e CPF.
- Custo serverless por evento: duração_ms × memória_gb × fator.

## Limitações

- Regex básico para PII; sem contexto semântico.
- Custo calculado por fórmula simplificada (sem preço real de provedor).

## Processo de desenvolvimento

Projeto individual de Kelvin Oliveira, construído com agentes de IA orquestrados e revisado pelo autor.

## Licença e autor

MIT — Copyright (c) 2026 Kelvin Rebelo de Oliveira. Autor: [Kelvin Oliveira](https://github.com/KelvinOliveiraCode) · [Portfólio](https://kelvinoliveiracode.github.io/portfolio/)
