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

If you have more `GPU` layers available set `--n_gpu_layers` to the higher number. To find the amount of avalibale  run the above command and look for `llm_load_tensors: offloaded 1/41 layers to GPU` in the output.

## Test API call

Set the environment variables:

```bash
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-xxx"
````

Then ping the model via `python` using `OpenAI` API:

```bash
python examples/test_open_llm/test_openai_api.py
```

If you're not using `CodeLLama` make sure to change the `model` parameter in the test script.

Or using `curl`:

```bash
curl --request POST \
     --url http://localhost:8000/v1/chat/completions \
     --header "Content-Type: application/json" \
     --data '{ "model": "llama", "prompt": "Who are you?", "max_tokens": 60}'
```

If this works also make sure that `langchain` interface works since that's how `gpte` interacts with LLMs.

## Langchain test

```bash
python examples/test_open_llm/test_langchain.py
```

If you're not using `CodeLLama` make sure to change the `model` parameter in the test script.

That's it 🤓 time to give `gpte` a try.