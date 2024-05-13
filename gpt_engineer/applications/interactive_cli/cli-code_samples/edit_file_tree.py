from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Window
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea


def generate_file_tree(files):
    """
    Generates a file tree from a list of file paths.
    """
    tree = {}
    for file in files:
        parts = file.split("/")
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
    return tree


def generate_tree_string(node, prefix=""):
    """
    Recursively generates a string representation of the file tree.
    """
    lines = []
    items = list(node.items())
    for i, (key, subnode) in enumerate(items):
        connector = "└─" if i == len(items) - 1 else "├─"
        if subnode is not None:  # Check if it's a directory or a commented directory
            lines.append(f"{prefix}{connector} {key}/")
            if subnode:  # Only append sub-tree if it's not commented out
                extension = "    " if i == len(items) - 1 else "│   "
                lines.extend(generate_tree_string(subnode, prefix + extension))
        else:  # it's a file or commented file
            lines.append(f"{prefix}{connector} {key}")
    return lines


def get_editable_tree(files):
    tree = generate_file_tree(files)
    tree_lines = generate_tree_string(tree)
    return "\n".join(tree_lines)


def interactive_edit_files(files):
    PromptSession()

    # Generate editable file tree
    editable_tree = get_editable_tree(files)

    # Text area for file tree
    text_area = TextArea(
        text=editable_tree, scrollbar=True, multiline=True, wrap_lines=False
    )

    # Ensure the text area starts in insert mode
    # text_area.buffer.cursor_position += len(text_area.text)
    text_area.buffer.insert_mode = False

    # Instructions wrapped in a Window
    instructions = Window(
        content=FormattedTextControl(
            text="Please comment out unneeded files to reduce context overhead.\n"
            'You can comment out lines by adding "#" at the beginning of the line.\n'
            "Press Ctrl-S to save and exit."
        ),
        height=3,  # Adjust height as necessary
        style="class:instruction",
    )

    # Container that holds both the instructions and the text area
    instruction_container = HSplit([instructions, text_area])

    # Create a layout out of the widget above
    layout = Layout(instruction_container)

    # Add key bindings for custom actions like save
    bindings = KeyBindings()

    @bindings.add("c-s")
    def _(event):
        # Saving functionality or further processing can be implemented here
        print("Saving and processing your tree...")
        event.app.exit()

    app = Application(layout=layout, key_bindings=bindings, full_screen=True)
    app.run()


# Example usage
tracked_files = [
    "project/src/main/java/com/example/MyApp.java",
    "project/src/main/resources/config.properties",
    "project/src/test/java/com/example/MyAppTest.java",
    "project/src/test/resources/testdata.txt",
    "project/lib/external-library.jar",
    "project/README.md",
]
interactive_edit_files(tracked_files)
