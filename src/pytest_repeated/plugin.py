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
                        error_preview = error[:80] + "..." if error and len(error) > 80 else error
                        details_lines.append(f"  Run {run_num}: {status} - {error_preview}")
                report.sections.append(("repeated details", "\n".join(details_lines)))

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
        verbose = f"PASSED ({passes}/{total})" if report.outcome == "passed" else f"FAILED ({passes}/{total})"

        # Return correct tuple shape
        return (report.outcome, short, verbose)
    return None  # use default


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_logreport(report):
    """Print detailed run results for -vvv."""
    outcome = yield
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
                        error_preview = error[:80] + "..." if error and len(error) > 80 else error
                        tw.line(f"  Run {run_num}: {status} - {error_preview}")
