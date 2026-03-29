# API classes

The classes in the [generated_receive folder](./generated_receive/) were automatically generated from the [JSON Schema](https://json-schema.org/) files in the [json_schema_receive folder](./json_schema_receive).
To convert from JSON Schema to pydantic dataclasses the [datamodel-code-generator tool](https://datamodel-code-generator.koxudaxi.dev/) is used.

Those files were copied over from the [signal-cli repository](https://github.com/AsamK/signal-cli).
From this [PR](https://github.com/AsamK/signal-cli/pull/1952).

The same for the [generated_send](./generated_send/) and [json_schema_send](./json_schema_send) folders.
Those come from signal-cli-rest-api and were copied directly from their documentation https://bbernhard.github.io/signal-cli-rest-api/

To generate the files run these commands at the root of the repository

```bash
uv run datamodel-codegen \
--input ./src/signalbot/api/json_schema_receive/ \
--input-file-type jsonschema \
--output-model-type pydantic_v2.BaseModel \
--formatters ruff-check ruff-format \
--snake-case-field \
--disable-timestamp \
--use-exact-imports \
--no-use-type-checking-imports \
--all-exports-scope recursive \
--all-exports-collision-strategy minimal-prefix \
--output ./src/signalbot/api/generated_receive
```

uv run datamodel-codegen \
--input ./src/signalbot/api/json_schema_send/signal-cli-rest-api.json \
--input-file-type jsonschema \
--output-model-type pydantic_v2.BaseModel \
--formatters ruff-check ruff-format \
--snake-case-field \
--disable-timestamp \
--use-exact-imports \
--no-use-type-checking-imports \
--all-exports-scope recursive \
--all-exports-collision-strategy minimal-prefix \
--output ./src/signalbot/api/generated_send
