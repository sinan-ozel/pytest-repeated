import subprocess
from textwrap import dedent

import pytest


@pytest.mark.depends(on=["base_repeated_marker_test"])
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


def test_z_test_statistical_determinsitic_fail_in_otherwise_successful_case(isolated_env):
    """Test statistical hypothesis testing with deterministic random seed."""
    base, env = isolated_env

    PYTEST_CODE = dedent(
        """
    import pytest
    import random

    random.seed(1729)

    call_count = {"count": 0}

    @pytest.mark.repeated(null=0.9, ci=0.95, n=200)
    def test_succeed_95_percent():
        call_count["count"] += 1
        if call_count["count"] > 60:
            raise RuntimeError("Deliberate RuntimeError after 60 runs")
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
    # Note that the p-value is high, because we wound up getting only 61 samples.
    # TODO: Fix and change the sample size. The last test fails for a deterministic reason and does not count.
    assert "(p=0.848" in stdout or "(p=0.848" in proc.stderr, stdout
