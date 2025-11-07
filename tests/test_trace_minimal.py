"""
Tests for Valiqor Trace SDK - Minimal Tracing
"""

import json
import tempfile
from pathlib import Path

from valiqor import Trace


def test_trace_session_creates_file():
    """Test that a trace session creates a JSONL file"""
    trace = Trace(app="test-app", env="test")
    
    with trace.session(metadata={"test": "value"}):
        trace.add_span(name="test.span", data="hello")
    
    # Check that file was created in temp directory
    temp_dir = Path(tempfile.gettempdir()) / "valiqor"
    assert temp_dir.exists(), "Trace directory not created"
    
    # Find trace files
    trace_files = list(temp_dir.glob("trace_*.jsonl"))
    assert len(trace_files) > 0, "No trace file created"
    
    print(f"✅ Test passed: Trace file created at {trace_files[0]}")


def test_trace_jsonl_structure():
    """Test that JSONL file has correct structure"""
    trace = Trace(app="test-app", env="test")
    
    with trace.session(metadata={"scenario": "test"}):
        trace.add_span(
            name="llm.call",
            model="gpt-4",
            tokens=100
        )
    
    # Read the most recent trace file
    temp_dir = Path(tempfile.gettempdir()) / "valiqor"
    trace_files = sorted(temp_dir.glob("trace_*.jsonl"), key=lambda p: p.stat().st_mtime)
    latest_trace = trace_files[-1]
    
    # Parse JSONL
    records = []
    with open(latest_trace, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    
    # Validate structure
    assert len(records) >= 3, "Should have metadata, span, and summary"
    
    # Check metadata record
    metadata = records[0]
    assert metadata["record_type"] == "metadata"
    assert "run_id" in metadata
    assert metadata["app"] == "test-app"
    
    # Check span record
    span = records[1]
    assert span["record_type"] == "span"
    assert span["name"] == "llm.call"
    assert span["model"] == "gpt-4"
    assert "span_id" in span
    
    # Check summary record
    summary = records[-1]
    assert summary["record_type"] == "summary"
    assert summary["span_count"] == 1
    assert "duration_ms" in summary
    
    print(f"✅ Test passed: JSONL structure valid with {len(records)} records")


def test_trace_span_decorator():
    """Test the @trace.span decorator"""
    trace = Trace(app="test-app", env="test")
    
    @trace.span("test_function")
    def my_function(x):
        return x * 2
    
    with trace.session():
        result = my_function(5)
    
    assert result == 10, "Function should return correct value"
    
    # Check that span was created
    temp_dir = Path(tempfile.gettempdir()) / "valiqor"
    trace_files = sorted(temp_dir.glob("trace_*.jsonl"), key=lambda p: p.stat().st_mtime)
    latest_trace = trace_files[-1]
    
    with open(latest_trace, "r", encoding="utf-8") as f:
        lines = f.readlines()
        span_records = [json.loads(line) for line in lines if "test_function" in line]
    
    assert len(span_records) == 1, "Should have one span from decorator"
    assert span_records[0]["name"] == "test_function"
    assert "duration_ms" in span_records[0]
    
    print("✅ Test passed: Span decorator works correctly")


def test_trace_redaction():
    """Test that sensitive data is redacted"""
    trace = Trace(app="test-app", env="test")
    
    with trace.session():
        trace.add_span(
            name="test.redaction",
            api_key="sk-1234567890abcdefghijk",  # Should be redacted
            password="secretpass123",  # Should be redacted
            safe_data="this is fine"
        )
    
    # Read trace file
    temp_dir = Path(tempfile.gettempdir()) / "valiqor"
    trace_files = sorted(temp_dir.glob("trace_*.jsonl"), key=lambda p: p.stat().st_mtime)
    latest_trace = trace_files[-1]
    
    with open(latest_trace, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check redaction
    assert "sk-1234567890abcdefghijk" not in content, "API key should be redacted"
    assert "secretpass123" not in content, "Password should be redacted"
    assert "[REDACTED]" in content, "Redaction marker should be present"
    assert "this is fine" in content, "Safe data should not be redacted"
    
    print("✅ Test passed: Sensitive data redacted")


if __name__ == "__main__":
    test_trace_session_creates_file()
    test_trace_jsonl_structure()
    test_trace_span_decorator()
    test_trace_redaction()
    print("\n🎉 All tests passed!")
