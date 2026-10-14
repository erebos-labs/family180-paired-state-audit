# Source and duplication audit

Session date: 2026-10-14. This is a bounded audit, not a proof that no other
implementation exists. No issue, pull request, message, or other external write
was made.

## Pinned authoritative source

Repository: `https://github.com/openai/math`

Revision: `1581d4cbdd69a0faf34b2089614fe2a814316a6a`

Paper:
`preprints/Paired-states-and-Hamiltonian-cycles-in-cubic-bipartite-planar-graphs-September-24-2026/build/paper.tex`

Required overview and entry point:
`lean/docs/180.md` and `lean/OAI/Combinatorics/Hamiltonian/Main.lean`.
They were read through the GitHub connector. The main theorem is inherited;
we did not compile it or certify its axioms.

The paper's setup and Sections 4-5 supplied all signed-state definitions used
by this checker. The source's later forest-lift, assembly, and corollary
material was also consulted but is not implemented or re-proved here. The
first full-file display was truncated; relevant sections were retrieved in
bounded ranges, including 340-670 and 670-end. No missing definition needed
for the implemented mechanism was filled in by a guess.

Relevant Lean dependencies inspected:

| File under `lean/OAI/Combinatorics/Hamiltonian/` | Inspected role / reading scope |
|---|---|
| TriangleSystem.lean | States, partners, thirdIndex, indexDelta, oppositeGraph; beginning through oriented-potential definitions, not a complete file audit |
| CycleReversal.lean | OppositeCycle, changedCorners, reverse, partner closure, involutivity, no fixed points; complete displayed file |
| PairPhases.lean | Phase change, fixed-second-state cancellation, orientation fibers and groupEquiv; initial display and end section read |
| PairPolynomials.lean | Common leading phase, polynomial state weights, group product, total nonvanishing, forest_pair_of_disk_circulation; beginning and ending inspected, not every intermediate proof line |
| StateDisk.lean | Incidence matching/disk counts and state_disk_delta; beginning and remaining 260-end sections read |
| Circulation.lean | Oriented triangular faces and white charges; displayed file read |
| ColoredDual.lean | Geometric incidence system, cycle_disk, weight differences; first 170 lines inspected |
| ExactDual.lean | Entry-point dependency and exact-dual realization route; first 120 lines inspected |

This is not a full transitive dependency audit. No `#print axioms`, Lean build,
comparison against challenge-statement source, or formalization of this checker
was run. Relevant differences were retained, notably the polynomial weights in
Lean versus exponential weights in the paper.

## Upstream history and artifact check

The repository's current default-head commit returned by the connector was the
requested pin. The latest commit metadata dated it 2026-10-12, and the
path-specific Hamiltonian history returned the initial publication commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a` dated 2026-10-06 as its single listed
entry. No subsequent edit of that path was found in this read.

The full preprint directory listing contained README.md, build/, and paper.pdf.
The build/ listing contained only paper.tex, references.bib, and
triangle-figure.tex. No executable signed-state checker was present in those
directories. The Hamiltonian Lean source directory and indexed code searches
were also inspected. The search for Hamiltonian Python code in openai/math did
not locate the requested audit.

The repository-wide Actions artifacts GET endpoint was rejected by the
connector's URL allowlist. We therefore did NOT inspect all CI artifacts.
Global code searches were noisy and not exhausted. These limitations rule out
any assertion that equivalent audits have been comprehensively excluded.

## Material derivative work found

Repository: `https://github.com/cjnott1999/barnette-conjecture`

Examined revision: `97bacb41f06fbecfc4029acc716620d51019318f`.
The README identifies its snapshot as 9 October 2026.

### Existing exact signed arithmetic

Path: `analysis/c136_signed_sum_independent.py`
Git blob: `e1d747f75aa348506433ce8985d00450c909e68b`.

This script was read, not executed by this session. It enumerates the three
states and two ordered disjoint pairs of a literal 8-vertex / C6-bipyramid
example. It performs integer determinant and signed-pair arithmetic and checks
three manually supplied bounded-face spoke circulations. Its reported signed
expression is `-i*(k^2-1)`, with a separate substitution `k=1+x`.

That is substantial prior overlap with our C6 arithmetic and must be credited.
The current package does not claim the first exact C6 signed-state calculation.
The script does not reconstruct a general rotation system, enumerate Q_s
cycles, implement the fixed-s sign-reversing involution, reconstruct all
undirected-cycle orientation fibers, or directly audit the paper's exponential
Taylor series on the requested fixture suite. It is therefore not an equivalent
implementation of the full requested verification target.

### Existing executable forest construction

Path: `collaboration/opus/opus_work/s11/paired_states_exec.py`
Git blob: `dc3483b9f87361b8ab91c647588e48380ce377ad`.

The script was read, not executed. It uses SAT and lazy cycle constraints to
find a good forest state, implements the later white-face-tree construction,
and checks a Hamiltonian-cycle output. It relies on local project imports and
Python-SAT. It does not enumerate the signed-state sum or check its involution
and Taylor mechanism. The README's reported random-trial and Lean-build results
are third-party reports, not computations performed by this handoff.

### Existing mathematical first-read audit

Path: `analysis/verify_paired_states_sept24_first_read.md`
Git blob: `ff67dfb6f31463295375ce9175de602536a1543e`.

This was read. It explicitly states that no computation was run for that
first-read audit, distinguishes its coverage limitations, and proposes finite
phase/involution/circulation tests resembling this task. It is useful prior
review, not an existing executable coverage certificate for these mechanisms.

### License boundary

The derivative README explicitly says no license has been chosen and default
copyright applies. None of the derivative scripts are copied or adapted into
this package. Their paths, revisions and blob hashes are recorded for attribution
and precise comparison. The new Python code was written from the mathematical
source definitions, not from those implementations.

## Decision on duplication

No equivalent complete executable signed-state audit was located in the
inspected paths and sources. A complementary finite replay was therefore built,
with explicit acknowledgment of the existing exact C6 work. This decision is
not established novelty. Unread, private, inaccessible, unindexed, or subsequent
artifacts can invalidate a broader absence claim; none is made.

## Source preservation and access limits

Upstream source text was accessible through connector reads. Direct network
transfer to the computation container did not succeed. The ZIP therefore
includes source provenance and an optional pinned retrieval helper rather than
pretending to contain byte-identical upstream source files. All new executable
source and all inputs/certificates are included and run offline.

`upstream/manifest.json` lists exact Git object hashes where returned by the
source reads. Git blob SHA-1 values identify `blob <length>\0<bytes>`, not raw-file
SHA-256. The package's separate SHA256SUMS file hashes its actual delivered
bytes. The optional downloader checks the Git blob hash before saving a file.
