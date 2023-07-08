import os
from dotenv import load_dotenv

def check_env_vars():
    """
    Check if API KEY env variable exist
    If it doesn’t, load from .env file
    """
    if os.getenv("OPENAI_API_KEY") is None:
        load_dotenv()

        # After attempting to load from .env, check again
        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("Cannot run the program without OPENAI_API_KEY environment variable.\nPlease set it in your environment or in a .env file.")

# Call the function when package is imported
check_env_vars()
