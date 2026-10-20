Vendored OIDF conformance suite client (MIT, see LICENSE.txt), unmodified.
Source: upstream/conformance-suite/scripts/conformance.py @ 7d420f716 (release-v5.3.3 pin, ADR-002).
sha256: 660214cc6ca9b3c09297f61908a575db7b1552e8f44eecd5740d1c27fa2cfca8
Why not run-test-plan.py: it handles WAITING with hard-coded per-test-family logic (run_test_module, lines 287-330),
and it is a hyphenated script with module globals, so it is not importable; our handoff plugins need that hook.
