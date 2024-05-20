Using with open/local models
============================

**Use `gpte` first with OpenAI models to get a feel for the `gpte` tool.**

**Then go play with experimental Open LLMs 🐉 support and try not to get 🔥!!**

At the moment the best option for coding is still the use of `gpt-4` models provided by OpenAI. But open models are catching up and are a good free and privacy-oriented alternative if you possess the proper hardware.

You can integrate `gpt-engineer` with open-source models by leveraging an OpenAI-compatible API.

We provide the minimal and cleanest solution below. What is described is not the only way to use open/local models, but the one we tested and would recommend to most users.

More details on why the solution below is recommended in [this blog post](https://zigabrencic.com/blog/2024-02-21).

Setup
-----

For inference engine we recommend for the users to use [llama.cpp](https://github.com/ggerganov/llama.cpp) with its `python` bindings `llama-cpp-python`.

We choose `llama.cpp` because:

- 1.) It supports the largest amount of hardware acceleration backends.
- 2.) It supports the diverse set of open LLMs.
- 3.) Is written in `python` and directly on top of `llama.cpp` inference engine.
- 4.) Supports the `openAI` API and `langchain` interface.

To install `llama-cpp-python` follow the official [installation docs](https://llama-cpp-python.readthedocs.io/en/latest/) and [those docs](https://llama-cpp-python.readthedocs.io/en/latest/install/macos/) for MacOS with Metal support.

If you want to benefit from proper hardware acceleration on your machine make sure to set up the proper compiler flags before installing your package.

- `linux`: `CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"`
- `macos` with Metal support: `CMAKE_ARGS="-DLLAMA_METAL=on"`
- `windows`: `$env:CMAKE_ARGS = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"`

This will enable the `pip` installer to compile the `llama.cpp` with the proper hardware acceleration backend.

Then run:

```bash
pip install llama-cpp-python
```

For our use case we also need to set up the web server that `llama-cpp-python` library provides. To install:

```bash
pip install 'llama-cpp-python[server]'
```

For detailed use consult the [`llama-cpp-python` docs](https://llama-cpp-python.readthedocs.io/en/latest/server/).

Before we proceed we need to obtain the model weights in the `gguf` format. That should be a single file on your disk.

In case you have weights in other formats check the `llama-cpp-python` docs for conversion to `gguf` format.

Models in other formats `ggml`, `.safetensors`, etc. won't work without prior conversion to `gguf` file format with the solution described below!

Which open model to use?
==================

Your best choice would be:

- CodeLlama 70B
- Mixtral 8x7B

We are still testing this part, but the larger the model you can run the better. Sure the responses might be slower in terms of (token/s), but code quality will be higher.

For testing that the open LLM `gpte` setup works we recommend starting with a smaller model. You can download weights of [CodeLlama-13B-GGUF by the `TheBloke`](https://huggingface.co/TheBloke/CodeLlama-13B-GGUF) choose the largest model version you can run (for example `Q6_K`), since quantisation will degrade LLM performance.

Feel free to try out larger models on your hardware and see what happens.

Running the Example
==================

To see that your setup works check [test open LLM setup](examples/test_open_llm/README.md).

If above tests work proceed 😉

For checking that `gpte` works with the `CodeLLama` we recommend for you to create a project with `prompt` file content:

```
Write a python script that sums up two numbers. Provide only the `sum_two_numbers` function and nothing else.

Provide two tests:

assert(sum_two_numbers(100, 10) == 110)
assert(sum_two_numbers(10.1, 10) == 20.1)
```

Now run the LLM in separate terminal:

```bash
python -m llama_cpp.server --model $model_path --n_batch 256 --n_gpu_layers 30
```

Then in another terminal window set the following environment variables:

```bash
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-xxx"
export MODEL_NAME="CodeLLama"
export LOCAL_MODEL=true
```

And run `gpt-engineer` with the following command:

```bash
gpte <project_dir> $MODEL_NAME --lite --temperature 0.1
```

The `--lite` mode is needed for now since open models for some reason behave worse with too many instructions at the moment. Temperature is set to `0.1` to get consistent best possible results.

That's it.

*If sth. doesn't work as expected, or you figure out how to improve the open LLM support please let us know.*

Using Open Router models
==================

In case you don't posses the hardware to run local LLM's yourself you can use the hosting on [Open Router](https://openrouter.ai) and pay as you go for the tokens.

To set it up you need to Sign In and load purchase 💰 the LLM credits. Pricing per token is different for (each model](https://openrouter.ai/models), but mostly cheaper then Open AI.

Then create the API key.

To for example use [Meta: Llama 3 8B Instruct (extended)](https://openrouter.ai/models/meta-llama/llama-3-8b-instruct:extended) with `gpte` we need to set:

```bash
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
export OPENAI_API_KEY="sk-key-from-open-router"
export MODEL_NAME="meta-llama/llama-3-8b-instruct:extended"
export LOCAL_MODEL=true
```

```bash
gpte <project_dir> $MODEL_NAME --lite --temperature 0.1
```

Using Azure models
==================

You set your Azure OpenAI key:
- `export OPENAI_API_KEY=[your api key]`

Then you call `gpt-engineer` with your service endpoint `--azure https://aoi-resource-name.openai.azure.com` and set your deployment name (which you created in the Azure AI Studio) as the model name (last `gpt-engineer` argument).

Example:
`gpt-engineer --azure https://myairesource.openai.azure.com ./projects/example/ my-gpt4-project-name`
