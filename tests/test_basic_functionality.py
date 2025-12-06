import subprocess
from textwrap import dedent

import pytest


def create_test_file_and_run(isolated_env, pytest_code, pytest_args=None):
    """Helper function to create a test file and run pytest on it.

    Args:
        isolated_env: Tuple of (base_path, env_dict) from isolated_env fixture
        pytest_code: String containing the test code to write
        pytest_args: List of pytest arguments (default: ["-v"])

    Returns:
        CompletedProcess object from subprocess.run
    """
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


@pytest.mark.depends(name="base_repeated_marker_test")
def test_repeated_marker_behavior(isolated_env):
    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        import random
        return random.choice([True, False])
    """
    )

    proc = create_test_file_and_run(isolated_env, PYTEST_CODE)

    stdout = proc.stdout
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "(5/5)" in stdout or "(5/5)" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_pass_equal(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        call_count["count"] += 1
        assert call_count["count"] > 3
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "PASSED (2/5)" in stdout or "PASSED (2/5)" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_pass_gt(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        call_count["count"] += 1
        assert call_count["count"] > 2
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "PASSED (3/5)" in stdout or "PASSED (3/5)" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_fail(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        call_count["count"] += 1
        assert call_count["count"] > 4
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "FAILED (1/5)" in stdout or "FAILED (1/5)" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_met_with_final_failure(isolated_env):
    """Test that threshold met results in PASSED even if last run fails."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        call_count["count"] += 1
        # Passes on runs 1 and 3, fails on runs 2, 4, 5
        assert call_count["count"] in [1, 3]
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    # Should PASS because 2/5 >= threshold of 2, even though last run failed
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "PASSED (2/5)" in stdout or "PASSED (2/5)" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_0_pass(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=0)
    def test_failing():
        assert False
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "PASSED (0/5)" in stdout or "PASSED (0/5)" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_pass_with_verbosity_level_3(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        call_count["count"] += 1
        # Passes on runs 1 and 3, fails on runs 2, 4, 5
        assert call_count["count"] in [1, 3]
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-vvv", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "PASSED (2/5)" in stdout or "PASSED (2/5)" in proc.stderr, stdout
    assert (
        "Run-by-run results:" in stdout or "Run-by-run results:" in proc.stderr
    ), stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_threshold_fail_with_verbosity_level_3(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=4)
    def test_flaky():
        call_count["count"] += 1
        # Passes on runs 1 and 3, fails on runs 2, 4, 5
        assert call_count["count"] in [1, 3], f'Expected: {1, 3}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-vvv", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "FAILED (2/5)" in stdout or "FAILED (2/5)" in proc.stderr, stdout
    assert (
        "Expected: (1, 3)" in stdout or "Expected: (1, 3)" in proc.stderr
    ), stdout
    assert "Got: " in stdout or "Got: " in proc.stderr, stdout
    assert (
        "Run-by-run results:" in stdout or "Run-by-run results:" in proc.stderr
    ), stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_fail_with_error_verbosity_level_3(isolated_env):
    """Test that KeyError details are shown in run-by-run output."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=4)
    def test_flaky():
        call_count["count"] += 1
        # Always fails with KeyError
        assert call_count["incorrect_key"] in [1, 3], f'Expected: {1, 3}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-vvv", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "FAILED (0/1)" in stdout, stdout
    assert (
        "'incorrect_key'" in stdout or "'incorrect_key'" in proc.stderr
    ), stdout
    # Should only show "Run 1:" and NOT "Run 2:", "Run 3:", etc.
    assert "Run 1:" in stdout, f"Expected 'Run 1:' in output\n{stdout}"
    assert (
        "Run 2:" not in stdout
    ), f"Expected NO 'Run 2:' in output (should stop after first run)\n{stdout}"

    assert "KeyError" in stdout or "KeyError" in proc.stderr, stdout
    assert (
        "Run-by-run results:" in stdout or "Run-by-run results:" in proc.stderr
    ), stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_deterministic_fail_with_error_after_first_test(isolated_env):
    """Test that non-AssertionError exceptions stop execution after first run."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=4)
    def test_flaky():
        call_count["count"] += 1
        print(f"CALL_COUNT={call_count['count']}")
        # Always fails with KeyError
        assert call_count["incorrect_key"] in [1, 3], f'Expected: {1, 3}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-vvv", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)

    # Test should fail immediately (not run all 5 times)
    assert proc.returncode != 0, (
        "Test should fail with KeyError\n"
        + "STDOUT:\n"
        + stdout
        + "\nSTDERR:\n"
        + proc.stderr
    )

    # Verify call_count only incremented once (test only ran once)
    assert (
        "CALL_COUNT=1" in stdout
    ), f"Expected 'CALL_COUNT=1' in output\n{stdout}"
    assert (
        "CALL_COUNT=2" not in stdout
    ), f"Expected NO 'CALL_COUNT=2' in output (should stop after first run)\n{stdout}"

    # Should show summary with 1 run
    assert (
        "0 out of 1 runs passed" in stdout
    ), f"Expected '0 out of 1 runs passed' in summary\n{stdout}"


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_deterministic_fail_with_error_verbosity_level_2(isolated_env):
    """Test that KeyError details are shown in run-by-run output."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=4)
    def test_flaky():
        call_count["count"] += 1
        # Always fails with KeyError
        assert call_count["incorrect_key"] in [1, 3], f'Expected: {1, 3}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-vv", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "FAILED (0/1)" in stdout, stdout
    assert "KeyError" in stdout or "KeyError" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_deterministic_fail_with_error_verbosity_level_1(isolated_env):
    """Test that KeyError details are shown in run-by-run output."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=4)
    def test_flaky():
        call_count["count"] += 1
        # Always fails with KeyError
        assert call_count["incorrect_key"] in [1, 3], f'Expected: {1, 3}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "(0/1)" in stdout, stdout
    assert "KeyError" in stdout or "KeyError" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_deterministic_fail_with_error_verbosity_level_1(isolated_env):
    """Test errors other than AssertionError cause failure even after some tries."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=1)
    def test_flaky():
        call_count["count"] += 1
        # Fail with RuntimeError after the first two runs.
        if call_count["count"] > 2:
            raise RuntimeError("Deliberate RuntimeError after two runs")
        assert call_count["count"] in [1, 2], f'Expected: {1, 2}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "(2/3)" in stdout, stdout
    assert "RuntimeError" in stdout or "RuntimeError" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_deterministic_fail_with_error_verbosity_level_2(isolated_env):
    """Test errors other than AssertionError cause failure even after some tries."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    call_count = {"count": 0}
    @pytest.mark.repeated(times=5, threshold=1)
    def test_flaky():
        call_count["count"] += 1
        # Fail with RuntimeError after the first two runs.
        if call_count["count"] > 2:
            raise RuntimeError("Deliberate RuntimeError after two runs")
        assert call_count["count"] in [1, 2], f'Expected: {1, 2}, Got: {call_count["count"]}'
    """
    )
    test_file = base / "test_sample.py"
    test_file.write_text(PYTEST_CODE)

    proc = subprocess.run(
        ["pytest", "-v", str(test_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    stdout = proc.stdout
    print(stdout)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    assert "FAILED (2/3)" in stdout, stdout
    assert "RuntimeError" in stdout or "RuntimeError" in proc.stderr, stdout
