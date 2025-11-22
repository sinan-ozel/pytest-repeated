# Introduction

Pytest plugin to repeat tests and pass if the test passes a number of times out of a total.

# Installation

```
pip install pytest-repeated
```

# 🚀 Usage Example

```
@pytest.mark.repeated(times=4, threshold=2)
def test_example_fail_once():
    import random
    assert random.choice([True, False])  # may pass or fail
```

This test will run four times and pass if we get `True` in at least two of the four iterations.

# 🛠️ Development

The only requirement is 🐳 Docker.
(The `.devcontainer` and `tasks.json` are prepared assuming a *nix system, but if you know the commands, this will work on Windows, too.)

1. Clone the repo.
2. Branch out.
3. Open in "devcontainer" on VS Code and start developing. Run `pytest` under `tests` to test.
4. Akternatively, if you are a fan of Test-Driven Development like me, you can run the tests without getting on a container. `.vscode/tasks.json` has the command to do so, but it's also listed here:
```
docker compose -f tests/docker-compose.yaml up --build --abort-on-container-exit --exit-code-from test
```

4. When satisfied, push and open a PR. The pipeline will publish automatically when your PR is merged.