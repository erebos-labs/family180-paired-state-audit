> Authoring record from the verified input. Publication and independent review
> status are updated in PUBLIC_REVIEW.md; original private ZIPs are not distributed.

# Review tables, v1.1.0

All data below are drawn from the delivered certificates. Both executable implementations recompute them from the fixture.

## Faces, orientation and color

| Face ID | Oriented vertices | Color | Role |
|---:|---|---|---|
| 0 | [0, 1, 2] | white |  |
| 1 | [0, 2, 9] | black | A |
| 2 | [0, 4, 11] | white |  |
| 3 | [0, 8, 4] | black | A |
| 4 | [0, 9, 8] | white |  |
| 5 | [0, 11, 1] | black | A |
| 6 | [1, 5, 7] | white |  |
| 7 | [1, 7, 2] | black | A |
| 8 | [1, 10, 5] | black | A |
| 9 | [1, 11, 10] | white |  |
| 10 | [2, 3, 9] | white |  |
| 11 | [2, 6, 3] | black | A |
| 12 | [2, 7, 6] | white |  |
| 13 | [3, 4, 8] | white |  |
| 14 | [3, 5, 4] | black | outer |
| 15 | [3, 6, 5] | white |  |
| 16 | [3, 8, 9] | black | A |
| 17 | [4, 5, 10] | white |  |
| 18 | [4, 10, 11] | black | A |
| 19 | [5, 6, 7] | black | A |

## State incidences

States are read in the face order `[1, 3, 5, 7, 8, 11, 16, 18, 19]`.

| Face | Allowed nonroot values |
|---:|---|
| 1 | [0, 2, 9] |
| 3 | [0, 8] |
| 5 | [0, 1, 11] |
| 7 | [1, 2, 7] |
| 8 | [1, 10] |
| 11 | [2, 6] |
| 16 | [8, 9] |
| 18 | [10, 11] |
| 19 | [6, 7] |

## Complete state list

| State ID | Values in A order | omega | Disjoint partner IDs | Q cyclic? |
|---:|---|---:|---|---|
| 0 | `[0, 8, 1, 2, 10, 6, 9, 11, 7]` | 1 | [8] | no |
| 1 | `[0, 8, 1, 7, 10, 2, 9, 11, 6]` | 2 | [7] | no |
| 2 | `[0, 8, 11, 2, 1, 6, 9, 10, 7]` | 2 | [6] | no |
| 3 | `[0, 8, 11, 7, 1, 2, 9, 10, 6]` | 3 | [5] | no |
| 4 | `[2, 8, 0, 1, 10, 6, 9, 11, 7]` | 0 | [8] | no |
| 5 | `[9, 0, 1, 2, 10, 6, 8, 11, 7]` | 2 | [3] | no |
| 6 | `[9, 0, 1, 7, 10, 2, 8, 11, 6]` | 3 | [2] | no |
| 7 | `[9, 0, 11, 2, 1, 6, 8, 10, 7]` | 3 | [1] | no |
| 8 | `[9, 0, 11, 7, 1, 2, 8, 10, 6]` | 4 | [0, 4] | yes |

## All ordered pairs

| Pair ID | r ID | s ID | J | Phase (real, imaginary) | omega(s) | D cycle lengths |
|---:|---:|---:|---:|---|---:|---|
| 0 | 0 | 8 | -3 | [0, 1] | 4 | [3, 3, 3] |
| 1 | 1 | 7 | -1 | [0, -1] | 3 | [3, 3, 3] |
| 2 | 2 | 6 | -1 | [0, -1] | 3 | [3, 3, 3] |
| 3 | 3 | 5 | 1 | [0, 1] | 2 | [3, 3, 3] |
| 4 | 4 | 8 | -1 | [0, -1] | 4 | [9] |
| 5 | 5 | 3 | -1 | [0, -1] | 3 | [3, 3, 3] |
| 6 | 6 | 2 | 1 | [0, 1] | 2 | [3, 3, 3] |
| 7 | 7 | 1 | 1 | [0, 1] | 2 | [3, 3, 3] |
| 8 | 8 | 0 | 3 | [0, -1] | 1 | [3, 3, 3] |
| 9 | 8 | 4 | 1 | [0, 1] | 0 | [9] |

## Complete fixed-s reversal orbit

| r | image | Q traversal | delta sum | J before | J after | J change | omega before/after |
|---:|---:|---|---:|---:|---:|---:|---|
| 0 | 4 | [0, 2, 1] | 3 | -3 | -1 | 2 | 4/4 |
| 4 | 0 | [0, 1, 2] | -3 | -1 | -3 | -2 | 4/4 |

The single orbit is `{0,4}` at fixed state 8. Its exact sum is `i*exp(4x)-i*exp(4x)=0`.

## Every integer incidence-spoke weight

| Face | Vertex | Weight |
|---:|---:|---:|
| 1 | 0 | 1 |
| 1 | 2 | 0 |
| 1 | 9 | 0 |
| 3 | 0 | 0 |
| 3 | 4 | 1 |
| 3 | 8 | 0 |
| 5 | 0 | 0 |
| 5 | 1 | 0 |
| 5 | 11 | 0 |
| 7 | 1 | 0 |
| 7 | 2 | 0 |
| 7 | 7 | 0 |
| 8 | 1 | 0 |
| 8 | 5 | 1 |
| 8 | 10 | 0 |
| 11 | 2 | 0 |
| 11 | 3 | 1 |
| 11 | 6 | 0 |
| 16 | 3 | 0 |
| 16 | 8 | 2 |
| 16 | 9 | 0 |
| 18 | 4 | 0 |
| 18 | 10 | 1 |
| 18 | 11 | 0 |
| 19 | 5 | 0 |
| 19 | 6 | 1 |
| 19 | 7 | 0 |

## Cycle groups

| Group | Pair IDs | Cycle count | Gaps | First degree | First coefficient (real, imaginary) |
|---:|---|---:|---|---:|---|
| 0 | [0, 1, 2, 3, 5, 6, 7, 8] | 3 | [1, 1, 1] | 3 | [0, 1] |
| 1 | [4, 9] | 1 | [4] | 1 | [0, -4] |

## Complete directly computed Taylor coefficients through degree 11

Each real/imaginary entry is `[numerator, denominator]`.

| Degree | Real coefficient | Imaginary coefficient |
|---:|---|---|
| 0 | [0, 1] | [0, 1] |
| 1 | [0, 1] | [-4, 1] |
| 2 | [0, 1] | [-8, 1] |
| 3 | [0, 1] | [-29, 3] |
| 4 | [0, 1] | [-49, 6] |
| 5 | [0, 1] | [-317, 60] |
| 6 | [0, 1] | [-499, 180] |
| 7 | [0, 1] | [-3089, 2520] |
| 8 | [0, 1] | [-4729, 10080] |
| 9 | [0, 1] | [-28757, 181440] |
| 10 | [0, 1] | [-6217, 129600] |
| 11 | [0, 1] | [-262649, 19958400] |
