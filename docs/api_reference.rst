.. _api_reference:

=============
API Reference
=============

:mod:`gpt_engineer.ai`: Ai
===========================

.. automodule:: gpt_engineer.ai
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: ai

    ai.create_chat_model
    ai.fallback_model
    ai.get_tokenizer
    ai.serialize_messages

:mod:`gpt_engineer.chat_to_files`: Chat To Files
=================================================

.. automodule:: gpt_engineer.chat_to_files
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: chat_to_files

    chat_to_files.parse_chat
    chat_to_files.to_files

:mod:`gpt_engineer.collect`: Collect
=====================================

.. automodule:: gpt_engineer.collect
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: collect

    collect.collect_learnings
    collect.send_learning
    collect.steps_file_hash

:mod:`gpt_engineer.db`: Db
===========================

.. automodule:: gpt_engineer.db
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: db

    db.archive

:mod:`gpt_engineer.learning`: Learning
=======================================

.. automodule:: gpt_engineer.learning
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: learning

    learning.ask_if_can_store
    learning.check_consent
    learning.collect_consent
    learning.extract_learning
    learning.get_session
    learning.human_input
    learning.logs_to_string

:mod:`gpt_engineer.main`: Main
===============================

.. automodule:: gpt_engineer.main
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: main

    main.main

:mod:`gpt_engineer.steps`: Steps
=================================

.. automodule:: gpt_engineer.steps
    :no-members:
    :no-inherited-members:

Classes
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: steps
    :template: class.rst

    steps.Config

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: steps

    steps.clarify
    steps.curr_fn
    steps.execute_entrypoint
    steps.fix_code
    steps.gen_clarified_code
    steps.gen_code
    steps.gen_entrypoint
    steps.gen_spec
    steps.gen_unit_tests
    steps.get_prompt
    steps.human_review
    steps.respec
    steps.setup_sys_prompt
    steps.simple_gen
    steps.use_feedback

