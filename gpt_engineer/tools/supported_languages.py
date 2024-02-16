"""
This module defines the supported programming languages for document chunking.

Variables:
    SUPPORTED_LANGUAGES (list): A list of dictionaries defining supported languages.
"""

SUPPORTED_LANGUAGES = [
    {"name": "Python", "extensions": [".py"], "tree_sitter_name": "python"},
    {
        "name": "JavaScript",
        "extensions": [".js", ".mjs"],
        "tree_sitter_name": "javascript",
    },
    {"name": "HTML", "extensions": [".html", ".htm"], "tree_sitter_name": "html"},
    {"name": "CSS", "extensions": [".css"], "tree_sitter_name": "css"},
    {"name": "Java", "extensions": [".java"], "tree_sitter_name": "java"},
    {"name": "C#", "extensions": [".cs"], "tree_sitter_name": "c_sharp"},
    {
        "name": "TypeScript",
        "extensions": [".ts", ".tsx"],
        "tree_sitter_name": "typescript",
    },
    {"name": "Ruby", "extensions": [".rb", ".erb"], "tree_sitter_name": "ruby"},
    {
        "name": "PHP",
        "extensions": [
            ".php",
            ".phtml",
            ".php3",
            ".php4",
            ".php5",
            ".php7",
            ".phps",
            ".php-s",
            ".pht",
            ".phar",
        ],
        "tree_sitter_name": "php",
    },
    {"name": "Go", "extensions": [".go"], "tree_sitter_name": "go"},
    {"name": "Kotlin", "extensions": [".kt", ".kts"], "tree_sitter_name": "kotlin"},
    {"name": "Rust", "extensions": [".rs"], "tree_sitter_name": "rust"},
    {
        "name": "C++",
        "extensions": [".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
        "tree_sitter_name": "cpp",
    },
    {"name": "C", "extensions": [".c", ".h"], "tree_sitter_name": "c"}
    # ---- the following are not supported by the current code chunker implementation ----
    # {
    #     "name": "Swift",
    #     "extensions": [".swift"],
    #     "tree_sitter_name": "swift"
    # },
]
