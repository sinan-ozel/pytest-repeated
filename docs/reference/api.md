# API Reference

Low-level API documentation for pytest-repeated internals and extension points.

!!! note "Using mkdocstrings"
    This page will be automatically generated from the source code docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

## Plugin Module

::: pytest_repeated.plugin
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members_order: source

## Key Functions

### pytest_runtest_call

Handles test repetition and error detection. This is the core hook that runs tests multiple times.

### pytest_runtest_makereport

Applies statistical evaluation (basic/frequentist/Bayesian) to determine overall test pass/fail.

### pytest_runtest_logreport

Displays run-by-run results at verbosity level 3 (`-vvv`).

## Extension Points

pytest-repeated integrates with pytest's hook system. If you're extending or modifying the plugin, these are the key hooks:

- **`pytest_configure`**: Plugin registration and configuration
- **`pytest_runtest_protocol`**: Test execution protocol override
- **`pytest_runtest_call`**: Individual test run execution
- **`pytest_runtest_makereport`**: Test result reporting
- **`pytest_runtest_logreport`**: Logging and verbosity handling

## Statistical Methods

### Wilson Score Interval (Frequentist)

pytest-repeated uses the Wilson score interval for constructing confidence intervals in frequentist testing. This method provides better coverage than the normal approximation, especially for small sample sizes.

### Beta-Binomial Model (Bayesian)

The Bayesian approach uses a Beta-Binomial conjugate prior model:

- **Prior**: Beta(α, β) distribution over success rate θ
- **Likelihood**: Binomial(n, θ) for observed successes
- **Posterior**: Beta(α + successes, β + failures)

The test evaluates P(θ ≥ threshold | data) using the posterior CDF.

## Next Steps

- [Parameters Reference](parameters.md) - All decorator parameters
- [Basic Usage](../usage/basic.md) - Using the plugin
- [Development Guide](../development.md) - Contributing to pytest-repeated
