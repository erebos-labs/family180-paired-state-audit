#!/usr/bin/env python3
"""Reproduce exactly four inputs, never a graph search. Checker is separate.

Original audit code prepared for Erebos Labs, 2026. See LICENSE.md.
"""
from __future__ import annotations
import json
from itertools import product
from pathlib import Path


def bipyramid(m: int) -> list[tuple[int, int, int]]:
    if m not in (4, 6, 8):
        raise ValueError("Only C4, C6 and C8 are in this investigation")
    u, v = m, m + 1
    return ([(u, j, (j + 1) % m) for j in range(m)] +
            [(v, (j + 1) % m, j) for j in range(m)])


def coned_cube() -> list[tuple[int, int, int]]:
    points = list(product((-1, 1), repeat=3))
    triangles = []
    for axis in range(3):
        for side in (-1, 1):
            face = [i for i, p in enumerate(points) if p[axis] == side]
            a = min(face)
            adjacent = lambda i, j: sum(x != y for x, y in zip(points[i], points[j])) == 1
            b = min(i for i in face if adjacent(a, i))
            c = next(i for i in face if i not in (a, b) and adjacent(b, i))
            d = next(i for i in face if i not in (a, b, c))
            u = [points[b][j] - points[a][j] for j in range(3)]
            v = [points[c][j] - points[b][j] for j in range(3)]
            cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
            face = [a, b, c, d] if side * cross[axis] > 0 else [a, d, c, b]
            center = 8 + 2 * axis + int(side == 1)
            triangles.extend((center, face[j], face[(j+1) % 4]) for j in range(4))
    return triangles


def make_input(name: str, triangles: list[tuple[int, int, int]]) -> dict:
    # The checker does not import this routine, and reconstructs all its claims.
    next_neighbor = {}
    dart_face = {}
    for f, triangle in enumerate(triangles):
        for j in range(3):
            a, b, c = triangle[j], triangle[(j+1) % 3], triangle[(j+2) % 3]
            next_neighbor.setdefault(b, {})[c] = a
            dart_face[a, b] = f
    rotations = {}
    for vertex, successor in sorted(next_neighbor.items()):
        first = min(successor)
        order = [first]
        while successor[order[-1]] != first:
            order.append(successor[order[-1]])
            if len(order) > len(successor):
                raise ValueError("Invalid generator vertex link")
        rotations[str(vertex)] = order
    color = {0: 0}
    queue = [0]
    for f in queue:
        t = triangles[f]
        for j in range(3):
            g = dart_face[t[(j+1) % 3], t[j]]
            if g not in color:
                color[g] = 1 - color[f]
                queue.append(g)
            if color[g] == color[f]:
                raise ValueError("Uncolorable generated fixture")
    return {
        "schema": "family180-fixture-v1", "name": name,
        "size_cap": 14, "rotation_convention": "counterclockwise",
        "rotation": rotations, "outer_face": list(triangles[0]),
        "faces": [{"vertices": list(t), "color": "black" if color[f] == 0 else "white"}
                  for f, t in enumerate(triangles)]}


def all_inputs() -> list[dict]:
    return [make_input(f"bipyramid_C{m}", bipyramid(m)) for m in (4, 6, 8)] + [
        make_input("coned_cube_14", coned_cube())]


def main() -> None:
    target = Path(__file__).resolve().parent / "fixtures"
    target.mkdir(exist_ok=True)
    for fixture in all_inputs():
        path = target / (fixture["name"] + ".json")
        path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(path.name)


if __name__ == "__main__":
    main()
