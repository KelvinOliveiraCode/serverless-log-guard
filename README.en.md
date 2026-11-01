# serverless-log-guard

**English** · [Português (Brasil)](README.md)

[![Python 3](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](#) [![PyYAML](https://img.shields.io/badge/PyYAML-only%20dep-3776AB?style=flat-square)](#) [![pytest](https://img.shields.io/badge/pytest-33%20tests-0A9EDC?style=flat-square&logo=pytest)](#) [![MIT License](https://img.shields.io/badge/License-MIT-f4c430?style=flat-square)](LICENSE)

## What it is

**A serverless log guard**: it normalises structured events, detects PII (credit card, CPF) via regex with masking, enforces retention policies (days per type), computes per-event cost (duration × memory) and simulates a handler run. It is an educational security/compliance lab for serverless functions.

## Status

An educational lab, working and tested (33 tests).

## Features

- **Event** (`evento.py`): `normalizar`, `carregar` (structured).
- **PII** (`pii.py`): `detectar(texto)` → `AchadoPII` (digits, card, CPF), `mascarar` (masks with ***). `_sobrepoe` manages overlaps.
- **Retention** (`retencao.py`): `carregar_politica` (YAML), `deve_manter` by type + days.
- **Cost** (`custo.py`): `calcular` (events, duration, memory), `custo_por_tipo`.
- **Handler** (`handler.py`): `executar` → `Resultado`.
- **CLI** (`slsguard`).

## Architecture

A `slsguard` package with `evento` (load), `pii` (detection+mask), `retencao` (policy), `custo` (finances), `handler` (simulation).

## Stack

- Python ≥ 3.10, PyYAML ≥ 6.0
- pytest (dev)

## Repository layout

```
serverless-log-guard/
├── src/slsguard/    # evento · pii · retencao · custo · handler · cli
├── tests/           # 33 tests
└── LICENSE          # MIT
```

## Prerequisites and installation

```bash
pip install -e .
```

## How to run

```bash
slsguard dados/
```

## Tests and quality

```bash
PYTHONPATH=src python -m pytest tests/   # 33 passed
```

## Technical decisions

- Regex-based PII: simple and transparent; basic card/CPF coverage.
- Serverless cost per event: duration_ms × memory_gb × factor.

## Known limitations

- Basic regex for PII; no semantic context.
- Cost computed by a simplified formula (no real provider pricing).

## Development process

An individual project by Kelvin Oliveira, built with orchestrated AI agents and reviewed by the author.

## License and author

MIT — Copyright (c) 2026 Kelvin Rebelo de Oliveira. Author: [Kelvin Oliveira](https://github.com/KelvinOliveiraCode) · [Portfolio](https://kelvinoliveiracode.github.io/portfolio/)
