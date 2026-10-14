# Independent review and public-distribution checks

Reviewed 14 October 2026 by a separate AI-assisted audit under Erebos Labs.
No result-changing mathematical or implementation error was found in the five
literal rooted fixtures or the executed v1.1.0 reversal and product identities.
This is finite executable verification, not an unrestricted theorem audit or
formal proof of the Python implementations.

## Findings

The v1.0.0 baseline's four literal fixtures reproduce 25 states, ten ordered pairs
and exact signed exponential sums. All Q_s are forests and all D groups have one
cycle, so that baseline alone does not execute the cancellation mechanism.

The new 12-vertex graph is the declared three-edge expansion of an octahedron.
Its 30 edges, 20 triangular faces, face coloring, roots {3,4,5}, and absence of
separating triangles were independently checked. Exact projected coordinates
pass all 309 nonincident edge-pair tests, vertex-on-edge checks and facial
orientation checks. The complete 1,728-assignment space yields nine states and
ten ordered disjoint pairs.

The only cyclic second state is s8. Its complete partner set is {r0,r4}; the
chosen Q cycle is the triangle on {0,1,2}. Reversal changes exactly three black
face assignments and is the transposition r0 ↔ r4. The bounded disk is one white
triangle, with I=B=l=0, W=1 and h=3. Indices -3 and -1 change by ±2; phases +i
and -i negate while the full second-state incidence vector and weight 4 remain
unchanged. Its exact exponential sum is zero.

The same graph has a three-cycle group with all eight orientations and gaps
(1,1,1), plus a nine-cycle group with gap 4. Complete group frequency dictionaries,
positive detour integrals, leading orders/phases, and every group and total
Fraction Taylor coefficient through degree 11 agree. The total is
`i(1-exp(x)+3 exp(2x)-3 exp(3x))`, beginning 0, -4i, -8i, -(29/3)i.

The separate `independent_replay.py` imports none of the author's implementations.
It uses Cartesian enumeration, union-find, exhaustive Q edge subsets, direct
spoke rotations and exact horizontal-ray parity geometry. Its reconstructed
complete orbit certificate agrees field by field, and its full orientation
sets, frequency dictionaries and rational coefficients agree with the primary
certificate. Some shared mathematical encoding assumptions remain in the trust
base; agreement is not formal program verification.

The author's twelve defined mutants are killed by identified semantic tests.
The three exact earlier mutations—discard cyclic fibers, require zero reversal
index change, and forget previous cycle factors—are also now rejected by both
tests and replay. These controls demonstrate the formerly missing coverage;
metadata-validation mutants should not be read as independent mathematical
counterexamples or exhaustive bug detection.

## Publication adaptation and observed checks

The verified input archive hash is recorded in provenance.json. Its original
75-file manifest and immutable baseline archive passed locally before packaging.
The public distribution has its own SHA256SUMS and fresh execution records.
It excludes original archives, transfer helpers, credentials, account information,
private execution/development records and upstream source snapshots.

The baseline source/data subset is byte-preserved. The public baseline replay
checks those file hashes and reruns four fixtures and 27 tests. Test 32 of the
new suite checks this public subset instead of a private ZIP. The independent
replay is relocated to repository-relative inputs and ignored output storage;
its mathematical implementation is unchanged. No other primary mathematical
module or certificate was changed for publication.

Fresh public-package checks on macOS arm64 / CPython 3.14.7 pass: baseline replay,
primary/fiber/author geometry replay, separate independent replay, 32 new tests
in normal and optimized Python, all twelve defined mutants and all three
historical mutants. Detailed commands, return codes and outputs are in
verification/. Traceback workspace paths in public logs are normalized; full
private execution records remain preserved locally. GitHub CI repeats these
checks on Python 3.11 and 3.13; its actual status is visible in Actions.

## Scope and stopping point

The general theorem is already formalized upstream at the pinned OpenAI revision.
No new theorem, proven novelty, Lean build, axiom audit, human referee review or
formal encoding proof is claimed here. The new fixture exercises one Q cycle,
two partners and one orbit. Larger fibers, multiple Q-cycle choices, even D-cycle
counts, c_min>1 and disconnected/isolated spoke graphs remain unverified.

The bounded finite follow-up is complete. Retain this regression baseline and
stop fixture work here. Publication does not expand its mathematical claims.
