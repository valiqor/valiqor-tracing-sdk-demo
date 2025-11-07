# Quick Start Guide - Valiqor Trace SDK

## 1-Minute Setup ⚡

### Install
```bash
cd valiqor-trace-sdk
pip install -e .
```

### Hello World
```python
from valiqor import Trace

trace = Trace(app="hello", env="dev")

with trace.session():
    trace.add_span(name="llm.call", model="gpt-4", response="Hello!")
```

**Output:** Trace saved to `/tmp/valiqor/trace_*.jsonl`

---

## 5-Minute Tutorial 🚀

### 1. Basic Tracing
```python
from valiqor import Trace

# Initialize
trace = Trace(app="my-app", env="dev")

# Create a session
with trace.session(metadata={"user": "demo"}):
    
    # Add spans manually
    trace.add_span(
        name="llm.call",
        model="gpt-4",
        tokens=100,
        latency_ms=850
    )
    
    trace.add_span(
        name="tool.run",
        tool_name="calculator",
        result=42
    )

# ✅ Trace automatically saved
```

### 2. Decorator Pattern
```python
from valiqor import Trace

trace = Trace(app="my-app", env="dev")

@trace.span("data_processing")
def process_data(x):
    return x * 2

with trace.session():
    result = process_data(21)  # Automatically traced!
```

### 3. RAG Pipeline
```python
from valiqor import Trace

trace = Trace(app="rag-app", env="dev")

with trace.session(metadata={"query": "What is AI?"}):
    
    # Retrieval
    trace.add_span(
        name="rag.retrieval",
        query="What is AI?",
        documents_retrieved=5,
        top_scores=[0.89, 0.85, 0.82]
    )
    
    # Generation
    trace.add_span(
        name="llm.call",
        model="gpt-4",
        input_tokens=850,
        output_tokens=320,
        cost_usd=0.0087
    )
```

### 4. CLI Usage
```bash
# Run demo trace
valiqor trace run --app demo --scenario s1

# Scan repository
valiqor scan . --out context_map.json
```

---

## Where Are My Traces? 📁

### Linux/Mac
```bash
ls /tmp/valiqor/*.jsonl
cat /tmp/valiqor/trace_*.jsonl | jq
```

### Windows
```powershell
dir $env:TEMP\valiqor\*.jsonl
type $env:TEMP\valiqor\trace_*.jsonl
```

---

## What's in a Trace? 📊

### JSONL Format
```jsonl
{"record_type": "metadata", "run_id": "run_abc", "app": "demo"}
{"record_type": "span", "name": "llm.call", "model": "gpt-4", "tokens": 100}
{"record_type": "summary", "run_id": "run_abc", "span_count": 1}
```

### Parse in Python
```python
import json

with open("/tmp/valiqor/trace_*.jsonl") as f:
    for line in f:
        record = json.loads(line)
        print(record["record_type"], record.get("name", ""))
```

---

## Safety Features 🔒

### Automatic Redaction
```python
trace.add_span(
    name="api.call",
    api_key="sk-1234567890",  # → [REDACTED]
    password="secret123",     # → [REDACTED]
    safe_data="this is fine"  # → "this is fine"
)
```

### Patterns Redacted
- API keys (`sk-*`, `api_key=...`)
- Passwords (`password=...`)
- Tokens (`token=...`, `bearer ...`)
- Emails
- SSNs
- Credit card numbers

---

## Testing ✅

### Run Tests
```bash
pytest tests/ -v
```

### Run Examples
```bash
python examples/simple_rag_demo.py
```

---

## Common Patterns 📚

### 1. Multi-Step Workflow
```python
with trace.session():
    trace.add_span(name="step1", data="...")
    trace.add_span(name="step2", data="...")
    trace.add_span(name="step3", data="...")
```

### 2. Error Handling
```python
with trace.session():
    try:
        risky_operation()
        trace.add_span(name="op", status="ok")
    except Exception as e:
        trace.add_span(name="op", status="error", error=str(e))
        raise
```

### 3. Nested Operations
```python
with trace.session():
    trace.add_span(name="parent", data="...")
    
    @trace.span("child_op")
    def child():
        return "result"
    
    child()
```

---

## Next Steps 📖

1. **Read the docs:** [README.md](README.md)
2. **Explore examples:** `examples/`
3. **Run tests:** `pytest tests/`
4. **Star on GitHub:** ⭐ [github.com/valiqor/trace-sdk](https://github.com/valiqor/trace-sdk)

---

## Need Help? 💬

- 📧 Email: support@valiqor.com
- 🐛 Issues: [GitHub Issues](https://github.com/valiqor/trace-sdk/issues)
- 📚 Docs: [docs.valiqor.com](https://docs.valiqor.com)

---

**Happy Tracing! 🎉**
