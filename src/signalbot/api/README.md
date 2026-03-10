# API classes

The classes in this [py-schema folder](./py_schema/) were automatically generated from the [JSON Schema](https://json-schema.org/) files in the [json-schema folder](./json_schema).
To convert from JSON Schema to pydantic dataclasses the [datamodel-code-generator tool](https://datamodel-code-generator.koxudaxi.dev/) is used.

Those files were copied over from the [signal-cli repository](https://github.com/AsamK/signal-cli).
From this [PR](https://github.com/AsamK/signal-cli/pull/1952).

To generate the files run this command at the root of the repository

```bash
uv run datamodel-codegen \
--input ./src/signalbot/api/json_schema/ \
--input-file-type jsonschema \
--output-model-type pydantic_v2.BaseModel \
--formatters ruff-check ruff-format \
--snake-case-field \
--reuse-model \
--reuse-scope tree \
--disable-timestamp \
--use-exact-imports \
--no-use-type-checking-imports \
--all-exports-scope recursive \
--all-exports-collision-strategy minimal-prefix \
--output ./src/signalbot/api/py_schema
```
