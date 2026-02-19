"""
Security tests for FileStore class.

This module tests the security fixes for path traversal vulnerabilities
in the FileStore.push() method.
"""
import pytest
import tempfile
from pathlib import Path

from gpt_engineer.core.default.file_store import FileStore
from gpt_engineer.core.files_dict import FilesDict


class TestFileStoreSecurity:
    """Test security features of FileStore."""
    
    def test_normal_file_creation(self):
        """Test that normal files are created successfully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            files = FilesDict({
                "test.py": "print('hello world')",
                "subdir/another.py": "import os"
            })
            
            store.push(files)
            
            # Verify files were created
            assert (Path(temp_dir) / "test.py").exists()
            assert (Path(temp_dir) / "subdir" / "another.py").exists()
    
    def test_path_traversal_blocked_dotdot(self):
        """Test that path traversal with ../ is blocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            files = FilesDict({
                "../../../etc/passwd": "malicious content"
            })
            
            with pytest.raises(ValueError, match="dangerous pattern"):
                store.push(files)
    
    def test_path_traversal_blocked_absolute(self):
        """Test that absolute paths are blocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            files = FilesDict({
                "/etc/passwd": "malicious content"
            })
            
            with pytest.raises(ValueError, match="Absolute paths are not allowed"):
                store.push(files)
    
    def test_path_traversal_blocked_home(self):
        """Test that paths to home directory are blocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            files = FilesDict({
                "~/malicious.sh": "rm -rf /"
            })
            
            with pytest.raises(ValueError, match="dangerous pattern"):
                store.push(files)
    
    def test_path_traversal_blocked_system_dirs(self):
        """Test that system directory paths are blocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            
            dangerous_paths = [
                "/usr/bin/malicious",
                "/var/log/hijack.log", 
                "/root/.ssh/authorized_keys",
                "C:\\Windows\\System32\\evil.exe"
            ]
            
            for dangerous_path in dangerous_paths:
                files = FilesDict({dangerous_path: "malicious content"})
                with pytest.raises(ValueError, match="dangerous pattern"):
                    store.push(files)
    
    def test_file_extension_allowlist(self):
        """Test that file extension allowlist works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Only allow .py and .txt files
            store = FileStore(temp_dir, allowed_extensions={".py", ".txt"})
            
            # This should work
            good_files = FilesDict({
                "script.py": "print('hello')",
                "readme.txt": "This is a readme"
            })
            store.push(good_files)
            
            # This should be blocked
            bad_files = FilesDict({
                "malware.exe": "binary content"
            })
            
            with pytest.raises(ValueError, match="not allowed"):
                store.push(bad_files)
    
    def test_file_extension_allowlist_none_allows_all(self):
        """Test that None allowlist allows all extensions (backward compatibility)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir, allowed_extensions=None)
            
            files = FilesDict({
                "script.py": "print('hello')",
                "data.json": '{"key": "value"}',
                "image.png": "binary data",
                "executable": "no extension"
            })
            
            # Should not raise any errors
            store.push(files)
    
    def test_complex_path_traversal_attempts(self):
        """Test various sophisticated path traversal attempts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            
            tricky_paths = [
                "subdir/../../../etc/passwd",  # Mixed legitimate and traversal
                "normal/../../../../../root/.bashrc",  # Deep traversal
                ".././../etc/hosts",  # Variations of dots
                "subdir\\..\\..\\..\\Windows\\System32\\evil.dll",  # Windows style
            ]
            
            for tricky_path in tricky_paths:
                files = FilesDict({tricky_path: "malicious content"})
                with pytest.raises(ValueError):
                    store.push(files)
    
    def test_path_stays_within_working_dir_even_with_symlinks(self):
        """Test that resolved paths stay within working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            
            # Create a legitimate subdirectory 
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            
            # Try to use relative path that would resolve outside working_dir
            files = FilesDict({
                "subdir/../../etc/passwd": "malicious content"
            })
            
            with pytest.raises(ValueError, match="escape working directory"):
                store.push(files)
    
    def test_empty_and_whitespace_paths(self):
        """Test handling of empty and whitespace-only paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileStore(temp_dir)
            
            problematic_paths = [
                "",  # Empty string
                "   ",  # Whitespace only  
                "\t\n",  # Tabs and newlines
            ]
            
            for bad_path in problematic_paths:
                files = FilesDict({bad_path: "content"})
                with pytest.raises(ValueError):
                    store.push(files)