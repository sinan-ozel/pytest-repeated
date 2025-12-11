# Decorator Placement & Compatibility

When using `@pytest.mark.repeated` alongside other pytest markers and decorators, placement and ordering matter.

## General Rule: Place `@pytest.mark.repeated` Last (Bottom)

**Recommended**: Put `@pytest.mark.repeated` as the **last decorator** (closest to the function definition):

```python
import pytest

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.repeated(times=50, threshold=48)
def test_integration_with_external_api():
    """repeated marker is last (bottom) - RECOMMENDED"""
    response = call_external_api()
    assert response.status_code == 200
```

## Why Bottom Placement?

Decorators in Python are applied **bottom-to-top**. The decorator closest to the function executes first in the wrapper chain:

```python
@decorator_A
@decorator_B
@decorator_C
def my_function():
    pass

# Equivalent to:
my_function = decorator_A(decorator_B(decorator_C(my_function)))
```

Placing `@pytest.mark.repeated` at the bottom ensures:

1. **Other markers are applied first** to the base test function
2. **Repeated wrapper is outermost**, controlling the overall execution
3. **Each repetition sees the full decorated test**, not a partial one

## Common Scenarios

### With `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize("input_val,expected", [(1, 2), (2, 4), (3, 6)])
@pytest.mark.repeated(times=10, threshold=9)
def test_doubling(input_val, expected):
    """
    Each parameter combination is repeated 10 times.
    Result: 3 parameter sets × 10 repetitions = 30 total test runs
    """
    result = random_doubler(input_val)  # Occasionally returns wrong value
    assert result == expected
```

**Order matters**:
- ✅ `parametrize` → `repeated`: Each parameter combo repeated 10 times
- ❌ `repeated` → `parametrize`: Would repeat the entire parametrized test 10 times (probably not what you want)

### With `@pytest.fixture` (as argument)

```python
@pytest.mark.repeated(times=20, threshold=19)
def test_with_fixture(temp_database):
    """
    Fixture runs once per repetition.
    repeated marker at bottom ensures fixture is properly set up each time.
    """
    result = query_random_record(temp_database)
    assert result is not None
```

Fixtures are **function arguments**, not decorators, so they're always inside the repetition loop.

### With `@pytest.mark.skip` or `@pytest.mark.skipif`

```python
@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
@pytest.mark.repeated(times=50, threshold=48)
def test_unix_specific_feature():
    """
    Skip condition evaluated before repetition.
    If test is skipped, it's skipped entirely (no repetitions).
    """
    result = unix_only_function()
    assert result > 0
```

Skip markers should typically be **above** (before) `repeated` so the skip is evaluated first.

### With `@pytest.mark.xfail`

```python
@pytest.mark.xfail(reason="Known flaky external dependency")
@pytest.mark.repeated(times=100, threshold=95)
def test_flaky_external_service():
    """
    xfail allows test to fail without failing the suite.
    Repetition still happens, but failures are marked as expected.
    """
    response = call_flaky_service()
    assert response.ok
```

`xfail` above `repeated` means the **entire repeated test** is expected to fail.

### With Custom Markers

```python
@pytest.mark.slow
@pytest.mark.requires_gpu
@pytest.mark.repeated(times=30, threshold=27)
def test_gpu_accelerated_model():
    """
    Custom markers (slow, requires_gpu) for test organization.
    repeated marker at bottom ensures proper execution.
    """
    prediction = gpu_model.predict(get_test_input())
    assert validate_prediction(prediction)
```

Custom markers for organization/filtering should be **above** `repeated`.

### With `pytest-depends`

```python
import pytest

@pytest.mark.dependency(depends=["test_setup"])
@pytest.mark.repeated(times=50, threshold=48)
def test_that_depends_on_setup():
    """
    Dependency marker ensures test_setup passed before this runs.
    repeated marker at bottom ensures dependency check happens first.
    """
    result = feature_requiring_setup()
    assert result is not None
```

Dependency markers should be **above** `repeated` so dependencies are checked before repetition starts.

## Multiple Repeated Tests

When multiple tests use `@pytest.mark.repeated`, each is independent:

```python
@pytest.mark.repeated(times=100, threshold=95)
def test_feature_a():
    assert feature_a_works()

@pytest.mark.repeated(times=50, threshold=48)
def test_feature_b():
    assert feature_b_works()
```

Each test's repetitions are isolated - they don't affect each other.

## Fixtures and Scope

### Function-Scoped Fixtures (default)

```python
@pytest.fixture
def fresh_database():
    db = create_database()
    yield db
    db.teardown()

@pytest.mark.repeated(times=20, threshold=19)
def test_with_function_scope(fresh_database):
    """
    Fixture runs 20 times (once per repetition).
    Each repetition gets a fresh database.
    """
    result = query_database(fresh_database)
    assert result is not None
```

### Module/Session-Scoped Fixtures

```python
@pytest.fixture(scope="module")
def shared_database():
    db = create_database()
    yield db
    db.teardown()

@pytest.mark.repeated(times=20, threshold=19)
def test_with_module_scope(shared_database):
    """
    Fixture runs ONCE for the entire module.
    All 20 repetitions share the same database.
    """
    result = query_database(shared_database)
    assert result is not None
```

**Important**: Module/session-scoped fixtures are **not recreated** between repetitions - all repetitions share the same instance.

## Combining Multiple Approaches

You can combine basic, frequentist, and Bayesian parameters, but **only one approach is evaluated**:

```python
# DON'T DO THIS - unclear which approach applies
@pytest.mark.repeated(
    times=100,
    threshold=95,           # Basic approach
    H0=0.90, ci=0.95,       # Frequentist approach - conflicts!
)
def test_confusing():
    pass
```

**Best practice**: Use only parameters for **one statistical approach** per test.

## Anti-Patterns

### ❌ Repeated Inside Parametrize

```python
# WRONG - unclear semantics
@pytest.mark.repeated(times=10, threshold=9)
@pytest.mark.parametrize("val", [1, 2, 3])
def test_wrong_order(val):
    pass
```

**Problem**: Repeats the entire parametrized test set, not individual parameters.

**Fix**: Put `parametrize` first (above), `repeated` last (bottom).

### ❌ Nested Repetition

```python
# WRONG - don't nest repeated markers
@pytest.mark.repeated(times=10, threshold=9)
@pytest.mark.repeated(times=5, threshold=4)  # What does this even mean?
def test_double_repeated():
    pass
```

**Problem**: Undefined behavior - pytest-repeated doesn't support nested repetition.

**Fix**: Use only **one** `@pytest.mark.repeated` per test.

### ❌ Assuming Fixture Runs Once

```python
@pytest.fixture
def expensive_setup():
    # Expensive operation
    return setup_ml_model()

@pytest.mark.repeated(times=100, threshold=95)
def test_with_expensive_fixture(expensive_setup):
    # WRONG assumption: fixture runs 100 times!
    pass
```

**Problem**: Function-scoped fixtures run on **every repetition** (100 times here).

**Fix**: Use module/session scope for expensive fixtures:

```python
@pytest.fixture(scope="module")
def expensive_setup():
    return setup_ml_model()
```

## Summary

| Scenario | Recommended Order | Example |
|----------|-------------------|---------|
| Basic usage | `repeated` at bottom | `@repeated(...)` |
| With parametrize | `parametrize` then `repeated` | `@parametrize` → `@repeated` |
| With skip/xfail | `skip/xfail` then `repeated` | `@skipif` → `@repeated` |
| With custom markers | Custom then `repeated` | `@slow` → `@repeated` |
| With dependencies | `dependency` then `repeated` | `@dependency` → `@repeated` |

**Golden Rule**: Keep `@pytest.mark.repeated` as the **last decorator** (closest to function) unless you have a specific reason not to.

## Next Steps

- [Basic Usage](basic.md) - Threshold-based testing
- [Frequentist](frequentist.md) - Hypothesis testing approach
- [Bayesian](bayesian.md) - Posterior probability approach
- [Parameters Reference](../reference/parameters.md) - All available parameters
