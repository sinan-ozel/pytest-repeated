# Basic Usage: Threshold-Based Testing

The simplest way to use pytest-repeated is with a threshold: "Pass if X out of Y tests succeed."

## Core Parameters

### `times` or `n`

Number of times to repeat the test. These are **aliases** - use whichever you prefer:

```python
@pytest.mark.repeated(times=20, threshold=19)  # Using 'times'
@pytest.mark.repeated(n=20, threshold=19)      # Using 'n' - exactly the same
```

### `threshold`

Minimum number of passes required for the test to succeed overall.

```python
@pytest.mark.repeated(times=100, threshold=95)
# Passes if ≥95 out of 100 runs succeed
```

## Examples

### Testing LLM Outputs

```python
import pytest

@pytest.mark.repeated(times=50, threshold=48)
def test_llm_math_question():
    """LLM should correctly answer '2+2' at least 48 out of 50 times."""
    response = call_llm("What is 2+2?")
    assert response.strip() == "4"
```

### Testing ML Model Predictions

```python
@pytest.mark.repeated(times=1000, threshold=900)
def test_model_accuracy():
    """Model should predict correctly at least 90% of the time."""
    sample = get_random_test_sample()
    prediction = model.predict(sample.features)
    assert prediction == sample.label
```

### Testing Randomized Algorithms

```python
@pytest.mark.repeated(n=200, threshold=190)
def test_monte_carlo_simulation():
    """Monte Carlo approximation should be within 5% at least 95% of the time."""
    result = monte_carlo_pi_estimate(iterations=10000)
    assert abs(result - 3.14159) < 0.16  # 5% tolerance
```

## When to Use Basic Threshold Testing

✅ **Best for:**
- Quick validation without statistical formalism
- Teams without strong statistics background
- Clear, easy-to-communicate requirements ("95 out of 100")
- Rapid prototyping and iteration

❌ **Consider alternatives when:**
- You need statistical rigor for formal testing ([Frequentist](frequentist.md))
- You have prior beliefs to incorporate ([Bayesian](bayesian.md))
- Stakeholders need confidence intervals or p-values

## Calculating Thresholds

A common approach is to set threshold based on desired success rate:

```python
# For 95% success rate with 100 runs:
@pytest.mark.repeated(times=100, threshold=95)

# For 99% success rate with 50 runs:
@pytest.mark.repeated(times=50, threshold=50)  # Actually 100%, might want threshold=49

# For 90% success rate with 1000 runs:
@pytest.mark.repeated(times=1000, threshold=900)
```

!!! warning "Edge Case"
    Setting `threshold` equal to `times` means **all runs must pass** - the test becomes fully deterministic. Consider if statistical testing is needed in this case.

## Error Handling

pytest-repeated distinguishes between:

1. **AssertionError** - Expected test failures, counted toward threshold
2. **Other exceptions** - Real bugs (TypeError, ValueError, etc.)

When a non-AssertionError occurs:
- Test execution **stops immediately**
- Test **fails** regardless of threshold
- Full error traceback is shown

Example:

```python
@pytest.mark.repeated(times=100, threshold=95)
def test_with_bug():
    result = risky_function()  # Might raise ValueError
    assert result > 0

# If risky_function() raises ValueError on run 10:
# - Runs 1-9 are counted
# - Run 10 raises ValueError -> test stops and FAILS
# - Runs 11-100 never execute
# - Even if 9/9 passed, the test FAILS due to the ValueError
```

This ensures bugs aren't masked by statistical thresholds.

## Performance Optimization

### Early Stopping with `stop_if_threshold_met`

For expensive tests, you can stop execution as soon as the threshold is met:

```python
@pytest.mark.repeated(times=1000, threshold=10, stop_if_threshold_met=True)
def test_expensive_operation():
    """Stops at 10 passes instead of running all 1000 times."""
    result = expensive_operation()
    assert result.is_valid()
```

**When to use:**
- Tests with expensive operations (API calls, model inference, database queries)
- You only need to verify a minimum number of successes
- Time/cost savings are important

**Default behavior** (`stop_if_threshold_met=False`):
- Runs all iterations to provide more information
- Useful when you want to know the actual success rate, not just that threshold was met

**Example comparison:**

```python
# Without early stopping - runs all 100 times
@pytest.mark.repeated(times=100, threshold=5)
def test_slow_api():
    response = slow_api_call()
    assert response.success

# With early stopping - stops at 5 passes (much faster!)
@pytest.mark.repeated(times=100, threshold=5, stop_if_threshold_met=True)
def test_slow_api_optimized():
    response = slow_api_call()
    assert response.success
```

!!! note "Compatibility"
    `stop_if_threshold_met` is **only compatible with threshold mode**. It cannot be used with frequentist (`H0`/`null`) or Bayesian (`posterior_threshold_probability`) approaches, as those require all runs to compute statistics accurately.

## Next Steps

- [Frequentist Testing](frequentist.md) - Add hypothesis testing rigor
- [Bayesian Testing](bayesian.md) - Incorporate prior knowledge
- [Parameters Reference](../reference/parameters.md) - Full parameter details
- [Decorator Placement](decorator-placement.md) - Using with other pytest markers
