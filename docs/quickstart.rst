==========
Quickstart
==========

Installation
============

To install LangChain run:

.. code-block:: console

    $ python -m pip install gpt-engineer

For more details, see our [Installation guide](/instllation.html).

Setup API Key
=============

Choose one of the following:

- Export env variable (you can add this to ``.bashrc`` so that you don't have to do it each time you start the terminal)

  .. code-block:: console

      $ export OPENAI_API_KEY=[your api key]

- Add it to the ``.env`` file:

  - Create a copy of ``.env.template`` named ``.env``
  - Add your ``OPENAI_API_KEY`` in .env

- If you want to use a custom model, visit our docs on `using open models and azure models <./open_models.html>`_.

- To set API key on windows check the `Windows README <./windows_readme_link.html>`_.

Building with ``gpt-engineer``
==============================

Create new code (default usage)
-------------------------------

- Create an empty folder for your project anywhere on your computer
- Create a file called ``prompt`` (no extension) inside your new folder and fill it with instructions
- Run ``gpte <project_dir>`` with a relative path to your folder
- For example, if you create a new project inside the gpt-engineer ``/projects`` directory:

  .. code-block:: console

    $ gpte projects/my-new-project

Improve Existing Code
---------------------

- Locate a folder with code which you want to improve anywhere on your computer
- Create a file called ``prompt`` (no extension) inside your new folder and fill it with instructions for how you want to improve the code
- Run ``gpte <project_dir> -i`` with a relative path to your folder
- For example, if you want to run it against an existing project inside the gpt-engineer ``/projects`` directory:

  .. code-block:: console

    $ gpte projects/my-old-project -i

By running ``gpt-engineer`` you agree to our `terms <./terms_link.html>`_.

To **run in the browser** you can simply:

.. image:: https://github.com/codespaces/badge.svg
   :target: https://github.com/gpt-engineer-org/gpt-engineer/codespaces
