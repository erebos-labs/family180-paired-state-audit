> Authoring record from the verified input. Publication and independent review
> status are updated in PUBLIC_REVIEW.md; original private ZIPs are not distributed.

# Current source and duplication check

Date: 14 October 2026. This is a bounded check, not proof that no equivalent
verification exists. Public GET/read/search operations only were used.

## Baseline and current revisions

The actual mounted baseline archive was available and its SHA-256 matched before
extraction. It was extracted only into a separate working directory. The required
baseline specification, status, limitations, generator/checker code and source
audit were read rather than reconstructed from the previous answer.

The current default-head commit returned for openai/math was still
1581d4cbdd69a0faf34b2089614fe2a814316a6a (12 October 2026). The current default-head
commit returned for cjnott1999/barnette-conjecture was still
97bacb41f06fbecfc4029acc716620d51019318f (9 October 2026). Thus neither inspected
default branch had advanced beyond the baseline's audited revisions. A subsequent
upstream PR-list read returned the known administrative/update PRs, not a new
paired-state verification contribution. This does not exhaust every branch or CI
artifact.

## Definition reads in this follow-up

Repository: https://github.com/openai/math
Pin: 1581d4cbdd69a0faf34b2089614fe2a814316a6a

| File | Range read in this follow-up | Definition/claim used | Git blob SHA-1 |
|---|---|---|---|
| preprints/Paired-states-and-Hamiltonian-cycles-in-cubic-bipartite-planar-graphs-September-24-2026/build/paper.tex | 210-260 and 350-515 | roots, incident bijections, ordered disjoint pairs, Q_s, disk signs, J, exponential weight, fixed-s reversal, spoke circulation | 01dd9e0c56b84f77c2051379e1202821bc2164cd |
| lean/OAI/Combinatorics/Hamiltonian/TriangleSystem.lean | 1-142 | State, Partner, thirdIndex, indexDelta, oppositeGraph | eea928c0019bd2e4b6faf3ab56a9acb39b992bc6 |
| lean/OAI/Combinatorics/Hamiltonian/CycleReversal.lean | 120-275 (through end) | changedCorners, reverse, reverse_partner, reverse_reverse, reverse_ne, reversal_involutive | d39e19f0e53942f7370e91329fd58b158a6eef8b |
| lean/OAI/Combinatorics/Hamiltonian/PairPhases.lean | 1-118 | phase, rawIndexSum, reverse_rawIndexSum_diff, reverse_phase, fixed_second_state_cancels | edeacc4405c2bf3306ce9727db5c6db53fdc3a18 |

The remaining inherited setup, cycle-product and weight-construction specification
was read in the actual baseline specification and its referenced source record.
The earlier source reads of Main.lean, docs/180.md and other dependencies are
preserved in the baseline's SOURCE_AUDIT.md. They were not all reread or compiled
in this follow-up. No transitive Lean dependency or axiom audit was performed.
Git blob SHA-1 is not a raw-file SHA-256; the new SHA256SUMS hashes actual bundled
bytes only.

## Equivalent nonvacuous verification search

Before new enumeration, the default heads and the baseline's credited artifacts
were compared. Additional current indexed searches in the credited derivative
used `involution`, `Q_s`, and the joint queries `Q_s involution` and
`involution phase`, restricted to Python for the precise joint queries. The
`Q_s involution` Python query returned zero results. Broader results included old
unrelated involution work and the state-descent program; these were screened by
path/snippet rather than every file being read in full. Public web searches for
the paired-state involution audit did not yield a usable matching primary source.
No conclusion is based on the unrelated web result returned.

The existing credited files remain relevant prior overlap:

- `analysis/c136_signed_sum_independent.py`: exact C6-bipyramid signed arithmetic,
  three states and two ordered pairs, but no cyclic-Q_s reversal implementation.
- `collaboration/opus/opus_work/s11/paired_states_exec.py`: SAT-based forest-state
  and Hamiltonian-cycle construction, not a signed involution certificate.
- `analysis/verify_paired_states_sept24_first_read.md`: mathematical review whose
  finite involution tests were recommendations, not executed verification.

Their baseline read records, exact blob identifiers and license boundary are
preserved unchanged. They are not presented as new findings of this follow-up.

A newly read relevant file was
`collaboration/opus/opus_work/s11/descent_probe.py`, blob
`aaf02c8ba24c434c63d946d315d1022477b17213`, at derivative revision 97bacb41...
It exhausts states of small generated graphs to study whether local state moves
decrease a Q_s component-count potential. It imports lattice_probe and graph
census helpers, not a fixed-second-state sign-reversing orbit audit. It was read,
not run or copied. Its existence does not establish that the new fixture is a
new graph or the first occurrence of a cyclic Q_s.

**Decision before enumeration:** no equivalent nonvacuous executable signed
reversal audit was located in the inspected work, so the one predeclared fixture
attempt proceeded. The result is not an established novelty or priority claim.

## Access and licensing limits

The baseline recorded an inaccessible repository-wide Actions-artifact endpoint.
This follow-up did not obtain or inspect all Actions artifacts, all repository
branches, private work or unindexed derivative files. Current default-head reads
and indexed searches cannot rule out equivalents in those places.

Upstream text was read via GitHub connector tools. No upstream files were
materialized as verbatim container copies in this follow-up. The package includes
actual local sources and the pinned provenance manifests, not a claimed full
upstream checkout. No unlicensed derivative code is redistributed or adapted.
The baseline's MIT notice for its local code is retained; upstream source
references retain the upstream Apache-2.0 attribution and the derivative's
reported no-license boundary.
