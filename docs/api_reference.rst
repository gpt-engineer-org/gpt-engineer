.. _api_reference:

=============
API Reference
=============

:mod:`gpt_engineer.applications`: Applications
===============================================

.. automodule:: gpt_engineer.applications
    :no-members:
    :no-inherited-members:

Classes
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: applications
    :template: class.rst

    applications.cli.cli_agent.CliAgent
    applications.cli.file_selector.DisplayablePath

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: applications

    applications.cli.collect.collect_and_send_human_review
    applications.cli.collect.collect_learnings
    applications.cli.collect.send_learning
    applications.cli.learning.ask_collection_consent
    applications.cli.learning.ask_for_valid_input
    applications.cli.learning.check_collection_consent
    applications.cli.learning.extract_learning
    applications.cli.learning.get_session
    applications.cli.learning.human_review_input
    applications.cli.main.get_preprompts_path
    applications.cli.main.load_env_if_needed
    applications.cli.main.load_prompt
    applications.cli.main.main

:mod:`gpt_engineer.benchmark`: Benchmark
=========================================

.. automodule:: gpt_engineer.benchmark
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: benchmark

    benchmark.__main__.get_agent
    benchmark.__main__.main
    benchmark.benchmarks.gpteng.eval_tools.assert_exists_in_source_code
    benchmark.benchmarks.gpteng.eval_tools.check_evaluation_component
    benchmark.benchmarks.gpteng.eval_tools.check_language
    benchmark.benchmarks.gpteng.eval_tools.run_code_class_has_property
    benchmark.benchmarks.gpteng.eval_tools.run_code_class_has_property_w_value
    benchmark.benchmarks.gpteng.eval_tools.run_code_eval_function
    benchmark.benchmarks.gpteng.load.eval_to_task
    benchmark.benchmarks.gpteng.load.expect_to_assertion
    benchmark.benchmarks.gpteng.load.load_gpteng
    benchmark.benchmarks.gptme.load.load_gptme
    benchmark.benchmarks.load.get_benchmark
    benchmark.run.print_results
    benchmark.run.run

:mod:`gpt_engineer.core`: Core
===============================

.. automodule:: gpt_engineer.core
    :no-members:
    :no-inherited-members:

Classes
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: core
    :template: class.rst

    core.base_agent.BaseAgent
    core.base_execution_env.BaseExecutionEnv
    core.default.disk_execution_env.DiskExecutionEnv
    core.default.disk_memory.DiskMemory
    core.default.simple_agent.SimpleAgent
    core.files_dict.FilesDict
    core.version_manager.BaseVersionManager

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: core

    core.ai.serialize_messages
    core.chat_to_files.apply_diffs
    core.chat_to_files.chat_to_files_dict
    core.chat_to_files.parse_diff_block
    core.chat_to_files.parse_diffs
    core.chat_to_files.parse_hunk_header
    core.default.paths.memory_path
    core.default.paths.metadata_path
    core.default.simple_agent.default_config_agent
    core.default.steps.curr_fn
    core.default.steps.execute_entrypoint
    core.default.steps.gen_code
    core.default.steps.gen_entrypoint
    core.default.steps.improve
    core.default.steps.salvage_correct_hunks
    core.default.steps.setup_sys_prompt
    core.default.steps.setup_sys_prompt_existing_code
    core.diff.count_ratio
    core.diff.is_similar
    core.files_dict.file_to_lines_dict

:mod:`gpt_engineer.tools`: Tools
=================================

.. automodule:: gpt_engineer.tools
    :no-members:
    :no-inherited-members:

Functions
--------------
.. currentmodule:: gpt_engineer

.. autosummary::
    :toctree: tools

    tools.custom_steps.clarified_gen
    tools.custom_steps.get_platform_info
    tools.custom_steps.lite_gen
    tools.custom_steps.self_heal
