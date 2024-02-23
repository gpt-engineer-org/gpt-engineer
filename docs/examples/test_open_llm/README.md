# Test that the Open LLM is running

First start the server by using only CPU:

```bash
export model_path="models/llama-2-7b.Q2_K.gguf"
python -m llama_cpp.server --model $model_path
```

Or with GPU support (recommended):

```bash
python -m llama_cpp.server --model models/llama-2-7b.Q2_K.gguf --n_gpu_layers 1
```

If you have more `GPU` layers available set `--n_gpu_layers` to the higher number.

## Test API call

Then ping it via `python` using `OpenAI` API:

```bash
python examples/test_open_llm/test_open_llm.py
```

Or via `curl`:

```bash
curl --request POST \
     --url http://localhost:8000/v1/chat/completions \
     --header "Content-Type: application/json" \
     --data '{ "model": "llama", "prompt": "Who are you?", "max_tokens": 60}'
```