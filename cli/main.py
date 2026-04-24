"""NudgeAI CLI entry point.

Usage:
    python -m cli <command> [options]

Commands:
    sync       Sync data from Google sources (calendar, drive, location, fit).
    index      Sync and embed all data into the RAG vector DB.
    query      Semantic search across indexed data.
    nudge      Generate a context-aware nudge from a free-text prompt.
    summary    Generate a daily summary.
    status     Show sync summary + RAG index stats.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYNC_DIR = PROJECT_ROOT / "data_sync"


def _print(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, default=str))
        return
    if isinstance(payload, str):
        print(payload)
        return
    print(json.dumps(payload, indent=2, default=str))


def _parse_filters(raw: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in raw or []:
        if "=" not in item:
            raise SystemExit(f"Invalid --filter '{item}'. Use key=value.")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def cmd_sync(args: argparse.Namespace) -> int:
    from data_ingestion.data_sync_manager import DataSyncManager

    mgr = DataSyncManager()
    params = {
        "calendar": {"max_results": args.max_results},
        "drive": {"max_results": args.max_results},
        "location": {"days": args.days},
        "fit": {"days": args.days},
    }

    if args.source:
        if args.source not in mgr.data_sources:
            print(f"Unknown source: {args.source}", file=sys.stderr)
            return 2
        results = {args.source: mgr.sync_source(args.source, params.get(args.source, {}))}
    else:
        results = mgr.sync_all(params)

    summary = {src: len(items) for src, items in results.items()}
    if args.save:
        out_dir = mgr.save_sync_results(results)
        summary["_saved_to"] = out_dir

    _print({"sync_summary": summary}, args.json)
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    from ragsystem.mcp_integration import rag_mcp_integrator

    types = args.types or ["calendar", "location", "fit"]
    stats = rag_mcp_integrator.sync_and_index_all_data(data_types=types)
    rag_stats = rag_mcp_integrator.get_rag_stats()
    _print({"indexed": stats, "rag": rag_stats}, args.json)
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    from ragsystem.mcp_integration import rag_mcp_integrator

    filters = _parse_filters(args.filter) or None
    results = rag_mcp_integrator.semantic_search(args.query, k=args.k, filters=filters)

    if args.json:
        _print({"query": args.query, "results": results}, True)
        return 0

    if not results:
        print(f"No matches for: {args.query}")
        return 0

    print(f"Top {len(results)} matches for: {args.query}\n")
    for i, r in enumerate(results, 1):
        doc = r.get("document", {})
        meta = doc.get("metadata", {})
        score = r.get("similarity_score", 0.0)
        title = meta.get("name") or meta.get("summary") or doc.get("id", "?")
        print(f"  {i}. [{score:.3f}] {title}  ({meta.get('type', '?')})")
    return 0


def cmd_nudge(args: argparse.Namespace) -> int:
    from ragsystem.mcp_integration import rag_mcp_integrator

    context = args.context or "What should I do next?"
    results = rag_mcp_integrator.semantic_search(context, k=args.k)
    nudge = {
        "context": context,
        "suggestions": [
            {
                "id": r.get("document", {}).get("id"),
                "score": r.get("similarity_score"),
                "metadata": r.get("document", {}).get("metadata", {}),
            }
            for r in results
        ],
    }
    _print(nudge, args.json)
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    from ragsystem.pattern_analyzer import pattern_analyzer

    summary = pattern_analyzer.generate_daily_summary(args.date)
    _print(summary, args.json)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    sync_summary_path = SYNC_DIR / "sync_summary.json"
    sync_summary: Dict[str, Any] = {}
    if sync_summary_path.exists():
        try:
            sync_summary = json.loads(sync_summary_path.read_text())
        except json.JSONDecodeError:
            sync_summary = {"_error": "invalid sync_summary.json"}

    rag_stats: Dict[str, Any] = {}
    try:
        from ragsystem.mcp_integration import rag_mcp_integrator

        rag_stats = rag_mcp_integrator.get_rag_stats()
    except Exception as exc:
        rag_stats = {"_error": str(exc)}

    payload = {"sync_summary": sync_summary, "rag": rag_stats}
    _print(payload, args.json)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nudgeai", description="NudgeAI command-line interface.")
    p.add_argument("--json", action="store_true", help="Emit JSON output.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("sync", help="Sync data sources.")
    s.add_argument("--source", choices=["calendar", "drive", "location", "fit"], default=None)
    s.add_argument("--days", type=int, default=14)
    s.add_argument("--max-results", type=int, default=15, dest="max_results")
    s.add_argument("--save", action="store_true", help="Persist results to data_sync/.")
    s.set_defaults(func=cmd_sync)

    i = sub.add_parser("index", help="Sync + embed into RAG.")
    i.add_argument("--types", nargs="+", choices=["calendar", "drive", "location", "fit"])
    i.set_defaults(func=cmd_index)

    q = sub.add_parser("query", help="Semantic search.")
    q.add_argument("query", help="Free-text query.")
    q.add_argument("-k", type=int, default=5)
    q.add_argument("--filter", action="append", default=[], help="key=value (repeatable).")
    q.set_defaults(func=cmd_query)

    n = sub.add_parser("nudge", help="Generate a context-aware nudge.")
    n.add_argument("--context", default=None)
    n.add_argument("-k", type=int, default=3)
    n.set_defaults(func=cmd_nudge)

    su = sub.add_parser("summary", help="Daily summary.")
    su.add_argument("--date", default=None, help="ISO date (YYYY-MM-DD).")
    su.set_defaults(func=cmd_summary)

    st = sub.add_parser("status", help="Sync + RAG index status.")
    st.set_defaults(func=cmd_status)

    return p


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
