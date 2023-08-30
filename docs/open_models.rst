Using with open/local models
============================

You can integrate ``gpt-engineer`` with open-source models by leveraging an OpenAI-compatible API. One such API is provided by the `text-generator-ui extension openai <https://github.com/oobabooga/text-generation-webui/blob/main/extensions/openai/README.md>`_.

Setup
-----

To get started, first set up the API with the Runpod template, as per the `instructions <https://github.com/oobabooga/text-generation-webui/blob/main/extensions/openai/README.md>`_.

Running the Example
-------------------

Once the API is set up, you can run the following example using WizardCoder-Python-34B hosted on Runpod:

.. code-block:: bash

  OPENAI_API_BASE=http://<host>:<port>/v1 python -m gpt_engineer.main benchmark/pomodoro_timer --steps benchmark TheBloke_WizardCoder-Python-34B-V1.0-GPTQ

To find the host and the exposed TCP port, check your Runpod dashboard. For example, my port was 40125.
