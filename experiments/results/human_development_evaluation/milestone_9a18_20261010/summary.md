# Pooled development evaluation

VALID_COMPLETED_DEVELOPMENT_POOLED

Single researcher; synthetic corpus; development queries; pooled ideal denominator. No final effectiveness or significance claim.

Main evaluation: NOT RUN. Null cells mean NOT COMPUTED, not zero.

| Method | Precision@5 | Precision@10 | MRR@10 | nDCG@10 (pooled) |
|---|---:|---:|---:|---:|
| R1 | 0.633333 | 0.494444 | 0.722222 | 0.517324 |
| R2 | 0.622222 | 0.500000 | 0.784722 | 0.524130 |
| R3 | 0.744444 | 0.577778 | 0.972222 | 0.663459 |
| R4 | 0.711111 | 0.588889 | 0.944444 | 0.646549 |

nDCG@5 tersedia pada JSON/CSV. Ideal ranking mencakup seluruh human-resolved pool per query.
Precision/MRR: grade >=1. nDCG: gain 2^grade-1; discount log2(rank+1).
Completion: 654/654 RESOLVED; 0 missing; 0 UNRESOLVED.
