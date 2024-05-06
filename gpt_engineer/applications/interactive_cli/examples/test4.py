from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

def main():
    print("Diff generated. Please Review, and stage the changes you want to keep.")

    # Define the options and create a completer with those options
    options = {'r': 'Retry', 's': 'Stage changes and continue', 'c': 'Commit changes and continue', 'u': 'Undo'}
    completer = WordCompleter(['r', 's', 'c', 'u'], ignore_case=True)
    session = PromptSession()

    # Using prompt to get user input
    result = session.prompt(
        "Please select your action \n r: Retry \n s: Stage \n c: Commit \n u: Undo \n\n",
        completer=completer
    ).lower()

    # Handle the user's choice
    if result == 'r':
        print("You have chosen to retry the diff generation.")
        # Add logic to retry generating the diff
    elif result == 's':
        print("You have chosen to stage the changes.")
        # Add logic to stage changes
    elif result == 'c':
        print("You have chosen to commit the changes.")
        # Add logic to commit changes
    elif result == 'u':
        print("Undo the last operation.")
        # Add logic to undo the last operation
    else:
        print("Invalid option selected, please run the program again.")

if __name__ == '__main__':
    main()
