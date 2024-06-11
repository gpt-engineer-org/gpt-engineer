import yaml
import pytest
from dotenv import load_dotenv

from gpt_engineer.core.ai import AI

from gpt_engineer.applications.feature_cli.file_selection import (
    FileSelection,
    paths_to_tree,
    tree_to_paths,
    paths_to_tree,
    file_selection_to_commented_yaml,
    commented_yaml_to_file_selection,
)

from gpt_engineer.applications.feature_cli.generation_tools import (
    fuzzy_parse_file_selection,
)


def test_tree_conversion():
    original_paths = [
        ".github/ISSUE_TEMPLATE/bug-report.md",
        ".github/ISSUE_TEMPLATE/documentation-clarification.md",
        ".github/ISSUE_TEMPLATE/feature-request.md",
        ".github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/automation.yml",
        ".github/workflows/ci.yaml",
        ".github/workflows/pre-commit.yaml",
        ".github/workflows/release.yaml",
        ".github/CODEOWNERS",
        ".github/CODE_OF_CONDUCT.md",
        ".github/CONTRIBUTING.md",
        ".github/FUNDING.yml",
        "docker/Dockerfile",
        "docker/README.md",
        "docker/entrypoint.sh",
        "docs/examples/open_llms/README.md",
        "docs/examples/open_llms/langchain_interface.py",
    ]

    tree = paths_to_tree(original_paths)
    reconstructed_paths = tree_to_paths(tree)

    assert sorted(original_paths) == sorted(
        reconstructed_paths
    ), "The file paths do not match after conversion!"


def test_tree_conversion_yaml():
    original_paths = [
        ".github/ISSUE_TEMPLATE/bug-report.md",
        ".github/ISSUE_TEMPLATE/documentation-clarification.md",
        ".github/ISSUE_TEMPLATE/feature-request.md",
        ".github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/automation.yml",
        ".github/workflows/ci.yaml",
        ".github/workflows/pre-commit.yaml",
        ".github/workflows/release.yaml",
        ".github/CODEOWNERS",
        ".github/CODE_OF_CONDUCT.md",
        ".github/CONTRIBUTING.md",
        ".github/FUNDING.yml",
        "docker/Dockerfile",
        "docker/README.md",
        "docker/entrypoint.sh",
        "docs/examples/open_llms/README.md",
        "docs/examples/open_llms/langchain_interface.py",
    ]

    tree = paths_to_tree(original_paths)
    yaml_tree = yaml.dump(tree)
    read_tree = yaml.safe_load(yaml_tree)
    reconstructed_paths = tree_to_paths(read_tree)

    assert sorted(original_paths) == sorted(
        reconstructed_paths
    ), "The file paths do not match after conversion!"


def test_file_selection_to_yaml():
    included_files = [
        "docker/Dockerfile",
        "docker/README.md",
        "docker/entrypoint.sh",
    ]

    excluded_files = [
        ".github/ISSUE_TEMPLATE/bug-report.md",
        ".github/ISSUE_TEMPLATE/documentation-clarification.md",
        ".github/ISSUE_TEMPLATE/feature-request.md",
        ".github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/automation.yml",
        ".github/workflows/ci.yaml",
        ".github/workflows/pre-commit.yaml",
        ".github/workflows/release.yaml",
        ".github/CODEOWNERS",
        ".github/CODE_OF_CONDUCT.md",
        ".github/CONTRIBUTING.md",
        ".github/FUNDING.yml",
        "docs/examples/open_llms/README.md",
        "docs/examples/open_llms/langchain_interface.py",
    ]

    commented_yaml = file_selection_to_commented_yaml(
        FileSelection(included_files, excluded_files)
    )

    assert (
        commented_yaml
        == """.github:
  ISSUE_TEMPLATE:
#  - bug-report.md
#  - documentation-clarification.md
#  - feature-request.md
  PULL_REQUEST_TEMPLATE:
#  - PULL_REQUEST_TEMPLATE.md
  workflows:
#  - automation.yml
#  - ci.yaml
#  - pre-commit.yaml
#  - release.yaml
  (./):
#  - CODEOWNERS
#  - CODE_OF_CONDUCT.md
#  - CONTRIBUTING.md
#  - FUNDING.yml
docker:
- Dockerfile
- README.md
- entrypoint.sh
docs:
  examples:
    open_llms:
#    - README.md
#    - langchain_interface.py
"""
    )


def test_yaml_to_file_selection():
    included_files = [
        "docker/Dockerfile",
        "docker/README.md",
        "docker/entrypoint.sh",
    ]

    excluded_files = [
        ".github/ISSUE_TEMPLATE/bug-report.md",
        ".github/ISSUE_TEMPLATE/documentation-clarification.md",
        ".github/ISSUE_TEMPLATE/feature-request.md",
        ".github/PULL_REQUEST_TEMPLATE/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/automation.yml",
        ".github/workflows/ci.yaml",
        ".github/workflows/pre-commit.yaml",
        ".github/workflows/release.yaml",
        ".github/CODEOWNERS",
        ".github/CODE_OF_CONDUCT.md",
        ".github/CONTRIBUTING.md",
        ".github/FUNDING.yml",
        "docs/examples/open_llms/README.md",
        "docs/examples/open_llms/langchain_interface.py",
    ]

    commented_yaml = file_selection_to_commented_yaml(
        FileSelection(included_files, excluded_files)
    )

    file_selection = commented_yaml_to_file_selection(commented_yaml)

    assert sorted(file_selection.included_files) == sorted(included_files)
    assert sorted(file_selection.excluded_files) == sorted(excluded_files)


@pytest.mark.skip(reason="Skipping as test requires AI")
def test_yaml_to_file_selection_fuzzy():

    load_dotenv()

    commented_yaml = """# gpt_engineer:
#   applications:
#     cli:
      - __init__.py
      - cli_agent.py
#       - collect.py
      - file_selector.py
      - learning.py
      - main.py"""

    file_selction = fuzzy_parse_file_selection(AI(), commented_yaml)

    assert file_selction == FileSelection(
        [
            "gpt_engineer/applications/cli/__init__.py",
            "gpt_engineer/applications/cli/cli_agent.py",
            "gpt_engineer/applications/cli/file_selector.py",
            "gpt_engineer/applications/cli/learning.py",
            "gpt_engineer/applications/cli/main.py",
        ],
        [
            "gpt_engineer/applications/cli/collect.py",
        ],
    )
