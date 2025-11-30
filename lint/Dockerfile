FROM python:3.11-slim

WORKDIR /workspace

# Copy only pyproject.toml to install dependencies
COPY pyproject.toml /tmp/pyproject.toml
COPY src/pytest_repeated/__init__.py /tmp/src/pytest_repeated/__init__.py

RUN pip install --upgrade pip && \
    cd /tmp && \
    pip install . && \
    pip install .[dev] && \
    rm -rf /tmp/*

# Default command: run tests
CMD ["/src/lint_and_format.sh"]
