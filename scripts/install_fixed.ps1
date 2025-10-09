Write-Host "Fixing pyperclip installation issue for gpt-engineer..." -ForegroundColor Green

# Update pip to latest version
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install compatible setuptools version first
Write-Host "Installing compatible setuptools version..."
python -m pip install "setuptools>=45.0,<66.0"

# Install pyperclip 1.8.2 specifically to avoid canonicalize_version error
Write-Host "Installing pyperclip 1.8.2..."
python -m pip install "pyperclip>=1.8.2,<1.9.0"

# Install gpt-engineer in development mode
Write-Host "Installing gpt-engineer..."
python -m pip install -e .

Write-Host "✅ Installation completed successfully!" -ForegroundColor Green
Write-Host "You can now run: gpte projects/example"