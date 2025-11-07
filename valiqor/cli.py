"""
Valiqor Trace SDK - Command Line Interface

Simple CLI for demo tracing and repository scanning.
"""

import argparse
import sys
from typing import List, Optional

from .context_scanner import scan_repo
from .trace import Trace


def main(argv: Optional[List[str]] = None):
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="valiqor",
        description="Valiqor Trace SDK - Local AI workflow tracing demo"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Trace command with subcommands
    trace_parser = subparsers.add_parser("trace", help="Trace commands")
    trace_subparsers = trace_parser.add_subparsers(dest="trace_command", help="Trace subcommands")
    
    run_parser = trace_subparsers.add_parser("run", help="Run demo trace")
    run_parser.add_argument("--app", required=True, help="Application name")
    run_parser.add_argument("--scenario", default="demo", help="Scenario ID")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan repository")
    scan_parser.add_argument("repo", help="Repository path")
    scan_parser.add_argument("--out", default="context_map.json", help="Output file")
    
    # Parse args
    args = parser.parse_args(argv)
    
    if args.command == "trace":
        if args.trace_command == "run":
            run_demo_trace(args.app, args.scenario)
        else:
            trace_parser.print_help()
            return 1
    elif args.command == "scan":
        run_scan(args.repo, args.out)
    else:
        parser.print_help()
        return 1
    
    return 0


def run_demo_trace(app: str, scenario: str):
    """Run a demo trace with synthetic spans"""
    print(f"🚀 Running demo trace for {app} (scenario: {scenario})")
    
    trace = Trace(app=app, env="demo")
    
    with trace.session(metadata={"scenario": scenario}):
        # Span 1: LLM call
        trace.add_span(
            name="llm.call",
            model="gpt-4",
            provider="openai",
            prompt="Analyze Q3 revenue for ACME Corp",
            response="Q3 revenue shows 15% growth...",
            input_tokens=120,
            output_tokens=85,
            latency_ms=1250,
            cost_usd=0.0045
        )
        
        # Span 2: Tool call
        trace.add_span(
            name="tool.normalize_currency",
            input={"amount": "$1.5M", "target": "USD"},
            output={"normalized": 1500000, "currency": "USD"},
            latency_ms=45
        )
        
        # Span 3: Judge note
        trace.add_span(
            name="judge.reason",
            evaluation="correct",
            confidence=0.95,
            reason="Response accurately reflects financial data",
            latency_ms=380
        )
    
    print("✅ Demo trace completed!")


def run_scan(repo_path: str, output_file: str):
    """Run repository scan"""
    print(f"📂 Scanning repository: {repo_path}")
    
    try:
        context = scan_repo(repo_path, output_file)
        print(f"✅ Context map saved with {context['file_count']} files")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
