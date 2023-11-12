import pytest
from gpt_engineer.core.chat_to_files import parse_chat

def test_standard_input():
    chat = """
file1.py
```python
print("Hello, World!")
```

file2.py
```python
def add(a, b):
    return a + b
```
    """
    expected = [
        ("file1.py", 'print("Hello, World!")'),
        ("file2.py", 'def add(a, b):\n    return a + b')
    ]
    assert parse_chat(chat) == expected

def test_no_code_blocks():
    chat = "Just some regular chat without code."
    expected = []
    assert parse_chat(chat) == expected

def test_special_characters_in_filename():
    chat = """
    file[1].py
    ```python
    print("File 1")
    ```

    file`2`.py
    ```python
    print("File 2")
    ```
    """
    expected = [
        ("file[1].py", 'print("File 1")'),
        ("file`2`.py", 'print("File 2")')
    ]
    parsed = parse_chat(chat)
    assert parsed == expected

def test_empty_code_blocks():
    chat = """
    empty.py
    ```
    ```
    """
    expected = [
        ("empty.py", '')
    ]
    assert parse_chat(chat) == expected

def test_mixed_content():
    chat = """
    script.sh
    ```bash
    echo "Hello"
    ```

    script.py
    ```python
    print("World")
    ```
    """
    expected = [
        ("script.sh", 'echo "Hello"'),
        ("script.py", 'print("World")')
    ]
    assert parse_chat(chat) == expected

def test_filename_line_break():
    chat = """
    file1.py
    
    ```python
    print("Hello, World!")
    ```
    """
    expected = [
        ("file1.py", 'print("Hello, World!")')
    ]
    assert parse_chat(chat) == expected

def test_filename_in_backticks():
    chat = """
    `file1.py`
    ```python
    print("Hello, World!")
    ```
    """
    expected = [
        ("file1.py", 'print("Hello, World!")')
    ]
    assert parse_chat(chat) == expected

def test_filename_with_file_tag():
    chat = """
    [FILE: file1.py]
    ```python
    print("Hello, World!")
    ```
    """
    expected = [
        ("file1.py", 'print("Hello, World!")')
    ]
    assert parse_chat(chat) == expected

def test_filename_with_different_extension():
    chat = """
    [id].jsx
    ```javascript
    console.log("Hello, World!")
    ```
    """
    expected = [
        ("[id].jsx", 'console.log("Hello, World!")')
    ]
    assert parse_chat(chat) == expected

# More tests can be added following the similar structure

if __name__ == "__main__":
    pytest.main()
