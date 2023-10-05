.. highlight:: shell

============
Installation
============


Stable release
--------------

To install gpt-engineer, run this command in your terminal:

.. code-block:: console

    $ pip install gpt_engineer

This is the preferred method to install file-processor, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

If you don't have the latest version of Python then `click here`_.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

From sources
------------

The sources for file-processor can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/AntonOsika/gpt-engineer.git

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ cd gpt-engineer
    $ pip install -e .


.. _Github repo: https://github.com/AntonOsika/gpt-engineer.git

Troubleshooting
-------------

For mac and linux system, there are sometimes slim python installations that do not include the gpt-engineer requirement tkinter, which is a standard library and thus not pip installable.

Check what version of python you have installed by running: 

.. code-block:: console

    $ python3 --version

If you don't have the latest version of Python then `click here`_.

If you are still stuck then `this`_ website can help you.

.. _click here: https://www.python.org/downloads/
.. _this: https://www.freecodecamp.org/news/pip-upgrade-and-how-to-update-pip-and-python/#:~:text=One%20of%20the%20easiest%20ways,with%20it%20is%20also%20updated.&text=For%20me%2C%20I%20picked%203.11%20because%20it%27s%20now%20stable.&text=Run%20the%20installer%20and%20follow%20every%20prompt%20you%20see.
To install tkinter on mac, you can for example use brew:

.. code-block:: console

    $ brew install python-tk

On debian-based linux systems you can use:

.. code-block:: console

    $ sudo apt-get install python3-tk
