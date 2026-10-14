# Exact results and coverage

Version 1.0.0; pinned upstream revision
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`.
All values below are outputs of the delivered checker, not assertions taken
from the fixture generator or a third-party log.

## Enumeration and embedding checks

| Fixture | V | E | Triangular faces | Black faces | Nonroots | Local choices before injectivity | States | Ordered disjoint pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C4 bipyramid | 6 | 12 | 8 | 4 | 3 | 8 | 2 | 2 |
| C6 bipyramid | 8 | 18 | 12 | 6 | 5 | 48 | 3 | 2 |
| C8 bipyramid | 10 | 24 | 16 | 8 | 7 | 288 | 4 | 2 |
| Coned cube | 14 | 36 | 24 | 12 | 11 | 23,328 | 16 | 4 |

Every input's reconstructed map is a sphere triangulation with the stated
face coloring and outer black triangle. The test suite compares its graph
against the literal bipyramid or coned-cube graph definition. All three-cliques
were checked to be facial; no separating triangle occurs in these fixtures.

The 25 states and 10 ordered pairs are recorded individually in
REVIEW_TABLES.md and the complete certificates. Exactly 10 states have a
partner; the remaining 15 still count as states and have not been discarded.
Every one of the 25 Q_s graphs is a forest. The one-root-per-component
consequence is checked only on partnered forest states, where its premise
applies; it is not silently imposed on partnerless states.

## Spoke graph and exact cancellation-product data

| Fixture | H0 vertices | H0 edges | Bounded H0 faces | Undirected groups | Cycles in each group | CCW gap(s) |
|---|---:|---:|---:|---:|---|---|
| C4 bipyramid | 9 | 9 | 1 | 1 | 1 | 1 |
| C6 bipyramid | 13 | 15 | 3 | 1 | 1 | 2 |
| C8 bipyramid | 17 | 21 | 5 | 1 | 1 | 3 |
| Coned cube | 25 | 33 | 9 | 2 | 1, 1 | 5, 5 |

H0 is connected in every case. Every bounded H0 face has signed circulation
exactly +1; the outer face has respectively -1, -3, -5 and -9. Root spokes,
bridges, and zero weights are retained. The full incidence weights and dual
unit-flow paths are in the certificates.

For each of the five undirected groups, the two opposite orientations are
exactly the two enumerated pairs in that fiber. Both directions' signs are
checked by independently computed disk interiors. The ten directed D cycles
have delta-sum -3 counterclockwise and +3 clockwise. The five counterclockwise
spoke detours have positive integrals equal to their enclosed H0 face counts.

For these specific inputs and deterministic weights, the complete sums are:

    Z_C4(x) = -i (exp(x) - 1)
    Z_C6(x) = -i (exp(2x) - 1)
    Z_C8(x) = -i (exp(3x) - 1)
    Z_cube(x) = i (exp(-x) + 1 - exp(4x) - exp(5x)).

Their constant coefficients vanish. Their first nonzero Taylor coefficients
are respectively -i, -2i, -3i and -10i, all in degree one. For the cube, the two
group contributions have leading coefficient -5i each. The total common-phase
addition is therefore checked nontrivially. The negative frequency -1 also
exercises exact Taylor computation for a negative integer weight sum.

For every group, frequency-by-frequency expansion of the cycle-product formula
agrees with the direct pair sum as a whole exponential polynomial. In addition,
a separately implemented rational polynomial convolution agrees through
Taylor degrees 5, 7, 9 and 13, respectively. Coefficients are coefficients of
x^d, with division by d!, not merely derivatives.

## Small hand-checkable C4 certificate

Roots are {0,1,4}. In face-ID order A=(1,5,6), the bounded black triangles are
(0,3,5), (1,5,2), and (2,3,4). The allowed nonroot choices are respectively
{3,5}, {2,5}, and {2,3}. Their only incident bijections are

    s0=(3,5,2),   s1=(5,2,3).

The two ordered disjoint pairs are (s0,s1) and (s1,s0). The sole nonzero spoke
weight is a(face 6, vertex 2)=1. Thus omega(s0)=1 and omega(s1)=0.
The first pair traverses D clockwise with J=+1; the second traverses it
counterclockwise with J=-1. Therefore

    Z(x)=i exp(0*x) - i exp(1*x),

whose x coefficient is -i. Q_s0 consists of edges {0,5},{1,2},{3,4}; Q_s1
consists of {0,3},{1,5},{2,4}. Both are forests. This illustrates exactly why
the C4 example tests signs and nonvanishing but not cyclic-Q cancellation.

## Executed tests

The final suite contains 27 tests: 14 explicitly named mutation tests, two
in-process fault-injection tests, and additional enumeration, embedding,
algebra, deterministic-generation and scope tests. All pass in normal Python
and in `python -O`. Replays with hash seeds 1 and 987654 give identical output.
The logs, test inventory, interpreter version and platform are included.

Mutations reject an altered embedding sign, a false incidence, an altered
nonbridge weight, noninteger or missing weights, an incorrect pair phase,
a nonincident state, a missing pair, an incorrect cycle gap or Taylor
denominator, a reversed face, a false face color, asymmetric adjacency, and a
bad rotation order. In-process injection of a wrong raw sign or J shift also
causes rejection. These failures occur through semantic reconstruction and
identity checks, not only through a checksum comparison.

An additional test correctly ACCEPTS a bridge-weight change at the low-level
circulation validator, because it does not change face integrals. It then
checks that a canonical certificate claiming the unmodified deterministic
construction is rejected. The initial test incorrectly expected a circulation
error for this bridge change; that failed run is preserved and not counted as
a passing final test.

## Not exercised or established

* Cyclic Q_s states: **0**. Cyclic partnered states: **0**. Actual sign-reversing
  involution executions: **0**. This part of the fixture audit is **vacuous**.
* D groups with multiple cycles: **0**. A separate artificial two-factor
  Gaussian/rational algebra test is not a geometric fixture and is not counted.
* First nonzero degree greater than one: **0**. Disconnected H0 examples: **0**.
* Lean builds, formal checker proofs, independent referee reviews, macOS runs,
  and unrestricted-theorem extensions performed here: **0**.

No mathematical counterexample to a paper claim was found. The contribution
is a correct finite replay with explicit incomplete mechanism coverage, not a
nonvacuous verification of every stage of the unrestricted proof.
