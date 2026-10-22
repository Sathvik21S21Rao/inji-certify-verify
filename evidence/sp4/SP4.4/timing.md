# SP4.4 timing (seconds, from each run's timing.tsv)

| run | up | tests | combined | down | total |
|---|---|---|---|---|---|
| kg-combined-seq1 | 69 | 21 | 0 | 13 | 103 |
| kg-combined-seq2 | 68 | 20 | 1 | 13 | 102 |
| kg-combined-seq3 | 68 | 21 | 0 | 14 | 103 |
| kg-combined-par1 | 68 | 14 | 0 | 14 | 96 |
| kg-combined-par2 | 68 | 14 | 0 | 14 | 96 |
| kg-combined-par3 | 68 | 14 | 0 | 13 | 95 |
| kg-certify-shim-on | 45 | 17 | - | 13 | 75 |
| fault-certify-shim-off | 45 | 8 | - | - | 53 |
| fault-certify-shim-on | 45 | 16 | - | 13 | 74 |
| fault-combined | 68 | 21 | 0 | 14 | 103 |
| c014-certify-shim-off | 347 (up failed, exit 3, both attempts) | - | - | - | - |

Mean over seq1..3 (combined, sequential): total=102.7
Mean over par1..3 (combined, parallel): total=95.7

Peak used MiB (free -m, 5 s samples) for par runs:
- kg-combined-par1: peak used=8961 MiB, min available=6438 MiB
- kg-combined-par2: peak used=8876 MiB, min available=6523 MiB
- kg-combined-par3: peak used=8813 MiB, min available=6586 MiB
