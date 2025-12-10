# Quick Start

Get started with statistical testing in under a minute!

## Minimal Example

Create a test file `test_example.py`:

```python
import pytest
import random

@pytest.mark.repeated(times=10, threshold=9)
def test_random_value():
    """Test passes if at least 9 out of 10 runs succeed."""
    value = random.random()
    assert value > 0.1  # Passes ~90% of the time
```

## Run the Test

```bash
pytest test_example.py
```

You'll see output showing:
- Number of runs attempted
- Number of passes and failures
- Overall test result

## Verbose Output

For detailed run-by-run results:

```bash
pytest test_example.py -vvv
```

At verbosity level 3 (`-vvv`), you'll see:
- Each individual run attempt
- Full error messages (not truncated)
- Statistical evaluation results

## What's Happening?

1. **Repetition**: The test runs 10 times
2. **Collection**: pytest-repeated tracks passes/failures
3. **Evaluation**: The test passes overall if ≥9 out of 10 runs succeed
4. **Reporting**: Results display in pytest's standard output

## Non-AssertionErrors

If a run raises anything other than `AssertionError` (like `TypeError`, `ValueError`, etc.), pytest-repeated:

1. **Stops immediately** - no more runs are attempted
2. **Fails the test** - regardless of threshold
3. **Shows the error** - full traceback is displayed

This ensures real bugs aren't hidden by statistical thresholds.

## Next Steps

- [Basic Usage](usage/basic.md) - Learn threshold-based testing in detail
- [Frequentist](usage/frequentist.md) - Null hypothesis testing approach
- [Bayesian](usage/bayesian.md) - Posterior probability approach
- [Parameters Reference](reference/parameters.md) - All available options
