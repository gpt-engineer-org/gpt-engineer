# Customizing steps

## How Each Step is Made
Each step in the steps module is a function that takes an AI and a set of databases as arguments. The function performs a specific task, such as generating code or clarifying instructions, and returns a list of messages. The messages are then saved to the databases and used in subsequent steps.

Here is an example of a step function:

<br>

```python
def simple_gen(ai: AI, dbs: FileRepositories):
    """Generate code based on the main prompt."""
    system = dbs.preprompts["generate"]
    user = dbs.input["main_prompt"]
    messages = ai.start(system, user)
    dbs.workspace["code.py"] = messages[-1]["content"]
    return messages
```
<br>

This function uses the AI to generate code based on the main prompt. It reads the main prompt from the input database, generates the code, and saves the code to the workspace database.

<br>

## How to Make Your Own Step
To make your own step, you need to define a function that takes an AI and a set of databases as arguments. Inside the function, you can use the AI to generate responses and the databases to store and retrieve data. Here is an example:

<br>

```python
def generate_function(ai: AI, dbs: DBs):
    """Generate a simple Python function."""
    function_name = dbs.input["function_name"]
    function_description = dbs.input["function_description"]
    system = "Please generate a Python function."
    user = f"I want a function named '{function_name}' that {function_description}."
    messages = ai.start(system, user)
    dbs.workspace[f"{function_name}.py"] = messages[-1]["content"]
    return messages
```

<br>

In this custom step, we're asking the AI to generate a Python function based on a function name and a description provided by the user. The function name and description are read from the input database. The generated function is saved to the workspace database with a filename that matches the function name. You would simply need to provide a `function_name` file and `function_description` file with necessary details in the input database (your project folder) to use this step.

<br>

For example, if the user provides the function name "greet" and the description "prints 'Hello, world!'", the AI might generate the following Python function:

```python
def greet():
    print('Hello, world!')
```

<br>

This function would be saved to the workspace database as `greet.py`.
