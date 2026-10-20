# SP1.4 peak host memory

Source: `cycleN-mem.tsv` (column 2 = `free -m` "used" MiB, sampled every 5 s from before `env.sh up all` until after wait-ready and stats). Idle baseline: `free-idle.txt` (taken 2026-10-20 21:06 before cycle 1).

| run | samples | peak used MiB | delta vs idle (8043 MiB) |
|---|---|---|---|
| idle | 1 (free-idle.txt) | 8043 | 0 |
| cycle 1 | 15 | 9925 | +1882 |
| cycle 2 | 15 | 9898 | +1855 |
| cycle 3 | 15 | 9896 | +1853 |

Note: the mem-tsv sampler is a 5 s poll; a sub-5 s spike would not appear. The peak is the max of the sampled values.

## docker stats per container (cycle 3, after wait-ready, `docker stats --no-stream`)

| container | MemUsage |
|---|---|
| oidf-server-1 | 695MiB |
| certify-certify-1 | 671.1MiB |
| verify-service | 380.8MiB |
| oidf-mongodb-1 | 74.42MiB |
| certify-database-1 | 43.27MiB |
| postgres-db | 45.05MiB |
| certify-certify-tls-1 | 18.57MiB |
| certify-certify-nginx-1 | 14.6MiB |
| oidf-nginx-1 | 17.2MiB |
| verify-verify-tls-1 | 15.61MiB |

Source: `evidence/sp1/SP1.4/cycle3.log`. Sum of the ten stats rows is about 1976 MiB, versus a host `free` delta of about 1853 MiB at cycle 3 peak. The two figures are not reconciled; the difference is not explained by this run [unknown].

Compared with `evidence/sp0/resources.log` (suite + Certify peak 9.0 GiB host used): this run peaked at 9925 MiB (about 9.7 GiB) host used in cycle 1, about 0.7 GiB above that figure; the SP0 number and this one may use different measurement methods, not compared here [observed: evidence/sp1/SP1.4/cycle1-mem.tsv].
