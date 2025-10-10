# Context window (token limit)

This note explains what a context window (token limit) is, why it matters when using LLMs, and practical strategies to work within it.

## What is the context window?

A model's context window (also called token limit) is the maximum number of tokens the model can accept as input (and sometimes include in output). Tokens roughly correspond to pieces of words; common English text averages ~0.7–1.3 tokens per word depending on vocabulary and punctuation.

If your prompt + conversation + document history exceed the context window, older content will be truncated (dropped) or the model will return an error depending on the client.

## Why it matters

- Cost: Many API providers bill per token. Sending more tokens increases costs.
- Performance: Larger inputs increase latency and can require more memory on the client/server side.
- Truncation / information loss: When the context exceeds the limit, parts of history or documents are omitted, which can break coherence, reasoning, or cause the model to lose earlier instructions or facts.

## Practical strategies

Below are three pragmatic strategies to manage content so it fits the context window while preserving useful information.

### 1) Truncation (simple, predictable)

When total tokens are too large, drop old or less-important content. This is easy, predictable, and safe for streaming/long chats. Use heuristics to drop older messages or large binary blobs (images, raw code) first.

Pros: simple, low compute overhead.
Cons: may drop crucial earlier context.

Conceptual pseudocode:

```
function build_payload(history, new_message, max_tokens):
    payload = [system_prompt]
    payload.append(new_message)
    for msg in reversed(history):  # start from most recent
        if token_count(payload) + token_count(msg) > max_tokens:
            break
        payload.prepend(msg)
    return payload
```

Tips:
- Keep a sliding window of the most recent N messages.
- Prefer to keep the system instructions and the most recent user/assistant turn.

### 2) Summarization / compaction (preserve meaning)

Compress older content into a shorter summary that preserves important facts. Periodically summarize the conversation or documents and store the summary in place of raw items. This preserves context at a lower token cost.

Pros: maintains semantic information; better for long-running sessions.
Cons: requires extra API calls or compute for summarization and careful prompt engineering to avoid losing critical specifics.

Conceptual pseudocode:

```
if total_tokens(history) > summary_threshold:
    chunk = select_oldest_chunk(history)
    summary = call_model_summarize(chunk)
    remove chunk from history
    append summary_marker(summary) to history

# Then build payload as in truncation, prioritizing summaries + recent messages
```

Implementation notes:
- Use structured summaries when possible: facts, entities, decisions, open tasks.
- Keep both a human-readable summary and a small machine-friendly key-value store for retrieval.
- Re-summarize incrementally: each time you summarize, append to the summary rather than re-summarize everything from scratch.

### 3) Configuration option (developer-facing control)

Expose a configuration option to tune how the system behaves when approaching the token limit. Example knobs:

- max_context_tokens: hard limit used when composing payloads.
- strategy: one of ["truncate", "summarize", "hybrid"].
- preserve_system_prompts: boolean; always keep system prompts.
- preserve_recent_turns: N recent user/assistant turns to always keep.

This lets users choose tradeoffs appropriate to their use case (cost vs. fidelity).

Example configuration object (JSON-like):

```
config = {
  "max_context_tokens": 32000,
  "strategy": "hybrid",
  "preserve_system_prompts": true,
  "preserve_recent_turns": 6,
  "summary_chunk_size": 4000  # tokens per summarization chunk
}
```

Hybrid strategy: try to include as much recent raw context as possible, then include summaries of older content, and finally truncate if still necessary.

## Pseudocode: hybrid end-to-end

```
function prepare_context(history, new_message, config):
    ensure system_prompt in history (or separate)

    # Step 1: try to keep recent turns
    payload = [system_prompt, new_message]
    for msg in reversed(history.recent(config.preserve_recent_turns)):
        if token_count(payload) + token_count(msg) <= config.max_context_tokens:
            payload.prepend(msg)

    # Step 2: include summaries of older content
    older = history.older_than_recent()
    for chunk in chunked(older, config.summary_chunk_size):
        summary = get_or_create_summary(chunk)
        if token_count(payload) + token_count(summary) <= config.max_context_tokens:
            payload.append(summary)
        else:
            break

    # Step 3: if still too large, truncate the least-important remaining items
    if token_count(payload) > config.max_context_tokens:
        payload = truncate_least_important(payload, config.max_context_tokens)

    return payload
```

## Troubleshooting notes & edge cases

- "Off-by-one" token errors: different tokenizers or APIs may count tokens differently. Always leave a safety buffer (e.g., 32–256 tokens) when computing allowed tokens for model input + expected output.

- Unexpected truncation of system messages: ensure system prompts are treated as highest priority and pinned into the payload.

- Cost spikes when summarizing: summarization itself consumes tokens (both input and output), so amortize summarization by doing it infrequently or offline when possible.

- Losing exact data (e.g., code or long tables): summaries can lose exact formatting or specifics. For cases where exactness matters, keep the original as a downloadable artifact and include a short index or pointer in the summary.

- Very long single documents: chunk documents into logical sections and summarize each section, or use retrieval (vector DB) + short relevant context injection instead of sending whole doc.

- Multi-user/parallel sessions: keep per-session histories and shared summaries carefully namespaced to avoid mixing users' contexts.

## Additional suggestions

- Instrument token usage and provide metrics to users (tokens per request, cost per request, average history length). This helps tune thresholds.
- Provide a debugging mode that prints the token counts and what was dropped or summarized before each request.
- When integrating with retrieval (vector DBs), index long documents and retrieve only the most relevant chunks to inject into prompts rather than pushing entire documents.

## References and further reading

- Tokenization and how tokens map to words depends on the model's tokenizer (BPE / byte-level BPE etc.).
- For long-running agents, consider combining summarization with retrieval-augmented generation (RAG) patterns.


---

Notes: this page is intentionally concise. If you have an existing draft on the canvas you want copied verbatim, paste it here or tell me where to read it and I will replace this content with the draft's exact text.
