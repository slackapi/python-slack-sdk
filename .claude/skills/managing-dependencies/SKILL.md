---
name: managing-dependencies
description: >-
  Use when adding, updating, pinning, or reviewing any dependency in this repo's requirements/*.txt files, including taking a Dependabot bump or writing a requirement line by hand. Also use when a pip install fails on the older Python jobs while newer ones pass, or when CI errors with "Could not find a version that satisfies", "No matching distribution found", "Requires-Python >=3.x", or "ResolutionImpossible". Triggers include: "add <package> to requirements", "bump/update <package>", "pin <package>", "fix this dependabot PR", "CI can't install <package> on Python 3.7/3.8/3.9", "requires-python error in the install step". This skill defines the layout and version-constraint conventions to follow; reach for it before hand-editing any requirements/*.txt file.
---

# Managing dependencies

## Overview

Every `requirements/*.txt` file in this repo follows **one layout convention** and **one version-constraint pattern**. This keeps a single set of pins working across the whole Python matrix and every diff readable. The mechanism for making one line behave differently per interpreter is [PEP 508](https://peps.python.org/pep-0508/) environment markers. That spec is the authority for the marker syntax used throughout this skill.

Two facts about this repo drive everything below:

- It supports **Python `>=3.7`** (`requires-python` and the classifiers in `pyproject.toml`). Its CI matrix in `.github/workflows/ci-build.yml` tests every version from **3.7 through 3.14 plus PyPy** (`pypy3.10`, `pypy3.11`).
- Many popular packages keep raising their minimum Python. A bump that raises a dependency's **lower bound** to a release requiring a newer Python makes pip's resolver find nothing installable on the old interpreters. The install step then fails there before tests even run.

The convention resolves this without dropping old-Python support. Pin each interpreter to the newest release it can actually install, using PEP 508 `python_version` markers.

## File-layout convention

Each file lists **one dependency per section**: Name of the dependency, an optional rationale note (starting with `Note:`, explaining why a version is pinned or split), then the requirement line(s), separated from the next section by a blank line. This makes every pin self-documenting.

```
# pytest
pytest>=7.0.1,<9

# pytest-cov
# Note: pytest-cov 7.1+ requires Python >=3.9; cap older interpreters below it.
pytest-cov>=4,<7.1.0; python_version < "3.9"
pytest-cov>=7.1.0,<8; python_version >= "3.9"
```

Keep this layout when adding or editing dependencies. Never leave an empty trailing `;` (a fossil of a collapsed split; delete it).

## Which files need Python-version markers

A marker split is only needed for requirements files installed across the **full** Python matrix. Which file you are editing decides this. To see where a file is installed, read `.github/workflows/ci-build.yml`. It is the source of truth for which Python versions install which requirements files.

| File                             | Installed on                                        | Needs markers?                      |
| -------------------------------- | --------------------------------------------------- | ----------------------------------- |
| `requirements/testing.txt`       | full matrix (3.7 → 3.14, pypy)                      | **Yes, if a bump raises the floor** |
| `requirements/optional.txt`      | full matrix (also packaged as the `optional` extra) | **Yes, if a bump raises the floor** |
| `requirements/tools.txt`         | latest supported Python only                        | No, just take the bump              |
| `requirements/databases.txt`     | latest supported Python only (databases job)        | No, just take the bump              |
| `requirements/documentation.txt` | not installed in CI (manual docs script only)       | No, just take the bump              |

If the bump lands in a latest-Python-only file, take it as-is. No markers, no ceiling, just the layout convention above.

**`optional.txt` is special:** it is read into wheel metadata via `[tool.setuptools.dynamic]` in `pyproject.toml` (`optional-dependencies.optional`). Use **full-line comments only** there, never trailing inline comments, so nothing leaks into the packaged metadata.

## The version-constraint pattern

When a dependency's floor rises to a release that requires a newer Python, **do not** just take the bump, and **do not** drop old-Python support to make CI pass. Instead, split the requirement into `python_version`-marked lines that **partition the whole matrix**. Every interpreter matches exactly one line. Old interpreters keep the last compatible release (with an explicit ceiling), and the newest line is open-ended so future Pythons stay covered.

```
# pytest
# Note: pytest 9 requires Python >=3.10; cap older interpreters below it.
pytest>=7.0.1,<9; python_version < "3.10"
pytest>=9.1.1,<10; python_version >= "3.10"
```

## Canonical marker style

Consistency matters because these lines are read and edited often, and a stray style makes diffs noisy. Standardize on this:

- Spaces around every operator: `python_version >= "3.10"`, never `python_version>="3.10"`.
- Double-quoted `major.minor` string: `"3.10"`. (`packaging` compares these version-aware, so
  `"3.10" > "3.9"` is correctly true, no lexicographic surprise.)
- Use `>=` / `<` for the Python boundary; avoid `>` / `<=` so the boundary version lands on exactly one side.
- One space after the `;`, none before: `pkg>=1,<2; python_version >= "3.10"`.
- The old-side line always carries an explicit upper bound (the floor-jump version).
- The marker set must be **exhaustive and mutually exclusive** across the matrix. The newest line ends open-ended (`>= "X.Y"`), never a bare `==` that leaves future Pythons unmatched.

## Deriving the versions to pin

You need two numbers: the **floor** (which Python the new release requires) and the old-side **ceiling** (the first release that raised that floor).

1. **Floor.** Read the metadata for the _exact target version_ at `https://pypi.org/pypi/<package>/<target-version>/json`. The `info.requires_python` field gives the new minimum (e.g. `">=3.10"`). A `null` there means the release declares no floor.

2. **Ceiling.** Walk the release history at `https://pypi.org/pypi/<package>/json` and find the **first version that raised the floor above the oldest matrix Python**. The old-side ceiling is `< <that version>`. For example, if `aiodns` jumped to `>=3.10` at version **4.0.0**, the old-side cap is `<4` even if the target is `4.0.4` (pinning `<4.0.4` would wrongly admit 4.0.0–4.0.3, which are also 3.10-only).

Why an explicit ceiling instead of trusting pip to filter by `Requires-Python`? Because that filtering only holds if every future release keeps its metadata correct; a single mis-tagged release would silently float onto an untested interpreter. An explicit ceiling makes the intent self-documenting and robust.

**If you arrived here from a red CI job:** the failing _install_ log is ground truth. It names the interpreter that failed and the versions pip was actually offered, e.g.:

```
ERROR: Ignored the following versions that require a different python version: 4.0.4 Requires-Python >=3.10
ERROR: Could not find a version that satisfies the requirement aiodns>=4.0.4 (from versions: ..., 3.6.0, 3.6.1)
```

Cross-check the PyPI value against that log so you are never guessing. (If instead the failure is a real test failure, or hits _every_ Python version, this pattern does not apply, so investigate the bump normally.)

## Two harder shapes

**Different old Pythons need different ceilings.** When several old interpreters each cap at a different release, emit one line per divergent interpreter with `== "X.Y"`, then a final open-ended line. This is the `aiohttp` pattern already in `testing.txt` / `optional.txt`:

```
# aiohttp
# Note: aiohttp's minimum Python rose in stages; cap each old interpreter at its last compatible release.
aiohttp>=3.7.3,<3.9; python_version == "3.7"
aiohttp>=3.7.3,<3.11; python_version == "3.8"
aiohttp>=3.13.5,<4; python_version >= "3.9"
```

**Only PyPy breaks.** Sometimes a bump drops PyPy _wheels_ while CPython at the same version is fine (the failing jobs are `pypy*`, not `3.7`/`3.8`/`3.9`). A `python_version` split would wrongly downgrade CPython too. Gate on the implementation instead, as in the `cryptography` pattern in `testing.txt`. Note the exact marker name and casing: **`implementation_name == "pypy"`** (lowercase `pypy`), not `platform_python_implementation`. A single gated line is enough. You do **not** need a second negated line for the other interpreters, because an unmarked line already applies everywhere the marked one is skipped.

```
# cryptography
# Note: cryptography 46+ dropped PyPy 3.10 wheels; pin to <46 for PyPy 3.10 only.
cryptography<46; implementation_name == "pypy" and python_version == "3.10"
```

## Collapse when a Python is dropped

Marker splits are maintenance cost, so remove them when they stop earning their keep. When a Python version is dropped from the CI matrix (and from `requires-python` / the classifiers), collapse any split whose only reason was that version back into a single unmarked line, and delete the trailing `;`. A leaner file is easier for both humans and Dependabot to reason about.

## What to leave alone

- **Do not touch `requires-python` or the CI matrix.** Keeping 3.7 working on old dependency versions is the entire point; changing the floor is a separate, deliberate decision.
- **Prefer markers over a Dependabot `ignore`.** An `ignore` rule freezes newer Pythons on the old version too, and hides the version knowledge in config. Reserve `ignore` for the rare dep that must stay pinned everywhere for reproducible output.
