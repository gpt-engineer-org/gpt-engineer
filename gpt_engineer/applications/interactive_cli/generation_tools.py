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


def generate_suggested_tasks(ai: AI, input: str) -> str:
    system_prompt = """
You are a software engineer work planning tool. Given a feature description, a list of tasks already completed, and sections of the code
repository we are working on, suggest a list of tasks to be done in order move towards the end goal of completing the feature.

First start by outputting your planning thoughts: an overview of what we are trying to achieve, what we have achieved so far, and what is left to be done. 

Then output the list of tasks to be done. Please try to keep the tasks small, actionable and independantly commitable. 

The output format will be XML as follows: 

<Response>
<PlanningThoughts>
<![CDATA[Include your thoughts here.]]>
</PlanningThoughts>
<Tasks>
<Task>
<![CDATA[Include a task description here]]>
</Task>
<Task>
<![CDATA[Include another task description here.]]>
</Task>
</Tasks>
<ClosingRemarks>
<![CDATA[Any additional closing remarks or thoughts you want to include.]]>
</ClosingRemarks>
</Response>

Respond in XML and nothing else.
"""
    
    ai.llm.callbacks.clear() # silent
    
    messages = ai.start(system_prompt, input,step_name="suggest-tasks")

    ai.llm.callbacks.append(StreamingStdOutCallbackHandler())
    
    return messages[-1].content.strip()