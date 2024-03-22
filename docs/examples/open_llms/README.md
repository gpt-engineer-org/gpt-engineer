# Test that the Open LLM is running

First start the server by using only CPU:

```bash
export model_path="TheBloke/CodeLlama-13B-GGUF/codellama-13b.Q8_0.gguf"
python -m llama_cpp.server --model $model_path
```

Or with GPU support (recommended):

```bash
python -m llama_cpp.server --model TheBloke/CodeLlama-13B-GGUF/codellama-13b.Q8_0.gguf --n_gpu_layers 1
```

If you have more `GPU` layers available set `--n_gpu_layers` to the higher number.

To find the amount of available  run the above command and look for `llm_load_tensors: offloaded 1/41 layers to GPU` in the output.

## Test API call

Set the environment variables:

```bash
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-xxx"
export MODEL_NAME="CodeLlama"
````

Then ping the model via `python` using `OpenAI` API:

```bash
python examples/open_llms/openai_api_interface.py
```

If you're not using `CodeLLama` make sure to change the `MODEL_NAME` parameter.

Or using `curl`:

```bash
curl --request POST \
     --url http://localhost:8000/v1/chat/completions \
     --header "Content-Type: application/json" \
     --data '{ "model": "CodeLlama", "prompt": "Who are you?", "max_tokens": 60}'
```

If this works also make sure that `langchain` interface works since that's how `gpte` interacts with LLMs.

## Langchain test

```bash
export MODEL_NAME="CodeLlama"
python examples/open_llms/langchain_interface.py
```

That's it 🤓 time to go back [to](/docs/open_models.md#running-the-example) and give `gpte` a try.
