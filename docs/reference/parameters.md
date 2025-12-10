# Parameters Reference

Complete reference for all `@pytest.mark.repeated` parameters.

## Parameter Overview

All parameters are specified as keyword arguments to the `@pytest.mark.repeated()` decorator:

```python
@pytest.mark.repeated(times=100, threshold=95)
def test_example():
    pass
```

## Common Parameters

### `times` or `n` 🔄

**Type**: `int`
**Required**: Yes (for all approaches)
**Aliases**: `times` ≡ `n`

Number of times to repeat the test.

```python
@pytest.mark.repeated(times=100, threshold=95)  # Using 'times'
@pytest.mark.repeated(n=100, threshold=95)      # Using 'n' - exactly the same
```

**Recommendations**:
- Minimum: 20-30 for basic threshold testing
- Typical: 50-200 for most use cases
- Large: 500-1000+ for precise statistical inference

---

## Basic Threshold Approach

### `threshold`

**Type**: `int`
**Required**: Yes (for basic approach)
**Range**: 0 to `times`

Minimum number of passes required for test to succeed overall.

```python
@pytest.mark.repeated(times=100, threshold=95)
# Test passes if ≥95 out of 100 runs succeed
```

**Examples**:
```python
# 95% success rate
times=100, threshold=95

# 90% success rate
times=50, threshold=45

# 99% success rate (strict)
times=200, threshold=198

# 100% success rate (no randomness)
times=10, threshold=10
```

**Notes**:
- `threshold` must be ≤ `times`
- Setting `threshold=times` means all runs must pass (deterministic)

---

## Frequentist Approach

### `H0` or `null`

**Type**: `float`
**Required**: Yes (for frequentist approach)
**Range**: 0.0 to 1.0
**Aliases**: `H0` ≡ `null`

The null hypothesis proportion - the baseline success rate to test against.

```python
@pytest.mark.repeated(times=100, H0=0.90, ci=0.95)    # Using 'H0'
@pytest.mark.repeated(times=100, null=0.90, ci=0.95)  # Using 'null' - exactly the same
```

**Interpretation**:
- Test **passes** if we can confidently reject H₀ (i.e., prove success rate > H₀)
- Test **fails** if we cannot reject H₀

**Examples**:
```python
# High bar: must exceed 95% success rate
H0=0.95

# Moderate bar: must exceed 80% success rate
null=0.80

# Low bar: must exceed 60% success rate
H0=0.60
```

### `ci`

**Type**: `float`
**Required**: Yes (for frequentist approach)
**Range**: 0.0 to 1.0

Confidence level for the confidence interval.

```python
@pytest.mark.repeated(times=100, H0=0.85, ci=0.95)
# 95% confidence interval
```

**Common values**:
- `0.90` - 90% confidence (less strict)
- `0.95` - 95% confidence (standard, recommended)
- `0.99` - 99% confidence (very strict)

**Notes**:
- Higher `ci` = stricter test = need more passes to reject H₀
- 0.95 is standard in most scientific fields

---

## Bayesian Approach

### `success_rate_threshold`

**Type**: `float`
**Required**: Yes (for Bayesian approach)
**Range**: 0.0 to 1.0

Minimum success rate your code must achieve.

```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,  # Code must succeed ≥85% of the time
    posterior_threshold_probability=0.95
)
```

**Examples**:
```python
# Strict: 95% success rate required
success_rate_threshold=0.95

# Moderate: 80% success rate required
success_rate_threshold=0.80

# Lenient: 60% success rate required
success_rate_threshold=0.60
```

### `posterior_threshold_probability`

**Type**: `float`
**Required**: Yes (for Bayesian approach)
**Range**: 0.0 to 1.0

How confident you need to be that `success_rate_threshold` is met.

```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.95  # 95% confidence required
)
```

**Common values**:
- `0.90` - 90% confidence (easier to pass)
- `0.95` - 95% confidence (standard, recommended)
- `0.99` - 99% confidence (very strict)

**Interpretation**: Test passes if P(success_rate ≥ success_rate_threshold | data) ≥ posterior_threshold_probability

### `prior_passes` or `prior_alpha`

**Type**: `int`
**Required**: Yes (for Bayesian approach)
**Range**: > 0 (typically ≥ 1)
**Aliases**: `prior_passes` ≡ `prior_alpha`

Prior belief: number of successes in your Beta prior.

```python
# Using 'prior_passes'
@pytest.mark.repeated(times=100, prior_passes=9, prior_failures=1, ...)

# Using 'prior_alpha' - exactly the same
@pytest.mark.repeated(times=100, prior_alpha=9, prior_beta=1, ...)
```

**Common patterns**:

```python
# Uninformative prior (let data decide)
prior_passes=1, prior_failures=1  # Beta(1,1) = uniform

# Weak prior favoring 80% success
prior_alpha=8, prior_beta=2  # Beta(8,2), mean=0.8, weak

# Strong prior favoring 90% success
prior_passes=90, prior_failures=10  # Beta(90,10), mean=0.9, strong
```

**Notes**:
- Higher values = stronger prior belief
- Prior mean = `prior_passes / (prior_passes + prior_failures)`

### `prior_failures` or `prior_beta`

**Type**: `int`
**Required**: Yes (for Bayesian approach)
**Range**: > 0 (typically ≥ 1)
**Aliases**: `prior_failures` ≡ `prior_beta`

Prior belief: number of failures in your Beta prior.

```python
# Using 'prior_failures'
@pytest.mark.repeated(times=100, prior_passes=85, prior_failures=15, ...)

# Using 'prior_beta' - exactly the same
@pytest.mark.repeated(times=100, prior_alpha=85, prior_beta=15, ...)
```

**Examples**:

```python
# Optimistic prior (expect high success)
prior_passes=19, prior_failures=1  # 95% expected success

# Balanced prior
prior_alpha=50, prior_beta=50  # 50% expected success, strong belief

# Pessimistic prior (expect low success)
prior_passes=3, prior_failures=7  # 30% expected success
```

**Notes**:
- Prior strength = `prior_passes + prior_failures`
- Sum of 2-10 = weak prior, 10-50 = moderate, 50+ = strong

---

## Parameter Aliases Summary

pytest-repeated supports multiple names for the same parameter to match different naming conventions:

| Primary Name | Alias(es) | Description |
|--------------|-----------|-------------|
| `times` | `n` | Number of repetitions |
| `H0` | `null` | Null hypothesis proportion (frequentist) |
| `prior_passes` | `prior_alpha` | Beta prior successes (Bayesian) |
| `prior_failures` | `prior_beta` | Beta prior failures (Bayesian) |

**Use whichever naming convention your team prefers** - they're functionally identical.

---

## Parameter Combinations

### Valid Combinations

**Basic Threshold Testing**:
```python
@pytest.mark.repeated(times=100, threshold=95)
```
Required: `times` (or `n`), `threshold`

**Frequentist Testing**:
```python
@pytest.mark.repeated(times=100, H0=0.90, ci=0.95)
# or
@pytest.mark.repeated(n=100, null=0.90, ci=0.95)
```
Required: `times`/`n`, `H0`/`null`, `ci`

**Bayesian Testing**:
```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.95,
    prior_passes=10,
    prior_failures=2
)
# or
@pytest.mark.repeated(
    n=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.95,
    prior_alpha=10,
    prior_beta=2
)
```
Required: `times`/`n`, `success_rate_threshold`, `posterior_threshold_probability`, `prior_passes`/`prior_alpha`, `prior_failures`/`prior_beta`

### Invalid Combinations

❌ **Don't mix approaches**:
```python
# WRONG - mixing basic and frequentist
@pytest.mark.repeated(times=100, threshold=95, H0=0.90, ci=0.95)
```

❌ **Don't mix aliases**:
```python
# WRONG - using both times and n
@pytest.mark.repeated(times=100, n=50, threshold=95)
```

**Best practice**: Use parameters for **one statistical approach** per test.

---

## Type Specifications

| Parameter | Type | Valid Range | Default |
|-----------|------|-------------|---------|
| `times` / `n` | `int` | > 0 | None (required) |
| `threshold` | `int` | 0 to `times` | None |
| `H0` / `null` | `float` | 0.0 to 1.0 | None |
| `ci` | `float` | 0.0 to 1.0 | None |
| `success_rate_threshold` | `float` | 0.0 to 1.0 | None |
| `posterior_threshold_probability` | `float` | 0.0 to 1.0 | None |
| `prior_passes` / `prior_alpha` | `int` | > 0 | None |
| `prior_failures` / `prior_beta` | `int` | > 0 | None |

---

## Examples by Use Case

### LLM Testing (Basic)
```python
@pytest.mark.repeated(times=50, threshold=48)
def test_llm_accuracy():
    response = call_llm("What is 2+2?")
    assert "4" in response
```

### LLM Testing (Frequentist)
```python
@pytest.mark.repeated(times=100, H0=0.90, ci=0.95)
def test_llm_exceeds_90_percent():
    response = call_llm("What is the capital of France?")
    assert "Paris" in response
```

### LLM Testing (Bayesian)
```python
@pytest.mark.repeated(
    times=100,
    success_rate_threshold=0.85,
    posterior_threshold_probability=0.95,
    prior_alpha=17,  # Previous testing showed ~85% success
    prior_beta=3
)
def test_llm_maintains_quality():
    response = call_llm("Translate 'hello' to French")
    assert "bonjour" in response.lower()
```

### ML Model Testing (Frequentist)
```python
@pytest.mark.repeated(n=500, null=0.80, ci=0.99)
def test_model_exceeds_baseline():
    sample = get_test_sample()
    prediction = model.predict(sample.features)
    assert prediction == sample.label
```

### Randomized Algorithm (Bayesian with uninformative prior)
```python
@pytest.mark.repeated(
    times=200,
    success_rate_threshold=0.90,
    posterior_threshold_probability=0.95,
    prior_passes=1,      # Uninformative prior
    prior_failures=1
)
def test_new_random_algorithm():
    result = random_algorithm(get_input())
    assert validate_result(result)
```

---

## Quick Decision Guide

**Choose your approach**:

1. **Need simple pass/fail?** → Use `threshold`
2. **Need statistical rigor with hypothesis testing?** → Use `H0` + `ci`
3. **Have prior knowledge to incorporate?** → Use `success_rate_threshold` + `posterior_threshold_probability` + priors

**Number of repetitions** (`times`):
- Quick tests: 20-50
- Standard tests: 100-200
- Precise tests: 500-1000+

---

## Next Steps

- [Basic Usage](../usage/basic.md) - Learn threshold-based testing
- [Frequentist](../usage/frequentist.md) - Hypothesis testing approach
- [Bayesian](../usage/bayesian.md) - Prior incorporation approach
- [API Reference](api.md) - Low-level API documentation
