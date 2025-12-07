import tempfile
import os
import shutil
from pathlib import Path
import subprocess
import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def create_test_file_and_run():
    """Helper function to create a test file and run pytest on it.

    Returns a callable that accepts:
        isolated_env: Tuple of (base_path, env_dict) from isolated_env fixture
        pytest_code: String containing the test code to write
        pytest_args: List of pytest arguments (default: ["-v"])

    Returns:
        CompletedProcess object from subprocess.run
    """

    def _create_and_run(isolated_env, pytest_code, pytest_args=None):
        base, env = isolated_env
        test_file = base / "test_sample.py"
        test_file.write_text(pytest_code)

        if pytest_args is None:
            pytest_args = ["-v"]

        proc = subprocess.run(
            ["pytest"] + pytest_args + [str(test_file)],
            capture_output=True,
            text=True,
            env=env,
        )
        return proc

    return _create_and_run


@pytest.fixture
def isolated_env():
    """
    Sets up an isolated temp directory for test files.
    The plugin is already installed via entry point, so no manual registration needed.
    Returns: (base_path, env)
    """
    temp_dir = tempfile.mkdtemp()
    base = Path(temp_dir)

    # Build environment
    env = os.environ.copy()

    yield base, env

    shutil.rmtree(temp_dir, ignore_errors=True)
