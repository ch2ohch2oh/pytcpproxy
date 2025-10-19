# pypxy

A simple Python TCP proxy service.

## Setup

1. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   For a production environment, install only the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   For a development environment, which includes all testing and linting tools, run:

   ```bash
   pip install -r requirements-dev.txt
   ```

## Usage

To start the proxy server, run:

```bash
python3 -m pypxy.proxy
```

The proxy will listen on port 8000 and forward connections to a pre-configured host and port (default: `localhost:12345`). You can change the target in `pypxy/proxy.py`.

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

## Linting and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

To check for linting errors, run:

```bash
ruff check .
```

To format the code, run:

```bash
ruff format .
```