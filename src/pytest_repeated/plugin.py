"""
pytest-mark ‘repeated’: run a test N times and pass if threshold of passes is met.
"""

import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "repeated(times, threshold): run a test multiple times and pass if threshold met"
    )

def pytest_runtest_call(item):
    marker = item.get_closest_marker("repeated")
    if marker is None:
        return

    times = marker.kwargs.get("times", 1)
    threshold = marker.kwargs.get("threshold", 1)

    passes = 0
    last_exc = None

    for _ in range(times):
        try:
            item.runtest()
        except Exception as e:
            last_exc = e
        else:
            passes += 1

    item._repeated_summary = (passes, times)

    if passes >= threshold:
        return
    raise last_exc

def pytest_runtest_makereport(item, call):
    report = pytest.TestReport.from_item_and_call(item, call)
    if hasattr(item, "_repeated_summary") and report.when == "call":
        passes, total = item._repeated_summary
        if report.passed:
            report.shortrepr = f"PASSED ({passes}/{total})"
        else:
            report.shortrepr = f"FAILED ({passes}/{total})"
    return report
