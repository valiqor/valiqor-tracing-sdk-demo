# Valiqor Trace SDK

> **Local AI Workflow Tracing for Demos & MVPs**  
> No network calls • No external services • Pure local JSONL traces

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MVP Target: Jan 2026](https://img.shields.io/badge/MVP-Jan%202026-green.svg)](https://valiqor.com)

---

## What is Valiqor Trace SDK?

A **lightweight, local-only tracing SDK** for capturing AI workflow execution during demos and MVPs. Think of it as a minimal observability layer that writes sanitized traces to local JSONL files — perfect for showcasing RAG pipelines, agent workflows, and LLM calls without the overhead of cloud platforms.

**Use this SDK when you want to:**
- Demo AI workflows with visual trace outputs
- Debug local LLM/RAG applications
- Prototype observability features before scaling
- Keep all data local with automatic PII redaction

**This SDK does NOT:**
- Send data to external services
- Require API keys or credentials
- Include proprietary eval/judge/fix logic
- Expose internal endpoints or configs

---

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```python
from valiqor import Trace

# Initialize tracer
trace = Trace(app="my-rag-app", env="dev")

# Trace a session
with trace.session(metadata={"user": "demo"}):
    
    # Add retrieval span
    trace.add_span(
        name="llm.call",
        model="gpt-4",
        prompt="What is RAG?",
        response="RAG stands for Retrieval-Augmented Generation...",
        latency_ms=850
    )
    
    # Add tool span
    trace.add_span(
        name="tool.search",
        query="latest AI papers",
        results_count=5
    )

# ✅ Trace saved to /tmp/valiqor/trace_<run_id>_<timestamp>.jsonl
```

### Decorator Usage

```python
@trace.span("data_processing")
def process_data(x):
    return x * 2

with trace.session():
    result = process_data(42)  # Automatically traced
```

---

## CLI Commands

### Run Demo Trace

```bash
valiqor trace run --app demo --scenario s1
```

**Output:**
```
🚀 Running demo trace for demo (scenario: s1)
📝 Valiqor trace started: /tmp/valiqor/trace_run_abc123_20250107_143022.jsonl
✅ Trace completed: 3 spans, 1675ms
   Saved to: /tmp/valiqor/trace_run_abc123_20250107_143022.jsonl
```

### Scan Repository

```bash
valiqor scan . --out context_map.json
```

**Output:**
```
📂 Scanning repository: .
📂 Scanned 47 files (125,483 bytes)
   Found 3 prompt files
   Saved to: context_map.json
```

---

## Examples

### RAG Demo with Full Tracing

```python
from valiqor import Trace

trace = Trace(app="rag-demo", env="dev")

with trace.session(metadata={"query": "Q3 highlights"}):
    
    # 1. Retrieval
    trace.add_span(
        name="rag.retrieval",
        query="Q3 financial highlights",
        retriever="vectordb",
        documents_retrieved=5,
        top_scores=[0.89, 0.85, 0.82],
        latency_ms=234
    )
    
    # 2. Generation
    trace.add_span(
        name="llm.call",
        model="gpt-4",
        input_tokens=850,
        output_tokens=320,
        cost_usd=0.0087,
        latency_ms=2100
    )
    
    # 3. Judge (optional quality check)
    trace.add_span(
        name="judge.evaluate",
        metric="relevance",
        score=0.92,
        reasoning="Response addresses query with specific data"
    )
```

See [examples/simple_rag_demo.py](examples/simple_rag_demo.py) for a runnable example.

---

## Sample Output (JSONL)

```jsonl
{"record_type": "metadata", "run_id": "run_abc123", "app": "rag-demo", "env": "dev"}
{"record_type": "span", "span_id": "span_x1y2", "name": "rag.retrieval", "documents_retrieved": 5, "latency_ms": 234}
{"record_type": "span", "span_id": "span_z3w4", "name": "llm.call", "model": "gpt-4", "cost_usd": 0.0087}
{"record_type": "summary", "run_id": "run_abc123", "duration_ms": 2514, "span_count": 2}
```

---

## Architecture

```
valiqor-trace-sdk/
├── valiqor/
│   ├── __init__.py           # Public API
│   ├── trace.py              # Trace & session()
│   ├── redact.py             # PII/token redaction
│   ├── context_scanner.py    # Repo scanner
│   ├── cli.py                # CLI commands
│   └── sinks/
│       └── file_sink.py      # Local JSONL writer
├── examples/
│   ├── simple_rag_demo.py    # Demo script
│   ├── sample_trace.jsonl    # Example output
│   └── eval_output.json      # Example eval result
├── tests/
│   ├── test_trace_minimal.py
│   └── test_context_scanner.py
└── pyproject.toml
```

---

## Features

| Feature | Status |
|---------|--------|
| ✅ Local JSONL traces | Stable |
| ✅ Automatic PII redaction | Stable |
| ✅ `@trace.span` decorator | Stable |
| ✅ CLI demo runner | Stable |
| ✅ Repository scanner | Stable |
| 🚧 HttpSink (enterprise) | Roadmap |
| 🚧 Judge/Eval integration | Interfaces only |
| 🚧 Cloud dashboard | Private repo |

---

## Privacy & Security

**All data stays local.** This SDK:
- Writes only to `/tmp/valiqor` (or OS temp dir)
- Never makes network calls
- Redacts API keys, passwords, tokens, PII
- Provides safe stubs for sensitive operations

For enterprise deployments, we offer a private `HttpSink` that integrates with our closed platform. Contact us for details.

---

## Development

### Setup

```bash
git clone https://github.com/valiqor/valiqor-trace-sdk
cd valiqor-trace-sdk
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Lint

```bash
ruff check valiqor/
```

---

## MVP Roadmap (Jan 2026)

- [x] Core tracing API
- [x] Local JSONL sink
- [x] CLI tools
- [x] Examples & tests
- [ ] Integration examples (LangChain, LlamaIndex)
- [ ] Visual trace viewer (HTML export)
- [ ] Docker demo container

---

## FAQ

**Q: Does this send data anywhere?**  
A: No. All traces are written locally to `/tmp/valiqor` as JSONL files.

**Q: Can I use this in production?**  
A: This SDK is designed for demos and MVPs. For production, consider our enterprise platform (contact us).

**Q: How do I visualize traces?**  
A: Traces are JSONL files. Use tools like `jq`, parse them in Python, or wait for our HTML viewer (coming soon).

**Q: What about enterprise features?**  
A: Contact us about our private platform with advanced eval, dashboards, and team collaboration.

---

## Contributing

We welcome contributions! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- **Website:** [valiqor.com](https://valiqor.com)
- **Demo:** [demo.valiqor.com](https://demo.valiqor.com)
- **Docs:** [docs.valiqor.com](https://docs.valiqor.com)
- **Enterprise:** [enterprise@valiqor.com](mailto:enterprise@valiqor.com)

---

**Built with ❤️ by the Valiqor Team**  
*Making AI workflows traceable, one span at a time.*
