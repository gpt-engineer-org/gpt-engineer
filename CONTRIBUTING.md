# Install Dev Dependencies

- `pip install -r requirements-dev.txt`

## Using black

Black is an opinionated code formatter for Python. It automatically formats your code according to a specific set of rules, resulting in a standardized and consistent codebase.

To use black:

1. Navigate to your project's root directory in the terminal or command prompt.
2. Run `black` followed by the path or file(s) you want to format.
3. Black will analyze your code and automatically apply the necessary formatting changes.
4. Review the changes made by Black to ensure they align with the pyproject.toml coding standards.

Using `black` ensures that your code is properly formatted, improving readability and maintainability across your codebase.

## Using dotenv

The `dotenv` library provides a convenient way to manage environment variables in Python applications.

To use `dotenv`:

1. Create a `.env` file in the same directory as your script.
2. Define your environment variables in the `.env` file using the `KEY=VALUE` format.
3. In your Python script, import `dotenv` and call `load_dotenv()` to load the environment variables from the `.env` file.
4. Access the environment variables using `os.getenv("KEY")`.

By using `dotenv`, you can keep sensitive information like API keys and database credentials separate from your code, making it easier to manage different development and deployment environments.

## Using pytest

`pytest` is a powerful testing framework for Python that simplifies writing and executing tests. It provides a clean and expressive syntax for creating test cases and offers various features such as fixtures, parameterization, and test discovery.

To use `pytest`:

1. Create test files with names starting with `test_` or ending with `_test.py`.
2. Define your test functions or classes using `assert` statements to check for expected behavior.
3. Run the tests by executing `pytest` in the terminal or command prompt within the test file's directory.

`pytest` will automatically discover and execute the test functions or classes. It provides detailed test results, including the number of tests executed, passed, and failed. Any failed assertions will display informative error messages.

You can leverage `pytest` features such as fixtures to set up and tear down test resources, parametrize tests to run them with different inputs, and organize tests using test classes or modules.

With `pytest`, you can create a comprehensive test suite to ensure the correctness and reliability of your Python code.

## Using ruff

Ruff is a command-line tool that helps you lint and format your Python code. It enforces a consistent code style and helps identify potential issues in your codebase.

To use ruff:

1. Navigate to your project's root directory in the terminal or command prompt.
2. Run `ruff` followed by the path or file(s) you want to analyze.
3. Ruff will perform linting and provide feedback on coding style violations or errors found in your code.

By using `ruff`, you can ensure consistent code quality and adhere to best practices when writing Python code.
