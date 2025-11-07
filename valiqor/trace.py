"""
Valiqor Trace SDK - Core Tracing Module

Public API for capturing AI workflow traces locally.
No network calls, no external services - pure local demo tracing.
"""

import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

from .redact import safe
from .sinks.file_sink import FileSink


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class Trace:
    """
    Main tracing client for capturing AI workflow execution.
    
    Example:
        trace = Trace(app="demo-app", env="dev")
        
        with trace.session(metadata={"user": "demo"}):
            trace.add_span(
                name="llm.call",
                model="gpt-4",
                prompt="Hello!",
                response="Hi there!"
            )
    """
    
    def __init__(
        self,
        app: str,
        env: str = "dev",
        sink: Optional[Any] = None
    ):
        """
        Initialize trace client.
        
        Args:
            app: Application name
            env: Environment (dev, staging, prod)
            sink: Optional custom sink. Defaults to FileSink.
        """
        self.app = app
        self.env = env
        self.sink = sink or FileSink()
        
        # Active session state
        self._active_run_id: Optional[str] = None
        self._session_start: Optional[float] = None
        self._spans: list = []
    
    @contextmanager
    def session(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for a trace session.
        
        Args:
            metadata: Optional metadata for this session
            
        Example:
            with trace.session(metadata={"scenario": "demo"}):
                trace.add_span("step1", data="...")
        """
        # Generate run ID
        run_id = generate_id("run")
        self._active_run_id = run_id
        self._session_start = time.time()
        self._spans = []
        
        # Open sink
        session_meta = {
            "app": self.app,
            "env": self.env,
            **(metadata or {})
        }
        filepath = self.sink.open(run_id, session_meta)
        
        print(f"📝 Valiqor trace started: {filepath}")
        
        try:
            yield self
        except Exception as e:
            # Record error
            self.add_span(
                name="session.error",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
        finally:
            # Write summary
            duration_ms = (time.time() - self._session_start) * 1000
            
            summary = {
                "record_type": "summary",
                "run_id": run_id,
                "duration_ms": round(duration_ms, 2),
                "span_count": len(self._spans),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.sink.write(summary, run_id)
            
            # Close sink
            self.sink.close(run_id)
            
            print(f"✅ Trace completed: {len(self._spans)} spans, {duration_ms:.0f}ms")
            print(f"   Saved to: {filepath}")
            
            # Reset state
            self._active_run_id = None
            self._session_start = None
            self._spans = []
    
    def add_span(self, name: str, **fields: Any) -> None:
        """
        Add a span to the active trace session.
        
        Args:
            name: Span name (e.g., "llm.call", "tool.run", "judge.eval")
            **fields: Arbitrary span data
            
        Example:
            trace.add_span(
                name="llm.call",
                model="gpt-4",
                prompt="What is 2+2?",
                response="4",
                latency_ms=245
            )
        """
        if self._active_run_id is None:
            raise RuntimeError("No active session. Use `with trace.session():`")
        
        # Sanitize fields
        safe_fields = safe(fields)
        
        # Create span record
        span = {
            "record_type": "span",
            "span_id": generate_id("span"),
            "run_id": self._active_run_id,
            "name": name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **safe_fields
        }
        
        # Write to sink
        self.sink.write(span, self._active_run_id)
        self._spans.append(span)
    
    def span(self, name: str) -> Callable:
        """
        Decorator for automatic span creation around a function.
        
        Args:
            name: Span name
            
        Example:
            @trace.span("data_processing")
            def process_data(x):
                return x * 2
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                error = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    error = e
                    raise
                finally:
                    duration_ms = (time.time() - start) * 1000
                    
                    self.add_span(
                        name=name,
                        function=func.__name__,
                        duration_ms=round(duration_ms, 2),
                        status="error" if error else "ok",
                        error=str(error) if error else None
                    )
            
            return wrapper
        return decorator
