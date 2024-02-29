Using with open/local models
============================

At the moment the best option for coding is still the use of `gpt-4` models provided by OpenAI. But open models are catching up and are a good free and privacy-oriented alternative if you possess the proper hardware.

You can integrate `gpt-engineer` with open-source models by leveraging an OpenAI-compatible API.

We provide the minimal and cleanest solution below. It's not the only way to use open/local models but the one we recommend and tested.

Setup
-----

For inference engine we recommend to the users to use [llama.cpp](https://github.com/ggerganov/llama.cpp) with its `python` bindings `llama-cpp-python`. We choose `llama.cpp` because it supports the largest amount of hardware acceleration backends.

To install `llama-cpp-python` follow the official [installation docs](https://llama-cpp-python.readthedocs.io/en/latest/) and for [MacOS with Metal support](https://llama-cpp-python.readthedocs.io/en/latest/install/macos/).

If you want to have benefit from proper hardware acceleration on your machine make sure to set up the proper compile flags:

- `linux`: `CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"`
- `macos` with Metal support: `CMAKE_ARGS="-DLLAMA_METAL=on"`
- `windows`: `$env:CMAKE_ARGS = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"`

Before running:

```bash
pip install llama-cpp-python
```

For the use of `API` we also need to set up the web server:

```bash
pip install 'llama-cpp-python[server]'
```

For detailed use consult the [`llama-cpp-python` docs](https://llama-cpp-python.readthedocs.io/en/latest/server/). 

Before we proceed we need to obtain the model weights in the `gguf` format. In case you have weights in other formats check the `llama-cpp-python` docs for conversion to `gguf` format.

Which open model to use
==================

Your best choice would be:

- [CodeLlama](examples/CodeLlama2.py)
- Mixtral 8x7B

But to first test the setup go and download weights [CodeLlama-7B-GGUF by the `TheBloke`](https://huggingface.co/TheBloke/CodeLlama-7B-GGUF). Once that works feel free to try out larger models on your hardware and see what happens.

On number of parameters
-------------------

Use the largest model possible that your hardware allows you to run. Sure the responses might be slower but code quality higher.

Running the Example
==================

To see that your setup works see [test open LLM](examples/test_open_llm/README.md).

On other inference libraries
-------------------

Using Azure models
==================

You set your Azure OpenAI key:
- `export OPENAI_API_KEY=[your api key]`

Then you call `gpt-engineer` with your service endpoint `--azure https://aoi-resource-name.openai.azure.com` and set your deployment name (which you created in the Azure AI Studio) as the model name (last `gpt-engineer` argument).

Example:
`gpt-engineer --azure https://myairesource.openai.azure.com ./projects/example/ my-gpt4-project-name`
