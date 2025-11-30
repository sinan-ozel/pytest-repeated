import math
import warnings

import pytest


def one_sided_proportion_test(r, n, N, alpha=0.05):
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


def _apply_statistical_test(report, passes, total, null, ci):
    """Apply statistical hypothesis test to determine test outcome.

    Args:
        report: The test report object to update
        passes: Number of passing runs
        total: Total number of runs
        null: Null hypothesis proportion (H0)
        ci: Confidence interval level
    """
    test_result = one_sided_proportion_test(r=null, n=passes, N=total, alpha=1 - ci)
    p_value = test_result["p_value"]

    if test_result["reject"]:
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
    threshold = marker.kwargs.get("threshold", 1)
    null = marker.kwargs.get("H0") or marker.kwargs.get("null")

    # Determine actual times and n
    if times is None and n is None:
        times = 1
        n = times
    elif times is None:
        times = n
    elif n is None:
        n = times

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

    for i in range(times):
        try:
            item.runtest()  # run the actual test function
            passes += 1
            run_details.append((i + 1, "PASS", None))
        except Exception as e:
            last_exception = e
            run_details.append((i + 1, "FAIL", str(e)))

    # Store summary for the report stage
    item._repeated_summary = (passes, times)
    item._repeated_run_details = run_details

    # Determine final result
    if passes < threshold:
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
                        error_preview = (
                            error[:80] + "..."
                            if error and len(error) > 80
                            else error
                        )
                        details_lines.append(
                            f"  Run {run_num}: {status} - {error_preview}"
                        )
                report.sections.append(
                    ("repeated details", "\n".join(details_lines))
                )

        # Get threshold to determine if test should pass
        marker = item.get_closest_marker("repeated")
        times = marker.kwargs.get("times")
        n = marker.kwargs.get("n")
        threshold = marker.kwargs.get("threshold", 1) if marker else 1
        null = marker.kwargs.get("H0")
        if null is None:
            null = marker.kwargs.get("null")
        ci = marker.kwargs.get("ci", 0.95)

        # Determine actual times and n
        if times is None and n is None:
            times = 1
            n = times
        elif times is None:
            times = n
        elif n is None:
            n = times

        if null is not None:
            # Use statistical test to determine pass/fail
            _apply_statistical_test(report, passes, total, null, ci)
        else:
            # Override outcome based on threshold
            if passes >= threshold:
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

    return report


def pytest_report_teststatus(report, config):
    """Customize terminal output for repeated tests."""
    if hasattr(report, "_repeated_summary") and report.when == "call":
        passes, total = report._repeated_summary

        # short progress character: use '+' for full pass, '.' otherwise
        short = "+" if passes == total else "."

        # verbose string shown in -v/-vv
        if hasattr(report, "_p_value"):
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
                        error_preview = (
                            error[:80] + "..."
                            if error and len(error) > 80
                            else error
                        )
                        tw.line(f"  Run {run_num}: {status} - {error_preview}")
