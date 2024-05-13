import xml.etree.ElementTree as ET

from feature import Feature
from files import Files
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from repository import GitContext

from gpt_engineer.core.ai import AI


def generate_branch_name(ai: AI, feature_description: str) -> str:
    system_prompt = """
    You are a branch name autocomplete / suggestion tool. Based on the users input, please respond with a single suggestion of a branch name and notthing else.

    Example:

    Input: I want to add a login button
    Output: feature/login-button
    """

    ai.llm.callbacks.clear()  # silent

    messages = ai.start(system_prompt, feature_description, step_name="name-branch")

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
    planning_thoughts = root.find("PlanningThoughts").text.strip()

    # Extract tasks
    tasks = [task.text.strip() for task in root.findall(".//Task")]

    # Extract closing remarks
    closing_remarks = root.find("ClosingRemarks").text.strip()

    # Create an instance of the response class
    response = TaskResponse(planning_thoughts, tasks, closing_remarks)

    return response


def build_context_string(feature: Feature, git_context: GitContext):
    return f"""I am working on a feature but breaking it up into small incremental tasks. Your job is to complete the incremental task provided to you - only that task and nothign more.

The purpose of this message is to give you wider context around the feature you are working on and what incremental tasks have already been completed so far.

## Feature - this is the description fo the current feature we are working on.
{feature.get_description()}

## Completed Tasks - these are the lists of tasks you have completed so far on the feature branch.
{feature.get_progress()["done"]}

## Git Context - these are the code changes made so far while implementing this feature. This may include work completed by you on previous tasks as well as changes made independently by me.
### Branch Changes - this is the cumulative diff of all the commits so far on the feature branch.
{git_context.branch_changes}

### Staged Changes - this is the diff of the current staged changes.
{git_context.staged_changes}
"""


def build_files_context_string(feature, git_context, files: Files):
    return f"""{build_context_string(feature, git_context)}

## Current Codebase - this is the as is view of the current code base including any unstaged changes.
{files.to_chat()}
"""


def generate_suggested_tasks(
    ai: AI, feature: Feature, git_context: GitContext, files: Files
) -> str:
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

    input = build_files_context_string(feature, git_context, files)

    # ai.llm.callbacks.clear() # silent

    messages = ai.start(system_prompt, input, step_name="suggest-tasks")

    # ai.llm.callbacks.append(StreamingStdOutCallbackHandler())

    xml = messages[-1].content.strip()

    return parse_task_xml_to_class(xml).tasks
