> Authoring record from the verified input. Publication and independent review
> status are updated in PUBLIC_REVIEW.md; original private ZIPs are not distributed.

# Exact specification and finite verification argument, v1.1.0

## 1. Authoritative baseline and target

The input archive is family180_audit_v1.0.0.zip with SHA-256
451210303f0a03c8dc384a3dcaafe92738b126b6f9d2d137fec385a44d18d86b.
Its specification, code, limitations, source audit and manifests were read before
constructing the new input. The archive is bundled unchanged.

The mathematical source remains openai/math at
1581d4cbdd69a0faf34b2089614fe2a814316a6a, particularly the paired-states paper's
state setup, Lemma 4.1, Proposition 5.1, Lemmas 5.2 and 5.3, and Section 5.3's
cycle product. Relevant Lean definitions and lemmas were read for comparison.
The paper's exponential expression, not Lean's product of linear weights, is the
expression replayed here. No assertion of equality of those full expressions is made.

The bounded target was to produce one embedded fixture for which there exists
an incident-bijection state s such that Q_s is cyclic and the COMPLETE disjoint
partner set R_s is nonempty, and then verify the entire fixed-s reversal map.
Every state and every ordered disjoint pair of the chosen fixture is enumerated.
No automorphism quotient or invariance assumption is imposed on states.

## 2. Definitions and hypotheses, unchanged

T is finite, connected and simple, cellularly embedded on an oriented sphere,
with at least four vertices and all faces bounded by simple triangles. Every
edge has one black and one white incident face. One specified black face t0 is
outer; R=V(t0) is the root set, A is the set of other black faces, and X=V(T)\R.
If there are k black faces then |V(T)|=k+2, |E(T)|=3k, the white face count is k,
and |A|=|X|=k-1. These identities are independently checked on the fixture.

A state r is a bijection A->X satisfying r(t) in V(t) for every t. A pair (r,s)
is ORDERED and satisfies r(t)!=s(t) for every t. Both states have the same range
X; 'disjoint' is pointwise incidence disjointness, not disjoint vertex ranges.
Q_s is spanning on all original vertices, with the edge opposite s(t) in each
t in A. These edges are distinct because every edge has a unique black face.

For an oriented original edge u->v, delta(u,v)=+1 if its black face lies to the
left, and -1 otherwise. J(r,s)=(sum_t delta(r(t),s(t)))/3, with divisibility
checked BEFORE division. Pair edges r(t)->s(t) form a union D of vertex-disjoint
simple directed cycles on X. For real incidence weights a(t,v), including root
incidences, omega(s)=sum_t a(t,s(t)), and

    Z(x)=sum_(r,s) i^J(r,s) exp(x omega(s)).

H0 has one center in each bounded black triangle and three spokes to its corners.
Center-to-vertex spoke traversal has weight a(t,v), with the reverse negated.
Integer weights are constructed by the paper's dual paths and checked directly
against every spoke-face boundary: +1 for each bounded face, minus their number
for the outer face. This instance has connected nonisolated H0; no general
componentwise extension is inserted into the implementation.

The paper's fixed-second-state cancellation requires a pair and a cyclic Q_s;
it does not require invoking the pair-existence theorem. The new fixture also
has no separating triangle, as explicitly checked, so that property is not an
unstated exception here.

## 3. One predeclared construction and caps

The complete declaration is PLAN.json, written before enumeration. Start with
the octahedron whose antipodal vertex pairs are (0,3),(1,4),(2,5). Original
coordinates are e1,e2,e3,-e1,-e2,-e3. Its eight faces are the triples choosing one
vertex from each antipodal pair, with outward orientation determined by an
integer determinant.

Expand only these three original edges into the indicated paths:

    3-1 becomes 3-6-7-1;
    4-2 becomes 4-8-9-2;
    5-0 becomes 5-10-11-0.

For an oriented old triangle (u,v,w), if u-v is selected and its oriented path
is p0=u,p1,p2,p3=v, replace that face by
(p0,p1,w),(p1,p2,w),(p2,p3,w). Reverse the path when the old dart is reversed.
The three selected original edges share no face. Equivalently, each new path
vertex is joined to the two opposite old corners of its selected edge.

The specified outer oriented triangle is (3,5,4); it is black. Its roots are
exactly {3,4,5}. No other root choice was tried. The resulting graph has 12
vertices, 30 edges and 20 triangular faces, ten of each color. Original vertices
have degree six and the six new vertices have degree four.

The hard search caps were 20 original vertices, 200,000 full Cartesian incident
assignments before injectivity filtering, 10,000 states, one fixture and two
hours total actual work. The actual product is 3^3*2^6=1,728, and the state count
is nine. The primary guard was explicitly adjusted from the inherited 14-vertex
limit to the declared 20-vertex limit, although this 12-vertex input fits both.
No cap was silently enlarged and no subsequent fixture search occurred.

## 4. Embedding verification, independently of generator assertions

The primary checker reads the rotation system, not the generator's face list.
Its left-face dart permutation is (u,v)->(v, predecessor(u) around v). It verifies
simple symmetric adjacency, connectedness, every dart orbit, simple triangular
faces, Euler characteristic two, dual face coloring, the exact outer face,
root set, incidences and all redundant face claims.

A second implementation constructs the expected graph directly from the fixed
antipodal pairs and paths and does not import the generator or checker. Give old
vertices coordinates +/-3e_i; the new path vertices have coordinates 2u+v and
u+2v in the original unit coordinates. Project from P=(-4/3,-4/3,-4/3) onto the
outer plane x+y+z=-3. For a point q in the scaled coordinates the projected point is

    p=P+(q-P)/(q_x+q_y+q_z+4).

Use its first two coordinates as exact planar coordinates. All coordinates are
rational. The three root positions are (-3,0),(0,-3),(0,0). The projection point
lies outside only the designated octahedral facet; alternatively the explicit
finite crossing and rotation checks below suffice to inspect this drawing.

The second code checks distinct projected vertices, no vertex inside another
edge, and all 309 nonincident original edge-pair tests. It obtains cyclic neighbor
orders by exact half-plane/cross-product angular sorting and compares these with
the supplied rotations up to cyclic rotation. It recomputes the triangular face
orbits, checks the negative area of the outer boundary and positive area of every
bounded face, and recomputes the face coloring from scratch.

For the spoke graph, geometric centers are placed at the rational planar
barycenters of bounded black triangles; its rotations and face boundaries are
recomputed by the same independent angular procedure. This need not use the
same precise locations as the paper's centers: each lies in its own open black
triangle and preserves the incidence embedding. All eight spoke-face boundaries
and their integer circulations agree with the primary combinatorial construction.

The geometric verifier is a second algorithm by the SAME assistant, not a
separate worker audit or a formalized encoding proof.

## 5. Exhaustiveness: nine states and ten ordered pairs

The primary enumerator branches on every unused incident nonroot vertex at each
face, validates each leaf, and checks its count by the subset-DP permanent.
The second enumerator examines all 1,728 Cartesian incident assignments and
compares the ENTIRE surviving state list, not just the count. It tests all 9^2
ordered state combinations for pointwise disjointness.

There is also a small human-readable completeness argument. Reorder the nine
black faces into these three local groups, listing only their nonroot choices:

    group 0: B={0,8},  M={8,9},   N={9,0,2};
    group 1: B={1,10}, M={10,11}, N={11,1,0};
    group 2: B={2,6},  M={6,7},   N={7,2,1}.

Write a_i=i, b_i=i-1 modulo 3, and x_i,y_i for that group's two new vertices.
The internal vertex x_i occurs only in B_i,M_i; y_i only in M_i,N_i. Covering both
exactly once forces one of precisely three local choices:

    type 0: (B_i,M_i,N_i)=(a_i,x_i,y_i);
    type 1: (B_i,M_i,N_i)=(x_i,y_i,a_i);
    type 2: (B_i,M_i,N_i)=(x_i,y_i,b_i).

Thus each group contributes both its internal vertices and exactly one original
nonroot. The three original choices form a permutation only when every group
uses its own a_i, or every group uses b_i. A proper nonempty mixture duplicates
an original vertex and misses another. There are therefore 2^3 self-choice
states (types 0/1 independently) and one all-type-2 state: exactly nine states.

Two self-choice states are disjoint exactly when their three type bits are
complementary, giving eight ordered pairs. The all-type-2 state is disjoint
from a self-choice state only when the latter is all type 0, giving two further
ordered pairs. It is not disjoint from itself. Total: ten ordered pairs.
This argument concerns this explicit graph only.

## 6. The complete qualifying fiber and its reversal

The primary sorted face-id order is

    A=(1,3,5,7,8,11,16,18,19).

In that order the unique cyclic second state and all its partners are

    s  =(9,0,11,7,1,2,8,10,6),     state id 8;
    r0 =(0,8,1,2,10,6,9,11,7),     state id 0;
    r4 =(2,8,0,1,10,6,9,11,7),     state id 4.

The Q_s edges are

    02, 48, 01, 12, (5,10), 36, 39, (4,11), 57.

Their connected components are {0,1,2}, {3,6,9}, {4,8,11}, {5,7,10}.
The cycle is C=(0,1,2). It is selected once from Q_s without using a partner.
Only faces 1,5,7 supply its edges. Changing r(t) to the third corner on exactly
those faces interchanges r0 and r4 and leaves the other six coordinates fixed.

This also explains uniqueness of the cyclic state without trusting a DFS.
In each local type, every new vertex is a leaf in Q. Type 0 contributes original
edge a_i b_i; types 1 and 2 contribute an edge from a_i to its distinct root.
After discarding the leaves, the only possible cycle is the triangle on 0,1,2,
and all three type-0 choices are necessary and sufficient to obtain it.
The all-type-2 state has no such cycle. Hence only s is cyclic.

The full reversal map on R_s={r0,r4} is the transposition r0<->r4. It is closed
on the complete partner set, bijective, fixed-point-free and involutive. The
code applies the SAME callable reversal operation twice. The separately written
validator additionally recomputes the expected replacement coordinate by
coordinate, and the geometric checker reconstructs it independently.

For r0 the directed opposite cycle is 0->2->1->0, clockwise, with delta sum +3.
For r4 it is 0->1->2->0, counterclockwise, with delta sum -3. Its bounded disk is
the single white face (0,1,2): I=B=l=0, W=1, h=3. The disk identities
B+W=2I+h-2, 3(B-W)=2l-h and B=I+l hold exactly. Each changed triangle also passes

    delta(u,s)-delta(r,s)=2 delta(r,u).

Directly summed indices and phases are

    J(r0,s)=-3,  phase(r0,s)=+i;
    J(r4,s)=-1,  phase(r4,s)=-i.

Thus the two transitions change J by +2 and -2. With the delivered integer
spoke weights, omega(s)=4 in both records. The exact fixed-state sum is

    i exp(4x) - i exp(4x) = 0.

Because the second-state incidence vector itself is unchanged, equal weight
is not inferred merely from the coincidental number 4. The records explicitly
verify the full second-state vector before and after each transition.

## 7. Incidental but nonvacuous multi-cycle coverage

The same graph, without additional search, has two undirected D groups:

1. Three disjoint triangles, with all eight independent orientations. Their
   counterclockwise vertex sequences are (0,9,8),(1,11,10),(2,7,6). The pairs of
   head-weight sums (L_plus,L_minus) are (2,1),(1,0),(1,0), so all gaps equal one.
   The whole group sum is i exp(x)(exp(x)-1)^3. Its first coefficient is +i in
   degree three, equal to (-i)^3 times the product of the three gaps.
2. One nine-cycle, with two orientations. Its head sums are (4,0), so its group
   sum is i(1-exp(4x)), with leading coefficient -4i in degree one.

Each group is compared as a full exponential-frequency dictionary, and every
rational Taylor coefficient through degree |X|+2=11 is checked. The primary
checker also compares direct Taylor expansion with independent polynomial
convolution of its cycle factors. The global sum is

    Z(x)=i(1-exp(x)+3 exp(2x)-3 exp(3x)).

Its first coefficient is -4i in degree one. The cyclic fiber removes precisely
the +i exp(4x) term of the three-cycle group and the -i exp(4x) term of the
nine-cycle group. This is a concrete cancellation between two DIFFERENT D groups.

## 8. Status and trust

The exact finite data and elementary completeness arguments above are supported
by executable primary checks, a separate geometric/enumerative implementation,
32 new tests and twelve defined killed implementation mutants. Complete records
are in certificates/ and REVIEW_TABLES.md. The original four fixtures and their
27 tests are preserved and rerun, not presented as new contributions.

There is no new unrestricted result, novelty claim, Lean compilation, axiom audit,
formal checker theorem, external worker review, or release authorization. See
LIMITATIONS.md for the remaining disconnected-H0, larger-orbit, multiple-Q-cycle,
even-D-cycle-count and c_min>1 coverage gaps.
