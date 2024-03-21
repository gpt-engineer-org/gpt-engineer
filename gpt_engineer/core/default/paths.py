"""
Module defining file system paths used by the application.

This module contains definitions of file system paths that are used throughout the
application to locate and manage various files and directories, such as logs, memory,
and preprompts.

Constants
---------
META_DATA_REL_PATH : str
    The relative path to the directory where metadata is stored.

MEMORY_REL_PATH : str
    The relative path to the directory where memory-related files are stored.

CODE_GEN_LOG_FILE : str
    The filename for the log file that contains all output from code generation.

DEBUG_LOG_FILE : str
    The filename for the log file that contains debug information.

ENTRYPOINT_FILE : str
    The filename for the entrypoint script that is executed to run the application.

ENTRYPOINT_LOG_FILE : str
    The filename for the log file that contains the chat related to entrypoint generation.

PREPROMPTS_PATH : Path
    The file system path to the directory containing preprompt files.

Functions
---------
memory_path : function
    Constructs the full path to the memory directory based on a given base path.

metadata_path : function
    Constructs the full path to the metadata directory based on a given base path.
"""
import os

from pathlib import Path

META_DATA_REL_PATH = ".gpteng"
MEMORY_REL_PATH = os.path.join(META_DATA_REL_PATH, "memory")
CODE_GEN_LOG_FILE = "all_output.txt"
IMPROVE_LOG_FILE = "improve.txt"
DIFF_LOG_FILE = "diff_errors.txt"
DEBUG_LOG_FILE = "debug_log_file.txt"
ENTRYPOINT_FILE = "run.sh"
ENTRYPOINT_LOG_FILE = "gen_entrypoint_chat.txt"
ENTRYPOINT_FILE = "run.sh"
PREPROMPTS_PATH = Path(__file__).parent.parent.parent / "preprompts"


def memory_path(path):
    """
    Constructs the full path to the memory directory based on a given base path.

    Parameters
    ----------
    path : str
        The base path to append the memory directory to.

    Returns
    -------
    str
        The full path to the memory directory.
    """
    return os.path.join(path, MEMORY_REL_PATH)


def metadata_path(path):
    """
    Constructs the full path to the metadata directory based on a given base path.

    Parameters
    ----------
    path : str
        The base path to append the metadata directory to.

    Returns
    -------
    str
        The full path to the metadata directory.
    """
    return os.path.join(path, META_DATA_REL_PATH)
