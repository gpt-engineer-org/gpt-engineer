Building Docs with Sphnix
=========================

This example shows a basic Sphnix docs project with Read the Docs. This project is using `sphnix` with `readthedocs` 
project template.

Some useful links are given below to lear and contribute in the project.

📚 [docs/](https://www.sphinx-doc.org/en/master/usage/quickstart.html)<br>
A basic Sphnix project lives in `docs/`, it was generated using Sphnix defaults. All the `*.rst` & `*.md` make up sections in the documentation. Both `.rst` and `.md` formats are supported in this project

⚙️ [.readthedocs.yaml](https://docs.readthedocs.io/en/stable/config-file/v2.html)<br>
Read the Docs Build configuration is stored in `.readthedocs.yaml`.


📍 [docs/requirements.txt](https://docs.readthedocs.io/en/stable/config-file/v2.html)<br>
Python dependencies are [pinned](https://docs.readthedocs.io/en/latest/guides/reproducible-builds.html) (uses [pip-tools](https://pip-tools.readthedocs.io/en/latest/)) here. Make sure to add your Python dependencies to `requirements.txt` or if you choose [pip-tools](https://pip-tools.readthedocs.io/en/latest/), edit `docs/requirements.txt`. 



Example Project usage
---------------------

`Poetry` is the package manager for `gpt-engineer`. In order to build documentation, we have to add docs requirements in 
development environment. 

This project has a standard readthedocs layout which is built by Read the Docs almost the same way that you would build it 
locally (on your own laptop!).

You can build and view this documentation project locally - we recommend that you activate a `Poetry` environment
and dependency management tool.

COPY files from project root to `docs/` to include in Documents
```console
cp README.md docs/
cp ROADMAP.md docs/
cp TERMS_OF_USE.md docs/
cp WINDOWS_README.md docs/
cp .github/CONTRIBUTING.md docs/
cp .github/CODE_OF_CONDUCT.md docs/
cp benchmark/RESULTS.md docs/
```
Update `repository_stats.md` file under `docs/`

```console
# Install required Python dependencies (MkDocs etc.)
poetry insall --with docs
cd docs/
# Create the `api_reference.rst` 
python create_api_rst.py

# Build the docs 
make html
```

Project Docs Structure 
----------------------
If you are new to Read the Docs, you may want to refer to the [Read the Docs User documentation](https://docs.readthedocs.io/).

Below is the rundown of documentation structure for `pandasai`, you need to know:

1. place your `docs/` folder alongside your Python project.
2. copy `.readthedocs.yaml` and the `docs/` folder into your project root.
3. `docs/api_reference.rst` contains the API documentation created using `docstring`.  Run the `create_api_rst.py` to update the API reference file.
4. Project is using standard Google Docstring Style.
5. Rebuild the documenation locally to see that it works.
6. Documentation are hosted on [Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/)


Read the Docs tutorial
----------------------

To get started with Read the Docs, you may also refer to the 
[Read the Docs tutorial](https://docs.readthedocs.io/en/stable/tutorial/). I

With every release, build the documentation manually. 
