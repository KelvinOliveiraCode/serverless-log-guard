# serverless-log-guard

<div align="center">

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-33%20passing-brightgreen?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-81%25-yellowgreen?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=flat-square" alt="Windows">
  <img src="https://img.shields.io/badge/deps-PyYAML%20only-blue?style=flat-square" alt="Deps">
</p>

</div>


A locally simulated serverless function: receives events, normalizes, filters
sensitive data, applies retention and estimates cost.

> **Nothing here is real.** No cloud is accessed, no provider is called.
> The function is plain Python, the trigger is a file, and the cost is an
> in-house model with fictitious prices.

## What it is

Twenty events in a JSONL, four levels, five planted PII categories. The
pipeline normalizes each event, detects and masks PII, decides by the
retention policy what stays, and sums the cost — with non-zero exit when
there is sensitive data in the batch.

## Why it was built

Serverless charges per execution and per storage, and cost control is the
main risk of the model. But the bigger risk is not in the bill: it is in the
log. A function that records a CPF in plaintext leaks data on every
execution, and retention without a policy keeps the leak for an indefinite
time.

## How to run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m pytest tests/ -v
python -m slsguard --help
```

With the environment active, the main flow:

```powershell
python -m slsguard executar dados/eventos-sinteticos.jsonl --politica dados/politica-retencao.yaml
```

```
eventos processados: 20
eventos retidos: 20
descartados pela retencao: 0
eventos com PII mascarada: 5
custo estimado: 0.5200
```

Run without installing (useful for a quick check):

```powershell
$env:PYTHONPATH="$PWD\src"; python -m slsguard executar dados/eventos-sinteticos.jsonl --politica dados/politica-retencao.yaml
```

Installation:

```powershell
pip install -e ".[dev]"
```

## The 5 PII categories

| Category | Planted example | Mask |
|---|---|---|
| CPF | 123.456.789-00 | only last 3 digits |
| E-mail | cliente.teste@example.invalid | only domain |
| Phone | (11) 90000-0000 | only area code |
| Card | 4111-1111-1111-1111 | only last 4 |
| IP | 192.168.99.77 | only /24 |

All PII is fictitious in valid format: CPF with invalid check digit,
.invalid domain, industry test number. The detector finds the 5 in the 5
events and nothing else — zero false positives, verified by the acceptance
check.

## Retention by level

| Level | Days |
|---|---|
| debug | 7 |
| info | 30 |
| error | 90 |
| audit | 365, never discarded |

Audit is evidence, and evidence discarded by routine is destroyed evidence.

## Cost and manual calculation

Base 0.02 per execution plus duration times price per ms times memory:
20 × 0.02 + 20 × 120 × 0.0001 × 0.5 = **0.52**. The arithmetic is open in
the module and the test pins the number.

## What I learned

- **Mask before retaining.** If retention came first, what got stored would
  contain PII. What stays retained is already clean.
- **A detector that finds everything and a bit more lies.** Five categories
  in five events, zero false positive — the other side is tested too.
- **Audit never expires.** Not a business rule, a consequence of what audit
  means.
- **A CLI that reports and still passes teaches you to ignore it.** With PII
  in the batch, exit code is 1.

## Tests

```powershell
python -m pytest -v
```

33 tests. They cover the event, the 5 categories, masking, retention at the
boundaries, the cost against the manual calculation, the handler, and the
CLI.

```powershell
python tools/verificar_aceite.py     # 5 PIIs + cost + CLI output
python tools/verificar_encoding.py   # no corrupted characters
```

## Limitations

- **Regex, not NLP.** PII outside the expected format slips through. It is a
  detector, not comprehension.
- **Duration and memory are batch parameters**, not measured. The cost is a
  model, not a measurement.
- **Age is simulated.** The CLI takes `--idade`; there is no real clock.
- **No cold start, transfer, or storage in the cost.** The model covers
  execution, duration, and memory.
- **Retention does not delete anything.** It decides what would stay; actual
  deletion would be another system.

## License

MIT.
