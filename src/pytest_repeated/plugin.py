import math
import sys
import warnings
from io import StringIO

import pytest
from mpmath import betainc


def bayes_one_sided_proportion_test(
    r,
    n,
    N,
    prior_successes=1,
    prior_failures=1,
    posterior_threshold_probability=0.95,
) -> dict:
    """Perform a one-sided Bayesian test for a population proportion.

    Uses Beta-Binomial conjugate prior to compute posterior probability
    that the true proportion p > r.

    Args:
        r (float): threshold proportion (0 <= r <= 1)
        n (int): number of successes observed (0 <= n <= N)
        N (int): total number of trials (N > 0)
        prior_successes (float): prior pseudo-count for successes (default 1, uninformative)
        prior_failures (float): prior pseudo-count for failures (default 1, uninformative)
        posterior_threshold_probability (float): credible threshold (default 0.95)

    Returns:
        dict: {
            "posterior_prob": float,  # P(p > r | data)
            "passes": bool,            # whether posterior_prob >= threshold
            "alpha": float,            # posterior Beta parameter
            "beta": float,             # posterior Beta parameter
        }
    """
    # Posterior parameters (Beta conjugate update)
    alpha = prior_successes + n
    beta = prior_failures + (N - n)

    # Posterior P(p > r) = 1 - F_Beta(r; alpha, beta)
    posterior_cdf = betainc(alpha, beta, 0, r, regularized=True)
    posterior_prob = float(1 - posterior_cdf)  # convert from mpmath to float

    return {
        "posterior_prob": posterior_prob,
        "passes": posterior_prob >= posterior_threshold_probability,
        "alpha": alpha,
        "beta": beta,
    }


def one_sided_proportion_test(r, n, N, alpha=0.05) -> dict:
    """Perform a one-sided hypothesis test for a population proportion.

    Uses exact binomial test for small samples (N < 30 or N*r*(1-r) < 10),
    and normal approximation for larger samples.

    H0: p <= r
    H1: p > r

    Args:
        r (float): hypothesized proportion under null (0 <= r <= 1)
        n (int): number of successes observed (0 <= n <= N)
        N (int): total number of trials (N > 0)
        alpha (float): significance level for the test (default 0.05)

    Returns:
        dict: {"p_value": float, "reject": bool, "p_hat": float, "method": str}

    Raises:
        ValueError: if input parameters are out of bounds
    """
    if not (0 <= r <= 1):
        raise ValueError("r must be in [0, 1]")
    if not (0 <= n <= N):
        raise ValueError("n must be in [0, N]")
    if N == 0:
        raise ValueError("N must be > 0")

    # Observed proportion
    p_hat = n / N

    # Handle edge cases for r = 0 or r = 1
    if r == 0:
        # H0: p <= 0 means any n>0 rejects immediately
        return {
            "p_value": 0.0 if n > 0 else 1.0,
            "reject": (n > 0),
            "p_hat": p_hat,
            "method": "exact",
        }
    if r == 1:
        # H0: p <= 1 is always true unless we need perfect success
        return {
            "p_value": 1.0 if n < N else 0.0,
            "reject": False,
            "p_hat": p_hat,
            "method": "exact",
        }

    # Decide which test to use based on sample size
    use_exact = N < 30 or N * r * (1 - r) < 10

    if use_exact:
        # Exact binomial test
        # P-value = P(X >= n | X ~ Binomial(N, r))
        # = sum_{k=n}^{N} C(N,k) * r^k * (1-r)^(N-k)

        # Use log probabilities to avoid overflow
        from math import comb, exp, log

        # Compute log(P(X = k)) for k from n to N
        log_probs = []
        for k in range(n, N + 1):
            # log(C(N,k) * r^k * (1-r)^(N-k))
            log_prob = log(comb(N, k)) + k * log(r) + (N - k) * log(1 - r)
            log_probs.append(log_prob)

        # Use log-sum-exp trick for numerical stability
        max_log_prob = max(log_probs)
        p_value = sum(exp(lp - max_log_prob) for lp in log_probs) * exp(
            max_log_prob
        )

        # Clamp to [0, 1] due to numerical errors
        p_value = max(0.0, min(1.0, p_value))

        return {
            "p_value": p_value,
            "reject": p_value < alpha,
            "p_hat": p_hat,
            "method": "exact_binomial",
        }
    else:
        # Normal approximation with continuity correction
        # Standard error from null proportion r
        se = math.sqrt(r * (1 - r) / N)

        # Apply continuity correction: use (n - 0.5) instead of n
        # This gives better approximation for discrete -> continuous
        Z = ((n - 0.5) / N - r) / se

        # One-sided p-value: P(Z >= z)
        # For right-tailed test: P(Z >= z) = 1 - Φ(z) = 0.5 * erfc(z/sqrt(2))
        p_value = 0.5 * math.erfc(Z / math.sqrt(2))

        return {
            "p_value": p_value,
            "reject": p_value < alpha,
            "p_hat": p_hat,
            "method": "normal_approximation",
        }


def _apply_statistical_test(report, passes, total, null, ci, item):
    """Apply statistical hypothesis test to determine test outcome.

    Args:
        report: The test report object to update
        passes: Number of passing runs
        total: Total number of runs
        null: Null hypothesis proportion (H0)
        ci: Confidence interval level
        item: The test item (to check for non-AssertionError)
    """
    test_result = one_sided_proportion_test(
        r=null, n=passes, N=total, alpha=1 - ci
    )
    p_value = test_result["p_value"]

    # Check if a non-AssertionError occurred
    has_non_assertion_error = (
        hasattr(item, "_repeated_has_non_assertion_error")
        and item._repeated_has_non_assertion_error
    )

    # Force failure if non-AssertionError occurred, otherwise use test result
    if has_non_assertion_error:
        report.outcome = "failed"
    elif test_result["reject"]:
        report.outcome = "passed"
    else:
        report.outcome = "failed"

    # make outcome text shorter in summary line
    report.shortrepr = f"(p={p_value:.3f})"
    report._p_value = p_value

    # Note which method was used (for transparency)
    method = test_result.get("method", "unknown")
    if total < 30 or total * null * (1 - null) < 10:
        warnings.warn(
            f"Using {method} test with N={total}. "
            f"For more reliable results, consider N >= 30.",
            UserWarning,
            stacklevel=2,
        )


def _apply_bayesian_test(
    report,
    passes,
    total,
    posterior_threshold_probability,
    prior_alpha,
    prior_beta,
    success_rate_threshold,
    item,
):
    """Apply Bayesian hypothesis test to determine test outcome.

    Args:
        report: The test report object to update
        passes: Number of passing runs
        total: Total number of runs
        posterior_threshold_probability: Credible threshold for posterior
        prior_alpha: Prior successes (Beta parameter)
        prior_beta: Prior failures (Beta parameter)
        success_rate_threshold: Minimum success rate to test for (required)
        item: The test item (to check for non-AssertionError)
    """
    if success_rate_threshold is None:
        raise ValueError(
            "success_rate_threshold is required when using posterior_threshold_probability. "
            "Specify the minimum success rate to test against, e.g., "
            "@pytest.mark.repeated(posterior_threshold_probability=0.95, success_rate_threshold=0.5) "
            "This is how many times you want the underlying code to behave as desired."
        )

    # We test if p > success_rate_threshold
    test_result = bayes_one_sided_proportion_test(
        r=success_rate_threshold,
        n=passes,
        N=total,
        prior_successes=prior_alpha,
        prior_failures=prior_beta,
        posterior_threshold_probability=posterior_threshold_probability,
    )
    posterior_prob = test_result["posterior_prob"]

    # Check if a non-AssertionError occurred
    has_non_assertion_error = (
        hasattr(item, "_repeated_has_non_assertion_error")
        and item._repeated_has_non_assertion_error
    )

    # Force failure if non-AssertionError occurred, otherwise use test result
    if has_non_assertion_error:
        report.outcome = "failed"
    elif test_result["passes"]:
        report.outcome = "passed"
    else:
        report.outcome = "failed"

    # make outcome text shorter in summary line
    report.shortrepr = (
        f"(P(p>{success_rate_threshold}|data)={posterior_prob:.3f})"
    )
    report._posterior_prob = posterior_prob
    report._success_rate_threshold = success_rate_threshold


def _resolve_times_and_n(times, n):
    """Resolve times and n parameters, handling None values.

    Args:
        times: Number of times to run the test (or None)
        n: Alternative name for times (or None)

    Returns:
        tuple: (times, n) with None values resolved
    """
    if times is None and n is None:
        times = 1
        n = times
    elif times is None:
        times = n
    elif n is None:
        n = times
    return times, n


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "repeated(times, threshold): run a test multiple times and pass if threshold met",
    )


def pytest_runtest_call(item):
    marker = item.get_closest_marker("repeated")
    if marker is None:
        return  # run normally

    times = marker.kwargs.get("times")
    n = marker.kwargs.get("n")
    threshold = marker.kwargs.get("threshold")
    null = marker.kwargs.get("H0") or marker.kwargs.get("null")
    posterior_threshold_probability = marker.kwargs.get(
        "posterior_threshold_probability"
    )

    # Validate that at most one test method is specified
    test_methods = [threshold, null, posterior_threshold_probability]
    non_none_count = sum(x is not None for x in test_methods)
    if non_none_count > 1:
        raise ValueError(
            "At most one of 'threshold', 'null' (or 'H0'), and "
            "'posterior_threshold_probability' can be specified"
        )

    # Set default threshold if no test method specified
    if non_none_count == 0:
        threshold = 1

    # Determine actual times and n
    times, n = _resolve_times_and_n(times, n)

    # Warn if using statistical test with insufficient trials
    if null is not None and times <= 1:
        warnings.warn(
            f"Statistical test (H0={null}) requires multiple trials. "
            f"Set times > 1 (currently times={times}).",
            UserWarning,
            stacklevel=2,
        )

    # Collect results
    passes = 0
    last_exception = None
    run_details = []

    # Get verbosity level safely
    try:
        verbosity = item.config.option.verbose
    except AttributeError:
        verbosity = 0

    for i in range(times):
        # Capture output from individual runs (unless at high verbosity)
        # This prevents output spam at verbosity level 1-2
        if verbosity >= 3:
            # At -vvv, show all output
            try:
                item.runtest()
                passes += 1
                run_details.append((i + 1, "PASS", None))
            except Exception as e:
                last_exception = e
                run_details.append((i + 1, "FAIL", str(e)))
                # Stop immediately on non-AssertionError exceptions
                if not isinstance(e, AssertionError):
                    break
        else:
            # Suppress output from individual runs
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            try:
                sys.stdout = StringIO()
                sys.stderr = StringIO()
                item.runtest()
                passes += 1
                run_details.append((i + 1, "PASS", None))
            except Exception as e:
                last_exception = e
                run_details.append((i + 1, "FAIL", str(e)))
                # Stop immediately on non-AssertionError exceptions
                if not isinstance(e, AssertionError):
                    break
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

    # Store summary for the report stage
    # Use actual number of runs (len of run_details) instead of planned times
    actual_runs = len(run_details)
    item._repeated_summary = (passes, actual_runs)
    item._repeated_run_details = run_details
    if last_exception is not None:
        item._repeated_last_exception = last_exception
        # Flag if the last exception was NOT an AssertionError
        item._repeated_has_non_assertion_error = not isinstance(
            last_exception, AssertionError
        )

    # For threshold-based tests, raise exception immediately if threshold not met
    # (Statistical and Bayesian tests are evaluated in pytest_runtest_makereport)
    if threshold is not None:
        if passes < threshold and last_exception is not None:
            raise last_exception


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if hasattr(item, "_repeated_summary") and report.when == "call":
        passes, total = item._repeated_summary
        msg = f"{passes} out of {total} runs passed"

        # append section visible under -vv
        report.sections.append(("repeated", msg))

        # Add detailed run-by-run results for -vvv
        if hasattr(item, "_repeated_run_details"):
            config = item.config
            verbosity = config.option.verbose
            if verbosity >= 3:
                details_lines = ["Run-by-run results:"]
                for run_num, status, error in item._repeated_run_details:
                    if status == "PASS":
                        details_lines.append(f"  Run {run_num}: {status}")
                    else:
                        # At -vvv, show full error without truncation
                        details_lines.append(
                            f"  Run {run_num}: {status} - {error}"
                        )
                report.sections.append(
                    ("repeated details", "\n".join(details_lines))
                )

        # Get the decorator kwargs
        marker = item.get_closest_marker("repeated")

        times = marker.kwargs.get("times")
        n = marker.kwargs.get("n")
        times, n = _resolve_times_and_n(times, n)

        threshold = marker.kwargs.get("threshold")
        null = marker.kwargs.get("H0")
        if null is None:
            null = marker.kwargs.get("null")
        ci = marker.kwargs.get("ci", 0.95)
        posterior_threshold_probability = marker.kwargs.get(
            "posterior_threshold_probability"
        )
        prior_alpha = marker.kwargs.get("prior_passes") or marker.kwargs.get(
            "prior_alpha", 1
        )
        prior_beta = marker.kwargs.get("prior_failures") or marker.kwargs.get(
            "prior_beta", 1
        )
        success_rate_threshold = marker.kwargs.get("success_rate_threshold")

        if posterior_threshold_probability is not None:
            # Use Bayesian test to determine pass/fail
            _apply_bayesian_test(
                report,
                passes,
                total,
                posterior_threshold_probability,
                prior_alpha,
                prior_beta,
                success_rate_threshold,
                item,
            )
        elif null is not None:
            # Use statistical test to determine pass/fail
            _apply_statistical_test(report, passes, total, null, ci, item)
        else:
            # Use threshold (default to 1 if not specified)
            if threshold is None:
                threshold = 1

            # Check if a non-AssertionError occurred
            has_non_assertion_error = (
                hasattr(item, "_repeated_has_non_assertion_error")
                and item._repeated_has_non_assertion_error
            )

            # Override outcome based on threshold
            # BUT: if a non-AssertionError occurred, always fail
            if has_non_assertion_error:
                report.outcome = "failed"
            elif passes >= threshold:
                report.outcome = "passed"
            else:
                report.outcome = "failed"

            # make outcome text shorter in summary line
            if passes == total:
                report.shortrepr = f"({passes}/{total})"
            else:
                report.shortrepr = f"({passes}/{total})"

        report._repeated_summary = (passes, total)
        if hasattr(item, "_repeated_run_details"):
            report._repeated_run_details = item._repeated_run_details
            report.config = config
        if hasattr(item, "_repeated_last_exception"):
            report._repeated_last_exception = item._repeated_last_exception
        # if report.outcome == "failed":
        #     if hasattr(report, "_repeated_last_exception"):
        #         raise report._repeated_last_exception

    return report


def pytest_report_teststatus(report, config):
    """Customize terminal output for repeated tests."""
    if hasattr(report, "_repeated_summary") and report.when == "call":
        passes, total = report._repeated_summary

        # short progress character: use '+' for full pass, '.' otherwise
        short = "+" if passes == total else "."

        # verbose string shown in -v/-vv
        if hasattr(report, "_posterior_prob"):
            posterior_prob = report._posterior_prob
            success_rate_threshold = getattr(
                report, "_success_rate_threshold", 0.5
            )
            verbose = (
                f"PASSED (P(p>{success_rate_threshold}|tests)={posterior_prob:.3f})"
                if report.outcome == "passed"
                else f"FAILED (P(p>{success_rate_threshold}|tests)={posterior_prob:.3f})"
            )
        elif hasattr(report, "_p_value"):
            p_value = report._p_value
            verbose = (
                f"PASSED (p={p_value:.3f})"
                if report.outcome == "passed"
                else f"FAILED (p={p_value:.3f})"
            )
        else:
            verbose = (
                f"PASSED ({passes}/{total})"
                if report.outcome == "passed"
                else f"FAILED ({passes}/{total})"
            )

        # Return correct tuple shape
        return (report.outcome, short, verbose)
    return None  # use default


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_logreport(report):
    """Print detailed run results for -vvv."""
    _ = yield
    if hasattr(report, "_repeated_summary") and report.when == "call":
        if hasattr(report, "config"):
            config = report.config
            verbosity = config.option.verbose
            if verbosity >= 3 and hasattr(report, "_repeated_run_details"):
                tw = config.get_terminal_writer()
                tw.line()
                tw.sep("-", "repeated details")
                tw.line("Run-by-run results:")
                for run_num, status, error in report._repeated_run_details:
                    if status == "PASS":
                        tw.line(f"  Run {run_num}: {status}")
                    else:
                        # At -vvv, show full error without truncation
                        tw.line(f"  Run {run_num}: {status} - {error}")
