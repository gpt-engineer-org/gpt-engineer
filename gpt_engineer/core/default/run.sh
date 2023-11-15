# Install dependencies
pip install -r requirements.txt

# Run the necessary parts of the codebase
python git_version_manager.py &
python lean_agent.py &
python on_disk_execution_env.py &
python on_disk_repository.py &
python paths.py &
python steps.py &
wait
