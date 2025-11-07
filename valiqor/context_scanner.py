"""
Valiqor Trace SDK - Repository Context Scanner

Scans local repositories to generate context maps for AI workflows.
Safe, local-only scanning with no external network calls.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set


# Allowed file extensions for scanning
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".yaml", ".yml", ".md",
    ".txt", ".toml", ".ini", ".cfg"
}

# Directories to prioritize for prompts/templates
PROMPT_DIRECTORIES = {
    "prompts", "templates", "prompt_templates",
    "llm_prompts", "ai_prompts"
}


def scan_repo(
    repo_dir: str,
    out_path: str,
    include_extensions: Optional[Set[str]] = None,
    max_files: int = 1000
) -> Dict:
    """
    Scan a repository and generate a context map.
    
    Args:
        repo_dir: Path to repository root
        out_path: Output path for context map JSON
        include_extensions: Optional custom extensions to include
        max_files: Maximum number of files to scan
        
    Returns:
        Context map dictionary
        
    Example:
        context = scan_repo("./my-app", "context_map.json")
        print(f"Scanned {context['file_count']} files")
    """
    repo_path = Path(repo_dir).resolve()
    
    if not repo_path.exists():
        raise ValueError(f"Repository not found: {repo_dir}")
    
    # Use provided extensions or defaults
    extensions = include_extensions or ALLOWED_EXTENSIONS
    
    # Context map structure
    context_map = {
        "repo_path": str(repo_path),
        "scan_timestamp": None,
        "file_count": 0,
        "total_size_bytes": 0,
        "files": [],
        "prompts": [],
        "structure": {}
    }
    
    # Walk repository
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Skip common ignored directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', 'venv', 'env',
            '.git', '.vscode', '.idea', 'dist', 'build'
        }]
        
        root_path = Path(root)
        rel_root = root_path.relative_to(repo_path)
        
        # Check if this is a prompt directory
        is_prompt_dir = any(p in str(rel_root).lower() for p in PROMPT_DIRECTORIES)
        
        for file in files:
            file_path = root_path / file
            ext = file_path.suffix.lower()
            
            # Check extension
            if ext not in extensions:
                continue
            
            # Check file limit
            if file_count >= max_files:
                break
            
            try:
                size = file_path.stat().st_size
                rel_path = file_path.relative_to(repo_path)
                
                file_info = {
                    "path": str(rel_path).replace("\\", "/"),
                    "size_bytes": size,
                    "extension": ext
                }
                
                context_map["files"].append(file_info)
                
                # Track prompts separately
                if is_prompt_dir or "prompt" in file.lower() or "template" in file.lower():
                    context_map["prompts"].append(file_info)
                
                total_size += size
                file_count += 1
                
            except (PermissionError, OSError):
                # Skip files we can't access
                continue
        
        if file_count >= max_files:
            break
    
    # Update summary
    context_map["file_count"] = file_count
    context_map["total_size_bytes"] = total_size
    context_map["scan_timestamp"] = _get_timestamp()
    
    # Build directory structure
    context_map["structure"] = _build_structure(context_map["files"])
    
    # Write to output file
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(context_map, f, indent=2, ensure_ascii=False)
    
    print(f"📂 Scanned {file_count} files ({total_size:,} bytes)")
    print(f"   Found {len(context_map['prompts'])} prompt files")
    print(f"   Saved to: {out_path}")
    
    return context_map


def _build_structure(files: List[Dict]) -> Dict:
    """Build nested directory structure from file list"""
    structure = {}
    
    for file_info in files:
        parts = Path(file_info["path"]).parts
        current = structure
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add file
        filename = parts[-1]
        current[filename] = file_info["size_bytes"]
    
    return structure


def _get_timestamp() -> str:
    """Get current ISO timestamp"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
