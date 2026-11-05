---
name: managing-dependencies
description: >-
  Use when adding, bumping, pinning, or reviewing a dependency in requirements.txt or requirements/*.txt, including taking or fixing a Dependabot PR. Also use when pip install fails on some Python versions in CI but not others ("Could not find a version that satisfies the requirement", "No matching distribution found", "Requires-Python", "ResolutionImpossible"), including PyPy-only failures, and when dropping support for an old Python version.
---

# Managing dependencies

This repo supports a range of Python versions, and one set of requirements files has to install on all of them. Dependabot proposes the newest release, so its bumps often raise a lower bound past what the oldest Pythons can install, and CI fails at the install step on those jobs only. The fix is to split the requirement with PEP 508 `python_version` markers so each Python gets the newest release it can install. Dropping an old Python to turn CI green is not the fix.

## Where the facts live

Read these instead of trusting memory; they change often.

- **Supported Pythons:** `requires-python` and the `Programming Language :: Python :: 3.X` classifiers in `pyproject.toml`, and the CI matrix.
- **Who installs a file, on which Python:** `grep -rn requirements .github/workflows scripts requirements pyproject.toml`. This also catches `-r` includes. For a hit in a script, find the CI job that runs it and read its `python-version`.
- **Whether a file ships to users:** a file that `pyproject.toml` reads into package metadata (`dependencies` or `optional-dependencies` under `[tool.setuptools.dynamic]`) ends up in the published wheel.

## Workflow

- [ ] 1. Find which Pythons install the file. A file installed only on the newest Python takes the bump as-is.
- [ ] 2. Find the newest release each affected Python can install (see "Finding the ceiling").
- [ ] 3. If every Python the line covers can install the new lower bound, take the bump as one line. Done.
- [ ] 4. Otherwise split the line (see "Splitting a line").
- [ ] 5. Re-read the section: no Python matches two lines, and the newest line is open-ended.

Change only the section you are fixing; don't reformat other sections in the same change.

## File layout

Each file starts with a `# pip install -r <path>` header, then one section per dependency: a `# <name>` line, optional `# Note:` lines, the requirement line(s), and a blank line.

```
# pip install -r requirements/testing.txt

# pkg
pkg>=1.4,<2; python_version < "3.9"
pkg>=2.0,<2.3; python_version == "3.9"
pkg>=2.5.1,<3; python_version >= "3.10"

# other-pkg
# Note: other-pkg 4.x breaks on Python 3.8 but declares no requires_python, so pip can't filter it.
other-pkg>=3,<4
```

**Notes:** write one only for what the lines can't say: a cap that isn't obvious, a coupling with another package, or a release with wrong metadata. Don't restate versions or which Python gets which release; a routine split needs no note. Existing notes that only restate their lines are legacy: drop one when you edit its section, and don't copy it.

## Finding the ceiling

An old Python's ceiling is the first release that dropped it, not the release Dependabot proposes. If `pkg` dropped 3.9 at 2.3 and the target is 2.5.1, the 3.9 line is `<2.3`, since 2.3 through 2.5.0 are 3.10-only too.

- **From a red CI job:** the failing install log is ground truth. The lowest version on its `Ignored the following versions that require a different python version` line is that Python's ceiling.
- **For any Python:** `pip index versions <pkg> --python-version 3.9` lists what 3.9 can install, newest first. Run it again for the next Python up; the first release newer than 3.9's newest is 3.9's ceiling.
- **The pre-bump lower bound** is in the Dependabot PR title (`update pkg requirement from <3,>=2.0 to >=2.5.1,<3`) or `git diff`.

## Splitting a line

Split only the Pythons that the bumped line covers and the new lower bound excludes. Leave existing bands for older Pythons alone, even when they are coarser than they could be.

- Lines run oldest Python to newest. The newest line takes the bump and stays open-ended (`>= "X.Y"`).
- Each band that splits off keeps the line's pre-bump lower bound and gets its ceiling from "Finding the ceiling". Pythons that share a ceiling share a band.
- Marker style: `pkg>=1,<2; python_version == "3.9"`. Spaces around operators, double-quoted `"X.Y"`, one space after `;`. A one-Python band is `== "X.Y"`; a band spanning several is `>= "X.Y" and < "X.Z"`, or `< "X.Z"` when it is the oldest. Boundaries use `>=` and `<` so each Python lands on exactly one side. `python_version` is major.minor only (3.9.5 reports `"3.9"`), so `== "3.9"` covers every 3.9 patch; don't use `python_full_version` here, where `== "3.9"` matches only 3.9.0.

A section with a single gated line (installed only on the newest Python, or only on PyPy) is intentional; don't fill in the other Pythons.

## Gotchas

- **Dependabot rewrites only the last line** of a split section, the open-ended one. When it bumps a split package, check which Pythons that line covers; the new lower bound may exclude the oldest of them, which then splits off.
- **Releases with no `requires_python`** can't be filtered by pip, so they install on Pythons they don't support and fail at import or test time rather than at install. `pip index` lists them too. Pin an explicit ceiling with a note saying why. When the culprit comes in loosely through another package, pin it in that package's section so the coupling stays visible.
- **Only PyPy jobs fail:** the release usually dropped PyPy wheels. Gate on the implementation instead of downgrading CPython: `pkg<46; implementation_name == "pypy" and python_version == "3.10"`. Lowercase `pypy`, and `implementation_name`, not `platform_python_implementation`. No unmarked companion line is needed.
- **Files that ship:** full-line comments only; an inline comment breaks the package build. Their lower bounds are the minimum users must install, so raise one only for a reason.
- **Not this pattern:** a real test failure, or an install failure on every Python. Investigate the bump normally.

## Dropping a Python version

When a Python leaves the classifiers and the CI matrix, merge any band that only served it into its neighbor. If a section is left with one line, remove its marker and the `;`.

## Leave alone

- `requires-python`, the classifiers, and the CI matrix. Changing which Pythons are supported is its own decision.
- Packages under `ignore` in `.github/dependabot.yml`: maintainers bump those by hand on purpose. Prefer a marker split over adding a new `ignore`, which freezes the package on every Python.
