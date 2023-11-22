# a) Install dependencies
pip install backoff openai langchain tiktoken

# b) Run all necessary parts of the codebase
python ai.py &
python base_agent.py &
python base_execution_env.py &
python base_repository.py &
python base_version_manager.py &
python chat_to_files.py &
python code.py &
python default/__init__.py &
python default/constants.py &
python default/git_version_manager.py &
python default/lean_agent.py &
python default/on_disk_execution_env.py &
python default/on_disk_repository.py &
python default/paths.py &
python default/steps.py &
python preprompt_holder.py &
python token_usage.py &
