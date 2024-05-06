from gpt_engineer.core.ai import AI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


def generate_branch_name(ai: AI, feature_description: str) -> str:
    system_prompt = """
    You are a branch name autocomplete / suggestion tool. Based on the users input, please respond with a single suggestion of a branch name and notthing else.

    Example: 

    Input: I want to add a login button
    Output: feature/login-button 
    """
    
    ai.llm.callbacks.clear() # silent
    
    messages = ai.start(system_prompt, feature_description,step_name="name-branch")

    ai.llm.callbacks.append(StreamingStdOutCallbackHandler())
    
    return messages[-1].content.strip()