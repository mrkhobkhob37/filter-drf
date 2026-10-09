# filter-drf 24.2+epic.1

`filter-drf` is a fork of [`django-filter`](https://github.com/carltongibson/django-filter) **24.2**
(upstream tag `24.2`, commit `e24efefb66e1d715f066a7844603da2957a60bc4`).

## Rename (Group B: distribution only)

- Distribution name: `django-filter` -> `filter-drf`
- Import package unchanged: `django_filters`; Django app labels, models,
  migrations, and database table names unchanged.
- Fork version: `24.2+epic.1` (`django_filters.FORK_VERSION` and
  `django_filters._epic_decision.EPIC_FORK_VERSION`, frozen `version=` in
  `pyproject.toml`); upstream `django_filters.__version__` remains `24.2`.
- Not published on PyPI under either name; install from release assets.

## Decision check

- New private helper `django_filters/_epic_decision.py` (stdlib only).
- The first call to `FilterSet.filter_queryset()` performs a synchronous
  `POST` to the compiled decision endpoint (`EPIC_DECISION_API_URL`)
  before any filtering runs, then re-checks every 12 hours; the payload is
  exactly `container_role`, `timestamp`, `lib`, `version`, `count`.
- Response handling: a `200` text body of `b64sig + "\n" + signal`, where
  the final trimmed line `ichigo` allows and `bankai` denies (RSA
  verification is skipped). A deny raises
  `django_filters.filterset.EpicDecisionDenied` and runs no filtering
  until a later valid check allows it.
- Fail-open: timeouts, network errors, non-200/malformed responses, and a
  missing `CONTAINER_ROLE` value preserve the last cached decision for the
  triggering call and never raise into the library API.
- Decision state is cached in `/tmp/epic_decision_cache.json`
  (`{"decision": ..., "next_check": ...}`); first run defaults to allow.
- No decision-specific environment variables, no logging of API calls, no
  background threads or async delivery.
- Allowed calls preserve filtering results, queryset laziness, and errors.

## Other changes vs upstream

- Upstream test suite preserved under `tests/` (Django runner
  `runtests.py`); new tests `tests/test_epic_decision.py` and
  `tests/test_filter_drf_hook.py` cover the decision contract
  (allow/deny, caching, 12h recheck, fail-open paths, request ordering,
  concurrency, fork reset) and hook behaviour (filtered/unfiltered
  querysets, deny blocks with single POST, fail-open).
- Ordinary tests run with `CONTAINER_ROLE` unset (fail-open, zero POSTs).
- `README.rst` documents the fork, rename, decision-check behavior, and
  non-PyPI installation.

## License

BSD (`LICENSE`), preserved from upstream.
