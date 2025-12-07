import subprocess
from textwrap import dedent

import pytest


@pytest.mark.depends(on=["base_repeated_marker_test"])
def test_bayesian_test(isolated_env, create_test_file_and_run):
    """Test Bayesian hypothesis testing with posterior_threshold_probability parameter."""
    pytest_code = dedent(
        """
    import pytest
    @pytest.mark.repeated(times=10, posterior_threshold_probability=0.95, success_rate_threshold=0.7)
    def test_always_passes():
        assert True
    """
    )

    proc = create_test_file_and_run(isolated_env, pytest_code)

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


@pytest.mark.depends(on=["base_repeated_marker_test"])
def test_bayesian_test_missing_kwarg_success_rate_threshold(
    isolated_env, create_test_file_and_run
):
    """Test that Bayesian testing raises error when success_rate_threshold is missing."""
    pytest_code = dedent(
        """
    import pytest
    @pytest.mark.repeated(times=10, posterior_threshold_probability=0.95)
    def test_always_passes():
        assert True
    """
    )

    proc = create_test_file_and_run(isolated_env, pytest_code)

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


@pytest.mark.depends(on=["base_repeated_marker_test"])
def test_bayesian_test_with_custom_prior(
    isolated_env, create_test_file_and_run
):
    """Test Bayesian hypothesis testing with custom prior parameters."""
    pytest_code = dedent(
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

    proc = create_test_file_and_run(isolated_env, pytest_code)

    stdout = proc.stdout
    print(stdout)
    # With informative prior (alpha=10, beta=10) centered at 0.5,
    # a small number of observations won't drastically change the posterior
    # Should show posterior probability in output
    assert (
        "P(p>0.5|tests)=" in stdout or "P(p>0.5|tests)=" in proc.stderr
    ), stdout


@pytest.mark.depends(on=["base_repeated_marker_test"])
def test_bayesian_test_with_alternative_prior_names(
    isolated_env, create_test_file_and_run
):
    """Test Bayesian hypothesis testing with prior_passes and prior_failures."""
    pytest_code = dedent(
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

    proc = create_test_file_and_run(isolated_env, pytest_code)

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
