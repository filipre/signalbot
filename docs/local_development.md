Contributions are welcome.

The first step to contribute is to install the package in editable mode.
For any changes, check that the tests still pass as detailed below.

### Local development

1. Clone the [repository](https://github.com/signalbot-org/signalbot).
2. Install [uv](https://docs.astral.sh/uv/).
3. Create a venv and install signalbot with its dependencies in it (including extra dependencies to be able to run the examples)
    ```bash
    uv sync --groups examples
    ```

    * You can install signalbot as an editable depedency in another repository (e.g. your own bot repository) like so
    ```
    uv add --editable ../signalbot
    ```

4. Install the prek hook for linting and formatting
    ```bash
    uv run prek install
    ```

### Unit Testing

The tests can be executed with

```bash
uv run pytest
```

### Serving the documentation locally

1. Install the docs dependencies
    ```bash
    uv sync --group docs
    ```
2. Run the mkdocs serve command
    ```bash
    uv run mkdocs serve --livereload --watch ./
    ```
