#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -e  # Exit immediately if a command exits with non-zero status

project_dir="/project"

# Run gpt-engineer with all passed arguments
gpt-engineer "$project_dir" "$@"

# Patch permissions of generated files
find "$project_dir" -mindepth 1 -maxdepth 1 ! -path "$project_dir/prompt" \
    -exec chown -R nobody:nogroup {} + \
    -exec chmod -R 777 {} +
