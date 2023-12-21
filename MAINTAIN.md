# Local development

Set up environment:
```shell
python3 -m pip install poetry==1.5.0
poetry env use 3.11
poetry install
poetry run pre-commit install
```

Run tests:
```shell
make test
```

# Build and publish

```shell
python3 -m pip install hatch
```

```shell
hatch build
hatch publish
```
