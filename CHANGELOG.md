# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.10] - 2026-02-24

### Added
- New parameter `stop_if_threshold_met` (default: `False`) for threshold mode
  - When set to `True`, stops test execution as soon as the threshold is met
  - Useful for expensive tests where early stopping can save time and resources
  - Only compatible with threshold mode (raises `ValueError` if used with frequentist or Bayesian modes)
- Comprehensive test coverage for `stop_if_threshold_met` feature
- Documentation for the new parameter in:
  - `docs/reference/parameters.md`
  - `docs/usage/basic.md`

### Changed
- Test execution can now terminate early in threshold mode when `stop_if_threshold_met=True`

## [0.3.9] - Previous Release

(Version history before 0.3.9 not documented)
