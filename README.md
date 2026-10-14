# Family 180 paired-state finite audit

Independent, AI-assisted executable verification by **Erebos Labs** of finite
examples from OpenAI's *Paired states and Hamiltonian cycles in cubic bipartite
planar graphs*.

**The general theorem is already formalized upstream.** This repository adds a
finite Python audit and regression evidence. It claims no new general theorem,
proven novelty, or new Lean verification. See the pinned
[upstream scope](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/docs/180.md),
[paper](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/Paired-states-and-Hamiltonian-cycles-in-cubic-bipartite-planar-graphs-September-24-2026/build/paper.tex)
and [attribution](ATTRIBUTION.md).

## Verified finite scope

The v1.0.0 baseline contains four rooted embeddings: C4/C6/C8 bipyramids and
the coned cube, with 25 states and ten ordered disjoint pairs. Its fixed-second-
state involution checks are vacuous: every Q_s is a forest and every D group
contains one cycle. Byte-preserved baseline source/data is under
[`baseline/v1.0.0`](baseline/v1.0.0).

Version **1.1.0** adds one literal 12-vertex octahedron edge-expansion fixture,
1,728 incident assignments, nine states and ten ordered disjoint pairs.
It exercises the complete two-partner reversal orbit r0 ↔ r4 at second state
s8, with J=-3 ↔ -1, unchanged weight 4 and exact cancellation. A genuine
three-cycle D group has all eight orientations and gaps (1,1,1).

The two group sums and total are:

```text
Z3(x) = i exp(x)(exp(x)-1)^3
Z1(x) = i(1-exp(4x))
Z(x)  = i(1-exp(x)+3 exp(2x)-3 exp(3x))
```

The total begins 0, -4i, -8i, -(29/3)i; group and total Taylor coefficients
through degree 11 are checked exactly. No floating-point mathematics, solver,
graph library or numerical exponential is used.

## Reproduce

Use CPython 3.11 or newer. No dependencies need installing.

```sh
python3 verify_hashes.py
python3 verify_baseline.py
python3 replay.py
python3 independent_replay.py
python3 -m unittest -v test_nonvacuous
python3 -O replay.py
python3 -O independent_replay.py
python3 -O -m unittest -v test_nonvacuous
python3 run_mutations.py --output replay_output/mutations
python3 historical_mutants.py --output replay_output/historical-mutants
```

The new 32-test suite, original 27 tests and all replays pass in the local public
package validation. The twelve defined implementation mutants are detected;
the exact three mutants that escaped the original four-fixture suite also fail
on the new fixture. Test 32 now checks the byte-preserved public baseline,
replacing the private input-archive check. See [PUBLIC_REVIEW.md](PUBLIC_REVIEW.md)
and fresh [verification logs](verification/logs).

`independent_check.py` is the author's second rational-geometry implementation.
`independent_replay.py` is the separate audit implementation; it imports none
of the delivered checker/builder/validator modules. It independently enumerates
states and partners, verifies geometry and disks, reconstructs the orbit and
all orientations, and checks exact frequency dictionaries and rational series.
Agreement is evidence, not a formal proof of program correctness.

## Limits and provenance

One Q cycle, two partners and one reversal orbit are exercised. Larger fibers,
multiple Q-cycle choices, multiple orbits, even D-cycle counts, c_min>1 and
disconnected or isolated spoke graphs remain uncovered. No Lean build, axiom
audit or formal encoding proof was performed. See [LIMITATIONS.md](LIMITATIONS.md).
Fixture work stops at this bounded result.

This release is a clean public repackaging of the verified v1.1.0 input.
The original ZIPs and private execution/development records are excluded.
[provenance.json](provenance.json) records their hashes and publication adaptations.
Mathematical modules and certificates retain their audited bytes; executable
publication changes concern paths, baseline preservation and test packaging.
Historical authoring documents remain labeled as such; this independent review
and public verification supersede their earlier unreviewed/unreleased status.

New audit material is MIT licensed. Referenced OpenAI sources retain their
Apache-2.0 license. No unlicensed derivative code is bundled or adapted.
