#!/usr/bin/env python3
"""Regression and semantic mutation tests. No claimed independent referee review."""
from __future__ import annotations
import copy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import checker as ck
import generate_fixtures as generator

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "bipyramid_C4": (2, 2, 1, -1),
    "bipyramid_C6": (3, 2, 1, -2),
    "bipyramid_C8": (4, 2, 1, -3),
    "coned_cube_14": (16, 4, 2, -10),
}


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = {p.stem: json.loads(p.read_text()) for p in (ROOT / "fixtures").glob("*.json")}
        cls.certs = {p.stem: json.loads(p.read_text()) for p in (ROOT / "certificates").glob("*.json")}
        cls.base = cls.fixtures["bipyramid_C4"]
        cls.cert = cls.certs["bipyramid_C4"]

    def test_all_delivered_certificates(self):
        for name, fixture in self.fixtures.items():
            with self.subTest(fixture=name):
                ck.verify_certificate(fixture, self.certs[name])
                summary = self.certs[name]["summary"]
                a, b, c, d = EXPECTED[name]
                self.assertEqual((summary["states"], summary["ordered_disjoint_pairs"], summary["undirected_groups"], summary["first_coefficient"][1]), (a, b, c, d))
                self.assertEqual(summary["cyclic_Q_states"], 0)
                self.assertEqual(summary["reversal_checks"], 0)
                self.assertEqual(summary["group_cycle_counts"], {"1": c})

    def test_second_state_enumerator_and_q_acyclicity(self):
        # Cartesian products and a separate union-find implementation, rather
        # than the main checker's backtracking, subset DP, and DFS cycle choice.
        for name, fixture in self.fixtures.items():
            with self.subTest(fixture=name):
                T = ck.Triangulation(fixture)
                choices = [sorted(v for v in T.faces[t] if v not in T.roots) for t in T.A]
                states = [s for s in product(*choices) if len(set(s)) == len(T.X)]
                self.assertEqual(states, [tuple(x["values"]) for x in self.certs[name]["states"]])
                for s in states:
                    parent = {v: v for v in T.map.vertices}
                    def root(v):
                        while parent[v] != v:
                            v = parent[v]
                        return v
                    for t, v in zip(T.A, s):
                        a, b = [w for w in T.faces[t] if w != v]
                        self.assertNotEqual(root(a), root(b))
                        parent[root(a)] = root(b)

    def test_generators_reproduce_literal_inputs(self):
        self.assertEqual({f["name"]: f for f in generator.all_inputs()}, self.fixtures)

    def test_bipyramid_and_cube_graphs_are_the_named_graphs(self):
        for m in (4, 6, 8):
            T = ck.Triangulation(self.fixtures[f"bipyramid_C{m}"])
            expected = {ck.edge(j, (j+1) % m) for j in range(m)}
            expected |= {ck.edge(pole, j) for pole in (m, m+1) for j in range(m)}
            self.assertEqual(set(T.map.edges), expected)
        T = ck.Triangulation(self.fixtures["coned_cube_14"])
        xyz = list(product((-1, 1), repeat=3))
        expected = {ck.edge(a, b) for a in range(8) for b in range(a+1, 8)
                    if sum(x != y for x, y in zip(xyz[a], xyz[b])) == 1}
        for axis in range(3):
            for side in (-1, 1):
                center = 8+2*axis+int(side == 1)
                expected |= {ck.edge(center, v) for v, p in enumerate(xyz) if p[axis] == side}
        self.assertEqual(set(T.map.edges), expected)

    def test_cyclic_rotation_start_and_face_order_irrelevant(self):
        altered = copy.deepcopy(self.base)
        for v, neighbors in altered["rotation"].items():
            altered["rotation"][v] = neighbors[1:] + neighbors[:1]
        altered["faces"].reverse()
        self.assertEqual(ck.audit(altered), self.cert)

    def mutation(self, change, expected=None):
        altered = copy.deepcopy(self.cert)
        change(altered)
        with self.assertRaises(ck.Rejected) as raised:
            ck.verify_certificate(self.base, altered)
        if expected:
            self.assertIn(expected, str(raised.exception))

    def test_mutation_altered_embedding_sign(self):
        self.mutation(lambda c: c["delta"][0].__setitem__("sign", -c["delta"][0]["sign"]))

    def test_mutation_altered_incidence(self):
        self.mutation(lambda c: c["incidences"][0]["nonroot_vertices"].append(c["roots"][0]))

    def test_mutation_altered_weight(self):
        T = ck.Triangulation(self.base)
        H, outer, centers = ck.spoke_embedding(T)
        # A nonbridge spoke has two different incident faces. Mutating it
        # violates the actual unit-circulation equations, not just canonicality.
        j = next(j for j, w in enumerate(self.cert["spokes"]["weights"])
                 if H.left[centers[w["face"]], w["vertex"]] != H.left[w["vertex"], centers[w["face"]]])
        self.mutation(lambda c: c["spokes"]["weights"][j].__setitem__("weight", c["spokes"]["weights"][j]["weight"]+1), "unit spoke-face circulation failed")

    def test_bridge_weight_freedom_is_not_a_circulation_error(self):
        T = ck.Triangulation(self.base)
        H, outer, centers = ck.spoke_embedding(T)
        weights, _ = ck.make_weights(H, outer, centers)
        t, v = next((t, v) for t, v in weights if H.left[centers[t], v] == H.left[v, centers[t]])
        weights[t, v] += 1
        _, circulation = ck.check_weights(H, outer, centers, weights)
        self.assertEqual(circulation, self.cert["spokes"]["face_circulations"])
        # A canonical replay certificate still must reproduce its exact inputs.
        j = next(j for j, w in enumerate(self.cert["spokes"]["weights"])
                 if (w["face"], w["vertex"]) == (t, v))
        self.mutation(lambda c: c["spokes"]["weights"][j].__setitem__("weight", c["spokes"]["weights"][j]["weight"]+1), "deterministic weight construction")

    def test_mutation_noninteger_weight(self):
        self.mutation(lambda c: c["spokes"]["weights"][0].__setitem__("weight", 0.5), "integrality")

    def test_mutation_deleted_weight(self):
        self.mutation(lambda c: c["spokes"]["weights"].pop(), "incidence/integrality")

    def test_mutation_pair_phase(self):
        self.mutation(lambda c: c["pairs"][0].__setitem__("phase", [0, -c["pairs"][0]["phase"][1]]))

    def test_mutation_nonincident_state(self):
        self.mutation(lambda c: c["states"][0]["values"].__setitem__(0, c["roots"][0]))

    def test_mutation_missing_pair(self):
        self.mutation(lambda c: c["pairs"].pop())

    def test_mutation_cycle_gap(self):
        self.mutation(lambda c: c["groups"][0]["cycles"][0].__setitem__("gap", 0))

    def test_mutation_taylor_denominator(self):
        self.mutation(lambda c: c["taylor"][2][1].__setitem__(1, 1))

    def test_mutation_reversed_face(self):
        altered = copy.deepcopy(self.base)
        altered["faces"][0]["vertices"].reverse()
        with self.assertRaises(ck.Rejected):
            ck.audit(altered)

    def test_mutation_wrong_face_color(self):
        altered = copy.deepcopy(self.base)
        altered["faces"][0]["color"] = "white"
        with self.assertRaises(ck.Rejected):
            ck.audit(altered)

    def test_mutation_asymmetric_edge(self):
        altered = copy.deepcopy(self.base)
        altered["rotation"]["0"].pop()
        with self.assertRaises(ck.Rejected):
            ck.audit(altered)

    def test_mutation_rotation_transposition(self):
        altered = copy.deepcopy(self.base)
        ns = altered["rotation"]["0"]
        ns[0], ns[1] = ns[1], ns[0]
        with self.assertRaises(ck.Rejected):
            ck.audit(altered)

    def test_fault_injection_j_phase_shift(self):
        original = ck.Triangulation.index
        with patch.object(ck.Triangulation, "index", lambda self, r, s: original(self, r, s)+2):
            with self.assertRaises(ck.Rejected):
                ck.audit(self.base)

    def test_fault_injection_delta_sign(self):
        original = ck.Triangulation.__init__
        def corrupted(self, fixture):
            original(self, fixture)
            # Mutate a dart actually used in a pair, preserving antisymmetry.
            r, s = self.states()
            a, b = r[0], s[0]
            self.delta[a, b] *= -1
            self.delta[b, a] *= -1
        with patch.object(ck.Triangulation, "__init__", corrupted):
            with self.assertRaises(ck.Rejected):
                ck.audit(self.base)

    def test_exact_gaussian_arithmetic_and_negative_powers(self):
        self.assertEqual(ck.mul(ck.I, ck.I), (-1, 0))
        for n in range(-12, 13):
            self.assertEqual(ck.mul(ck.phase(n), ck.phase(-n)), ck.ONE)
            self.assertEqual(ck.phase(n+2), ck.scale(ck.phase(n), -1))
        self.assertEqual(ck.mul((Fraction(1, 2), Fraction(1, 3)), (Fraction(2), Fraction(-3))), (Fraction(2), Fraction(-5, 6)))

    def test_exact_taylor_including_factorial_and_negative_exponent(self):
        self.assertEqual(ck.taylor({-2: ck.I}, 3), [(0, 1), (0, -2), (0, 2), (0, Fraction(-4, 3))])

    def test_two_cycle_algebra_only_not_a_graph_fixture(self):
        # This exercises convolution; it supplies NO cyclic-Q_s or geometric
        # multi-cycle coverage. Factors have gaps 3 and 2.
        factors = [ck.exponential_sum([(ck.MINUS_I, 2), (ck.I, -1)]),
                   ck.exponential_sum([(ck.MINUS_I, 3), (ck.I, 1)])]
        expanded = ck.exponential_product(*factors)
        series = ck.taylor(expanded, 6)
        convolution = ck.polynomial_product(ck.taylor(factors[0], 6), ck.taylor(factors[1], 6), 6)
        self.assertEqual(series, convolution)
        self.assertEqual(series[:3], [ck.ZERO, ck.ZERO, (-6, 0)])

    def test_deterministic_cycle_choice_unit(self):
        # A graph utility unit test, not a triangulation/state involution test.
        e = [(0, 1), (1, 2), (2, 0), (0, 3)]
        self.assertEqual(ck.find_cycle(e), (0, 1, 2))
        self.assertEqual(ck.find_cycle(reversed(e)), (0, 1, 2))
        self.assertIsNone(ck.find_cycle([(0, 1), (1, 2), (2, 3)]))

    def test_size_caps(self):
        with self.assertRaises(ValueError):
            generator.bipyramid(10)
        altered = copy.deepcopy(self.base)
        altered["rotation"].update({str(j): [0] for j in range(6, 15)})
        with self.assertRaises(ck.Rejected):
            ck.audit(altered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
