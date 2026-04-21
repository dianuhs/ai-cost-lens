# Examples

Sample billing exports for all three supported providers.

## Analyze by model

```bash
ai-cost-lens analyze --input examples/openai-sample.csv --group-by model --format table
```

Expected output:

```
  -----------------------------------------------------------------------
  Model                  Cost  Input Tok    Output Tok   Requests  Provider
  -----------------------------------------------------------------------
  gpt-4o              $9.9050    365000        128000        450  openai
  o1-mini             $3.7100    135000         53000        235  openai
  gpt-4o-mini         $1.6480   2670000        720000       6300  openai
  text-embedding-...  $0.2560   6400000              0      2130  openai
  -----------------------------------------------------------------------
  TOTAL              $15.5190
```

## Analyze by day

```bash
ai-cost-lens analyze --input examples/anthropic-sample.csv --group-by day --format json
```

## Compare two periods

```bash
ai-cost-lens compare \
  --baseline examples/openai-sample.csv \
  --proposed examples/bedrock-sample.csv \
  --group-by model
```

## Multi-provider combined analysis

Concatenate exports from multiple providers (skip repeated headers) and analyze together:

```bash
(head -1 examples/openai-sample.csv; tail -n +2 examples/openai-sample.csv; tail -n +2 examples/anthropic-sample.csv) > combined.csv
ai-cost-lens analyze --input combined.csv --group-by model --format table
```
