import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "repeated(times, threshold): run a test multiple times and pass if threshold met"
    )


def pytest_runtest_call(item):
    marker = item.get_closest_marker("repeated")
    if marker is None:
        return  # run normally

    times = marker.kwargs.get("times", 1)
    threshold = marker.kwargs.get("threshold", 1)

    # Collect results
    passes = 0
    last_exception = None

    for i in range(times):
        try:
            item.runtest()  # run the actual test function
        except Exception as e:
            last_exception = e
        else:
            passes += 1

    # Store summary for the report stage
    item._repeated_summary = (passes, times)

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

        # Get threshold to determine if test should pass
        marker = item.get_closest_marker("repeated")
        threshold = marker.kwargs.get("threshold", 1) if marker else 1

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

    return report


def pytest_report_teststatus(report, config):
    """Customize terminal output for repeated tests."""
    if hasattr(report, "_repeated_summary") and report.when == "call":
        passes, total = report._repeated_summary

        # short progress character: use '+' for full pass, '.' otherwise
        short = "+" if passes == total else "."

        # verbose string shown in -v/-vv
        verbose = f"PASSED ({passes}/{total})" if report.outcome == "passed" else f"FAILED ({passes}/{total})"

        # Return correct tuple shape
        return (report.outcome, short, verbose)
    return None  # use default
