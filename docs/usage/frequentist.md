# Frequentist Testing: Null Hypothesis Approach

For teams with statistical training, pytest-repeated supports **null hypothesis testing** with confidence intervals.

## Overview

Instead of setting a simple threshold, you:

1. Define a **null hypothesis** (H₀): "The code's true success rate is ≤ X%"
2. Set a **confidence level**: "I want to be 95% confident when rejecting H₀"
3. Run the test multiple times
4. **Reject H₀** if the lower bound of the confidence interval exceeds the null hypothesis

The test **passes** when we can confidently reject the null hypothesis (i.e., prove the code performs better than the threshold).

## Core Parameters

### `H0` or `null`

The null hypothesis proportion - the baseline success rate you want to exceed. These are **aliases**:

```python
@pytest.mark.repeated(times=100, H0=0.8, ci=0.95)     # Using 'H0'
@pytest.mark.repeated(times=100, null=0.8, ci=0.95)   # Using 'null' - exactly the same
```

### `ci`

Confidence level (0 to 1) for the confidence interval. Common values:

- `0.90` - 90% confidence
- `0.95` - 95% confidence (recommended)
- `0.99` - 99% confidence (very strict)

## How It Works

pytest-repeated uses the **Wilson score interval** to construct a confidence interval for the true success rate:

1. Run the test `times` iterations
2. Calculate observed success rate: passes / times
3. Construct Wilson score confidence interval at level `ci`
4. Check if the **lower bound** > `H0` (null hypothesis)

**Test passes** if: `lower_bound_of_CI > H0`
**Test fails** if: `lower_bound_of_CI ≤ H0`

## Examples

### LLM Response Quality

```python
import pytest

@pytest.mark.repeated(times=100, H0=0.90, ci=0.95)
def test_llm_provides_accurate_answer():
    """
    Null hypothesis: LLM accuracy ≤ 90%
    We reject H0 (test passes) if we're 95% confident accuracy > 90%
    """
    response = call_llm("What is the capital of France?")
    assert "Paris" in response
```

If 96 out of 100 runs pass, the 95% CI might be [0.902, 0.987]. Since 0.902 > 0.90, we reject H₀ and the test passes.

### ML Model Performance

```python
@pytest.mark.repeated(n=200, null=0.85, ci=0.99)
def test_model_exceeds_baseline():
    """
    Null hypothesis: Model accuracy ≤ 85%
    We need 99% confidence that accuracy > 85%
    """
    sample = get_random_validation_sample()
    prediction = model.predict(sample.features)
    assert prediction == sample.label
```

### A/B Testing New Algorithm

```python
@pytest.mark.repeated(times=500, H0=0.75, ci=0.95)
def test_new_algorithm_beats_old():
    """
    Null hypothesis: New algorithm success rate ≤ 75% (old algorithm's rate)
    Test passes if we're 95% confident new algorithm > 75%
    """
    result = new_algorithm(get_test_case())
    expected = ground_truth(get_test_case())
    assert result == expected
```

## When to Use Frequentist Testing

✅ **Best for:**
- Teams with statistical/scientific background
- Need for formal hypothesis testing
- Quality assurance requiring statistical rigor
- Publishing results that need confidence intervals
- Regulatory or compliance requirements

❌ **Consider alternatives when:**
- Team lacks statistics training ([Basic](basic.md) threshold is simpler)
- You have prior knowledge to incorporate ([Bayesian](bayesian.md))
- Simple pass/fail communication is sufficient

## Choosing Parameters

### Confidence Level (`ci`)

Higher confidence = stricter test = need more passes:

```python
# 95% confidence (standard in most sciences)
@pytest.mark.repeated(times=100, H0=0.8, ci=0.95)

# 99% confidence (very strict, need strong evidence)
@pytest.mark.repeated(times=100, H0=0.8, ci=0.99)

# 90% confidence (less strict, easier to pass)
@pytest.mark.repeated(times=100, H0=0.8, ci=0.90)
```

### Sample Size (`times`)

More repetitions = narrower confidence interval = more precise:

```python
# Small sample - wide CI, less precise
@pytest.mark.repeated(times=50, H0=0.85, ci=0.95)

# Medium sample - moderate CI
@pytest.mark.repeated(times=200, H0=0.85, ci=0.95)

# Large sample - narrow CI, very precise
@pytest.mark.repeated(times=1000, H0=0.85, ci=0.95)
```

### Null Hypothesis (`H0`)

Set based on your minimum acceptable performance:

```python
# High bar - code must be very reliable
@pytest.mark.repeated(times=100, H0=0.95, ci=0.95)

# Moderate bar - code should work most of the time
@pytest.mark.repeated(times=100, H0=0.80, ci=0.95)

# Low bar - code just needs to work more often than not
@pytest.mark.repeated(times=100, H0=0.60, ci=0.95)
```

## Statistical Details

### Wilson Score Interval

pytest-repeated uses the **Wilson score interval** rather than the normal approximation. The Wilson interval:

- ✅ Works well even with small sample sizes
- ✅ Never produces invalid intervals (outside [0,1])
- ✅ Provides better coverage than normal approximation
- ✅ Recommended by statisticians for proportion confidence intervals

### One-Sided Test

The test is **one-sided** - we only check if performance exceeds H₀, not whether it falls below some upper bound.

- If `lower_CI_bound > H0`: **Reject H₀** → test **passes**
- If `lower_CI_bound ≤ H0`: **Fail to reject H₀** → test **fails**

## Interpretation

When the test **passes**:
> "We are [ci×100]% confident that the true success rate exceeds [H0×100]%"

When the test **fails**:
> "We cannot be [ci×100]% confident that the true success rate exceeds [H0×100]%"

Example with `times=100, H0=0.90, ci=0.95`:
- **Pass**: "We are 95% confident the true success rate exceeds 90%"
- **Fail**: "We cannot be 95% confident the success rate exceeds 90%"

## Error Handling

Like all pytest-repeated modes, frequentist testing stops immediately on non-AssertionErrors:

```python
@pytest.mark.repeated(times=100, H0=0.85, ci=0.95)
def test_with_potential_bug():
    result = risky_function()  # Might raise ValueError
    assert result > threshold

# If ValueError occurs on run 15:
# - Test stops immediately
# - Test FAILS regardless of H0/CI
# - Statistical evaluation is not performed
```

## Next Steps

- [Bayesian Testing](bayesian.md) - Incorporate prior knowledge
- [Basic Testing](basic.md) - Simpler threshold approach
- [Parameters Reference](../reference/parameters.md) - Full parameter details
- [Decorator Placement](decorator-placement.md) - Using with other pytest markers
