# enumerating definitions by walking modules silently under-covers

Date: 2026-10-16 · Tags: `python` `introspection` `verification` `registries`

## Symptom

An inventory built by "import each module, iterate `vars(module)`" reports a
total. Nothing raises. Nothing warns. The total is simply **not all of them**,
and there is no signal that says so.

```console
total 122 {'internal': 23, 'ti': 84, 'legacy': 15}
```

The real number of `legacy` entries was 24. Fifteen were found, nine were not,
and the nine were invisible precisely because they were defined somewhere the
walk never looked.

Worse than the missing rows: the walk was also used to decide each entry's
*label*. So the label depended on **where a name happened to be defined** rather
than on what it was — two names with identical standing came out with different
classifications, purely by accident of layout.

## The wrong assumption

"The walk is exhaustive, because it iterates everything."

It iterates everything *reachable as a module attribute at that moment*. Names
that are assembled at runtime — `__getattr__` on a package, aliases assigned in
`__init__`, plugins registered later, descriptors — are not in `vars()` and will
never be seen. The walk returns a plausible number, which is the dangerous part:
a wrong count that looks like a count reads as verified.

## Spot it in 5 seconds

Ask what the inventory would be compared *against*:

```python
set(r["name"] for r in catalog() if r["kind"] == "legacy") == set(legacy.NAMES)
# False
```

If there is no authoritative set to compare against, that is the actual bug —
you have two sources of truth that can silently disagree. If there is one, the
equality check is a one-liner.

Secondary tell: a *classification* that changes when you move a definition
between modules without changing what it means. Labels must be derived from a
declaration, never from a location.

## Fix

Make the list declarative and let the walk *decorate* it, instead of the walk
*being* it.

```python
# one registry, one truth
LEGACY = {"stdev": {...}, "Fpdf": {...}, ...}

def catalog():
    rows = []
    for name, info in LEGACY.items():        # the inventory comes from here
        target = getattr(info["module"], info["target"])
        rows.append(build_row(name, signature_of(target), kind=info["kind"]))
    for modname in MODULES:                  # the walk only adds metadata
        ...
    return rows
```

Plus the assertion, in the test suite, so it cannot rot:

```python
def test_catalog_reports_every_registered_name_exactly_once():
    reported = [r["name"] for r in catalog() if r["kind"] == "legacy"]
    assert sorted(reported) == sorted(legacy.NAMES)
```

And dedupe by **name**, not by `id()`. `id()`-based dedupe *hides* duplicate
definitions instead of surfacing them — which is how the same alias sat defined
in three different modules, unnoticed, for the whole life of the project. The
`id()` dedupe was subtracting 8 rows and quietly lowering the total.

```python
seen.add(id(obj))     # hides "this alias is defined twice"
seen.add(attr)        # a duplicate name now trips the uniqueness test
```

## Globalise it

Every "discover the things by looking" step:

- `dir()` / `vars()` as a stand-in for a declared API (`__all__` exists for a
  reason, and it is also a claim that can be tested);
- plugin systems that enumerate entry points at import time;
- pytest collection: a test module that fails to import is *skipped*, so the
  suite goes green with fewer tests (an assertion on the *number* of collected
  examples is the guard);
- CLI subcommand lists built from a directory scan;
- `import *` re-exports.

The shape is constant: discovery is an approximation of a declaration, and it
fails open. Whenever a list is produced by introspection, either assert it
equals a declared list or accept that its completeness is unknown.

## Evidence

Real session, same file, before and after. Note the count moving in the
*unintuitive* direction — deleting duplicated definitions first made the total
*fall*, because the `id()`-dedupe had been hiding them:

```text
# id()-dedupe, aliases also defined inside the implementation modules
total 122 {'internal': 23, 'ti': 84, 'legacy': 15}

# name-dedupe, before the duplicates were deleted from the modules
total 133 {'internal': 23, 'ti': 87, 'legacy': 23}

# registry-driven, duplicates removed, missing rows emitted
total 130 {'internal': 23, 'ti': 84, 'legacy': 23}

# and the claim is now checked, not asserted
legacy.NAMES = 23        catalog() legacy rows = 23
```

Three different totals for the same codebase in one afternoon, none of which
raised anything.

## Takeaway

A discovered list is a guess about a declared list. If you can't name the
declaration it is supposed to match, you don't know that it does.
