SHELL := /bin/bash

.PHONY: help install dev-install

.DEFAULT_GOAL := help

.SILENT:

help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  help           Return this message with usage instructions."
	@echo "  install        Will install the dependencies and create a virtual environment."
	@echo "  dev-install    Will install the dev dependencies too."

dev-install:create-venv install-dev-dependencies install-pre-commit

install: create-venv install-dependencies farewell

install-dependencies:
	@echo "Installing dependencies..." && \
	pip install . >> /dev/null

create-venv:
	@echo "Creating virtual environment..." && \
	python -m venv venv && \
	source venv/bin/activate && \
	pip install --upgrade pip

install-dev-dependencies:
	@echo "Installing dependencies..." && \
	source venv/bin/activate && \
	pip install -r requirements.txt

install-pre-commit:
	@echo "Installing pre-commit hooks..." && \
	source venv/bin/activate && \
	pre-commit install
