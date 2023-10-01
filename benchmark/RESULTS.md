# Benchmarks

```bash
python scripts/benchmark.py

```

## 2023-06-21

| Benchmark          | Ran | Works | Perfect |
|--------------------|-----|-------|---------|
| currency_converter | ✅  | ❌    | ❌      |
| image_resizer      | ✅  | ✅    | ❌      |
| pomodoro_timer     | ✅  | ✅    | ✅      |
| url_shortener      | ✅  | ✅    | ❌      |
| file_explorer      | ✅  | ✅    | ❌      |
| markdown_editor    | ✅  | ✅    | ❌      |
| timer_app          | ✅  | ✅    | ✅      |
| file_organizer     | ✅  | ✅    | ✅      |
| password_generator | ✅  | ✅    | ✅      |
| todo_list          | ✅  | ✅    | ✅      |

## Notes on errors

Most errors was that it wasn't importing correctly or just executing. The code
itself was usually not the problem.


## 2023-06-21

| Benchmark          | Ran | Works | Perfect |
|--------------------|-----|-------|---------|
| currency_converter | ✅  | ❌    | ❌      |
| image_resizer      | ✅  | ✅    | ✅      |
| pomodoro_timer     | ✅  | ✅    | ✅      |
| url_shortener      | ✅  | ✅    | ✅      |
| file_explorer      | ✅  | ✅    | ✅      |
| markdown_editor    | ✅  | ✅    | ❌      |
| timer_app          | ✅  | ❌    | ❌      |
| weather_app        | ✅  | ✅    | ✅      |
| file_organizer     | ✅  | ✅    | ✅      |
| password_generator | ✅  | ✅    | ✅      |
| todo_list          | ✅  | ✅    | ✅      |

### Notes on the errors

Most errors come from that the "generate entrypoint" are incorrect. Ignoring
those, we get 8/11 fully correct.

All errors are very easy to fix.

One error was trying to modify a constant.
One error was that the html template was not fully filled in.
One error is that a dependency was used incorrectly and easy to fix


## 2023-06-19

| Benchmark          | Ran | Works | Perfect |
|--------------------|-----|-------|---------|
| currency_converter | ❌  | ❌    | ❌      |
| image_resizer      | ✅  | ❌    | ❌      |
| pomodoro_timer     | ❌  | ❌    | ❌      |
| url_shortener      | ❌  | ❌    | ❌      |
| file_explorer      | ✅  | ✅    | ✅      |
| markdown_editor    | ❌  | ❌    | ❌      |
| timer_app          | ✅  | ❌    | ❌      |
| weather_app        | ❌  | ❌    | ❌      |
| file_organizer     | ✅  | ✅    | ✅      |
| password_generator | ✅  | ✅    | ✅      |
| todo_list          | ✅  | ❌    | ❌      |

### Notes on the errors

**timer_app** almost works with unit tests config

- failure mode: undefined import/conflicting names

**file_explorer** works

**file organiser**: works

**image_resizer** almost works with unit tests config

- failure mode: undefined import

**todo_list** runs. doesn't really work with unit tests config
Uncaught ReferenceError: module is not defined

- failure mode: placeholder text

url_shortener starts but gets the error:
  SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 8636125824 and this is thread id 13021003776.

markdown_editor:
failing tests, 'WebDriver' object has no attribute 'find_element_by_id'

pomodoro: doesn't run it only tests

currency_converter: backend doesn't return anything

weather_app only runs test, no code existed

# GPT 3.5 Benchmarks


## 2023-08-20 (8358b60e1c6dcfc517c47c15708422d9a7d1d83a)
| Benchmark          | Version       | Ran | Works | Perfect |
|--------------------|---------------|-----|-------|---------|
| currency_converter | GPT3.5 default| ✅  | ❌    | ❌       |
| image_resizer      | GPT3.5 default| ✅  | ✅    | ✅      |
| pomodoro_timer     | GPT3.5 default| ✅  | ✅    | ❌      |
| url_shortener      | GPT3.5 default| ❌  | ❌    | ❌      |
| file_explorer      | GPT3.5 default| ✅  | ✅    | ❌      |
| markdown_editor    | GPT3.5 default| ✅  | ❌    | ❌      |
| timer_app          | GPT3.5 default| ✅  | ✅    | ✅      |
| file_organizer     | GPT3.5 default| ✅  | ✅    | ❌      |
| password_generator | GPT3.5 default| ✅  | ✅    | ✅      |
| todo_list          | GPT3.5 default| ✅  | ✅    | ❌      |

### Notes on the errors

#### GPT3.5
- `pomodoro_timer`: notifications didn't work.
- `file_explorer`: deletion didn't work.
- `file_organizer`: only handled a very small set of formats.
- `todo_list`: tasks couldn't be marked as completed.
- `url_shortener`: file names were wrong. Nothing could be run.
