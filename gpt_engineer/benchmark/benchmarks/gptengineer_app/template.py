from gpt_engineer.core.files_dict import FilesDict

index_html = """
<!DOCTYPE html>
<html>
  <head>
    <title>Title (change me!)</title>
    <script src="main.js"></script>
    <link rel="stylesheet" href="main.css" />
  </head>
    <body>
      <!-- Implement the task here -->
    </body>
</html>
"""

main_js = """// Implement the task here"""

main_css = """
body {
    font-family: Arial, sans-serif;
}
"""


def create_template():
    """Creates a basic HTML + CSS + JS template."""
    return FilesDict(
        {
            "index.html": index_html,
            "main.css": main_css,
            "main.js": main_js,
        }
    )
