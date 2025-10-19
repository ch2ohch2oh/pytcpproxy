# pytcpproxy

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
python3 -m pypxy.proxy <remote_host> <remote_port>
```

- `<remote_host>`: The remote host to forward traffic to.
- `<remote_port>`: The remote port to forward traffic to.

You can also specify the local host and port to listen on:

```bash
python3 -m pypxy.proxy <remote_host> <remote_port> --local-host <local_host> --local-port <local_port>
```

- `--local-host`: The local host to listen on (default: `0.0.0.0`).
- `--local-port`: The local port to listen on (default: `8000`).

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