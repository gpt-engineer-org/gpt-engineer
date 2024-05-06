from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

def main():
    branch_name_suggestion = 'feat/name'
    print("Great, sounds like a useful feature.")
    branch_name = prompt('Please confirm or edit the feature branch name: ', default=branch_name_suggestion)
    print(f'Creating feature branch: {branch_name}')

if __name__ == '__main__':
    main()
