# AI Cost Lens

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![AI for FinOps](https://img.shields.io/badge/AI-OpenAI%20%7C%20Anthropic%20%7C%20Bedrock-ff6b35)](https://github.com/cloudandcapital/ai-cost-lens)
[![FOCUS 2026](https://img.shields.io/badge/FOCUS-2026-brightgreen)](https://focus.finops.org)

**AI and LLM spend tracking — model-level cost visibility across OpenAI, Anthropic, and AWS Bedrock.**

Part of the [Cloud & Capital](https://github.com/cloudandcapital) FinOps pipeline.  
AI spend feeds into [Cloud Cost Guard](https://github.com/cloudandcapital/cloud-cost-guard) — the unified FinOps dashboard.

---

**Features:**
- Per-model cost breakdown across all major AI providers
- Daily spend trends and period-over-period comparison
- Token efficiency analysis — cost per 1K tokens by model and task type
- Unused or redundant model detection (paying for multiple models doing the same job)
- FOCUS 2026 compliant export — AI spend in the same schema as cloud infrastructure
- JSON output compatible with Cloud Cost Guard's `ai_spend` report section

---

## Install

```bash
pip install "git+https://github.com/cloudandcapital/ai-cost-lens.git"
# or
pipx install .
```

---

## Setup

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# AWS Bedrock (uses AWS credentials)
export AWS_PROFILE=finops-prod
export AWS_DEFAULT_REGION=us-east-1
```

---

## Usage

```bash
# Summarize AI spend across all configured providers (last 30 days)
ai-cost-lens summary --days 30

# Per-model cost breakdown
ai-cost-lens breakdown --provider anthropic

# Token efficiency report
ai-cost-lens efficiency --days 30

# Export FOCUS 2026 CSV
ai-cost-lens export --format focus2026 --output ai-spend-focus2026.csv

# JSON output for Cloud Cost Guard
ai-cost-lens summary --format json > ai_spend.json
```

---

## Output (JSON)

```json
{
  "total_cost": 13160.00,
  "daily_average": 438.67,
  "trend": {
    "change_percentage": 8.4,
    "change_amount": 1024.00
  },
  "models": [
    { "model": "claude-sonnet-4-6", "provider": "anthropic", "cost": 4820.00 },
    { "model": "gpt-4o",            "provider": "openai",    "cost": 3960.00 },
    { "model": "claude-opus-4-7",   "provider": "anthropic", "cost": 2140.00 }
  ],
  "providers": ["anthropic", "openai", "bedrock"]
}
```

---

## Part of the Cloud & Capital Pipeline

| Tool | Role |
|------|------|
| [FinOps Lite](https://github.com/cloudandcapital/finops-lite) | Cost pull + FOCUS 2026 export |
| [FinOps Watchdog](https://github.com/cloudandcapital/finops-watchdog) | Anomaly detection |
| [Recovery Economics](https://github.com/cloudandcapital/recovery-economics) | Resilience cost modeling |
| **AI Cost Lens** | AI/LLM spend tracking |
| [Cloud Cost Guard](https://github.com/cloudandcapital/cloud-cost-guard) | Unified dashboard |
| [SaaS Cost Analyzer](https://github.com/cloudandcapital/saas-cost-analyzer) | SaaS license governance |
| [Tech Spend Command Center](https://github.com/cloudandcapital/tech-spend-command-center) | Executive reporting |

---

## License

MIT © 2025 Diana Molski, Cloud & Capital
