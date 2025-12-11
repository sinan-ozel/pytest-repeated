![Tests & Lint](https://github.com/sinan-ozel/pytest-repeated/actions/workflows/cicd.yaml/badge.svg?branch=main)
![PyPI](https://img.shields.io/pypi/v/pytest-repeated.svg)
![Downloads](https://static.pepy.tech/badge/pytest-repeated)
![Monthly Downloads](https://static.pepy.tech/badge/pytest-repeated/month)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://sinan-ozel.github.io/pytest-repeated/)
![License](https://img.shields.io/github/license/sinan-ozel/pytest-repeated.svg)

# Introduction

This is a statistical unit testing plugin for pytest. 📊
It repeats tests and pass if the underlying test passes a number of times out of a total,
or it passes by rejecting the null hypothesis of a one-sided proportion test.

📚 **[Full Documentation](https://sinan-ozel.github.io/pytest-repeated/)** | [Quick Start](#-installation) | [Examples](#-usage)

## Purpose: 🔄📊
I want to leverage `pytest` for model evaluation in a way that can be readily incorporated into CI/CD flows.

## 🎲 The Case For Statistical Unit Testing
Originally, unit testing was expected to be completely deterministic.
That was because computer programs behaved completely deterministically.
More recently, computer programs started incorporating statistical procedures.
First starting with data science algorithms such as recommendation engines,
and more recently with LLMs, computer outputs are random variables.

Statistical testing is not new.
In manufacturing, statistical testing is incorporated as part of QA processes for decades.
It is time, as of Dec 2025, to incorporate statistical testing.

(Also consider giving `pytest-repeat` a look - I wrote `pytest-repeated` for _statistical_ testing, as in, there are situations where one or two failures out of a hundred is acceptable.)

# 📦 Installation

```
pip install pytest-repeated
```

# 🚀 Usage Examples

## 🎲 Basic Usage

```
@pytest.mark.repeated(times=19, threshold=20)
def test_example_random():
    import random
    assert random.choice([True, False])  # may pass or fail
```

This test will run four times and pass if we get `True` in at least 19 of the 20 iterations.

This is the test that is easiest to explain to stakeholders.

Note that the test will repeat on `AssertionError` (the `assert`) statement,
but it will actually stop and fail on all other errors.
These are all considered to be detereministic failures, caused by bugs.
Use the `assert` statements to compare against outputs that are random variables (RCs) such as data science predictions or LLM-generated contents and their assessments.

## 📈 Statistical (Frequentist) Usage

```
@pytest.mark.repeated(null=0.9, ci=0.95, n=10)
def test_succeed_50_percent():
    assert random.random() < 0.5
```

For those of us with frequentist background, this is a statistical test.
Our null hypothesis is that the underlying code will succeed at least 90% of the time, set by the kwarg `null`.
We would like to reject this `null` hypothesis with a .95 level of confidence, so we set the kwarg `ci` to .95.
If this test passes, that means that the underlying (decorated) test (`test_example_random`) is likely to pass 90% of the time with a .95 level of confidence.
Another way to think about this is: If the `null` had been correct (The test's chance of success is less than 90% in real operation), we would have less than 5% (1-CI) probability to have the test passed as many times as it did.
Admittedly, this is confusing to express to many. However, rejecting a null is a roundabout way of expressing our level of confidence in a world of uncertainty, but it is a well-established and objective way.
Use this in organizations that have an established understanding of probability. 🎯

## 📚 Further Frequentist Knowledge

The test below will correctly fail to reject the null, and the test will fail:

```
@pytest.mark.repeated(null=0.9, ci=0.95, n=10)
def test_succeed_50_percent():
    assert random.random() < 0.5
```

Underlying truth: The code works only 50% of the time. (We know this because of the example, but in production code, we will not know the underlying truth.)
Our condition to pass: The underlying should be working at least 90% of the time.
Null Hypothesis: The underlying is working at least 90% of the time or less. (Null Hypothesis)
Result: We (correctly) fail to reject the null at a 95% level of confidence.


The following test will likely reject the null, and correctly pass, as desired.

```
@pytest.mark.repeated(null=0.9, ci=0.95, n=1000)
    def test_succeed_95_percent():
        assert random.random() < 0.95
```

The following test will likely incorrectly fail to reject the null (because of the low repetition), resulting in a Type II error.

```
@pytest.mark.repeated(null=0.9, ci=0.95, n=50)
    def test_succeed_95_percent():
        assert random.random() < 0.95
```


## 🔮 Bayesian Usage
```
@pytest.mark.repeated(posterior_threshold_probability=.9, success_rate_threshold=0.7, n=200)
def test_example_random():
    import random
    assert random.choice([True, False])  # may pass or fail
```

In this example, we are interpreting the pass as follows: I believe that the code is likely work as desired 90% of the time.
This belief is based on a Bayesian update based on the 200 trials.
The test passes if after these 200 trials, our updated belief is greater than 70%.
In other words, if the test passed, we believe that there is at least a 70% probability that the code works as desired 90% of the time.
This is much easier to digest and interpret compared to the frequentist method, but is somewhat more subjective.

If you know more about Bayesian statistics, you can also set the alpha and beta of prior.
The prior is Beta-distributed.
`prior_alpha` and `prior_beta` correspond to the initial number of successes and failures before the test was run.

PS: I love Bayesian statistics, but I am not an expert.
If you spot a mistake or unexpected behaviour, please reach out through github and suggest a correction if anything is wrong or amiss. 🤝

## 🤔 Choosing Between Bayesian and Frequentist Approach

Honestly, in most cases, just go with the top example.

Frequentist statistics will work if an organization has lots of people with a background where they already know frequentist statistics.

Bayesian will work better if you want to tell people,
"Hey, I am 90% sure that the code will work as desired 99% of the time." It is still a mouthful, but more advanced than saying "well it passed 5 times out of 6."

It is also a challenge to tell stakeholders that the code will fail some of the time, or that the deployment pipeline is going to be very slow if they want more certainty. However, these seem to be realities of coding as Data Science, ML models and finally LLMs take their positions in our programs.

![Frequentists vs Bayesians](https://www.explainxkcd.com/wiki/images/7/78/frequentists_vs_bayesians.png)

Caricature is funny but somehow misleading, so please read this explanation if you feel the need to understand a bit better.
[https://www.explainxkcd.com/wiki/index.php/1132:_Frequentists_vs._Bayesians](https://www.explainxkcd.com/wiki/index.php/1132:_Frequentists_vs._Bayesians)


# 🛠️ Development

The only requirement is 🐳 Docker.
(The `.devcontainer` and `tasks.json` are prepared assuming a *nix system, but if you know the commands, this will work on Windows, too.)

1. Clone the repo.
2. Branch out.
3. Open in "devcontainer" on VS Code and start developing. Run `pytest` under `tests` to test.
4. Alternatively, if you are a fan of Test-Driven Development like me, you can run the tests without getting on a container. `.vscode/tasks.json` has the command to do so, but it's also listed here:
```
docker compose -f tests/docker-compose.yaml up --build --abort-on-container-exit --exit-code-from test
```

4. When satisfied, push and open a PR. The pipeline will publish automatically when your PR is merged.

# 🚧 Future Plans

- [ ] Optimized testing - stop conditions. ⚡
- [ ] Sequential testing. 📐
- [ ] Ability to set the seed. 🌱
- [ ] Report and fail on speed ⏱️
