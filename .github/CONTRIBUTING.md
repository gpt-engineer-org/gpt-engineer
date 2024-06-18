# Contributing to gpt-engineer

The gpt-engineer is a community project and lives from your contributions - they are warmly appreciated. The main contribution avenues are:
- Pull request: implement code and have it reviewed and potentially merged by the maintainers. Implementations of existing feature requests or fixes to bug reports are likely to be merged.
- Bug report: report when something in gpt-engineer doesn't work. Do not report errors in programs written _by_ gpt-engineer.
- Feature request: provide a detailed sketch about something you want to have implemented in gpt-engineer. There is no guarantee that features will be implemented.
- Discussion: raise awareness of a potential improvement. This is often a good starting point before making a detailed feature request.

By participating in this project, you agree to abide by the [code of conduct](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/.github/CODE_OF_CONDUCT.md).

## Merge Policy for Pull Requests
Code that is likely to introduce breaking changes, or significantly change the user experience for users and developers, require [board approval](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/GOVERNANCE.md) to be merged. Smaller code changes can be merged directly.
As a rule, cosmetic pull requests, for example rephrasing the readme or introducing more compact syntax, that do not yield clear practical improvements are not merged. Such pull requests are generally discouraged, both to save time for the maintainers and to establish a lower bar for becoming a contributor.

## Getting Started with Pull Requests to gpt-engineer

To get started with contributing, please follow these steps:

1. Fork the repository and clone it to your local machine.
2. Install any necessary dependencies.
3. Create a new branch for your changes: `git checkout -b my-branch-name`.
4. Make your desired changes or additions.
5. Run the tests to ensure everything is working as expected.
6. Commit your changes: `git commit -m "Descriptive commit message"`.
7. Push to the branch: `git push origin my-branch-name`.
8. Submit a pull request to the `main` branch of the original repository.

## Code Style

Please make sure to follow the established code style guidelines for this project. Consistent code style helps maintain readability and makes it easier for others to contribute to the project.

To enforce this we use [`pre-commit`](https://pre-commit.com/) to run [`black`](https://black.readthedocs.io/en/stable/index.html) and [`ruff`](https://beta.ruff.rs/docs/) on every commit.

To install gpt-engineer as a developer, clone the repository and install the dependencies with:

```bash
$ poetry install
$ poetry shell
```

And then install the `pre-commit` hooks with:

```bash
$ pre-commit install

# output:
pre-commit installed at .git/hooks/pre-commit
```

If you are not familiar with the concept of [git hooks](https://git-scm.com/docs/githooks) and/or [`pre-commit`](https://pre-commit.com/) please read the documentation to understand how they work.

As an introduction of the actual workflow, here is an example of the process you will encounter when you make a commit:

Let's add a file we have modified with some errors, see how the pre-commit hooks run `black` and fails.
`black` is set to automatically fix the issues it finds:

```bash
$ git add chat_to_files.py
$ git commit -m "commit message"
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted chat_to_files.py

All done! ✨ 🍰 ✨
1 file reformatted.
```

You can see that `chat_to_files.py` is both staged and not staged for commit. This is because `black` has formatted it and now it is different from the version you have in your working directory. To fix this you can simply run `git add chat_to_files.py` again and now you can commit your changes.

```bash
$ git status
On branch pre-commit-setup
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
    modified:   chat_to_files.py

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
    modified:   chat_to_files.py
```

Now let's add the file again to include the latest commits and see how `ruff` fails.

```bash
$ git add chat_to_files.py
$ git commit -m "commit message"
black....................................................................Passed
ruff.....................................................................Failed
- hook id: ruff
- exit code: 1
- files were modified by this hook

Found 2 errors (2 fixed, 0 remaining).
```

Same as before, you can see that `chat_to_files.py` is both staged and not staged for commit. This is because `ruff` has formatted it and now it is different from the version you have in your working directory. To fix this you can simply run `git add chat_to_files.py` again and now you can commit your changes.

```bash
$ git add chat_to_files.py
$ git commit -m "commit message"
black....................................................................Passed
ruff.....................................................................Passed
fix end of files.........................................................Passed
[pre-commit-setup f00c0ce] testing
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Now your file has been committed and you can push your changes.

At the beginning this might seem like a tedious process (having to add the file again after `black` and `ruff` have modified it) but it is actually very useful. It allows you to see what changes `black` and `ruff` have made to your files and make sure that they are correct before you commit them.

### Important Note When `pre-commit` Fails in the Build Pipeline
Sometimes `pre-commit` will seemingly run successfully, as follows:

```bash
black................................................(no files to check)Skipped
ruff.................................................(no files to check)Skipped
check toml...........................................(no files to check)Skipped
check yaml...........................................(no files to check)Skipped
detect private key...................................(no files to check)Skipped
fix end of files.....................................(no files to check)Skipped
trim trailing whitespace.............................(no files to check)Skipped
```

However, you may see `pre-commit` fail in the build pipeline upon submitting a PR.  The solution to this is to run `pre-commit run --all-files` to force `pre-commit` to execute these checks, and make any necessary file modifications, to all files.


## Licensing

By contributing to gpt-engineer, you agree that your contributions will be licensed under the [LICENSE](https://github.com/gpt-engineer-org/gpt-engineer/blob/main/LICENSE) file of the project.

Thank you for your interest in contributing to gpt-engineer! We appreciate your support and look forward to your contributions.
