import xml.etree.ElementTree as ET
import json

from gpt_engineer.applications.feature_cli.domain import FileSelection
from gpt_engineer.core.ai import AI

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


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


def build_git_context_string(git_context):
    return f"""## Git Context - these are the code changes made so far while implementing this feature. This may include work completed by you on previous tasks as well as changes made independently by me.
### Branch Changes - this is the cumulative diff of all the commits so far on the feature branch.
{git_context.branch_changes}

### Staged Changes - this is the diff of the current staged changes.
{git_context.staged_changes}"""


def build_feature_context_string(feature, git_context):
    feature_string = f"""## Feature - this is the description fo the current feature we are working on.
{feature.get_description()}

## Completed Tasks - these are the lists of tasks you have completed so far on the feature branch.
{feature.get_progress()["done"]}
"""

    if git_context:
        return f"""{feature_string}

{build_git_context_string(git_context)}
"""

    return feature_string


def build_files_context_string(feature, git_context, files):
    return f"""{build_feature_context_string(feature, git_context)}

## Current Codebase - this is the as is view of the current code base including any unstaged changes.
{files.to_chat()}
"""


def generate_suggested_tasks(ai: AI, feature, git_context, files) -> str:
    system_prompt = """
You are a software engineer work planning tool. Given a feature description, a list of tasks already completed, and sections of the code
repository we are working on, suggest a list of implementation tasks to be done in order to move towards the end goal of completing the feature.

An implementation task consists of actually writing some code - and doesnt include review or research tasks, or any other activity other tha writing code.

First start by outputting your planning thoughts: an overview of what we are trying to achieve, what we have achieved so far, and what implementation tasks are left to be done.

Then output the list of between 0 and 3 implementation tasks to be done which get us closer to our goal. Please try to keep the tasks small, actionable and independantly commitable.

We only need to move towards our goal with these tasks, we dont have to complete the feature in these 3 steps.

The output format will be XML as follows:

<Response>
<PlanningThoughts>
<![CDATA[Include your thoughts here.]]>
</PlanningThoughts>
<Tasks>
<Task number="1">
<![CDATA[Include a task description here]]>
</Task>
<Task number="2">
<![CDATA[Include another task description here.]]>
</Task>
<Task number="3">
<![CDATA[Include another task description here.]]>
</Task>
</Tasks>
<ClosingRemarks>
<![CDATA[Any additional closing remarks or thoughts you want to include.]]>
</ClosingRemarks>
</Response>

Respond in XML and nothing else.

You may send as as little as 0 tasks and as many as 3. If you believe the feature is complete, send 0 tasks.
"""

    input = build_files_context_string(feature, git_context, files)

    ai.llm.callbacks.clear()  # silent

    messages = ai.start(system_prompt, input, step_name="suggest-tasks")

    ai.llm.callbacks.append(StreamingStdOutCallbackHandler())

    raw_response = messages[-1].content.strip()

    xml_start = raw_response.find("<")
    xml_end = raw_response.rfind(">") + 1
    xml = raw_response[xml_start:xml_end]

    try:
        resp = parse_task_xml_to_class(xml)
    except:
        print(raw_response)

    return resp


def fuzzy_parse_file_selection(ai: AI, yaml_string: str) -> FileSelection:
    # todo: load prompt from ptompts/fuzzy_file_parser

    system_prompt = """## Explanation
You are a fuzzy yaml parser, who correctly parses yaml even if it is not strictly valid.

A user has been given a yaml representation of a file structure, represented like so:

.github:
  ISSUE_TEMPLATE:
    - bug-report.md
    - documentation-clarification.md
    - feature-request.md
  PULL_REQUEST_TEMPLATE:
    - PULL_REQUEST_TEMPLATE.md
  workflows:
    - automation.yml
    - ci.yaml
    - pre-commit.yaml
    - release.yaml
  (./):
  - CODEOWNERS
  - CODE_OF_CONDUCT.md
  - CONTRIBUTING.md
  - FUNDING.yml

Folders are represented as keys in a dictionary, files are items in a list. Any files listed under the (./) key can be assumed to be files of the folder above that.

The given example maps to these file paths:

".github/ISSUE_TEMPLATE/bug-report.md",
".github/ISSUE_TEMPLATE/documentation-clarification.md",
".github/ISSUE_TEMPLATE/feature-request.md",
".github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md",
".github/workflows/automation.yml",
".github/workflows/ci.yaml",
".github/workflows/pre-commit.yaml",
".github/workflows/release.yaml",
".github/CODEOWNERS",
".github/CODE_OF_CONDUCT.md",
".github/CONTRIBUTING.md",
".github/FUNDING.yml",

An example of the yaml file after commenting might be something like this:


.github:
  # ISSUE_TEMPLATE:
  #   - bug-report.md
  #   - documentation-clarification.md
  #   - feature-request.md
  # PULL_REQUEST_TEMPLATE:
  #   - PULL_REQUEST_TEMPLATE.md
  workflows:
    - automation.yml
    - ci.yaml
    - pre-commit.yaml
    - release.yaml
  # (./):
  # - CODEOWNERS
  - CODE_OF_CONDUCT.md
  - CONTRIBUTING.md
  # - FUNDING.yml


This would convert into:

{
    "included_files": [
        ".github/workflows/automation.yml",
        ".github/workflows/ci.yaml",
        ".github/workflows/pre-commit.yaml",
        ".github/workflows/release.yaml",
        ".github/CODE_OF_CONDUCT.md",
        ".github/CONTRIBUTING.md"
    ],
    "excluded_files": [ 
        ".github/ISSUE_TEMPLATE/bug-report.md",
        ".github/ISSUE_TEMPLATE/documentation-clarification.md",
        ".github/ISSUE_TEMPLATE/feature-request.md",
        ".github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS",
        ".github/FUNDING.yml"
    ]
}


Although the commmented content wasnt strictly correct yaml, their intentions were clear. They wanted to retain the files in the workflow folder aswell as the code of conduct and contributing guides

Based on commented yaml inputs such as this, your job is to output JSON, indicating which files have been included and which have been excluded.

Excluded files are always commented out with a # like in the above example.

The json you should return will be like this:

{
    "included_files": [
        "folder1/file5",
        "folder1/folder3/file3",
        "file7"
    ],
    "excluded_files": [ 
        "folder1/folder2/file1",
        "folder1/folder2/file2",
        "folder1/folder3/file4",
        "folder1/file5",
    ]
}

Files can only be included or excluded, not both. If you are confused about the state of a file make your best guess - and if you really arent sure then mark it as included.

Respond in JSON and nothing else.

## Examples

Example 1:

Input:

.github:
  ISSUE_TEMPLATE:
    - bug_report.md 
    - feature_request.md
  PULL_REQUEST_TEMPLATE:
    - pull_request_template.md
  # workflows:
  #   - ci.yml
  #   - release.yml

Output:

{
    "included_files": [
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        ".github/PULL_REQUEST_TEMPLATE/pull_request_template.md"
    ],
    "excluded_files": [ 
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml"
    ]
}

Example 2:

Input:

source:
  # controllers:
  #   - MainController.cs 
  #   - AuthController.cs
  models:
    - User.cs
    - Post.cs
  views:
    Home:
      - Index.cshtml
      # - About.cshtml
    Auth:  
      - Login.cshtml
      - Register.cshtml
  (./):
    - Dockerfile

Output:

{
    "included_files": [
        "source/models/User.cs",
        "source/models/Post.cs", 
        "source/views/Home/Index.cshtml",
        "source/views/Auth/Login.cshtml",
        "source/views/Auth/Register.cshtml"
        "source/Dockerfile",
    ],
    "excluded_files": [
        "source/controllers/MainController.cs",
        "source/controllers/AuthController.cs", 
        "source/views/Home/About.cshtml"
    ]
}

Example 3:

Input:

src:
  main:
    java:
      com:
        example:
          # controllers:
          #   - UserController.java
          #   - PostController.java
          models:
            - User.java 
            - Post.java
          # repositories:
          #   - UserRepository.java
          #   - PostRepository.java
          services:
            - UserService.java
            - PostService.java
    resources:
      - application.properties
  test:
    java:
      com:
        example:
          controllers:
            - UserControllerTest.java
            - PostControllerTest.java
  (./):
    - pom.xml
    - Dockerfile

Output:

{
    "included_files": [
        "src/main/java/com/example/models/User.java",
        "src/main/java/com/example/models/Post.java",
        "src/main/java/com/example/services/UserService.java", 
        "src/main/java/com/example/services/PostService.java",
        "src/main/resources/application.properties",
        "src/test/java/com/example/controllers/UserControllerTest.java",
        "src/test/java/com/example/controllers/PostControllerTest.java",
        "pom.xml",
        "Dockerfile"
    ],
    "excluded_files": [
        "src/main/java/com/example/controllers/UserController.java",
        "src/main/java/com/example/controllers/PostController.java",
        "src/main/java/com/example/repositories/UserRepository.java",
        "src/main/java/com/example/repositories/PostRepository.java" 
    ]
}

Example 4:

Input: 


app:
  # controllers:
  #   - application_controller.rb
  #   - users_controller.rb 
  models:
    - user.rb
    - post.rb
  views:
    layouts:
      - application.html.erb
    users:
      - index.html.erb
      - show.html.erb
    posts:
      - index.html.erb
      # - show.html.erb
  (./):  
    - Gemfile
    - config
config:
  environments:
    - development.rb
    - test.rb 
    # - production.rb
  initializers:
    - application_controller_renderer.rb
  locales:
    - en.yml 
  # routes.rb
db:
  migrate:
    - 20211025120523_create_users.rb
    - 20211025120530_create_posts.rb
test:
  fixtures:
    - users.yml  
    - posts.yml
  # controllers:
  #   - users_controller_test.rb
  #   - posts_controller_test.rb 
  models:
    - user_test.rb
    - post_test.rb


Output:

{
    "included_files": [
        "app/models/user.rb",
        "app/models/post.rb",
        "app/views/layouts/application.html.erb",
        "app/views/users/index.html.erb", 
        "app/views/users/show.html.erb",
        "app/views/posts/index.html.erb",
        "app/Gemfile",
        "config/environments/development.rb",
        "config/environments/test.rb",
        "config/initializers/application_controller_renderer.rb",
        "config/locales/en.yml",
        "db/migrate/20211025120523_create_users.rb",
        "db/migrate/20211025120530_create_posts.rb",
        "test/fixtures/users.yml",
        "test/fixtures/posts.yml",
        "test/models/user_test.rb",
        "test/models/post_test.rb"
    ],
    "excluded_files": [
        "app/controllers/application_controller.rb",
        "app/controllers/users_controller.rb",
        "app/views/posts/show.html.erb",
        "config/environments/production.rb",
        "config/routes.rb",
        "test/controllers/users_controller_test.rb",
        "test/controllers/posts_controller_test.rb"
    ]
}

## IMPORTANT
Remember any line that is commented is an excluded file. Any line that is NOT commented - is an included file.
"""

    # ai.llm.callbacks.clear()  # silent

    messages = ai.start(system_prompt, yaml_string, step_name="fuzzy-parse-yaml")

    # ai.llm.callbacks.append(StreamingStdOutCallbackHandler())

    json_string = messages[-1].content.strip()

    # strip anything before first { and after last }
    json_string = json_string[json_string.find("{") : json_string.rfind("}") + 1]

    data = json.loads(json_string)

    return FileSelection(data["included_files"], data["excluded_files"])
