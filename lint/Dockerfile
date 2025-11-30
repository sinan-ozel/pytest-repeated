FROM python:3.11-slim

WORKDIR /app

# Copy pyproject.toml from the parent directory
COPY pyproject.toml .
COPY src/pytest_repeated ./src/pytest_repeated
COPY lint/lint_and_format.sh ./src/lint_and_format.sh

RUN pip install --upgrade pip
RUN pip install .           # Install main project dependencies
RUN pip install .[dev]     # Install development dependencies

# Default command: run tests
CMD ["/src/lint_and_format.sh"]
