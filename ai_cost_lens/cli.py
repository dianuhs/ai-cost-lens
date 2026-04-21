"""AI Cost Lens CLI — FOCUS-style cost analysis for OpenAI, Anthropic, and AWS Bedrock."""

from __future__ import annotations

import csv
import io
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import click

from .providers.detector import FOCUS_FIELDNAMES, FocusRecord, load_and_normalize

SCHEMA_VERSION = "1.0"
EXIT_SUCCESS = 0
EXIT_USAGE_ERROR = 2
EXIT_INPUT_FILE_ERROR = 3
EXIT_SCHEMA_DATA_ERROR = 4
EXIT_INTERNAL_ERROR = 5


class InputFileError(Exception):
    pass


class SchemaDataError(Exception):
    pass


@click.group()
def cli() -> None:
    """AI Cost Lens — FOCUS-style cost analysis for OpenAI, Anthropic, and AWS Bedrock."""


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------

@cli.command("analyze")
@click.option(
    "--input", "input_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to AI billing CSV export.",
)
@click.option(
    "--group-by",
    type=click.Choice(["model", "day"], case_sensitive=False),
    default="model",
    show_default=True,
    help="Aggregate by model name or by calendar day.",
)
@click.option(
    "--format", "output_format",
    type=click.Choice(["json", "csv", "table"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Output format.",
)
@click.pass_context
def analyze(ctx: click.Context, input_path: Path, group_by: str, output_format: str) -> None:
    """Read an AI billing CSV and produce FOCUS-style cost analysis."""
    try:
        records = _load(input_path)
        rows = _aggregate(records, group_by.lower())
        _emit_analyze(rows, group_by.lower(), output_format.lower(), sys.stdout)
    except InputFileError as exc:
        click.echo(f"Input file error: {exc}", err=True)
        ctx.exit(EXIT_INPUT_FILE_ERROR)
    except SchemaDataError as exc:
        click.echo(f"Schema/data error: {exc}", err=True)
        ctx.exit(EXIT_SCHEMA_DATA_ERROR)
    except Exception as exc:
        click.echo(f"Internal error: {exc}", err=True)
        ctx.exit(EXIT_INTERNAL_ERROR)


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

@cli.command("compare")
@click.option(
    "--baseline", "baseline_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to baseline period billing CSV.",
)
@click.option(
    "--proposed", "proposed_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to proposed/comparison period billing CSV.",
)
@click.option(
    "--group-by",
    type=click.Choice(["model", "day"], case_sensitive=False),
    default="model",
    show_default=True,
    help="Aggregate by model name or by calendar day.",
)
@click.pass_context
def compare(ctx: click.Context, baseline_path: Path, proposed_path: Path, group_by: str) -> None:
    """Compare AI spend between two time periods side by side."""
    try:
        baseline_records = _load(baseline_path)
        proposed_records = _load(proposed_path)
        baseline_rows = _aggregate(baseline_records, group_by.lower())
        proposed_rows = _aggregate(proposed_records, group_by.lower())
        _emit_compare(baseline_rows, proposed_rows, group_by.lower(),
                      str(baseline_path), str(proposed_path), sys.stdout)
    except InputFileError as exc:
        click.echo(f"Input file error: {exc}", err=True)
        ctx.exit(EXIT_INPUT_FILE_ERROR)
    except SchemaDataError as exc:
        click.echo(f"Schema/data error: {exc}", err=True)
        ctx.exit(EXIT_SCHEMA_DATA_ERROR)
    except Exception as exc:
        click.echo(f"Internal error: {exc}", err=True)
        ctx.exit(EXIT_INTERNAL_ERROR)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load(path: Path) -> List[FocusRecord]:
    if not path.exists():
        raise InputFileError(f"File not found: {path}")
    try:
        return load_and_normalize(path)
    except ValueError as exc:
        raise SchemaDataError(str(exc)) from exc
    except PermissionError as exc:
        raise InputFileError(f"File not readable: {path}") from exc


def _aggregate(records: List[FocusRecord], group_by: str) -> List[Dict[str, Any]]:
    """Return sorted list of {key, cost, input_tokens, output_tokens, requests, provider}."""
    totals: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "cost": 0.0, "input_tokens": 0, "output_tokens": 0, "requests": 0, "providers": set(),
    })

    for r in records:
        key = r.ServiceName if group_by == "model" else r.ChargePeriodStart
        try:
            totals[key]["cost"] += float(r.BilledCost or 0)
        except ValueError:
            pass
        try:
            totals[key]["input_tokens"] += int(r.input_tokens or 0)
        except ValueError:
            pass
        try:
            totals[key]["output_tokens"] += int(r.output_tokens or 0)
        except ValueError:
            pass
        try:
            totals[key]["requests"] += int(r.requests or 0)
        except ValueError:
            pass
        totals[key]["providers"].add(r.provider)

    rows = []
    for key, data in totals.items():
        rows.append({
            "key": key,
            "cost": round(data["cost"], 4),
            "input_tokens": data["input_tokens"],
            "output_tokens": data["output_tokens"],
            "requests": data["requests"],
            "provider": ",".join(sorted(data["providers"])),
        })

    rows.sort(key=lambda r: r["cost"], reverse=True)
    return rows


def _emit_analyze(rows: List[Dict[str, Any]], group_by: str, fmt: str, out) -> None:
    label = "Model" if group_by == "model" else "Date"
    if fmt == "json":
        payload = {
            "schema_version": SCHEMA_VERSION,
            "group_by": group_by,
            "total_cost": round(sum(r["cost"] for r in rows), 4),
            "rows": rows,
        }
        json.dump(payload, out, indent=2)
        out.write("\n")
    elif fmt == "csv":
        writer = csv.DictWriter(out, fieldnames=["key", "cost", "input_tokens", "output_tokens", "requests", "provider"],
                                lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    else:
        _print_table(rows, label, out)


def _print_table(rows: List[Dict[str, Any]], label: str, out) -> None:
    if not rows:
        out.write("No data.\n")
        return
    key_w = max(len(label), max(len(str(r["key"])) for r in rows))
    prov_w = max(8, max(len(r["provider"]) for r in rows))
    header = f"  {label:<{key_w}}  {'Cost':>10}  {'Input Tok':>12}  {'Output Tok':>12}  {'Requests':>10}  {'Provider':<{prov_w}}"
    sep = "  " + "-" * (len(header) - 2)
    out.write(f"{sep}\n{header}\n{sep}\n")
    total_cost = 0.0
    for r in rows:
        out.write(
            f"  {str(r['key']):<{key_w}}  ${r['cost']:>9.4f}  {r['input_tokens']:>12,}  "
            f"{r['output_tokens']:>12,}  {r['requests']:>10,}  {r['provider']:<{prov_w}}\n"
        )
        total_cost += r["cost"]
    out.write(f"{sep}\n")
    out.write(f"  {'TOTAL':<{key_w}}  ${total_cost:>9.4f}\n")


def _emit_compare(baseline: List[Dict], proposed: List[Dict], group_by: str,
                  baseline_name: str, proposed_name: str, out) -> None:
    b_map = {r["key"]: r["cost"] for r in baseline}
    p_map = {r["key"]: r["cost"] for r in proposed}
    all_keys = sorted(set(b_map) | set(p_map))

    label = "Model" if group_by == "model" else "Date"
    key_w = max(len(label), max((len(k) for k in all_keys), default=8))
    header = f"  {label:<{key_w}}  {'Baseline':>12}  {'Proposed':>12}  {'Delta':>12}"
    sep = "  " + "-" * (len(header) - 2)

    out.write(f"Comparison: {baseline_name}  vs  {proposed_name}\n")
    out.write(f"{sep}\n{header}\n{sep}\n")

    rows = []
    for key in all_keys:
        b = b_map.get(key, 0.0)
        p = p_map.get(key, 0.0)
        rows.append((key, b, p, p - b))
    rows.sort(key=lambda r: abs(r[3]), reverse=True)

    total_b = total_p = 0.0
    for key, b, p, delta in rows:
        sign = "+" if delta >= 0 else ""
        out.write(f"  {key:<{key_w}}  ${b:>11.4f}  ${p:>11.4f}  {sign}${delta:>10.4f}\n")
        total_b += b
        total_p += p
    total_d = total_p - total_b
    sign = "+" if total_d >= 0 else ""
    out.write(f"{sep}\n")
    out.write(f"  {'TOTAL':<{key_w}}  ${total_b:>11.4f}  ${total_p:>11.4f}  {sign}${total_d:>10.4f}\n")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
