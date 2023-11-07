import os
META_DATA_REL_PATH = ".gpteng"
MEMORY_REL_PATH = os.path.join(META_DATA_REL_PATH, "memory")
ENTRYPOINT_FILE = "run.sh"
CODE_GEN_LOG_FILE = "all_output.txt"

def memory_path(path):
    return os.path.join(path, MEMORY_REL_PATH)


