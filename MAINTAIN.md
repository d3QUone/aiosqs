# Local development

Set up environment:
```shell
python3 -m pip install poetry
poetry env use 3.11
poetry install
```

Run tests:
```shell
make test
```

# Build and publish

```shell
hatch build
hatch publish
```
