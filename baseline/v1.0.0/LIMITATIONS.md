# Limitations and trust boundary

The full theorem is not the subject of a new claim. This package checks four
finite embeddings with one specified outer black face each. It does not prove a
statement about all bipyramids, all small Eulerian triangulations, or arbitrary
cubic bipartite planar graphs.

**The main missing execution is the involution.** All Q_s are forests. Its code
exists, but its partner-closure, involution, fixed-point, and phase-change branch
has no valid geometric execution in this run. Arithmetic phase-shift tests and
a standalone DFS triangle test must not be represented as such an execution.

Every observed D is one cycle. The coned cube has two DIFFERENT undirected groups,
not two cycles in one group. It tests addition of common-phase group
contributions, but not geometric multi-cycle multiplication. An algebra-only
two-factor test is explicitly separated from graph coverage.

H0 must be connected with no isolated vertices in this implementation. All four
fixtures were checked to meet that restriction. The paper's componentwise
circulation construction also permits disconnected components and isolated
vertices; those cases are outside this package's implemented input scope.
The original Q_s graphs do retain isolated original vertices.

Cycle orientations are computed by dual face flood-fill on a genus-zero
rotation system. The relation between such combinatorial embeddings and sphere
embeddings uses the usual surface construction/classification and the Jordan
separation argument in the human specification. That bridge has not been
formalized in Lean here. Python, integer arithmetic, Fraction, and manually
reviewed code are trusted. Certificate checks recompute data but share code with
the certificate generator; only state counts/enumeration and Q acyclicity have
additional, separately written algorithms in the test suite.

A malformed JSON input may raise a standard Python exception rather than the
custom Rejected exception. This is a research checker for the supplied files,
not a hardened parser for hostile data. All tested corruptions are rejected;
there is no claim that a finite mutation suite exhausts all software defects.

Weight freedom matters. Changing a bridge weight need not change any face
circulation. Such a weight can remain mathematically valid. The low-level
circulation validator accepts it; the canonical certificate replay rejects it
because the declared deterministic weight construction no longer reproduces
it. The nonbridge mutation test separately establishes rejection by the actual
unit-circulation equations. See CHANGELOG.md for the preserved initial test
mistake. This is not a counterexample to the circulation lemma.

The duplication audit is bounded to inspected upstream paths/history and
relevant indexed derivative files. Global code search was noisy and not read
exhaustively. Actions artifacts, inaccessible or unindexed material, private
repositories and future work may contain equivalent audits. 'Not located' is
not 'does not exist' and not an established novelty claim.

The archive includes all newly written code and data, not a complete verbatim
copy of openai/math. Upstream sources were read through the GitHub connector.
The pinned source manifest/download helper records how to retrieve them, but
container network transfers failed in this session. The optional helper is
not part of the offline proof/checking dependency chain. No unlicensed code
from cjnott1999/barnette-conjecture is redistributed.

Neither Lean nor lake was found in PATH. No Lean build, axiom audit, formal
encoding theorem, independent referee review, macOS run, or claim of unrestricted
correctness of the newly written checker is made.
