"""Module for retrieving version information of gpt-engineer."""
import os
import importlib.metadata
from pathlib import Path

def get_version_info():
    """
    Get version information for gpt-engineer.
    Returns a tuple of (version, install_type) where install_type is either 'pip' or 'development'.
    """
    try:
        version = importlib.metadata.version("gpt-engineer")
        install_type = "pip"
    except importlib.metadata.PackageNotFoundError:
        # Check if we're in a development environment (git repo)
        root_dir = Path(__file__).parent.parent.parent
        if (root_dir / ".git").exists():
            version = "development"
            install_type = "development"
        else:
            version = "unknown"
            install_type = "unknown"
    
    return version, install_type