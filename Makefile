SHELL := /bin/bash

# Color codes
COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m

.PHONY: help install dev-install run

.DEFAULT_GOAL := help

.SILENT:

name := $(word 2,$(MAKECMDGOALS))

help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  help           	Return this message with usage instructions."
	@echo "  install        	Will install the dependencies and create a virtual environment."
	@echo "  dev-install    	Will install the dev dependencies too."
	@echo "  run <folder_name>  Runs GPT Engineer on the folder with the given name."

dev-install: install

install: create-venv upgrade-pip install-dependencies install-pre-commit farewell

create-venv:
	@echo -e "$(COLOR_CYAN)Creating virtual environment...$(COLOR_RESET)" && \
	python -m venv venv

upgrade-pip:
	@echo -e "$(COLOR_CYAN)Upgrading pip...$(COLOR_RESET)" && \
	source venv/bin/activate && \
	pip install --upgrade pip >> /dev/null

install-dependencies:
	@echo -e "$(COLOR_CYAN)Installing dependencies...$(COLOR_RESET)" && \
	source venv/bin/activate && \
	pip install -e . >> /dev/null

install-pre-commit:
	@echo -e "$(COLOR_CYAN)Installing pre-commit hooks...$(COLOR_RESET)" && \
	source venv/bin/activate && \
	pre-commit install

farewell:
	@echo -e "$(COLOR_GREEN)All done!$(COLOR_RESET)"

run:
	@echo -e "$(COLOR_CYAN)Running GPT Engineer on $(COLOR_GREEN)$(name)$(COLOR_CYAN) folder...$(COLOR_RESET)" && \
	source venv/bin/activate && \
	gpt-engineer projects/$(name)

