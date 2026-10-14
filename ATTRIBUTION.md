# Attribution and license boundaries

The states, partners, disk identity, fixed-second-state involution, positive
spoke circulations and cycle-product argument are inherited mathematics from
OpenAI's *Paired states and Hamiltonian cycles in cubic bipartite planar graphs*
and its cited literature. The general theorem and its Lean formalization belong
to the upstream work, not this finite audit.

Authoritative repository: [openai/math](https://github.com/openai/math).
Pinned commit: `1581d4cbdd69a0faf34b2089614fe2a814316a6a`.
Upstream source is Apache-2.0 licensed and is referenced rather than vendored.
Its license is available at
[the pinned LICENSE](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/LICENSE).
The Python audit follows the paper's exponential formulation; Lean uses
products of linear polynomial weights. Equality of the full expressions is
not claimed here.

Prior exact C6 arithmetic and related executable forest construction in
[cjnott1999/barnette-conjecture](https://github.com/cjnott1999/barnette-conjecture)
are credited at commit `97bacb41f06fbecfc4029acc716620d51019318f`, particularly
[c136_signed_sum_independent.py](https://github.com/cjnott1999/barnette-conjecture/blob/97bacb41f06fbecfc4029acc716620d51019318f/analysis/c136_signed_sum_independent.py).
That repository reports no license. None of its code is redistributed, adapted
or relicensed; it is not an executable dependency. The bounded prior-work check
does not establish novelty or priority.

The audit/checkers, literal fixture data, certificates, tests and documentation
are published under the MIT grant in LICENSE and LICENSE.md, copyright 2026
Erebos Labs audit contributors. This includes the separate independent replay
and public packaging utilities. The work is AI-assisted; no human referee or
formal checker certification is implied.

Python's standard library is an external runtime dependency and is not bundled.
