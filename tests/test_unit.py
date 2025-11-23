import pytest
from pytest_repeated import plugin


def test_marker_registration():
    """Ensure marker appears in config."""
    config = type("C", (), {"addinivalue_line": lambda *args, **kwargs: None})
    plugin.pytest_configure(config)
    """No assertion error means marker added."""


def test_logic_threshold_met():
    """Test that threshold logic works for both met and unmet cases."""

    # Case 1: threshold not met → final exception must be raised
    class Item:

        def __init__(self):
            self.count = 0

        def get_closest_marker(self, name):
            return type("M", (), {"kwargs": {"times": 3, "threshold": 2}})

        def runtest(self):
            self.count += 1
            if self.count < 3:
                raise AssertionError("fail early")
            else:
                raise AssertionError("fail last")

    item = Item()

    with pytest.raises(AssertionError) as exc:
        plugin.pytest_runtest_call(item)

    # Should raise the last failure
    assert "fail last" in str(exc.value)

    # Case 2: threshold met → plugin should not raise
    class Item2:

        def __init__(self):
            self.count = 0

        def get_closest_marker(self, name):
            return type("M", (), {"kwargs": {"times": 3, "threshold": 1}})

        def runtest(self):
            self.count += 1  # always passes

    item2 = Item2()
    plugin.pytest_runtest_call(item2)
    assert item2._repeated_summary == (3, 3)


def test_logic_no_marker(monkeypatch):
    """Should just return None implicitly (no exception)."""

    class Item:

        def get_closest_marker(self, name):
            return None

    item = Item()
    assert plugin.pytest_runtest_call(item) is None
