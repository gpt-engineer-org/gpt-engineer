import logging
import tempfile

from pathlib import Path
from typing import Union, Set

from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.linting import Linting

logger = logging.getLogger(__name__)


class FileStore:
    """
    Module for managing file storage in a temporary directory.

    This module provides a class that manages the storage of files in a temporary directory.
    It includes methods for uploading files to the directory and downloading them as a
    collection of files.

    Classes
    -------
    FileStore
        Manages file storage in a temporary directory, allowing for upload and download of files.

    Imports
    -------
    - tempfile: For creating temporary directories.
    - Path: For handling file system paths.
    - Union: For type annotations.
    - FilesDict: For handling collections of files.
    """

    def __init__(self, path: Union[str, Path, None] = None, allowed_extensions: Set[str] = None):
        if path is None:
            path = Path(tempfile.mkdtemp(prefix="gpt-engineer-"))

        self.working_dir = Path(path).resolve()
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.id = self.working_dir.name.split("-")[-1]
        
        # Security: Optional file extension allowlist
        # If None, all extensions are allowed (backward compatibility)
        self.allowed_extensions = allowed_extensions

    def _validate_path(self, file_name: str) -> Path:
        """
        Validates and sanitizes a file path to prevent security vulnerabilities.
        
        Args:
            file_name: The requested file name/path from user input
            
        Returns:
            Path: A validated, resolved path within the working directory
            
        Raises:
            ValueError: If the path is invalid, contains dangerous patterns,
                       or would escape the working directory
        """
        # Remove dangerous characters and normalize the path
        sanitized = str(file_name).strip()
        
        # Block obvious path traversal attempts
        dangerous_patterns = ['../', '..\\', '~/', '/etc/', '/usr/', '/var/', 
                             '/tmp/', '/root/', '/home/', 'C:\\', 'c:\\']
        for pattern in dangerous_patterns:
            if pattern.lower() in sanitized.lower():
                logger.warning(f"Blocked dangerous path pattern: {sanitized}")
                raise ValueError(f"Path contains dangerous pattern: {pattern}")
        
        # Create path relative to working directory and resolve it
        try:
            # Ensure it's treated as relative to working_dir
            if Path(sanitized).is_absolute():
                logger.warning(f"Blocked absolute path: {sanitized}")
                raise ValueError("Absolute paths are not allowed")
                
            candidate_path = (self.working_dir / sanitized).resolve()
            
            # Critical security check: ensure resolved path is within working_dir
            if not str(candidate_path).startswith(str(self.working_dir)):
                logger.warning(f"Path traversal attempt blocked: {sanitized} -> {candidate_path}")
                raise ValueError("Path would escape working directory")
                
        except (OSError, ValueError) as e:
            logger.warning(f"Invalid path rejected: {sanitized} - {e}")
            raise ValueError(f"Invalid file path: {sanitized}")
        
        # Optional: Check file extension allowlist
        if self.allowed_extensions is not None:
            file_suffix = candidate_path.suffix.lower()
            if file_suffix not in self.allowed_extensions:
                logger.warning(f"File extension not allowed: {file_suffix} for {sanitized}")
                raise ValueError(f"File extension '{file_suffix}' is not allowed")
        
        return candidate_path

    def push(self, files: FilesDict):
        """
        Pushes files to the working directory with security validation.
        
        Args:
            files: FilesDict containing file names and contents
            
        Returns:
            self: For method chaining
            
        Raises:
            ValueError: If any file path fails security validation
        """
        successful_writes = []
        
        try:
            for name, content in files.items():
                # Security validation - this will raise ValueError if path is unsafe
                validated_path = self._validate_path(name)
                
                # Ensure parent directories exist
                validated_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file with validated path
                with open(validated_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                successful_writes.append(validated_path)
                logger.debug(f"Successfully wrote file: {name} -> {validated_path}")
                
        except Exception as e:
            # If any file fails, log the error but continue processing others
            # This maintains backward compatibility while improving security
            logger.error(f"Failed to write file '{name}': {e}")
            # Re-raise the exception to alert calling code
            raise
            
        return self

    def linting(self, files: FilesDict) -> FilesDict:
        # lint the code
        linting = Linting()
        return linting.lint_files(files)

    def pull(self) -> FilesDict:
        files = {}
        for path in self.working_dir.glob("**/*"):
            if path.is_file():
                with open(path, "r") as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError:
                        content = "binary file"
                    files[str(path.relative_to(self.working_dir))] = content
        return FilesDict(files)
