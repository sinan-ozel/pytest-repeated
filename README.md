![Tests & Lint](https://github.com/sinan-ozel/pytest-repeated/actions/workflows/cicd.yaml/badge.svg?branch=main)
![PyPI](https://img.shields.io/pypi/v/pytest-repeated.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-repeated)
![License](https://img.shields.io/github/license/sinan-ozel/pytest-repeated.svg)

# Introduction

This is a statistical unit testing plugin for pytest.
It repeats tests and pass if the underlying test passes a number of times out of a total,
or it passes by rejecting the null hypothesis of a one-sided proportion test.

## Purpose
I want to leverage `pytest` for model evaluation in a way that can be readily incorporated into CI/CD flows.

## The Case For Statistical Umit Testing
Originally, unit testing was expected to be completely deterministeic.
That was because computer programs behaved completely deterministically.
More recently, computer programs started incoprating staitsical procedures.
First starting with data science algrothims such as recommendation engines,
and more recently with LLMs, computer outputs are random varaibles.

Staitiscal testing is not new.
In manufacturing, statistical testing is incorporated as part of QA processes for decased.
It is time, as of Dec 2025, to incorporate statiscal testing.

(Also consider giving `pytest-repeat` a look - I wrote `pytest-repeated` for _statistical_ testing, as in, there are situations where one or two failures out of a hundred is acceptable.)

# Installation

```
pip install pytest-repeated
```

# 🚀 Usage Example

## Basic Usage

```
@pytest.mark.repeated(times=4, threshold=2)
def test_example_random():
    import random
    assert random.choice([True, False])  # may pass or fail
```

This test will run four times and pass if we get `True` in at least two of the four iterations.

This is the test that is easiest to explain to stakeholders.

## Statistical Usage

```
@pytest.mark.repeated(null=.9, ci=0.95, n=200)
def test_example_random():
    import random
    assert random.choice([True, False])  # may pass or fail
```

For those of us with frequentist background, this is a statistical test.
Our null hypothesis is that the underlying test will fail at most 90% of the time, set by the kwarg `null`.
We would like to reject this `null` hypothesis with a .95 level of confidence, so we set the kwarcg `ci` to .95.
If this test passes, that means that the underlying (decorated) test (`test_example_random`) is likely to pass 90% of the time with a .95 level of confidence.
If this sounds like a mouthful, it is, that is just frequentist statistics.
Rejecting a null is a roundabout way of expressing our level of confidence in a world of uncertainty, but it is a well-established and objective way.


# 🛠️ Development

The only requirement is 🐳 Docker.
(The `.devcontainer` and `tasks.json` are prepared assuming a *nix system, but if you know the commands, this will work on Windows, too.)

1. Clone the repo.
2. Branch out.
3. Open in "devcontainer" on VS Code and start developing. Run `pytest` under `tests` to test.
4. Akternatively, if you are a fan of Test-Driven Development like me, you can run the tests without getting on a container. `.vscode/tasks.json` has the command to do so, but it's also listed here:
```
docker compose -f tests/docker-compose.yaml up --build --abort-on-container-exit --exit-code-from test
```

4. When satisfied, push and open a PR. The pipeline will publish automatically when your PR is merged.

# Future Plans

- [ ] Optimized testing - stop conditions.
- [ ] Sequential testing.
- [ ] Ability to set the seed.
- [ ] Report and fail on speed
- [ ] A Bayesian test with a prior and desired posterior