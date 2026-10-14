> Authoring record from the verified input. Publication and independent review
> status are updated in PUBLIC_REVIEW.md; original private ZIPs are not distributed.

# Results v1.1.0

## New fixture only

| Quantity | Exact result |
|---|---:|
| Triangulation vertices / edges / faces | 12 / 30 / 20 |
| Black / white faces | 10 / 10 |
| Roots | 3,4,5 |
| Nonroots / bounded black faces | 9 / 9 |
| Full candidate incident assignments | 1,728 |
| States | 9 |
| Ordered disjoint pairs | 10 |
| Cyclic Q_s states | 1 |
| Cyclic Q_s states with a disjoint partner | 1 |
| Partners of the qualifying state | 2 |
| Complete reversal orbits | 1 two-element orbit |
| Directed reversal transitions checked | 2 |
| D groups | 2 |
| D group cycle counts | 1 and 3 |
| Bounded H0 faces | 7 |
| Separating triangles | 0 |

Every candidate graph quantity above is recomputed from the input rotation system.
The second checker also uses exact rational geometric rotations, 309 nonincident
edge-pair tests, all Cartesian incident assignments and exhaustive edge-subset
cycle detection. The latter examines 512 subsets for each nine-edge Q or D, not
a graph search or new fixture construction.

## Fixed-state result

In face order (1,3,5,7,8,11,16,18,19):

```text
s  = (9,0,11,7,1,2,8,10,6)   [id 8]
r0 = (0,8,1,2,10,6,9,11,7)   [id 0]
r4 = (2,8,0,1,10,6,9,11,7)   [id 4]
```

Q_s has cycle (0,1,2). Its complete partner set is {r0,r4}. Reversal changes only
faces 1,5,7, and maps r0 to r4 and r4 to r0. J changes from -3 to -1 and back,
so its changes are +2 and -2 and phases are +i and -i. The complete second state
is unchanged; the computed integer weight is 4 in both cases. The exact fiber
sum is i exp(4x)-i exp(4x)=0.

## Full cycle-group and Taylor identities

The three-cycle group has all eight orientations and weight gaps (1,1,1):

    Z_3(x) = i exp(x)(exp(x)-1)^3.

Its first nonzero coefficient is +i in degree 3. The one-cycle group has two
orientations and weight gap 4:

    Z_1(x) = i(1-exp(4x)).

Its first coefficient is -4i in degree 1. The complete sum is

    Z(x) = i(1-exp(x)+3 exp(2x)-3 exp(3x)).

The frequency-4 exponential terms cancel between DIFFERENT D groups at the
fixed state. The direct Taylor coefficients through degree 11 agree with the
cycle product and exact convolution; see REVIEW_TABLES.md and full JSON data.
The first few coefficients are 0, -4i, -8i, -(29/3)i.

## Tests and inherited replay

All 32 new tests pass in ordinary and optimized Python. All twelve defined
implementation mutants are killed by semantic tests; the unmodified control
passes. The actual mutation sources are defined as exact patches, with syntax
checks, hashes, test failures and process return codes. These are not the
unspecified Atlas mutants.

The original archive again passes its exact SHA-256 check, all 41 original file
hashes, all four fixture replays and all 27 original tests. The four inherited
fixtures still total 25 states and 10 ordered pairs. Across the old four and
this new fixed graph, the bookkeeping totals are 34 states and 20 ordered pairs;
this is not a census of triangulations or a claim of graph-family completeness.

## Interpretation

The requested nonvacuous finite cancellation target succeeded. The same single
fixture also removes the complete absence of multiple-cycle D coverage, through
a three-cycle example. Larger reversal fibers, multiple Q-cycle choices, even
D-cycle counts, c_min>1, and disconnected/isolated spoke graphs remain uncovered.
No new general theorem, unrestricted correctness guarantee, novelty claim, Lean
build or independent worker review is attached to this result.
