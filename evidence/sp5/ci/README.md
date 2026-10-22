# GitHub Actions runs (22 Oct 2026, ubuntu-24.04, fresh runners, testrig driver)

| Run | Inputs | certify | verify | combined | Run conclusion |
|---|---|---|---|---|---|
| 39751717857 | fault=none, shim=false | GREEN 14 ok (7m49s) | GREEN 9 ok + 11 ok (7m13s) | GREEN, all 3 gates (12m9s) | success |
| 39751732547 | fault=strip-credential-endpoint, shim=false | RED new_failure 1 (5m29s) | GREEN (4m52s) | RED certify-shim-off new_failure 1 (9m51s) | failure (as intended) |

- Gate tables: `art-<run>/conformance-<target>/<config>/gate.md`. The red rows are `NEW_FAILURE` on `oid4vci-1_0-issuer-metadata-test` (`VCICheckRequiredMetadataFields`), the same as local `evidence/sp4/SP4.14/tr-fault-i.log`.
- The combined known-good timing on a fresh runner (`art-39751717857/conformance-combined/timing.tsv`): build 395 s, up 135 s, tests 151 s, total 703 s. That includes the first clone of the upstream repos and two Maven builds (cold-start M-i on a GitHub runner).
- MinIO uploads on the runner: `art-*/conformance-*/minio-ls.xml`, with one `full-report` per config.
- `run-<id>.txt`: `gh run view` output. `log-39751732547.txt`: the full log of the red run. `log-39751717857-{certify,verify,combined}.txt`: the job logs of the green run, from the jobs API.
- The source commit is `89f5574` (public repo), as recorded in `run-info.txt`.
- An earlier pair of dispatches (39751587588, 39751603413) failed in `setup-java` before any test ran: `cache: maven` needs a `pom.xml`. Fixed by `cache-dependency-path: compose/.env.pinned`.
