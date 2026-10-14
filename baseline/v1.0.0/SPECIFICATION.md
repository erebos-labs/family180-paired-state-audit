# Mathematical specification and verification argument

## 1. Source and scope

The definitions below are extracted from the pinned paper, principally its
state setup, Lemma 4.1, Proposition 5.1, Lemmas 5.2 and 5.3, and the equations
(5.1), (5.2), (5.4), and (5.5) for the index, sum, product, and leading term.
The exact revision and source paths are in `upstream/manifest.json`.
They are inherited mathematics, not claims of a new contribution.

The investigation target is finite verification of this mechanism on the three
requested bipyramids, followed by at most one explicitly constructed additional
fixture. The additional fixture is the coned cube, with exactly 14 vertices.
There is no quantification over all triangulations of order at most 14 in the
reported result. No coordinate symmetry, coefficient invariance, or restriction
of the enumerated states is imposed.

## 2. Definitions, assumptions, and quantifiers

Let T be a finite connected simple graph cellularly embedded in an oriented
sphere, with at least four vertices. Every face boundary is a simple triangle.
Faces are colored black or white, with opposite colors across every edge. Fix a
black face t0 as the outer face of the corresponding plane embedding. Its three
vertices are the roots R. Set

    A = {black faces other than t0},   X = V(T) minus R.

If there are k black faces, side counting and Euler give k white faces,
3k edges, k+2 vertices, and |A|=|X|=k-1. A state is a bijection r:A -> X with
r(t) a vertex of t for every t. A pair is an ORDERED pair (r,s) of states such
that r(t) != s(t) for EVERY t in A. This is pointwise incidence disjointness,
not disjoint ranges of vertices: both ranges are X.

Q_s is the spanning subgraph on all vertices of T, with the edge opposite s(t)
in each t in A. No such edge is repeated, since each edge has exactly one black
incident face. The roots and any isolated vertices are retained.

For an oriented edge u->v, delta(u,v)=+1 precisely when its black incident face
is on the left; otherwise delta(u,v)=-1. Thus delta is antisymmetric. In
particular, the counterclockwise boundary directions of a bounded black
triangle have sign +1. For a pair define

    D(r,s) = {edge directed r(t) -> s(t) : t in A},
    J(r,s) = (1/3) sum_t delta(r(t),s(t)).

The code checks divisibility by 3 BEFORE integer division. It never uses
floor-division as a substitute for the integrality assertion. Because r and s
are bijections, each nonroot has one incoming and one outgoing edge. The
underlying edges are distinct; consequently D is a vertex-disjoint union of
simple cycles of length at least 3 covering X.

Every state-directed simple cycle C has delta-sum -3 when counterclockwise and
+3 when clockwise (paper Lemma 4.1). For its bounded disk, h is the boundary
length, I the number of strictly interior vertices, B and W the numbers of
black and white faces, and l the number of boundary edges whose black face is
inside. The identities checked are

    B+W = 2I+h-2,  3(B-W) = 2l-h,  B = I+l.

The matching identity is checked using the actual state supplying every tail.
This statement is not extended to arbitrary oriented cycles.

Place a center in each bounded black triangle, and connect it to its three
vertices inside that triangle. H0 is the graph of these incidence spokes,
including original vertices. A weight a(t,v) is assigned to EVERY spoke,
including root incidences. Traversing center(t)->v contributes a(t,v), and the
reverse contributes its negative. The paper permits real weights; this finite
replay chooses integer weights by the paper's dual-path construction.

For a state s, omega(s)=sum_t a(t,s(t)); roots never occur in this particular sum.
The phase and the paper's finite exponential sum are

    phase(r,s) = i^J(r,s),
    Z(x) = sum_(r,s) phase(r,s) exp(x omega(s)).

## 3. Fixed-s cancellation specification

For EVERY enumerated s for which Q_s is cyclic, choose a simple undirected cycle
C_s using ONLY s, the fixed embedding and vertex labels. The implementation uses
a sorted-neighbor DFS on Q_s, starting at the least unvisited vertex, and
canonicalizes the first cycle found. It does not choose a cycle separately for
each partner r.

For EVERY partner r of that s, let u(t) be the third vertex of t besides r(t)
and s(t). Orient opposite edges r(t)->u(t). The checker is specified to verify
that C_s becomes a directed root-avoiding cycle. Change r(t) to u(t) on exactly
the supplying faces of C_s and leave other values unchanged, obtaining r'. It
checks all of the following, directly on the reconstructed states:

* r' is an incident bijection A->X and is a partner of s;
* the map on the complete partner set is a bijection, has no fixed point, and
  its second application restores r;
* the local identity delta(u,s)-delta(r,s)=2 delta(r,u) holds on every changed
  triangle, and the actual disk identity gives J(r',s)-J(r,s) in {-2,+2};
* the phases negate and the exponential exponent remains omega(s);
* the complete fixed-s exponential polynomial is identically zero.

**Executed coverage:** in this package the set of cyclic s is empty for all four
fixtures. These loops have zero iterations. The code being present and the
universal loop passing do not constitute a nonvacuous test of the involution.
There is no claim that the unexercised branch is independently validated.

## 4. Rotation-system encoding and orientation independence

An input contains counterclockwise cyclic neighbor lists, one outer oriented
triangle, and redundant claimed faces and colors. Vertex labels are consecutive
nonnegative integers. The checker derives the left-face permutation of darts by

    (u,v) -> (v, predecessor of u in the cyclic neighbor list at v).

It verifies symmetric simple adjacency, connectedness, unique vertex neighbors,
all dart orbits, three distinct corners in every orbit, and V-E+F=2. Gluing an
oriented disk into each face orbit of this rotation system produces a connected
closed orientable surface. The ordinary classification of orientable surfaces
identifies Euler characteristic 2 with the sphere. This standard mathematical
bridge is part of the human specification, not a Lean-verified encoding theorem.
The redundant oriented faces and a freshly computed dual BFS coloring must
match the input's face claims exactly.

For a simple cycle, the checker removes its edges from the dual adjacency,
flood-fills the face component containing t0, and treats the other component as
the bounded interior. It requires exactly two components and a consistent side
for every cycle dart. Counterclockwise means that this bounded interior is on
the left. In particular, the orientation is NOT inferred from delta-sum, phase,
or the desired sign of a weight gap.

The spoke embedding is obtained by stellar subdivision of every bounded black
triangle followed by deletion of every original T edge. The new face regions
are recomputed by union of stellar face regions across deleted edges, and the
outer region is the one containing t0. Independent dart-face reconstruction on
the restricted spoke rotations must agree with that region correspondence.

**Explicit implementation restriction:** the current Embedding implementation
requires connected nonisolated H0. All four fixtures satisfy this. The paper
allows disconnected H0 and isolated vertices and works componentwise; that
additional case is not implemented or verified here. This restriction belongs
to the finite checker, not to the original theorem or its extracted definitions.

## 5. Exhaustiveness and independent counting

For each t in the fixed ordered list A, the only candidate values are the
recomputed nonroot vertices of t. Backtracking branches on EVERY such value
not already used. At a leaf, injectivity and the size equality force range X;
every leaf is checked again using the original incident-bijection definition.

Conversely, a state has one permitted value at each step, never repeats a
value, and hence follows one unique branch to a leaf. Thus this procedure
enumerates exactly all states. There is no quotient by automorphisms or a
symmetry assumption on states. A separate subset-DP permanent recurrence checks
the total count. The test suite also enumerates the full Cartesian product of
incident choices and checks state-list equality, then verifies all Q_s forests
with a separately written union-find procedure instead of DFS.

Every ordered pair of states is tested for pointwise disjointness, including
both orders. This supplies the complete pair set. The local product sizes
before injectivity filtering are 8, 48, 288 and 23,328 respectively. The state
counts are 2, 3, 4 and 16; the ordered pair counts are 2, 2, 2 and 4.

Implementation guards are 14 original vertices, 24 triangular faces, 200,000
local choices and 10,000 states. Only the four prescribed constructions are
run. A guard rejection on another input would be a scope/tractability rejection,
not a mathematical counterexample or an exclusion result.

## 6. Integer weights and cycle products

On the connected H0 dual, a deterministic BFS tree is rooted at the outer face.
For each bounded face f, route one unit along its tree path to the outer face.
At a crossing assign +1 to the spoke dart with the departing face on its left
and -1 to its reverse. All contributions at an intermediate face cancel. The
resulting integer weights have signed boundary circulation +1 on EVERY bounded
face and minus the number of bounded faces on the outer face.

The checker does not trust this construction argument as a computed assertion:
it sums every reconstructed spoke-face boundary using the resulting weights
and checks each prescribed circulation. For any simple counterclockwise spoke
cycle, summing its interior face boundaries cancels all interior darts, leaving
its cycle sum equal to the positive number of faces enclosed. Every detoured D
cycle is also checked explicitly using independently determined interior faces.

Pairs are grouped by their literal sorted undirected edge set D. The complete
2-regular decomposition on X is reconstructed from those edges. For each cycle
C let L_+(C) be the sum of head weights in its counterclockwise orientation and
L_-(C) the head-weight sum in the opposite orientation. The checker verifies
that the detour of C through its supplying centers is simple, has the same
orientation, and has integral

    L_+(C)-L_-(C) = number of bounded H0 faces inside its detour > 0.

All 2^c independent cycle orientations are enumerated. Each is independently
validated as two incident bijections, and their pair IDs must be exactly the
whole D fiber. For every group the following exact finite exponential
polynomial identity is checked by expanding and collecting every frequency:

    sum_(r,s) in group i^J exp(x omega(s))
      = product_C [-i exp(x L_+(C)) + i exp(x L_-(C))].

This coefficient-dictionary comparison is stronger than equality of a truncated
Taylor series. It does not evaluate exp at numerical sample points.

All Gaussian integers are pairs of Python integers; Gaussian rationals are
pairs of Fraction values. An exponential polynomial is stored as a dictionary
integer frequency w -> Gaussian coefficient b_w. The coefficient of x^d is
computed as sum_w b_w w^d/d!, including negative w. A separate truncated
polynomial convolution multiplies the individual cycle Taylor series.
Both computations must agree through degree |X|+2, which is 5, 7, 9 or 13 here.

Each group has no nonzero term before c(D), and its degree-c(D) coefficient is
checked to be

    (-i)^c(D) product_C (L_+(C)-L_-(C)).

For c_min=min_D c(D), the direct Z coefficient is checked against

    (-i)^c_min sum_[D:c(D)=c_min] product_C (L_+(C)-L_-(C)),

and is checked nonzero. The direct sum is also compared to its forest-only
restriction. With no cyclic fibers in these fixtures, this last equality is
vacuous as a test of cancellation, and is labelled accordingly.

## 7. Precise finite claim and its support

For EACH of the four delivered literal fixtures, the reconstructed rotation
system is a face-2-colored sphere triangulation of the claimed graph, the
recorded state and ordered pair lists are exhaustive, and every executed
incidence, disk, phase, group, weight and coefficient identity above holds
exactly. The resulting Z are:

    C4: -i(exp(x)-1)
    C6: -i(exp(2x)-1)
    C8: -i(exp(3x)-1)
    coned cube: i(exp(-x)+1-exp(4x)-exp(5x)).

The verification argument consists of the encoding and exhaustiveness arguments
in Sections 4-5, exact arithmetic procedures in Section 6, and the delivered
complete tables accepted by those procedures. Every finite assignment considered
can be independently replayed without upstream libraries or a solver. This is a
computer-assisted finite verification, with the Python runtime and the manually
reviewed encoding in its trust base. It is not a kernel-checked proof.

The two-cycle algebra unit test multiplies two artificial factors with gaps 3
and 2 and obtains leading coefficient -6 in degree 2. It tests arithmetic only;
it is not an additional embedded fixture or evidence about a multi-cycle D.

## 8. Relationship to the Lean source

`TriangleSystem.lean` defines states, partners, third corners, `indexDelta`, and
`oppositeGraph`. `CycleReversal.lean` provides the partner reversal and its
involution and fixed-point-free properties. `PairPhases.lean` proves the phase
change and the fixed-second-state cancellation. `StateDisk.lean`,
`Circulation.lean`, and `ColoredDual.lean` relate disk counts, oriented faces,
charges and slopes. `PairPolynomials.lean` proves grouping and nonvanishing using
products of LINEAR POLYNOMIAL weights. Its state weight is a product of
`1 + w(t,s(t))*X`, not the paper's exponential weight.

This checker deliberately verifies the paper's exponential formulation. It does
not assert equality of the two complete weighted expressions, does not execute
Lean's noncomputable definitions, and does not audit every dependency of
`Barnette.main`. Its definitions were read from sources, not reconstructed from
prior chat conclusions. No Lean compilation or axiom audit was performed here.
