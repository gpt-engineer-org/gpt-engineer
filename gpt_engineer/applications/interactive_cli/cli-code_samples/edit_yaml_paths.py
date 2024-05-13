from pathlib import Path

import yaml

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Label, TextArea


def create_yaml_file(file_paths):
    """Generates a YAML structure from a list of file paths."""
    root = {}
    for file_path in file_paths:
        parts = Path(file_path).parts
        current = root
        for part in parts:
            current = current.setdefault(part, {})
    return yaml.dump(root, sort_keys=False)


def edit_yaml(yaml_content):
    """Opens a Prompt Toolkit session to edit the YAML content."""
    kb = KeyBindings()

    # @kb.add("c-q")
    # def exit_(event):
    #     "Press Control-Q to exit."
    #     event.app.exit()

    # @kb.add("c-c")
    # def exit_(event):
    #     "Press Control-Q to exit."
    #     event.app.exit()

    # @kb.add("c-s")
    # def save_exit(event):
    #     "Press Control-S to save and exit."
    #     with open("edited_yaml.yaml", "w") as f:
    #         f.write(text_area.text)
    #     print("File saved as 'edited_yaml.yaml'")
    #     event.app.exit()

    # @kb.add("c-t")
    # def comment_uncomment(event):
    #     """Toggle comment on the current line with Ctrl-T."""
    #     tb = text_area.buffer
    #     doc = tb.document
    #     line_text = doc.current_line_before_cursor + doc.current_line_after_cursor
    #     if line_text.strip().startswith("#"):
    #         tb.delete_before_cursor(len(line_text) - len(line_text.lstrip("#")))
    #     else:
    #         tb.insert_text("#", move_cursor=False)

    text_area = TextArea(
        text=yaml_content,
        scrollbar=True,
        multiline=True,
        wrap_lines=False,
        line_numbers=True,
    )

    # Instruction label
    instructions = Label(
        text="Use Ctrl-S to save and exit, Ctrl-Q to quit without saving, Ctrl-T to toggle comment.",
        dont_extend_height=True,
    )

    # Combine text area and instructions label in a vertical layout
    layout = Layout(HSplit([text_area, instructions]))

    app = Application(layout=layout, key_bindings=kb, full_screen=False)
    app.run()


def main(file_paths):
    """Generate a YAML file from file paths and open it for editing."""
    yaml_data = create_yaml_file(file_paths)

    edit_yaml(yaml_data)


# Example usage:
file_paths = ["/path/to/file1.txt", "/path/to/file2.txt", "/path/to/dir/file3.txt"]

main(file_paths)
