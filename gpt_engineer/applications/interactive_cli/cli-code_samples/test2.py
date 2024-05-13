from prompt_toolkit.shortcuts import radiolist_dialog


def main():
    print("Use the arrow keys to navigate. Press Enter to select.")
    tasks = [
        ("0", "Generate Whole Feature"),
        ("1", "Task A - Create a view file for account page"),
        ("2", "Task B - Make an API call to retrieve account information"),
        ("3", "Enter a custom task"),
    ]

    result = radiolist_dialog(
        title="Suggested tasks",
        text="Select the task to start with, or enter a custom task:",
        values=tasks,
    ).run()

    if result == "3":
        from prompt_toolkit import prompt

        custom_task = prompt("Enter your custom task description: ")
        print(f"You entered a custom task: {custom_task}")
    else:
        task_description = next((desc for key, desc in tasks if key == result), None)
        print(f"You selected: {task_description}")


if __name__ == "__main__":
    main()
