> Authoring record from the verified input. Publication and independent review
> status are updated in PUBLIC_REVIEW.md; original private ZIPs are not distributed.

# Limitations and trust boundary

This version verifies ONE literal rooted embedded graph, not all graphs of
order at most 20 and not the unrestricted theorem. The old four examples remain
separate inherited fixtures. No graph census, root search, randomized generation,
or alternative construction was run.

## Bounds

The predeclared caps were 20 vertices of T, 200,000 candidate incident assignments
BEFORE injectivity filtering, 10,000 states, one fixture and two hours total actual
work. The candidate product is checked before enumeration. The actual counts are
12 vertices, 1,728 candidate assignments and 9 states. H0 has 21 vertices because
its nine black centers are auxiliary vertices; the cap applies to T, not to the
paper's auxiliary spoke graph. This convention does not enlarge the graph search.
Repeated replay and fault injection concern the same fixed input space.

## Scope of new coverage

The fixed state has a single triangular Q cycle and exactly two partners. There
is only one two-element reversal orbit. It does not exercise choosing among two
Q cycles using s alone, larger reversal fibers, or several orbits at fixed s.
A faulty selector whose error is observable only with multiple Q cycles could
still escape these tests. The actual selector is evaluated outside the partner
loop and takes only Q_s.

The multiple-cycle gap is no longer wholly absent: one valid D group has THREE
cycles and all eight orientations are verified. There is no two-cycle D group,
no other even cycle count, and the global minimum c_min is still one. These
uncovered cases must not be silently promoted to verified coverage.

The primary embedding class still requires a connected nonisolated H0. This
fixture meets that condition; disconnected H0 or isolated vertices remain outside
implemented input scope, though the paper permits them componentwise.

## Implementation and review

All arithmetic is exact, but Python, its standard library, the manually reviewed
encoding and these source implementations are trusted. The rational geometry
check is a separate implementation, not an independent person or agent. No Lean
proof of the encoding, build of upstream Lean, axiom audit, formal code correctness
proof, macOS execution or independent review of v1.1.0 occurred here.

The main replay and explicit orbit validator share some primary helpers. The
separate geometry checker does not import them, but was written by the same
assistant. Its role is described precisely in its source and specification;
agreement is evidence, not a general proof of software correctness.

Twelve specified implementation mutants were detected. This is not a guarantee
that every faulty implementation will be rejected. Some checks are logically
redundant, and deleting a redundant check may leave acceptance behavior unchanged.
Metadata-validation mutants test rejection of corrupted records, not a new
mathematical counterexample. No definitions of the Atlas mutants were received,
so no claim is made that those exact mutants are killed by this version.

## Source and duplication audit

The current default revisions matched the baseline's inspected revisions. The
new searches were bounded, and some results were only screened by names/snippets.
The two credited scripts and the newly read descent probe are not equivalent to
this signed reversal replay. Unread, private, unindexed or inaccessible artifacts
may contain equivalent work. No novelty or priority is asserted.

Upstream files were read through the GitHub connector, not saved as verbatim
container downloads. This ZIP contains exact local code, inputs, certificates,
source manifests and source-read records, not a complete upstream checkout.
The derivative repository's unlicensed code is not copied or adapted here.

## Stopping point

The authorized finite target succeeded without extending any search bound. No
further fixture was attempted. Preserve this baseline and seek a review of its
specific computations rather than starting another search in this follow-up.
