# softphone connector

[//]: # (Please fill in content about this module.)

## What this package does

[//]: # (Please fill in content about what this module does.)

## Developing

### Setting up your environment with Poetry

#### Windows

Install Poetry:

```bash
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python
```

#### Linux

Install Poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

## Installing dependencies

### Creating lock file

```bash
poetry lock
```

### Installing from lock file

```bash
poetry install
```

## Running tests

```bash
pytest
```

## Configuration

To add default configuration options to this package, add them to limepkg-softphone-connector/limepkg_softphone_connector/__init__.py like so:

```python
def default_config():
    return {
        'my-option': 'its default value'
    }
```

These options can later be retrieved like this:

```python
import lime_config

def my_function():
    opt = lime_config.config.plugins['limepkg-softphone-connector']['my-option']
```
