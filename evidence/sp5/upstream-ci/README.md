# Oracle 5: the api-test patches under each repo's own push-trigger.yml (22 Oct 2026)

Public forks: `github.com/Sathvik21S21Rao/inji-certify` and `github.com/Sathvik21S21Rao/inji-verify`. Each has two branches:
- `release-conformance-base`: the pin (`0d52155` / `64b2790`), unchanged.
- `release-conformance-patch`: the pin plus `testrig-bridge/inji-<c>.patch` (Certify 6 files +384/−3, Verify 5 files +377/−2).

Both branches match the workflows' `release*` push trigger.

| Repo | Run (base / patch) | `build-maven-apitest-*` | `build-apitest-*-local` | Every job, base vs patch |
|---|---|---|---|---|
| inji-certify | 39762805079 / 39762803343 | success / success | success / success | identical (`inji-certify-{base,patch}-jobs.tsv`, 12 jobs) |
| inji-verify | 39762815235 / 39762814445 | success / success | success / success | identical (`inji-verify-{base,patch}-jobs.tsv`, 18 jobs; `run-apitest-pr` success on both) |

Both runs are red overall, base and patch alike, for jobs that need MOSIP's secrets. For example, `build-dockers` stops at `docker login` with "Cannot perform an interactive login from a non TTY device", because the fork has no Docker Hub credentials (`*-build-dockers.log`). The patch changes no job's conclusion. Result: the patched api-test modules build under the repos' own CI wherever the unpatched ones do.
