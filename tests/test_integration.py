import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

PYTEST_CODE = """import pytest

@pytest.mark.repeated(times=5, threshold=2)
def test_flaky():
    import random
    return random.choice([True, False])
"""


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


def test_repeated_marker_behavior(isolated_env):
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(times=5, threshold=2)
    def test_flaky():
        import random
        return random.choice([True, False])
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
def test_threshold_fail_with_error_verbosity_level_3(isolated_env):
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
    assert "FAILED (0/5)" in stdout or "FAILED (0/5)" in proc.stderr, stdout
    assert (
        "'incorrect_key'" in stdout or "'incorrect_key'" in proc.stderr
    ), stdout
    assert "KeyError" in stdout or "KeyError" in proc.stderr, stdout
    assert (
        "Run-by-run results:" in stdout or "Run-by-run results:" in proc.stderr
    ), stdout


def test_z_test(isolated_env):
    """Test statistical hypothesis testing with H0 parameter."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(H0=0.9, ci=0.95, times=3)
    def test_always_passes():
        assert True
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
    # With 3/3 passes and H0=0.9, p-value will be ~0.28, which fails to reject H0
    # so the test should FAIL
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show p-value in output
    assert "(p=" in stdout or "(p=" in proc.stderr, stdout
    # Should have warnings about exact binomial test usage
    assert "exact_binomial" in stdout or "exact_binomial" in proc.stderr, stdout


def test_threshold_pass_equal(isolated_env):
    """Test statistical hypothesis testing with H0 parameter."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(H0=0.9, ci=0.95, n=3)
    def test_always_passes():
        assert True
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
    # With 3/3 passes and H0=0.9, p-value will be ~0.28, which fails to reject H0
    # so the test should FAIL
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show p-value in output
    assert "(p=0.729" in stdout or "(p=0.729" in proc.stderr, stdout
    # Should have warnings about exact binomial test usage
    assert "exact_binomial" in stdout or "exact_binomial" in proc.stderr, stdout


def test_z_test_alternative_kwargs(isolated_env):
    """Test statistical hypothesis testing with H0 parameter using alternative kwarg names."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(null=0.9, ci=0.95, n=3)
    def test_always_passes():
        assert True
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
    # With 3/3 passes and null=0.9, p-value will be 0.729, which fails to reject H0
    # so the test should FAIL
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show p-value in output
    assert "(p=" in stdout or "(p=" in proc.stderr, stdout
    # Should have warnings about exact binomial test usage
    assert "exact_binomial" in stdout or "exact_binomial" in proc.stderr, stdout


def test_z_test_statistical_fail_to_reject(isolated_env):
    """Test statistical hypothesis testing with deterministic random seed."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    import random

    random.seed(1729)

    @pytest.mark.repeated(null=0.9, ci=0.95, n=10)
    def test_succeed_50_percent():
        assert random.random() < 0.5
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
    print("=" * 80)
    print("STDERR:")
    print(proc.stderr)
    print("=" * 80)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show p-value in output
    assert "(p=0.998" in stdout or "(p=0.998" in proc.stderr, stdout


def test_z_test_statistical_reject_and_pass(isolated_env):
    """Test statistical hypothesis testing with deterministic random seed."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    import random

    random.seed(1729)

    @pytest.mark.repeated(null=0.9, ci=0.95, n=200)
    def test_succeed_95_percent():
        assert random.random() < 0.95
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
    print("=" * 80)
    print("STDERR:")
    print(proc.stderr)
    print("=" * 80)
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show p-value in output
    assert "(p=0.039" in stdout or "(p=0.039" in proc.stderr, stdout


def test_z_test_statistical_reject_with_type2_error(isolated_env):
    """Test statistical hypothesis testing with deterministic random seed."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    import random

    random.seed(1729)

    @pytest.mark.repeated(null=0.9, ci=0.95, n=150)
    def test_succeed_95_percent():
        assert random.random() < 0.95
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
    print("=" * 80)
    print("STDERR:")
    print(proc.stderr)
    print("=" * 80)
    assert proc.returncode != 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show p-value in output
    assert "(p=0.067" in stdout or "(p=0.067" in proc.stderr, stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_bayesian_test(isolated_env):
    """Test Bayesian hypothesis testing with posterior_threshold_probability parameter."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(times=10, posterior_threshold_probability=0.95, success_rate_threshold=0.7)
    def test_always_passes():
        assert True
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
    # With 10/10 passes, posterior probability should be very high
    # so the test should PASS
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show posterior probability in output
    assert (
        "P(p>0.7|tests)=" in stdout or "P(p>0.7|tests)=" in proc.stderr
    ), stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_bayesian_test_missing_kwarg_success_rate_threshold(isolated_env):
    """Test that Bayesian testing raises error when success_rate_threshold is missing."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(times=10, posterior_threshold_probability=0.95)
    def test_always_passes():
        assert True
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
    stderr = proc.stderr
    print(stdout)
    print("=" * 80)
    print("STDERR:")
    print(stderr)
    print("=" * 80)

    # Should fail with a clear error message
    assert proc.returncode != 0, "STDOUT:\n" + stdout + "\nSTDERR:\n" + stderr
    # Should contain the error message about missing success_rate_threshold
    combined_output = stdout + stderr
    assert (
        "success_rate_threshold is required" in combined_output
    ), combined_output


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_bayesian_test_with_custom_prior(isolated_env):
    """Test Bayesian hypothesis testing with custom prior parameters."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(
        times=5,
        posterior_threshold_probability=0.90,
        success_rate_threshold=0.5,
        prior_alpha=10,
        prior_beta=10
    )
    def test_some_passes():
        import random
        random.seed(42)
        assert random.random() < 0.6
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
    # With informative prior (alpha=10, beta=10) centered at 0.5,
    # a small number of observations won't drastically change the posterior
    # Should show posterior probability in output
    assert (
        "P(p>0.5|tests)=" in stdout or "P(p>0.5|tests)=" in proc.stderr
    ), stdout


@pytest.mark.depends(on=["test_repeated_marker_behavior"])
def test_bayesian_test_with_alternative_prior_names(isolated_env):
    """Test Bayesian hypothesis testing with prior_passes and prior_failures."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    @pytest.mark.repeated(
        times=10,
        posterior_threshold_probability=0.95,
        success_rate_threshold=0.5,
        prior_passes=5,
        prior_failures=5
    )
    def test_always_passes():
        assert True
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
    # With 10/10 passes and a prior centered at 0.5, should still have very high posterior
    assert proc.returncode == 0, (
        "STDOUT:\n" + stdout + "\nSTDERR:\n" + proc.stderr
    )
    # Should show posterior probability in output
    assert (
        "P(p>0.5|tests)=" in stdout or "P(p>0.5|tests)=" in proc.stderr
    ), stdout
