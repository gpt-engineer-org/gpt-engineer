=====
Usage
=====

**Step 1: Settting an OPENAI_API Key**
- Before getting started, we need to set an OPENAI_API Key.

**For Windows:**
- Set your ‘OPENAI_API_KEY’ Environment Variable through the Control Panel:

1) Open System properties and select Advanced system settings
2) Select Environment Variables
3)  Select 'New' from the User variables section(top). Add your name/key value pair, replacing <yourkey> with your API key.
  ```
  Variable name: OPENAI_API_KEY
  Variable value: <yourkey>
  ```
 **For MAC OS/Linux:**
- Set your ‘OPENAI_API_KEY’ Environment Variable using zsh:
1) Run the following command in your terminal, replacing yourkey with your API key.
```
echo "export OPENAI_API_KEY='yourkey'" >> ~/.zshrc
```
2) Update the shell with the new variable:
```
source ~/.zshrc
```
3) Confirm that you have set your environment variable using the following command:
```
echo $OPENAI_API_KEY
```
**Step 2: Installation**
- Before you can begin using GPT-Engineer, you need to ensure that it is installed on your system. You can install it using the following command:
```
pip install gpt-engineer
```
**Step 3: Initial Code Generation**
- To start the code generation process, you provide a prompt to GPT-Engineer. This prompt outlines the task you want the generated code to accomplish. For example:
```
gpt-engineer --prompt "Generate a Python function that calculates the factorial of a number."
```
- GPT-Engineer will then generate a preliminary code snippet based on the provided prompt.

**Step 4: Inspecting and Refining the Initial Code**
- After generating the initial code, it's time to inspect and refine it according to your preferences. You might need to make adjustments to the generated code to better suit your requirements or coding style. You can do this manually by editing the generated code.

**Step 5: User Feedback**
- The feedback step is a crucial part. It involves providing feedback to GPT-Engineer on the generated code. This feedback helps the model understand your preferences and allows it to improve subsequent code generations.
```
gpt-engineer --steps feedback
```
- When prompted, you can provide feedback on the generated code. For example, you might point out specific improvements, request changes, or explain why certain parts of the code need adjustment.


- Create an empty folder. If inside the repo, you can run:
  - `cp -r projects/example/ projects/my-new-project`
- Fill in the `prompt` file in your new folder
- `gpt-engineer projects/my-new-project`
  - (Note, `gpt-engineer --help` lets you see all available options. For example `--steps use_feedback` lets you improve/fix code in a project)

By running gpt-engineer you agree to our [terms](https://github.com/AntonOsika/gpt-engineer/blob/main/TERMS_OF_USE.md).

Results
=======
- Check the generated files in `projects/my-new-project/workspace`


To **run in the browser** you can simply:

.. image:: https://github.com/codespaces/badge.svg
   :target: https://github.com/AntonOsika/gpt-engineer/codespaces
