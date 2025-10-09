#!/bin/bash

echo "Fixing pyperclip installation issue for gpt-engineer..."

# Update pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install compatible setuptools version first
echo "Installing compatible setuptools version..."
pip install "setuptools>=45.0,<66.0"

# Install pyperclip 1.8.2 specifically to avoid canonicalize_version error
echo "Installing pyperclip 1.8.2..."
pip install "pyperclip>=1.8.2,<1.9.0"

# Install gpt-engineer in development mode
echo "Installing gpt-engineer..."
pip install -e .

echo "✅ Installation completed successfully!"
echo "You can now run: gpte projects/example"