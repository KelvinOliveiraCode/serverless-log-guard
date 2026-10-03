# slsguard

Função serverless simulada localmente: recebe evento, normaliza, filtra dado
sensível, aplica retenção e calcula custo estimado.

A locally simulated serverless function: receives events, normalizes, filters
sensitive data, applies retention and estimates cost.

> **Nada aqui é real.** Nenhuma nuvem é acessada, nenhum provedor é chamado.
> A "função" é Python puro, o gatilho é um arquivo e o custo é um modelo
> próprio com preços fictícios.

## O que é

Vinte eventos num JSONL, quatro níveis, cinco categorias de PII plantadas. O
pipeline normaliza cada evento, detecta e mascara PII, decide pela política
de retenção o que fica, e soma o custo — com saída diferente de zero quando
há dado sensível no lote.

## Por que foi feito

Serverless cobra por execução e por armazenamento, e controle de custo é o
principal risco do modelo. Mas o risco maior não está na fatura: está no log.
Função que registra CPF em texto claro vaza dado a cada execução, e retenção
sem política guarda o vazamento por tempo indeterminado.

## Como rodar

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

Instalação:

```powershell
pip install -e ".[dev]"
```

## As 5 categorias de PII

| Categoria | Exemplo plantado | Máscara |
|---|---|---|
| CPF | 123.456.789-00 | só últimos 3 dígitos |
| E-mail | cliente.teste@example.invalid | só domínio |
| Telefone | (11) 90000-0000 | só DDD |
| Cartão | 4111-1111-1111-1111 | só últimos 4 |
| IP | 192.168.99.77 | só /24 |

Toda PII é fictícia em formato válido: CPF com dígito inválido, domínio
.invalid, número de teste da indústria. O detector acha as 5 nos 5 eventos e
mais nada — zero falso positivo, verificado pelo aceite.

## Retenção por nível

| Nível | Dias |
|---|---|
| debug | 7 |
| info | 30 |
| erro | 90 |
| auditoria | 365, nunca descartada |

Auditoria é prova, e prova descartada por rotina é prova destruída.

## O custo e o cálculo manual

Base 0.02 por execução mais duração vezes preço por ms vezes memória:
20 × 0.02 + 20 × 120 × 0.0001 × 0.5 = **0.52**. A aritmética está aberta no
módulo e o teste trava o número.

## O que aprendi

- **Mascarar antes de reter.** Se a retenção viesse primeiro, o guardado teria
  PII. O que fica retido já está limpo.
- **Detector que acha tudo e mais um pouco mente.** Cinco categorias em cinco
  eventos, zero falso positivo — o outro lado também é testado.
- **Auditoria não expira.** Não é regra de negócio, é consequência do que
  auditoria significa.
- **CLI que relata e passa ensina a ignorar.** Com PII no lote, saída 1.

## Testes

```powershell
python -m pytest -v
```

33 testes. Cobrem o evento, as 5 categorias, o mascaramento, a retenção nas
fronteiras, o custo contra o cálculo manual, o handler e a CLI.

```powershell
python tools/verificar_aceite.py     # 5 PIIs + custo + saida do CLI
python tools/verificar_encoding.py   # nenhum caractere corrompido
```

## Limitações

- **Regex, não NLP.** PII fora do formato esperado passa. É detector, não
  compreensão.
- **Duração e memória são parâmetros do lote**, não medidos. O custo é modelo,
  não medição.
- **Idade é simulada.** A CLI recebe `--idade`; não há relógio real.
- **Sem cold start, transferência ou armazenamento no custo.** O modelo cobre
  execução, duração e memória.
- **Retenção não apaga nada.** Decide o que ficaria; o descarte real seria
  outro sistema.

## Licença

MIT.

---

## English

A locally simulated serverless function: 20 events, 5 planted PII categories,
retention policy, cost model. Nothing real, no cloud accessed.

### The 5 PII categories

CPF, e-mail, phone, card, IP — fictitious in valid format. Detected in 5
events, zero false positives. Masked by type before retention.

### Retention

debug 7 days, info 30, erro 90, auditoria 365 and never discarded.

### Cost

20 × 0.02 + 20 × 120 × 0.0001 × 0.5 = **0.52**. Open arithmetic, pinned by test.

### Tests

33 tests.

```powershell
python -m pytest -v
python tools/verificar_aceite.py
python tools/verificar_encoding.py
```

### Limitations

Regex not NLP; batch parameters not measured; simulated age; no cold start;
retention decides, doesn't delete.

### License

MIT.