Contributions are welcome.

The first step to contribute is to install the package in editable mode.
For any changes, check that the tests still pass as detailed below.

### Local development

1. Install [uv](https://docs.astral.sh/uv/).
2. Create a venv and install signalbot with its dependencies in it
    ```bash
    uv sync
    ```
3. Install the prek hook for linting and formatting
    ```bash
    uv run prek install
    ```

### Unit Testing

The tests can be executed with

```bash
uv run pytest
```

In many cases, we can mock receiving and sending messages to speed up development time.
To do so, you can use `signalbot.utils.ChatTestCase` which sets up a "skeleton" bot.
Then, you can send messages using the `@mock_chat` decorator in `signalbot.utils`.
You can find an example implementation in `tests/test_chat.py`.

### Serving the documentation locally

1. Install the docs dependencies
    ```bash
    uv sync --group docs
    ```
2. Run the mkdocs serve command
    ```bash
    uv run mkdocs serve --livereload --watch ./
    ```
