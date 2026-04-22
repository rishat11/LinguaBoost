# LinguaBoost Constitution

## Core Principles

### Library-first and clarity

Public APIs are small, predictable, and documented where behavior is not obvious. Prefer explicit names and stable interfaces over clever shortcuts. Breaking changes require a version bump and a short migration note in changelog or release notes.

### Testing and correctness

Behavior that users or other modules rely on is covered by automated tests. Bug fixes include a regression test when practical. Language-learning and linguistic logic is tested with representative edge cases (empty input, unicode, ambiguous parses) appropriate to the feature.

### Spec-driven alignment

Feature work follows the Spec Kit flow when used in this repo: constitution stays the source of governing rules; specifications describe *what* and *why* before low-level implementation plans. Deviations from the constitution are documented in the spec or plan with rationale.

### Security and data handling

Untrusted input is validated at boundaries. Secrets and credentials do not enter the codebase or tests. If the project later handles user data, storage and retention follow least-privilege and clear documentation.

### Accessibility and inclusive content

User-facing strings and learning content avoid unnecessary cultural bias; formatting supports localization (unicode, pluralization hooks where relevant). Error messages are actionable and respectful.

## Development workflow

Use `pyproject.toml` as the source of truth for dependencies and tooling. Formatting and linting (e.g. Ruff) stay consistent with project config. Pull requests keep diffs focused on the stated task.

## Quality bar

Code merged to the main branch passes the project’s automated checks (lint, tests) and respects this constitution. New dependencies are justified by need, license compatibility, and maintenance burden.

## Governance

This constitution is amended by explicit decision (team agreement or maintainer approval) and recorded by bumping the version and updating **Last Amended**. Routine development does not override these principles without an amendment.

**Version**: 1.0.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-04-22
