import tempfile
import os
import shutil
from pathlib import Path
import pytest

pytest_plugins = ["pytester"]


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


