"""
Tests for Valiqor Trace SDK - Context Scanner
"""

import json
import tempfile
from pathlib import Path

from valiqor.context_scanner import scan_repo


def test_scan_repo_creates_context_map():
    """Test that scan_repo creates a valid context map"""
    
    # Create a temporary test repository
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "main.py").write_text("print('hello')")
        (temp_path / "config.json").write_text('{"key": "value"}')
        (temp_path / "README.md").write_text("# Test Project")
        
        # Create a prompts directory
        prompts_dir = temp_path / "prompts"
        prompts_dir.mkdir()
        (prompts_dir / "system_prompt.txt").write_text("You are a helpful assistant")
        
        # Create subdirectory
        sub_dir = temp_path / "src"
        sub_dir.mkdir()
        (sub_dir / "utils.py").write_text("def helper(): pass")
        
        # Scan repository
        output_file = temp_path / "context_map.json"
        context = scan_repo(str(temp_path), str(output_file))
        
        # Validate context structure
        assert context["file_count"] == 5, f"Should find 5 files, found {context['file_count']}"
        assert len(context["files"]) == 5
        assert len(context["prompts"]) == 1, "Should find 1 prompt file"
        assert context["prompts"][0]["path"] == "prompts/system_prompt.txt"
        
        # Check that output file was created
        assert output_file.exists(), "Output file should be created"
        
        # Validate JSON structure
        with open(output_file, "r", encoding="utf-8") as f:
            saved_context = json.load(f)
        
        assert saved_context["file_count"] == 5
        assert "structure" in saved_context
        assert "scan_timestamp" in saved_context
        
        print(f"✅ Test passed: Context map created with {context['file_count']} files")


def test_scan_repo_skips_ignored_dirs():
    """Test that scanner skips common ignored directories"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create files in main directory
        (temp_path / "main.py").write_text("code")
        
        # Create ignored directories with files
        node_modules = temp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.js").write_text("should be ignored")
        
        venv_dir = temp_path / "venv"
        venv_dir.mkdir()
        (venv_dir / "lib.py").write_text("should be ignored")
        
        # Scan
        output_file = temp_path / "context.json"
        context = scan_repo(str(temp_path), str(output_file))
        
        # Should only find main.py, not ignored files
        assert context["file_count"] == 1, f"Should find only 1 file, found {context['file_count']}"
        assert context["files"][0]["path"] == "main.py"
        
        print("✅ Test passed: Ignored directories skipped")


def test_scan_repo_file_structure():
    """Test that file structure is correctly built"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create nested structure
        (temp_path / "app.py").write_text("app")
        
        src = temp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("main")
        
        utils = src / "utils"
        utils.mkdir()
        (utils / "helper.py").write_text("helper")
        
        # Scan
        output_file = temp_path / "context.json"
        context = scan_repo(str(temp_path), str(output_file))
        
        # Check structure
        structure = context["structure"]
        assert "app.py" in structure
        assert "src" in structure
        assert isinstance(structure["src"], dict)
        assert "main.py" in structure["src"]
        assert "utils" in structure["src"]
        assert "helper.py" in structure["src"]["utils"]
        
        print("✅ Test passed: File structure correctly built")


if __name__ == "__main__":
    test_scan_repo_creates_context_map()
    test_scan_repo_skips_ignored_dirs()
    test_scan_repo_file_structure()
    print("\n🎉 All scanner tests passed!")
