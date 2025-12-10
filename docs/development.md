# Development Guide

Contributing to pytest-repeated and setting up a development environment.

## Requirements

The only requirement is **🐳 Docker**.

The `.devcontainer` and `tasks.json` are prepared assuming a *nix system (Linux/macOS), but the commands will work on Windows with appropriate modifications.

## Development Setup

### Option 1: VS Code Dev Container (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sinan-ozel/pytest-repeated.git
   cd pytest-repeated
   ```

2. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Open in Dev Container**:
   - Open the folder in VS Code
   - When prompted, click "Reopen in Container"
   - Or use Command Palette: `Dev Containers: Reopen in Container`

4. **Start developing**:
   - The container has all dependencies installed
   - Run tests: `pytest` from the `tests/` directory
   - Code is live-mounted, changes reflect immediately

### Option 2: Docker Compose (Without Dev Container)

If you prefer Test-Driven Development or don't use VS Code:

```bash
docker compose -f tests/docker-compose.yaml up --build --abort-on-container-exit --exit-code-from test
```

This command:
- Builds the test container
- Runs all tests
- Exits with the test exit code (useful for CI/CD)
- Cleans up containers when done

You can also find this command in `.vscode/tasks.json`.

## Project Structure

```
pytest-repeated/
├── src/
│   └── pytest_repeated/
│       └── plugin.py          # Main plugin code
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Shared fixtures
│   ├── docker-compose.yaml    # Test environment
│   ├── Dockerfile             # Test container
│   ├── test_unit.py           # Unit tests
│   └── test_integration.py    # Integration tests
├── docs/                      # Documentation (MkDocs)
├── scripts/
│   └── semver_compare.py      # Version comparison utility
├── pyproject.toml             # Project metadata & dependencies
├── mkdocs.yml                 # Documentation configuration
└── README.md
```

## Running Tests

### All Tests

From the `tests/` directory:

```bash
pytest
```

### Specific Test File

```bash
pytest test_unit.py
pytest test_integration.py
```

### Specific Test

```bash
pytest test_integration.py::test_basic_functionality
```

### With Verbosity

```bash
pytest -v          # Verbose
pytest -vv         # More verbose
pytest -vvv        # Maximum verbosity (shows run-by-run output)
```

### With Coverage

```bash
pytest --cov=pytest_repeated --cov-report=html
```

Coverage report will be in `htmlcov/index.html`.

## Code Style

pytest-repeated follows standard Python conventions:

- **PEP 8** for code style
- **Type hints** where appropriate
- **Docstrings** for public functions

### Linting

Linting is handled by the CI/CD pipeline. To run locally:

```bash
# In dev container or with appropriate tools installed
ruff check src/
black --check src/
```

## Making Changes

### 1. Write Tests First (TDD)

```python
# tests/test_integration.py

@pytest.mark.dependency(name="test_new_feature")
def test_new_feature(create_test_file_and_run):
    """Test the new feature."""
    test_code = '''
import pytest

@pytest.mark.repeated(times=10, new_param=True)
def test_example():
    assert True
'''
    result = create_test_file_and_run(test_code)
    assert result.ret == 0
```

### 2. Implement the Feature

```python
# src/pytest_repeated/plugin.py

def pytest_runtest_call(item):
    marker = item.get_closest_marker("repeated")
    if not marker:
        return

    new_param = marker.kwargs.get("new_param", False)
    # Implement new feature...
```

### 3. Run Tests

```bash
pytest tests/
```

### 4. Update Documentation

Add documentation for your new feature in the appropriate docs file.

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add new_param for feature X"
git push origin feature/your-feature-name
```

## Contributing Workflow

1. **Fork or clone** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** with tests
4. **Verify tests pass**: Run pytest locally
5. **Commit**: Use clear commit messages
6. **Push**: `git push origin feature/your-feature`
7. **Open a Pull Request** on GitHub
8. **Wait for CI/CD**: Tests and linting will run automatically
9. **Address review feedback** if any
10. **Merge**: Maintainer will merge when ready

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- **On PR**: Runs tests and linting
- **On merge to main**: Publishes to PyPI automatically

Pipeline file: `.github/workflows/cicd.yaml`

## Testing Strategies

### Unit Tests (`test_unit.py`)

Tests for individual functions and components in isolation.

### Integration Tests (`test_integration.py`)

Tests for full plugin behavior using the `create_test_file_and_run` fixture:

```python
def test_something(create_test_file_and_run):
    test_code = '''
import pytest

@pytest.mark.repeated(times=10, threshold=9)
def test_example():
    assert True
'''
    result = create_test_file_and_run(test_code)
    assert result.ret == 0
    assert "passed" in result.stdout.str()
```

This fixture:
- Creates a temporary test file
- Runs pytest on it
- Returns the result for assertions

### Test Dependencies (`pytest-depends`)

Some tests depend on others:

```python
@pytest.mark.dependency(name="test_setup")
def test_setup():
    # Setup test
    pass

@pytest.mark.dependency(depends=["test_setup"])
def test_that_needs_setup():
    # This only runs if test_setup passes
    pass
```

## Releasing New Versions

Releases are automated via GitHub Actions when merging to `main`:

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   version = "0.4.0"  # Increment according to semver
   ```

2. Commit and push to main (via PR):
   ```bash
   git commit -am "chore: bump version to 0.4.0"
   ```

3. CI/CD automatically:
   - Runs tests
   - Builds package
   - Publishes to PyPI
   - Creates GitHub release

## Debugging Tips

### Debug Test Execution

Use `pytest --pdb` to drop into debugger on failure:

```bash
pytest --pdb
```

### Debug Plugin Hooks

Add print statements or use `pytest --log-cli-level=DEBUG`:

```python
# In plugin.py
import logging
logger = logging.getLogger(__name__)

def pytest_runtest_call(item):
    logger.debug(f"Running test: {item.nodeid}")
    # ...
```

Run with:
```bash
pytest --log-cli-level=DEBUG
```

### View Full Tracebacks

```bash
pytest --tb=long
```

## Questions or Issues?

- **Bug reports**: Open an issue on GitHub
- **Feature requests**: Open an issue with `[Feature Request]` prefix
- **Questions**: Open a discussion on GitHub Discussions

## Future Plans

Planned features (help wanted!):

- [ ] **Optimized testing** - stop conditions ⚡
- [ ] **Sequential testing** 📐
- [ ] **Ability to set the seed** 🌱
- [ ] **Report and fail on speed** ⏱️

See [GitHub Issues](https://github.com/sinan-ozel/pytest-repeated/issues) for more details.

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to make testing better! 🚀

## License

pytest-repeated is licensed under the MIT License. See [LICENSE](https://github.com/sinan-ozel/pytest-repeated/blob/main/LICENSE) for details.
