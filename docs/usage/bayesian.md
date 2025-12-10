# Bayesian Testing: Posterior Probability Approach

For teams that want to incorporate **prior knowledge** into testing, pytest-repeated supports **Bayesian inference** using the Beta-Binomial conjugate prior.

## Overview

Bayesian testing allows you to:

1. Encode **prior beliefs** about your code's success rate (using a Beta distribution)
2. Update those beliefs with **observed test results**
3. Calculate the **posterior probability** that your code meets a performance threshold
4. Pass the test if the posterior probability exceeds a specified level

This approach naturally incorporates uncertainty and prior knowledge into your tests.

## Core Parameters

### `success_rate_threshold`

The minimum success rate you want your code to achieve (0 to 1):

```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,  # Code should succeed ≥85% of the time
    posterior_threshold_probability=0.95
)
```

### `posterior_threshold_probability`

How confident you need to be that `success_rate_threshold` is met (0 to 1):

```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.95  # 95% confidence required
)
```

**Test passes** if: `P(true_rate ≥ success_rate_threshold) ≥ posterior_threshold_probability`

### Prior Parameters: `prior_passes` / `prior_alpha` (aliases)

Represents prior successes in your belief about the code. These are **aliases**:

```python
# Using 'prior_passes'
@pytest.mark.repeated(times=100, prior_passes=8, prior_failures=2, ...)

# Using 'prior_alpha' - exactly the same
@pytest.mark.repeated(times=100, prior_alpha=8, prior_beta=2, ...)
```

Higher values = stronger prior belief.

### Prior Parameters: `prior_failures` / `prior_beta` (aliases)

Represents prior failures in your belief about the code. These are **aliases**:

```python
# Using 'prior_failures'
@pytest.mark.repeated(times=100, prior_passes=9, prior_failures=1, ...)

# Using 'prior_beta' - exactly the same
@pytest.mark.repeated(times=100, prior_alpha=9, prior_beta=1, ...)
```

## How It Works

pytest-repeated uses **Beta-Binomial conjugate prior** Bayesian inference:

1. **Prior**: Start with Beta(prior_passes, prior_failures) belief about success rate
2. **Likelihood**: Observe test results (passes and failures)
3. **Posterior**: Update to Beta(prior_passes + observed_passes, prior_failures + observed_failures)
4. **Decision**: Calculate P(rate ≥ success_rate_threshold) from posterior
5. **Pass/Fail**: Test passes if posterior probability ≥ posterior_threshold_probability

## Examples

### Uninformative Prior (Let Data Decide)

```python
import pytest

@pytest.mark.repeated(
    times=200,
    success_rate_threshold=0.90,
    posterior_threshold_probability=0.95,
    prior_passes=1,    # Weak prior: nearly uninformative
    prior_failures=1
)
def test_new_llm_feature():
    """
    Testing a completely new feature - no prior knowledge.
    Using Beta(1,1) = uniform prior.
    """
    response = call_llm_new_feature("test input")
    assert validate_response(response)
```

With weak priors (1, 1), the test outcome is almost entirely determined by observed data.

### Informative Prior (Incorporate History)

```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.90,
    prior_alpha=85,     # Previous experience: 85 successes
    prior_beta=15       # Previous experience: 15 failures
)
def test_improved_model():
    """
    Old model succeeded ~85% of the time.
    New model should maintain at least that performance.
    Strong prior: Beta(85, 15) centered at 0.85.
    """
    prediction = improved_model.predict(get_test_sample())
    assert prediction == ground_truth()
```

With strong priors (85, 15), you need less new data to confirm/reject beliefs.

### Optimistic Prior

```python
@pytest.mark.repeated(
    times=50,
    success_rate_threshold=0.95,
    posterior_threshold_probability=0.90,
    prior_passes=19,    # Optimistic: 19 successes
    prior_failures=1    # Only 1 failure expected
)
def test_highly_reliable_component():
    """
    Component is expected to be very reliable (95%+).
    Prior: Beta(19, 1) centered at 0.95.
    """
    result = reliable_function()
    assert result is not None
```

### Pessimistic Prior (Strict Requirements)

```python
@pytest.mark.repeated(
    n=150,
    success_rate_threshold=0.70,
    posterior_threshold_probability=0.95,
    prior_alpha=7,      # Pessimistic: only 7 successes
    prior_beta=3        # 3 failures expected
)
def test_experimental_algorithm():
    """
    Experimental algorithm - we're skeptical.
    Prior: Beta(7, 3) centered at 0.70.
    Need strong evidence to pass.
    """
    output = experimental_algo(get_input())
    assert validate(output)
```

## When to Use Bayesian Testing

✅ **Best for:**
- Incorporating historical performance data
- Testing iterative improvements to existing code
- Teams comfortable with Bayesian reasoning
- When prior beliefs should influence test outcomes
- Situations with limited test data but strong priors

❌ **Consider alternatives when:**
- No prior knowledge exists ([Frequentist](frequentist.md) or [Basic](basic.md))
- Team unfamiliar with Bayesian statistics
- Stakeholders prefer frequentist confidence intervals
- You want simpler interpretation

## Choosing Parameters

### Prior Strength

Weak prior (data-driven):
```python
prior_passes=1, prior_failures=1  # Beta(1,1) = uniform, nearly uninformative
```

Moderate prior:
```python
prior_alpha=10, prior_beta=2  # Beta(10,2), centered at ~0.83, moderate confidence
```

Strong prior:
```python
prior_passes=100, prior_failures=10  # Beta(100,10), centered at ~0.91, high confidence
```

**Rule of thumb**: Sum of priors ≈ strength. `prior_passes + prior_failures = 10` is moderate, `100` is strong.

### Sample Size

The strength of new evidence depends on `times`:

```python
# Strong prior, small sample - prior dominates
@pytest.mark.repeated(times=20, prior_alpha=100, prior_beta=10, ...)

# Weak prior, large sample - data dominates
@pytest.mark.repeated(times=500, prior_passes=1, prior_failures=1, ...)

# Balanced
@pytest.mark.repeated(times=100, prior_alpha=10, prior_beta=2, ...)
```

### Success Rate Threshold

Set based on minimum acceptable performance:

```python
# Strict requirement
success_rate_threshold=0.95

# Moderate requirement
success_rate_threshold=0.80

# Lenient requirement
success_rate_threshold=0.60
```

### Posterior Probability

How certain you need to be:

```python
# Very confident (strict)
posterior_threshold_probability=0.99

# Standard confidence
posterior_threshold_probability=0.95

# Lower confidence (easier to pass)
posterior_threshold_probability=0.90
```

## Understanding Beta Distribution

The Beta(α, β) distribution describes beliefs about a probability:

- **Mean**: α / (α + β)
- **Strength**: α + β (higher = stronger belief)

Examples:

```python
# Beta(1, 1) - uniform, no preference
prior_alpha=1, prior_beta=1  # Mean: 0.5, weak

# Beta(9, 1) - strong belief in 90% success
prior_passes=9, prior_failures=1  # Mean: 0.9, moderate strength

# Beta(90, 10) - very strong belief in 90% success
prior_alpha=90, prior_beta=10  # Mean: 0.9, strong

# Beta(50, 50) - strong belief in 50% success
prior_passes=50, prior_failures=50  # Mean: 0.5, very strong
```

## Bayesian Update Example

Starting with Beta(8, 2) prior, observing 18 passes and 2 failures in 20 runs:

**Prior**: Beta(8, 2)
- Mean: 8/(8+2) = 0.8
- Strength: 10

**Observed**: 18 passes, 2 failures

**Posterior**: Beta(8+18, 2+2) = Beta(26, 4)
- Mean: 26/(26+4) = 0.867
- Strength: 30

If `success_rate_threshold=0.85`, calculate P(rate ≥ 0.85) from Beta(26, 4).

If this probability ≥ `posterior_threshold_probability`, test **passes**.

## Statistical Details

### Beta-Binomial Conjugate Prior

The Beta distribution is the **conjugate prior** for binomial likelihood:

- **Prior**: θ ~ Beta(α, β)
- **Likelihood**: k successes in n trials ~ Binomial(n, θ)
- **Posterior**: θ ~ Beta(α + k, β + n - k)

This mathematical convenience means we can calculate the exact posterior analytically.

### Posterior Probability Calculation

To test if success rate ≥ threshold, we calculate:

P(θ ≥ success_rate_threshold | data) = 1 - CDF_Beta(α_post, β_post)(success_rate_threshold)

Where CDF_Beta is the cumulative distribution function of the posterior Beta distribution.

## Error Handling

Like all pytest-repeated modes, Bayesian testing stops immediately on non-AssertionErrors:

```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.95,
    prior_alpha=10,
    prior_beta=2
)
def test_with_potential_bug():
    result = risky_function()  # Might raise ValueError
    assert result > threshold

# If ValueError occurs:
# - Test stops immediately
# - Test FAILS regardless of posterior
# - Bayesian update is not performed
```

## Interpretation

When the test **passes**:
> "Based on prior beliefs and observed data, we are [posterior_threshold_probability×100]% confident the true success rate is at least [success_rate_threshold×100]%"

When the test **fails**:
> "Based on prior beliefs and observed data, we cannot be [posterior_threshold_probability×100]% confident the success rate meets [success_rate_threshold×100]%"

Example with `success_rate_threshold=0.90, posterior_threshold_probability=0.95`:
- **Pass**: "We are 95% confident the true success rate is at least 90%"
- **Fail**: "We cannot be 95% confident the success rate is at least 90%"

## Next Steps

- [Frequentist Testing](frequentist.md) - Null hypothesis approach without priors
- [Basic Testing](basic.md) - Simple threshold approach
- [Parameters Reference](reference/parameters.md) - Full parameter details
- [Decorator Placement](decorator-placement.md) - Using with other pytest markers
