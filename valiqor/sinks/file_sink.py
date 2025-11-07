"""
Valiqor Trace SDK - File Sink

Local JSONL writer for trace data. No network calls, no external services.
Writes sanitized traces to OS temp directory with autoflush.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class FileSink:
    """
    Local file sink that writes traces to JSONL format.
    
    Usage:
        sink = FileSink()
        sink.open("run_123", {"app": "demo"})
        sink.write({"span": "llm_call", "data": {...}})
        sink.close("run_123")
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize file sink.
        
        Args:
            base_dir: Base directory for traces. If None, uses OS temp dir.
        """
        if base_dir is None:
            # Use OS-appropriate temp directory
            self.base_dir = Path(tempfile.gettempdir()) / "valiqor"
        else:
            self.base_dir = Path(base_dir)
        
        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Active file handles
        self._handles: Dict[str, Any] = {}
    
    def open(self, run_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Open a new trace file for writing.
        
        Args:
            run_id: Unique identifier for this trace run
            metadata: Optional metadata to write as first line
            
        Returns:
            Path to the created file
        """
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"trace_{run_id}_{timestamp}.jsonl"
        filepath = self.base_dir / filename
        
        # Open file for writing
        handle = open(filepath, "w", encoding="utf-8", buffering=1)  # Line buffered
        self._handles[run_id] = handle
        
        # Write metadata as first line if provided
        if metadata:
            meta_record = {
                "record_type": "metadata",
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **metadata
            }
            handle.write(json.dumps(meta_record, ensure_ascii=False) + "\n")
            handle.flush()
        
        return str(filepath)
    
    def write(self, obj: Dict[str, Any], run_id: Optional[str] = None) -> None:
        """
        Write an object to the trace file.
        
        Args:
            obj: Dictionary to write
            run_id: Run ID to write to. If None, uses the first opened run.
        """
        # Get handle
        if run_id is None:
            if not self._handles:
                raise ValueError("No active trace runs. Call open() first.")
            run_id = list(self._handles.keys())[0]
        
        handle = self._handles.get(run_id)
        if handle is None:
            raise ValueError(f"No active trace for run_id: {run_id}")
        
        # Add timestamp if not present
        if "timestamp" not in obj:
            obj["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Write line
        handle.write(json.dumps(obj, ensure_ascii=False) + "\n")
        handle.flush()  # Autoflush for immediate visibility
    
    def close(self, run_id: Optional[str] = None) -> None:
        """
        Close a trace file.
        
        Args:
            run_id: Run ID to close. If None, closes all open runs.
        """
        if run_id is None:
            # Close all
            for handle in self._handles.values():
                handle.close()
            self._handles.clear()
        else:
            handle = self._handles.pop(run_id, None)
            if handle:
                handle.close()
    
    def __del__(self):
        """Cleanup: close any open handles"""
        self.close()
    
    def get_trace_path(self, run_id: str) -> Optional[str]:
        """Get the file path for a specific run ID"""
        handle = self._handles.get(run_id)
        if handle:
            return handle.name
        return None
