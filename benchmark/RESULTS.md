# Benchmarks

```bash
python scripts/benchmark.py
```

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

## Notes on the errors

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

## Notes on the errors

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
