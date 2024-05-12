from gpt_engineer.core.ai import AI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import xml.etree.ElementTree as ET



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


class TaskResponse:
    def __init__(self, planning_thoughts, tasks, closing_remarks):
        self.planning_thoughts = planning_thoughts
        self.tasks = tasks
        self.closing_remarks = closing_remarks

    def __str__(self):
        return f"Planning Thoughts: {self.planning_thoughts}\nTasks: {'; '.join(self.tasks)}\nClosing Remarks: {self.closing_remarks}"


def parse_task_xml_to_class(xml_data):
    # Parse the XML data
    root = ET.fromstring(xml_data)
    
    # Extract the planning thoughts
    planning_thoughts = root.find('PlanningThoughts').text.strip()

    # Extract tasks
    tasks = [task.text.strip() for task in root.findall('.//Task')]
    
    # Extract closing remarks
    closing_remarks = root.find('ClosingRemarks').text.strip()
    
    # Create an instance of the response class
    response = TaskResponse(planning_thoughts, tasks, closing_remarks)
    
    return response


def generate_suggested_tasks(ai: AI, input: str) -> str:
    system_prompt = """
You are a software engineer work planning tool. Given a feature description, a list of tasks already completed, and sections of the code
repository we are working on, suggest a list of tasks to be done in order to move towards the end goal of completing the feature.

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
    
    # ai.llm.callbacks.clear() # silent
    
    messages = ai.start(system_prompt, input,step_name="suggest-tasks")

    # ai.llm.callbacks.append(StreamingStdOutCallbackHandler())
    
    xml = messages[-1].content.strip()

    return parse_task_xml_to_class(xml).tasks

