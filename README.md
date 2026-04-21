# AI Cost Lens

[![CI](https://github.com/dianuhs/ai-cost-lens/actions/workflows/test.yml/badge.svg)](https://github.com/dianuhs/ai-cost-lens/actions/workflows/test.yml)

**Part of the Visibility → Variance → Tradeoffs pipeline.**

| Tool | Role | Repo |
|------|------|------|
| FinOps Lite | Cost visibility — AWS/Azure/GCP spend, FOCUS 1.0 export | [dianuhs/finops-lite](https://github.com/dianuhs/finops-lite) |
| FinOps Watchdog | Anomaly detection — spend spikes from any cost CSV | [dianuhs/finops-watchdog](https://github.com/dianuhs/finops-watchdog) |
| Recovery Economics | Resilience modeling — backup/restore cost + scenario compare | [dianuhs/recovery-economics](https://github.com/dianuhs/recovery-economics) |
| Cloud Cost Guard | Dashboard — spend trends, savings coverage, rightsizing | [dianuhs/cloud-cost-guard](https://github.com/dianuhs/cloud-cost-guard) |
| **AI Cost Lens** | AI spend observability — model-level cost analysis across OpenAI, Anthropic, Bedrock | [dianuhs/ai-cost-lens](https://github.com/dianuhs/ai-cost-lens) |

These five tools form one production FinOps pipeline built for finance and engineering teams: pull raw cost data → detect anomalies → model resilience tradeoffs → surface everything in a dashboard → understand AI model spend specifically.

---

**AI Cost Lens** is a CLI tool that reads billing exports from OpenAI, Anthropic, and AWS Bedrock and produces FOCUS-style cost analysis at the model level.

## What It Does

- Reads billing CSV exports from **OpenAI**, **Anthropic**, and **AWS Bedrock**
- **Auto-detects provider** from CSV column signatures — no `--provider` flag needed
- Outputs FOCUS 1.0 columns: `BilledCost`, `ResourceId`, `ServiceName`, `ChargePeriodStart`, `ChargePeriodEnd`, `ChargeType`
- `ServiceName` = the **model name** (e.g. `gpt-4o`, `claude-sonnet-4-6`, `amazon.nova-pro-v1:0`)
- `--group-by model` — rank spend by model
- `--group-by day` — show daily AI spend trends
- `--format json/csv/table` — machine-readable or human-readable
- `--compare` — compare two billing periods side by side

## Install

```bash
pip install -e .
# or
pipx install "git+https://github.com/dianuhs/ai-cost-lens.git"
```

## Provider Support

| Provider | Detection signal | Source |
|----------|-----------------|--------|
| OpenAI | `model` column + model name starts with `gpt-`, `o1`, `o3`, `whisper`, `dall-e` | platform.openai.com/usage → Export CSV |
| Anthropic | `model` column + model name starts with `claude-` | console.anthropic.com → Usage → Export |
| AWS Bedrock | `model_id` column | Cost Explorer or CUR export |

## Quickstart

### Analyze by model

```bash
ai-cost-lens analyze \
  --input examples/openai-sample.csv \
  --group-by model \
  --format table
```

```
  ----------------------------------------------------------------------------------
  Model                      Cost  Input Tok    Output Tok   Requests  Provider
  ----------------------------------------------------------------------------------
  gpt-4o                  $9.9050    365000        128000        450  openai
  o1-mini                 $3.7100    135000         53000        235  openai
  gpt-4o-mini             $1.6480   2670000        720000       6300  openai
  text-embedding-3-small  $0.2560   6400000             0       2130  openai
  ----------------------------------------------------------------------------------
  TOTAL                  $15.5190
```

### Analyze by day

```bash
ai-cost-lens analyze \
  --input examples/anthropic-sample.csv \
  --group-by day \
  --format json
```

### Compare two periods

```bash
ai-cost-lens compare \
  --baseline examples/openai-sample.csv \
  --proposed examples/bedrock-sample.csv \
  --group-by model
```

### Machine-readable output

```bash
ai-cost-lens analyze --input billing.csv --format json | jq '.rows[] | select(.cost > 5)'
ai-cost-lens analyze --input billing.csv --format csv > ai-spend.csv
```

## Exit Codes

- `0` success
- `2` CLI usage error
- `3` input file error
- `4` schema/data error
- `5` internal error

## Examples

See [`examples/`](examples/) for sample CSVs and expected outputs for all three providers.

## Pipeline

AI Cost Lens adds AI model spend observability to the pipeline:

1. **[FinOps Lite](https://github.com/dianuhs/finops-lite)** — pull infrastructure spend from AWS/Azure/GCP
2. **[FinOps Watchdog](https://github.com/dianuhs/finops-watchdog)** — detect anomalies in that spend
3. **[Recovery Economics](https://github.com/dianuhs/recovery-economics)** — model resilience cost tradeoffs
4. **[Cloud Cost Guard](https://github.com/dianuhs/cloud-cost-guard)** — dashboard layer
5. **AI Cost Lens** — model-level AI spend: which models cost most, how spend is trending, how providers compare

## License

MIT
