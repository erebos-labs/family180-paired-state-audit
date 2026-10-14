#!/usr/bin/env python3
"""Exact, bounded replay of the paper's paired-state mechanism.

Standard library only; no floating point, numerical exponentials, SAT solver,
external graph library, or generator imports. All checks survive python -O.
This is not a Lean proof or an unrestricted theorem. See SPECIFICATION.md.
Original audit code prepared for Erebos Labs, 2026. See LICENSE.md.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations, product
import json
from math import factorial, prod
from pathlib import Path
from typing import Iterable

VERSION = "1.1.0"
PIN = "1581d4cbdd69a0faf34b2089614fe2a814316a6a"
MAX_VERTICES, MAX_TRIANGLES, MAX_STATES, MAX_LOCAL_CHOICES = 20, 36, 10000, 200000
ZERO, ONE = (0, 0), (1, 0)
I, MINUS_I = (0, 1), (0, -1)


class Rejected(ValueError):
    """Invalid input, violated identity, or certificate mismatch."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def add(a: tuple, b: tuple) -> tuple:
    return a[0] + b[0], a[1] + b[1]


def mul(a: tuple, b: tuple) -> tuple:
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def scale(a: tuple, k: int | Fraction) -> tuple:
    return a[0] * k, a[1] * k


def phase(j: int) -> tuple[int, int]:
    return (ONE, I, (-1, 0), MINUS_I)[j % 4]


def edge(u: int, v: int) -> tuple[int, int]:
    return (min(u, v), max(u, v))


def darts(cycle: Iterable[int]) -> list[tuple[int, int]]:
    c = tuple(cycle)
    return list(zip(c, c[1:] + c[:1]))


def canonical(cycle: Iterable[int]) -> tuple[int, ...]:
    c = tuple(cycle)
    require(bool(c), "empty face walk")
    return min(c[i:] + c[:i] for i in range(len(c)))


def undirected_cycle(cycle: Iterable[int]) -> tuple[int, ...]:
    c = tuple(cycle)
    return min(canonical(c), canonical(reversed(c)))


class Embedding:
    """Connected orientable cellular rotation system, checked to have genus 0.

    Every dart belongs to exactly one left-face orbit. With CCW rotations,
    the next dart after u->v is v->(predecessor of u around v).
    Faces may have repeated vertices here, as spoke graphs can have bridges.
    """
    def __init__(self, rotation: dict[int, list[int]]):
        self.rotation = {v: tuple(ns) for v, ns in rotation.items()}
        self.vertices = sorted(rotation)
        require(bool(self.vertices), "empty embedding")
        for v, ns in self.rotation.items():
            require(bool(ns), "this bounded checker requires connected nonisolated H0")
            require(len(ns) == len(set(ns)) and v not in ns, "loop or duplicate neighbor")
            require(all(w in rotation and v in rotation[w] for w in ns), "asymmetric incidence")
        reached, queue = {self.vertices[0]}, [self.vertices[0]]
        for v in queue:
            for w in rotation[v]:
                if w not in reached:
                    reached.add(w)
                    queue.append(w)
        require(len(reached) == len(rotation), "embedding disconnected")
        unseen = {(v, w) for v in rotation for w in rotation[v]}
        self.edges = sorted({edge(*d) for d in unseen})
        walks = []
        while unseen:
            first = min(unseen)
            current, walk = first, []
            while current in unseen:
                unseen.remove(current)
                u, v = current
                walk.append(u)
                ns = self.rotation[v]
                current = v, ns[(ns.index(u) - 1) % len(ns)]
            require(current == first, "face orbit does not close")
            walks.append(canonical(walk))
        self.faces = sorted(walks)
        require(len(set(self.faces)) == len(self.faces), "duplicate oriented face")
        self.left = {d: f for f, walk in enumerate(self.faces) for d in darts(walk)}
        require(len(self.left) == 2 * len(self.edges), "dart coverage")
        require(len(rotation) - len(self.edges) + len(self.faces) == 2, "rotation system is not a sphere")

    def inside(self, cycle: Iterable[int], outer: int) -> tuple[set[int], bool]:
        c = tuple(cycle)
        require(len(c) >= 3 and len(c) == len(set(c)), "not a simple cycle")
        boundary = {edge(*d) for d in darts(c)}
        require(boundary <= set(self.edges), "cycle uses nonexistent edge")
        dual = {f: set() for f in range(len(self.faces))}
        for u, v in self.edges:
            if (u, v) not in boundary:
                a, b = self.left[u, v], self.left[v, u]
                dual[a].add(b)
                dual[b].add(a)
        def component(start: int) -> set[int]:
            seen, queue = {start}, [start]
            for f in queue:
                for g in dual[f]:
                    if g not in seen:
                        seen.add(g)
                        queue.append(g)
            return seen
        outside = component(outer)
        inside = set(dual) - outside
        require(bool(inside) and component(min(inside)) == inside, "cycle does not separate into two disks")
        left_inside = [self.left[d] in inside for d in darts(c)]
        require(all(left_inside) or not any(left_inside), "cycle side orientation inconsistent")
        return inside, all(left_inside)


def embedding_from_faces(faces: list[tuple[int, ...]]) -> Embedding:
    """Used for stellar subdivision only, never to accept fixture claims."""
    successor = defaultdict(dict)
    used = set()
    for face in faces:
        for j, b in enumerate(face):
            a, c = face[j-1], face[(j+1) % len(face)]
            require((a, b) not in used, "duplicate stellar dart")
            used.add((a, b))
            require(c not in successor[b], "duplicate stellar corner")
            successor[b][c] = a
    rotation = {}
    for v, nxt in successor.items():
        first, ns = min(nxt), []
        w = first
        while w not in ns:
            ns.append(w)
            require(w in nxt, "broken stellar vertex link")
            w = nxt[w]
        require(w == first and len(ns) == len(nxt), "nonmanifold stellar link")
        rotation[v] = ns
    result = Embedding(rotation)
    require(result.faces == sorted(canonical(f) for f in faces), "stellar face reconstruction mismatch")
    return result


class Triangulation:
    def __init__(self, fixture: dict):
        require(fixture.get("schema") == "family180-fixture-v1", "fixture schema")
        require(fixture.get("rotation_convention") == "counterclockwise", "rotation convention")
        rotation = {int(v): ns for v, ns in fixture["rotation"].items()}
        require(all(type(v) is int and type(w) is int for v, ns in rotation.items() for w in ns), "integer labels")
        require(4 <= len(rotation) <= MAX_VERTICES, "vertex cap exceeded")
        require(set(rotation) == set(range(len(rotation))), "vertex labels must be consecutive")
        self.map = Embedding(rotation)
        self.faces = self.map.faces
        require(len(self.faces) <= MAX_TRIANGLES, "triangle cap exceeded")
        require(all(len(f) == len(set(f)) == 3 for f in self.faces), "not a simple sphere triangulation")
        outer = canonical(fixture["outer_face"])
        require(outer in self.faces, "outer face not an oriented facial triangle")
        self.outer = self.faces.index(outer)
        self.roots = set(outer)
        color = {self.outer: 0}
        queue = [self.outer]
        for f in queue:
            for a, b in darts(self.faces[f]):
                g = self.map.left[b, a]
                require(g != f, "edge has same face on both sides")
                if g not in color:
                    color[g] = 1 - color[f]
                    queue.append(g)
                require(color[g] != color[f], "faces are not bipartite")
        require(len(color) == len(self.faces), "face coloring incomplete")
        self.color = color
        claims = fixture["faces"]
        require(len(claims) == len(self.faces), "claimed face count")
        claimed = {canonical(f["vertices"]): f["color"] for f in claims}
        require(len(claimed) == len(self.faces), "duplicate claimed face")
        actual = {face: "black" if color[f] == 0 else "white" for f, face in enumerate(self.faces)}
        require(claimed == actual, "face incidence or coloring claim disagrees with rotation")
        self.A = [f for f in range(len(self.faces)) if color[f] == 0 and f != self.outer]
        self.X = sorted(set(rotation) - self.roots)
        require(len(self.A) == len(self.X), "state domain/codomain sizes")
        self.incidence = [sorted(set(self.faces[t]) & set(self.X)) for t in self.A]
        self.delta = {d: (1 if color[f] == 0 else -1) for d, f in self.map.left.items()}
        require(all(self.delta[u, v] == -self.delta[v, u] for u, v in self.map.edges), "delta antisymmetry")
        black_counts = sum(c == 0 for c in color.values())
        require(black_counts * 2 == len(self.faces) and len(self.map.edges) == 3*black_counts and len(rotation) == black_counts+2, "Euler/color counts")
        graph_edges = set(self.map.edges)
        face_sets = {frozenset(f) for f in self.faces}
        self.nonfacial_triangles = [list(c) for c in combinations(self.map.vertices, 3)
                                   if all(edge(a, b) in graph_edges for a, b in combinations(c, 2))
                                   and frozenset(c) not in face_sets]

    def state_valid(self, s: tuple[int, ...]) -> bool:
        return (len(s) == len(self.A) and set(s) == set(self.X) and len(set(s)) == len(s)
                and all(v in self.faces[t] for t, v in zip(self.A, s)))

    def states(self) -> list[tuple[int, ...]]:
        require(prod(map(len, self.incidence)) <= MAX_LOCAL_CHOICES, "local enumeration cap exceeded")
        found = []
        def visit(prefix: tuple, used: set) -> None:
            if len(prefix) == len(self.A):
                require(self.state_valid(prefix), "enumerated assignment is not a state")
                found.append(prefix)
                require(len(found) <= MAX_STATES, "state cap exceeded")
                return
            for v in self.incidence[len(prefix)]:
                if v not in used:
                    visit(prefix + (v,), used | {v})
        visit((), set())
        # Independent counting recurrence on subsets of X (the permanent).
        positions = {v: j for j, v in enumerate(self.X)}
        count = {0: 1}
        for choices in self.incidence:
            nxt = defaultdict(int)
            for mask, n in count.items():
                for v in choices:
                    bit = 1 << positions[v]
                    if not mask & bit:
                        nxt[mask | bit] += n
            count = nxt
        require(len(found) == count.get((1 << len(self.X))-1, 0), "permanent count mismatch")
        return found

    def q_edges(self, s: tuple) -> list[tuple[int, int]]:
        require(self.state_valid(s), "Q_s requested for nonstate")
        result = [edge(*(set(self.faces[t]) - {v})) for t, v in zip(self.A, s)]
        require(len(set(result)) == len(result), "opposite edges repeat")
        return result

    def index(self, r: tuple, s: tuple) -> int:
        raw = sum(self.delta[u, v] for u, v in zip(r, s))
        require(raw % 3 == 0, "raw delta sum not divisible by three")
        return raw // 3

    def disk_check(self, cycle: tuple, r: tuple) -> dict:
        inside, ccw = self.map.inside(cycle, self.outer)
        require(set(cycle).isdisjoint(self.roots), "state-directed cycle reaches a root")
        interior_vertices = set().union(*(set(self.faces[f]) for f in inside)) - set(cycle)
        require(interior_vertices.isdisjoint(self.roots), "root inside bounded cycle")
        supplier = []
        for u, v in darts(cycle):
            f = self.map.left[u, v]
            if self.color[f] != 0:
                f = self.map.left[v, u]
            require(f in self.A and r[self.A.index(f)] == u, "cycle not directed by supplied state")
            supplier.append(f)
        require(len(set(supplier)) == len(supplier), "repeated black face on state cycle")
        h, interior = len(cycle), len(interior_vertices)
        black = sum(self.color[f] == 0 for f in inside)
        white = len(inside) - black
        l = sum(f in inside for f in supplier)
        require(black + white == 2*interior + h-2, "disk Euler identity")
        require(3*(black-white) == 2*l-h, "signed disk side count")
        require(black == interior+l, "state matching disk count")
        raw = sum(self.delta[d] for d in darts(cycle))
        require(raw == (-3 if ccw else 3), "state disk delta identity")
        return {"vertices": list(cycle), "counterclockwise": ccw,
                "inside_faces": sorted(inside), "I": interior, "B": black, "W": white,
                "h": h, "l": l, "delta_sum": raw, "supplier_faces": supplier}


def find_cycle(edges: Iterable[tuple[int, int]]) -> tuple[int, ...] | None:
    """A deterministic cycle choice using only the supplied undirected graph."""
    adjacency = defaultdict(list)
    for a, b in sorted(edges):
        adjacency[a].append(b)
        adjacency[b].append(a)
    visited, active, path = set(), set(), []
    def dfs(v: int, parent: int | None):
        visited.add(v)
        active.add(v)
        path.append(v)
        for w in sorted(adjacency[v]):
            if w == parent:
                continue
            if w in active:
                return undirected_cycle(path[path.index(w):])
            if w not in visited:
                answer = dfs(w, v)
                if answer:
                    return answer
        path.pop()
        active.remove(v)
        return None
    for v in sorted(adjacency):
        if v not in visited:
            answer = dfs(v, None)
            if answer:
                return answer
    return None


def components(vertices: list[int], edges: Iterable[tuple[int, int]]) -> list[list[int]]:
    adjacency = {v: set() for v in vertices}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    result, remaining = [], set(vertices)
    while remaining:
        seen, queue = {min(remaining)}, [min(remaining)]
        for v in queue:
            for w in sorted(adjacency[v]):
                if w not in seen:
                    seen.add(w)
                    queue.append(w)
        result.append(sorted(seen))
        remaining -= seen
    return result


def cycle_union(vertices: list[int], edges: tuple) -> list[tuple[int, ...]]:
    adjacency = defaultdict(list)
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    require(set(adjacency) == set(vertices) and all(len(ns) == 2 for ns in adjacency.values()), "D is not 2-regular on X")
    result = []
    for component in components(vertices, edges):
        a = min(component)
        walk = [a, min(adjacency[a])]
        while True:
            nxt = next(v for v in adjacency[walk[-1]] if v != walk[-2])
            if nxt == a:
                break
            require(nxt not in walk, "D cycle repeats vertex")
            walk.append(nxt)
        require(set(walk) == set(component), "D component is not a cycle")
        result.append(undirected_cycle(walk))
    return sorted(result)


def spoke_embedding(T: Triangulation) -> tuple[Embedding, int, dict[int, int]]:
    centers = {t: len(T.map.vertices) + j for j, t in enumerate(T.A)}
    stellar_faces = []
    for f, face in enumerate(T.faces):
        if f in centers:
            stellar_faces.extend((centers[f], a, b) for a, b in darts(face))
        else:
            stellar_faces.append(face)
    stellar = embedding_from_faces(stellar_faces)
    # Deleting all original edges merges face regions. Track which contains infinity.
    parent = list(range(len(stellar.faces)))
    def root(f: int) -> int:
        while parent[f] != f:
            f = parent[f]
        return f
    for a, b in T.map.edges:
        parent[root(stellar.left[a, b])] = root(stellar.left[b, a])
    original = set(T.map.vertices)
    rotation = {v: [w for w in ns if not (v in original and w in original)]
                for v, ns in stellar.rotation.items()}
    H = Embedding(rotation)
    regions = []
    for face in H.faces:
        ids = {root(stellar.left[d]) for d in darts(face)}
        require(len(ids) == 1, "spoke face not one merged stellar region")
        regions.append(next(iter(ids)))
    require(len(set(regions)) == len(regions) == len({root(f) for f in range(len(stellar.faces))}), "spoke region correspondence")
    outer_region = root(stellar.faces.index(T.faces[T.outer]))
    require(outer_region in regions, "spoke exterior missing")
    return H, regions.index(outer_region), centers


def make_weights(H: Embedding, outer: int, centers: dict[int, int]) -> tuple[dict, list]:
    """One integer unit on a deterministic dual path from every bounded face."""
    dual = defaultdict(list)
    for a, b in H.edges:
        l, r = H.left[a, b], H.left[b, a]
        if l != r:
            dual[l].append((r, (a, b)))
            dual[r].append((l, (b, a)))
    parent, queue = {outer: None}, [outer]
    for f in queue:
        for g, d in sorted(dual[f]):
            if g not in parent:
                parent[g] = (f, (d[1], d[0]))
                queue.append(g)
    require(len(parent) == len(H.faces), "spoke dual is disconnected")
    weights_dart = {d: 0 for d in H.left}
    paths = []
    for start in range(len(H.faces)):
        if start == outer:
            continue
        f, route = start, []
        while f != outer:
            g, (a, b) = parent[f]
            require(H.left[a, b] == f and H.left[b, a] == g, "dual path orientation")
            weights_dart[a, b] += 1
            weights_dart[b, a] -= 1
            route.append({"from_face": f, "to_face": g, "dart": [a, b]})
            f = g
        paths.append({"start_face": start, "steps": route})
    weights = {(t, v): weights_dart[c, v] for t, c in centers.items() for v in H.rotation[c]}
    return weights, paths


def check_weights(H: Embedding, outer: int, centers: dict, weights: dict) -> tuple[dict, list[int]]:
    expected = {(t, v) for t, c in centers.items() for v in H.rotation[c]}
    require(set(weights) == expected and all(type(w) is int for w in weights.values()), "spoke weight incidence/integrality")
    directed = {}
    for (t, v), w in weights.items():
        c = centers[t]
        directed[c, v], directed[v, c] = w, -w
    require(set(directed) == set(H.left), "spoke weight dart coverage")
    circulation = [sum(directed[d] for d in darts(face)) for face in H.faces]
    require(circulation == [-(len(H.faces)-1) if f == outer else 1 for f in range(len(H.faces))], "unit spoke-face circulation failed")
    return directed, circulation


def exponential_sum(terms: list[tuple[tuple, int]]) -> dict:
    result = {}
    for coefficient, exponent in terms:
        result[exponent] = add(result.get(exponent, ZERO), coefficient)
    return {e: c for e, c in sorted(result.items()) if c != ZERO}


def exponential_product(a: dict, b: dict) -> dict:
    return exponential_sum([(mul(c, d), u+v) for u, c in a.items() for v, d in b.items()])


def taylor(poly: dict, cap: int) -> list[tuple]:
    # coeff of x^d, NOT derivative: the factorial is indispensable.
    return [tuple(sum(Fraction(c[j] * e**d, factorial(d)) for e, c in poly.items()) for j in (0, 1))
            for d in range(cap+1)]


def polynomial_product(a: list[tuple], b: list[tuple], cap: int) -> list[tuple]:
    result = [(Fraction(0), Fraction(0)) for _ in range(cap+1)]
    for i, c in enumerate(a):
        for j, d in enumerate(b[:max(0, cap+1-i)]):
            result[i+j] = add(result[i+j], mul(c, d))
    return result


def serialize_exp(poly: dict) -> list[dict]:
    return [{"exponent": e, "coefficient": list(c)} for e, c in sorted(poly.items())]


def serialize_series(series: list[tuple]) -> list:
    return [[[Fraction(x).numerator, Fraction(x).denominator] for x in c] for c in series]


def reverse_partner(T: Triangulation, r: tuple, s: tuple, cycle: tuple) -> tuple:
    """Change only first-state choices on one cycle chosen using s alone.

    Deliberately a callable operation: the audit applies this SAME operation
    twice, rather than checking a separately inlined inverse formula.
    The caller checks closure, fixed points, the two applications and phase.
    """
    boundary = {edge(*d) for d in darts(cycle)}
    q = T.q_edges(s)
    return tuple(next(v for v in T.faces[t] if v not in (r[j], s[j]))
                 if q[j] in boundary else r[j] for j, t in enumerate(T.A))


def audit(fixture: dict, supplied_weights: list[dict] | None = None) -> dict:
    T = Triangulation(fixture)
    states = T.states()
    pairs = [(r, s) for r, s in product(states, repeat=2) if all(a != b for a, b in zip(r, s))]
    require(bool(pairs), "no pair: nonvanishing target has no premise")
    sid = {s: j for j, s in enumerate(states)}
    pair_id = {p: j for j, p in enumerate(pairs)}
    H, outerH, centers = spoke_embedding(T)
    weights, routes = make_weights(H, outerH, centers)
    if supplied_weights is not None:
        candidate = {(w["face"], w["vertex"]): w["weight"] for w in supplied_weights}
        require(len(candidate) == len(supplied_weights), "duplicate supplied weight")
        check_weights(H, outerH, centers, candidate)
        require(candidate == weights, "certificate is not the prescribed deterministic weight construction")
    weighted_dart, circulations = check_weights(H, outerH, centers, weights)
    omega = {s: sum(weights[t, v] for t, v in zip(T.A, s)) for s in states}
    q = {s: T.q_edges(s) for s in states}
    selected_cycle = {s: find_cycle(q[s]) for s in states}
    groups, pair_records = defaultdict(list), []
    for j, (r, s) in enumerate(pairs):
        require(T.state_valid(r) and T.state_valid(s), "pair state validation")
        D = tuple(sorted(edge(a, b) for a, b in zip(r, s)))
        require(len(set(D)) == len(T.A), "pair repeats an undirected edge")
        cycles = cycle_union(T.X, D)
        nxt = dict(zip(r, s))
        disk_records = []
        for c in cycles:
            c = c if nxt[c[0]] == c[1] else canonical(reversed(c))
            require(all(nxt[a] == b for a, b in darts(c)), "pair edge orientations inconsistent")
            disk_records.append(T.disk_check(c, r))
        index = T.index(r, s)
        require(index == sum(-1 if c["counterclockwise"] else 1 for c in disk_records), "J cycle decomposition")
        pair_records.append({"id": j, "r": sid[r], "s": sid[s], "J": index,
                             "phase": list(phase(index)), "omega_s": omega[s],
                             "D": [list(e) for e in D], "cycles": disk_records})
        groups[D].append(j)
    reversals = []
    cyclic_states = [s for s in states if selected_cycle[s] is not None]
    for s in cyclic_states:
        cycle = selected_cycle[s]
        cycle_edges = {edge(*d) for d in darts(cycle)}
        changed = [j for j, e in enumerate(q[s]) if e in cycle_edges]
        partners = [r for r, ss in pairs if ss == s]
        images = []
        for r in partners:
            third = {j: next(v for v in T.faces[T.A[j]] if v not in (r[j], s[j])) for j in changed}
            outgoing = {r[j]: third[j] for j in changed}
            oriented = cycle if outgoing[cycle[0]] == cycle[1] else canonical(reversed(cycle))
            require(all(outgoing[a] == b for a, b in darts(oriented)), "Q cycle not directed by partner")
            disk = T.disk_check(oriented, r)
            rr = reverse_partner(T, r, s, cycle)
            require(T.state_valid(rr) and (rr, s) in pair_id, "reversal not a partner state")
            require(rr != r, "reversal has fixed point")
            back = reverse_partner(T, rr, s, cycle)
            require(back == r, "reversal not involutive")
            for j in changed:
                u = third[j]
                require(T.delta[u, s[j]] - T.delta[r[j], s[j]] == 2*T.delta[r[j], u], "local reversal sign identity")
            delta_j = T.index(rr, s) - T.index(r, s)
            require(delta_j in (-2, 2), "reversal J change")
            require(phase(T.index(rr, s)) == scale(phase(T.index(r, s)), -1), "reversal phase does not negate")
            images.append(rr)
            reversals.append({"pair": pair_id[r, s], "image_pair": pair_id[rr, s],
                              "cycle": list(cycle), "disk": disk, "J_change": delta_j,
                              "unchanged_exponent": omega[s]})
        require(set(images) == set(partners) and len(images) == len(set(images)), "reversal not bijective on partner fiber")
        require(exponential_sum([(phase(T.index(r, s)), omega[s]) for r in partners]) == {}, "fixed-s sum not zero")
    group_records, total_product_terms = [], []
    cap = len(T.X) + 2
    for D, members in sorted(groups.items()):
        cycles = cycle_union(T.X, D)
        cycle_records, orientation_assignments = [], []
        factors = []
        for c in cycles:
            _, ccw = T.map.inside(c, T.outer)
            c = c if ccw else canonical(reversed(c))
            suppliers = []
            for a, b in darts(c):
                t = T.map.left[a, b]
                if T.color[t] != 0:
                    t = T.map.left[b, a]
                require(t in T.A, "cycle supplied by outer black face")
                suppliers.append(t)
            plus = sum(weights[t, b] for t, (_, b) in zip(suppliers, darts(c)))
            minus = sum(weights[t, a] for t, (a, _) in zip(suppliers, darts(c)))
            detour = tuple(v for a, t in zip(c, suppliers) for v in (a, centers[t]))
            spoke_inside, spoke_ccw = H.inside(detour, outerH)
            gap = sum(weighted_dart[d] for d in darts(detour))
            require(spoke_ccw, "spoke detour reverses geometric orientation")
            require(plus - minus == gap == len(spoke_inside) and gap > 0, "cycle weight gap/face sum")
            factor = exponential_sum([(MINUS_I, plus), (I, minus)])
            factors.append(factor)
            cycle_records.append({"ccw_vertices": list(c), "supplier_faces": suppliers,
                                  "L_plus": plus, "L_minus": minus, "gap": gap,
                                  "spoke_cycle": list(detour), "inside_spoke_faces": sorted(spoke_inside)})
            orientation_assignments.append((c, suppliers))
        oriented_pairs = set()
        for flips in product((False, True), repeat=len(cycles)):
            r, s = [None]*len(T.A), [None]*len(T.A)
            for flip, (c, ts) in zip(flips, orientation_assignments):
                for t, (a, b) in zip(ts, darts(c)):
                    j = T.A.index(t)
                    require(r[j] is None, "orientation assigned black face twice")
                    r[j], s[j] = (b, a) if flip else (a, b)
            rr, ss = tuple(r), tuple(s)
            require(T.state_valid(rr) and T.state_valid(ss) and all(a != b for a, b in zip(rr, ss)), "orientation not disjoint states")
            require((rr, ss) in pair_id, "orientation missing from enumerated pairs")
            oriented_pairs.add(pair_id[rr, ss])
        require(oriented_pairs == set(members) and len(members) == 2**len(cycles), "cycle orientations not exactly the group")
        direct = exponential_sum([(tuple(pair_records[j]["phase"]), pair_records[j]["omega_s"]) for j in members])
        expanded, series_product = {0: ONE}, [ONE] + [ZERO]*cap
        for factor in factors:
            expanded = exponential_product(expanded, factor)
            series_product = polynomial_product(series_product, taylor(factor, cap), cap)
        require(direct == expanded, "group exponential polynomial identity failed")
        series_direct = taylor(direct, cap)
        require(series_direct == series_product, "direct Taylor vs product convolution")
        c = len(cycles)
        leading = scale(phase(-c), prod(x["gap"] for x in cycle_records))
        require(all(v == ZERO for v in series_direct[:c]) and series_direct[c] == leading and leading != ZERO, "group leading coefficient")
        group_records.append({"D": [list(e) for e in D], "member_pairs": members,
                              "cycle_count": c, "cycles": cycle_records,
                              "exponential_sum": serialize_exp(direct),
                              "taylor": serialize_series(series_direct), "leading_coefficient": list(leading)})
        total_product_terms.extend((coefficient, exponent) for exponent, coefficient in expanded.items())
    total = exponential_sum([(tuple(p["phase"]), p["omega_s"]) for p in pair_records])
    require(total == exponential_sum(total_product_terms), "global regrouping")
    series = taylor(total, cap)
    cmin = min(g["cycle_count"] for g in group_records)
    expected_leading = scale(phase(-cmin), sum(prod(c["gap"] for c in g["cycles"]) for g in group_records if g["cycle_count"] == cmin))
    require(all(c == ZERO for c in series[:cmin]) and series[cmin] == expected_leading and expected_leading != ZERO, "global first coefficient")
    forest_terms = [(tuple(p["phase"]), p["omega_s"]) for p in pair_records if selected_cycle[states[p["s"]]] is None]
    require(total == exponential_sum(forest_terms), "cyclic fibers fail to cancel globally")
    # The rooted-component consequence is checked only where a partner exists.
    for _, s in pairs:
        if selected_cycle[s] is None:
            require(all(len(set(c) & T.roots) == 1 for c in components(T.map.vertices, q[s])), "forest root component count")
    state_records = [{"id": sid[s], "values": list(s), "omega": omega[s],
                      "Q_edges": [list(e) for e in q[s]],
                      "Q_components": components(T.map.vertices, q[s]),
                      "chosen_cycle": list(selected_cycle[s]) if selected_cycle[s] else None,
                      "partner_count": sum(ss == s for _, ss in pairs)} for s in states]
    summary = {"vertices": len(T.map.vertices), "edges": len(T.map.edges), "triangles": len(T.faces),
               "black_faces": len(T.A)+1, "nonroots": len(T.X), "local_choice_space": prod(map(len, T.incidence)),
               "states": len(states), "ordered_disjoint_pairs": len(pairs), "cyclic_Q_states": len(cyclic_states),
               "cyclic_Q_states_with_partners": sum(any(ss == s for _, ss in pairs) for s in cyclic_states),
               "reversal_checks": len(reversals), "undirected_groups": len(groups),
               "group_cycle_counts": dict(sorted(Counter(g["cycle_count"] for g in group_records).items())),
               "spoke_vertices": len(H.vertices), "spoke_edges": len(H.edges), "bounded_spoke_faces": len(H.faces)-1,
               "c_min": cmin, "first_coefficient": list(expected_leading),
               "separating_triangles": len(T.nonfacial_triangles),
               "involution_fixture_coverage": "nonvacuous" if reversals else "vacuous"}
    result = {"schema": "family180-certificate-v1", "checker_version": VERSION, "upstream_pin": PIN,
              "fixture": fixture["name"], "summary": summary,
              "faces": [{"id": j, "vertices": list(f), "color": T.color[j]} for j, f in enumerate(T.faces)],
              "outer_face_id": T.outer, "roots": sorted(T.roots), "A": T.A, "X": T.X,
              "incidences": [{"face": t, "nonroot_vertices": vs} for t, vs in zip(T.A, T.incidence)],
              "delta": [{"dart": list(d), "sign": s} for d, s in sorted(T.delta.items())],
              "spokes": {"centers": [{"face": t, "vertex": c} for t, c in centers.items()],
                         "rotation": H.rotation, "faces": [list(f) for f in H.faces], "outer_face": outerH,
                         "weights": [{"face": t, "vertex": v, "weight": w} for (t, v), w in sorted(weights.items())],
                         "dual_unit_paths": routes, "face_circulations": circulations},
              "states": state_records, "pairs": pair_records, "reversals": reversals,
              "groups": group_records, "Z": serialize_exp(total), "taylor": serialize_series(series), "taylor_cap": cap}
    # Normalize integer dictionary keys exactly as JSON round-tripping does.
    return json.loads(json.dumps(result))


def verify_certificate(fixture: dict, certificate: dict) -> None:
    # No hash shortcut: semantic reconstruction precedes certificate comparison.
    fresh = audit(fixture, certificate["spokes"]["weights"])
    require(certificate == fresh, "certificate differs from recomputed incidences/signs/states/cycles/weights/sums")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write certificates; default verifies the delivered ones")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    summaries = {}
    for path in sorted((args.root / "fixtures").glob("*.json")):
        fixture = json.loads(path.read_text(encoding="utf-8"))
        certificate = audit(fixture)
        destination = args.root / "certificates" / path.name
        if args.write:
            destination.parent.mkdir(exist_ok=True)
            destination.write_text(json.dumps(certificate, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        else:
            verify_certificate(fixture, json.loads(destination.read_text(encoding="utf-8")))
        summaries[fixture["name"]] = certificate["summary"]
        print(json.dumps({"fixture": fixture["name"], "status": "PASS", **certificate["summary"]}, sort_keys=True))
    require(len(summaries) == 1, "expected the single declared follow-up fixture")
    if args.write:
        (args.root / "results.json").write_text(json.dumps(summaries, indent=2, sort_keys=True)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
