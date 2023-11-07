import os
META_DATA_REL_PATH = ".gpteng"
MEMORY_REL_PATH = os.path.join(META_DATA_REL_PATH, "memory")

def memory_path(path):
    return os.path.join(path, MEMORY_REL_PATH)


