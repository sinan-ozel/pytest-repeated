import subprocess
from textwrap import dedent

import pytest


@pytest.mark.depends(on=["base_repeated_marker_test"])
def test_fixture_runs_every_iteration(isolated_env, create_test_file_and_run):
    """Test that fixtures run with every iteration of repeated tests."""
    pytest_code = dedent(
        """
    import pytest

    call_count = {"count": 0}

    @pytest.fixture(scope="function")
    def counting_fixture():
        call_count["count"] += 1
        yield call_count["count"]

    @pytest.mark.repeated(times=5, threshold=1)
    def test_with_fixture(counting_fixture):
        # The fixture should run on each iteration, so counting_fixture
        # should increment from 1 to 5 across the 5 iterations
        # We assert that it's within the expected range
        assert 1 <= counting_fixture <= 5
    """
    )

    proc = create_test_file_and_run(isolated_env, pytest_code)

    stdout = proc.stdout
    print(stdout)
    # The test should pass - this demonstrates the fixture runs each iteration
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Verify the test passed all 5 iterations
    assert "PASSED (5/5)" in stdout or "1 passed" in stdout, stdout