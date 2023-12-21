# Local development

Set up environment:
```shell
python3 -m pip install poetry==1.5.0
poetry env use 3.11
poetry install
poetry run pre-commit install
```


## Unit-tests

```shell
make test
```


## E2E tests

To run integration (or end-to-end) tests on a real instance of Amazon SQS put your credentials in local file:
```shell
cp .env_example .env
```

Run special tests after `.env` file is ready:
```shell
make test_e2e
```


# Build and publish

Update package version manually inside `aiosqs/__init__.py` file and inside `pyproject.toml` file.

Then install a tool to publish:
```shell
python3 -m pip install hatch
```

```shell
hatch build
hatch publish
```
