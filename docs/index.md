# pytest-repeated

![Tests & Lint](https://github.com/sinan-ozel/pytest-repeated/actions/workflows/cicd.yaml/badge.svg?branch=main)
![PyPI](https://img.shields.io/pypi/v/pytest-repeated.svg)
![Downloads](https://static.pepy.tech/badge/pytest-repeated)
![Monthly Downloads](https://static.pepy.tech/badge/pytest-repeated/month)
![License](https://img.shields.io/github/license/sinan-ozel/pytest-repeated.svg)

A statistical unit testing plugin for pytest. 📊

## What is pytest-repeated?

`pytest-repeated` enables **statistical unit testing** by repeating tests multiple times and evaluating results using statistical methods. It's designed for testing code with non-deterministic outputs like:

- 🤖 Large Language Model (LLM) outputs
- 📊 Machine learning model predictions
- 🎲 Data science algorithms with randomness
- 🔀 Any code that produces random variables

## Why Statistical Testing?

Originally, unit testing was completely deterministic because computer programs behaved deterministically. Today, with the rise of:

- Data science algorithms (recommendation engines, etc.)
- Machine learning models
- Large Language Models (LLMs)

...computer outputs are **random variables**. Statistical testing has been part of QA processes in manufacturing for decades. It's time to incorporate it into software testing.

!!! tip "Looking for simple repetition?"
    If you just need to repeat tests without statistical evaluation, check out [`pytest-repeat`](https://github.com/pytest-dev/pytest-repeat). `pytest-repeated` is specifically for _statistical_ testing where some failures are acceptable.

## Three Testing Approaches

pytest-repeated offers three ways to evaluate repeated tests:

1. **[Basic Usage](usage/basic.md)** - Simple threshold-based: "Pass if X out of Y tests succeed"
2. **[Frequentist](usage/frequentist.md)** - Hypothesis testing with null hypothesis and confidence intervals
3. **[Bayesian](usage/bayesian.md)** - Posterior probability that code meets success criteria

Choose the approach that best fits your team's statistical background and communication needs.

## Quick Example

```python
import pytest
import random

@pytest.mark.repeated(times=20, threshold=19)
def test_llm_output():
    response = call_llm("What is 2+2?")
    assert "4" in response  # May occasionally fail due to LLM randomness
```

This test runs 20 times and passes if at least 19 iterations succeed.

## Key Features

✨ **Flexible evaluation**: Basic threshold, frequentist, or Bayesian approaches
🛡️ **Smart error handling**: Stops on non-AssertionErrors (real bugs)
📊 **Statistical rigor**: Proper hypothesis testing and confidence intervals
🔍 **Detailed reporting**: Run-by-run results at high verbosity
⚡ **CI/CD ready**: Integrates seamlessly into pytest workflows

## Next Steps

- [Installation](installation.md) - Get started in seconds
- [Quick Start](quickstart.md) - Run your first statistical test
- [Usage Guide](usage/basic.md) - Learn all three testing methods
- [Parameters Reference](reference/parameters.md) - Complete decorator options
