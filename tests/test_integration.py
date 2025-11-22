import os
import shutil
import tempfile
from pathlib import Path
import pytest


def test_repeated_marker_behavior():
    """
    Integration test that loads the real plugin implementation from disk,
    then runs pytest inside an isolated temporary environment.
    """

    # Locate your actual plugin file
    plugin_path = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "pytest_repeated"
        / "plugin.py"
    )
    assert plugin_path.exists(), f"Plugin not found: {plugin_path}"

    # Create a full isolated test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp = Path(temp_dir)

        # Copy plugin package into isolated environment
        pkg_dir = tmp / "pytest_repeated"
        pkg_dir.mkdir()
        shutil.copy(plugin_path, pkg_dir / "plugin.py")

        # Add __init__.py so pytest can discover the package
        (pkg_dir / "__init__.py").write_text("")

        # Create test file using pytest.mark.repeated
        test_file = tmp / "test_sample.py"
        test_file.write_text(
            """
import pytest

@pytest.mark.repeated(times=5, threshold=2)
def test_flaky():
    import random
    return random.choice([True, False])
"""
        )

        # Add temp directory to PYTHONPATH so pytest can import the plugin
        env = os.environ.copy()
        env["PYTHONPATH"] = temp_dir + os.pathsep + env.get("PYTHONPATH", "")

        # Run pytest and explicitly load plugin module
        result = pytest.main(
            [
                str(tmp),
                "-q",
                "-p", "pytest_repeated.plugin",   # load plugin
            ]
        )
        assert result == 0, "Flaky test should succeed with threshold logic"
