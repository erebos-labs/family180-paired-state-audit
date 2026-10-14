"""Independent finite replay: standard library, no delivered checker imports.

Faces are accepted only after oriented corner/link and named-graph checks.
Enumerates Cartesian products, uses union-find for disks and Q, and constructs
spoke rotations directly from original vertex sectors (no stellar subdivision).
"""
from pathlib import Path
from itertools import product, combinations
from collections import defaultdict
from fractions import Fraction
from math import factorial
import json

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'replay_output' / 'independent'
OUTPUT.mkdir(parents=True, exist_ok=True)
PKG = ROOT

def check(ok, msg):
    if not ok:
        raise RuntimeError(msg)

def canon(c):
    c = tuple(c)
    return min(c[i:] + c[:i] for i in range(len(c)))

def darts(c):
    return list(zip(c, c[1:] + c[:1]))

def edge(a, b):
    return tuple(sorted((a, b)))

def partition(vertices, edges):
    parent = {v: v for v in vertices}
    def find(v):
        while v != parent[v]:
            v = parent[v]
        return v
    cyclic = False
    for a, b in edges:
        x, y = find(a), find(b)
        cyclic |= x == y
        parent[x] = y
    groups = defaultdict(set)
    for v in vertices:
        groups[find(v)].add(v)
    return list(groups.values()), cyclic

def region(faces, cycle, outer):
    left = {d: i for i, f in enumerate(faces) for d in darts(f)}
    boundary = {edge(*d) for d in darts(cycle)}
    dual = [(left[a, b], left[b, a]) for a, b in left
            if a < b and edge(a, b) not in boundary]
    groups, _ = partition(range(len(faces)), dual)
    check(len(groups) == 2, 'disk separation')
    inside = next(g for g in groups if outer not in g)
    side = [left[d] in inside for d in darts(cycle)]
    check(len(set(side)) == 1, 'disk side')
    return inside, side[0]

def face_orbits(rot):
    successor = {(a, b): (b, ns[ns.index(a)-1])
                 for b, ns in rot.items() for a in ns}
    seen, faces = set(), []
    for first in sorted(successor):
        if first in seen:
            continue
        d, walk = first, []
        while d not in seen:
            seen.add(d); walk.append(d[0]); d = successor[d]
        check(d == first, 'spoke face closes')
        faces.append(canon(walk))
    return sorted(faces)

def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def on_segment(a, b, p):
    return cross(a,b,p)==0 and all(min(a[k],b[k]) <= p[k] <= max(a[k],b[k]) for k in (0,1))

def polygon_contains(p, cycle, xy):
    # Exact horizontal-ray parity, independent of the supplied winding routine.
    odd = False
    for u, v in darts(cycle):
        a,b=xy[u],xy[v]
        check(not on_segment(a,b,p), 'sample lies on polygon boundary')
        if (a[1] > p[1]) != (b[1] > p[1]):
            intersection = a[0]+(p[1]-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if intersection > p[0]: odd = not odd
    return odd

def geometric_inside(faces, cycle, outer, xy):
    return {i for i,t in enumerate(faces) if i != outer and
            polygon_contains(tuple(sum(xy[v][k] for v in t)/3 for k in (0,1)),cycle,xy)}

def verify_planar_geometry(fixture, edges, faces, outer):
    old = [(3,0,0),(0,3,0),(0,0,3),(-3,0,0),(0,-3,0),(0,0,-3)]
    coords = dict(enumerate(old))
    for u,x,y,v in ((3,6,7,1),(4,8,9,2),(5,10,11,0)):
        coords[x] = tuple(Fraction(2*a+b,3) for a,b in zip(old[u],old[v]))
        coords[y] = tuple(Fraction(a+2*b,3) for a,b in zip(old[u],old[v]))
    check(coords == {int(k):tuple(v) for k,v in fixture['construction']['integer_coordinates'].items()}, 'fixed construction coordinates')
    xy = {v:tuple((Fraction(q[k])+Fraction(4,3))/(sum(q)+4)-Fraction(4,3) for k in (0,1)) for v,q in coords.items()}
    check(len(set(xy.values())) == 12, 'distinct planar vertices')
    tests=0
    for a,b in edges:
        for v in xy:
            if v not in (a,b): check(not on_segment(xy[a],xy[b],xy[v]), 'vertex on unrelated edge')
    for (a,b),(c,d) in combinations(sorted(edges),2):
        if len({a,b,c,d}) != 4: continue
        tests += 1
        check(not any((on_segment(xy[a],xy[b],xy[c]), on_segment(xy[a],xy[b],xy[d]), on_segment(xy[c],xy[d],xy[a]),on_segment(xy[c],xy[d],xy[b]))), 'nonincident edges touch')
        check(not (cross(xy[a],xy[b],xy[c])*cross(xy[a],xy[b],xy[d]) < 0 and cross(xy[c],xy[d],xy[a])*cross(xy[c],xy[d],xy[b]) < 0), 'nonincident edges cross')
    check(tests == 309, 'all nonincident edge pairs')
    for i,t in enumerate(faces):
        signed = cross(*(xy[v] for v in t))
        check(signed < 0 if i == outer else signed > 0, 'outer and bounded face geometric orientation')
    check(polygon_contains((sum(xy[v][0] for v in range(3))/3,sum(xy[v][1] for v in range(3))/3),faces[outer],xy), 'inner triangle lies in outer triangle')
    print('GEOMETRY PASS: exact planar coordinates, 309 edge pairs, oriented faces')
    return xy

def verify_reversal(faces, outer, black, roots, A, X, states, all_Q, weights, cert, xy):
    def all_cycles(edges):
        found=[]
        # Exhaustive edge subsets plus degree/connectivity criterion, no DFS.
        for mask in range(1<<len(edges)):
            chosen=[e for j,e in enumerate(edges) if mask>>j&1]
            vertices={v for e in chosen for v in e}
            if len(chosen)<3 or len(chosen)!=len(vertices): continue
            if any(sum(v in e for e in chosen)!=2 for v in vertices): continue
            if len(partition(vertices,chosen)[0])==1: found.append(set(chosen))
        return found
    left={d:i for i,t in enumerate(faces) for d in darts(t)}
    def J(r,s):
        raw=sum(1 if left[a,b] in black else -1 for a,b in zip(r,s))
        check(raw%3==0,'reversal index integrality');return raw//3
    phases=[(1,0),(0,1),(-1,0),(0,-1)]
    records=json.loads((PKG/'certificates/reversal_fibers.json').read_text())
    fibers=[]; transitions=[]
    for sid,(s,Q) in enumerate(zip(states,all_Q)):
        cycles=all_cycles(Q)
        partners=[(i,r) for i,r in enumerate(states) if all(a!=b for a,b in zip(r,s))]
        if not cycles or not partners: continue
        check(len(cycles)==1, 'one literal Q cycle')
        boundary=cycles[0]; vertices={v for e in boundary for v in e}
        check(vertices=={0,1,2}, 'literal qualifying cycle')
        check(set(roots).isdisjoint(vertices),'Q roots avoided')
        rowmap={};rows=[]
        for rid,r in partners:
            changed=[j for j,e in enumerate(Q) if e in boundary]
            rr=tuple(next(v for v in faces[t] if v not in (r[j],s[j])) if j in changed else r[j] for j,t in enumerate(A))
            check(rr in states and all(a!=b for a,b in zip(rr,s)) and rr!=r, 'independent partner closure and no fixed point')
            image=states.index(rr);rowmap[rid]=image
            again=tuple(next(v for v in faces[t] if v not in (rr[j],s[j])) if j in changed else rr[j] for j,t in enumerate(A))
            check(again==r,'same independent reversal applied twice')
            outgoing={r[j]:rr[j] for j in changed};c=[min(vertices)]
            while outgoing[c[-1]]!=c[0]: c.append(outgoing[c[-1]])
            c=tuple(c);check(set(c)==vertices,'directed Q cycle')
            region_ids,ccw=region(faces,c,outer)
            check(region_ids==geometric_inside(faces,c,outer,xy),'Q disk rational geometry agrees with dual partition')
            check(region_ids=={faces.index((0,1,2))},'single white triangle disk')
            check(all(t not in black for t in region_ids),'Q disk white')
            suppliers=[left[a,b] if left[a,b] in black else left[b,a] for a,b in darts(c)]
            check(all(r[A.index(t)]==a for t,(a,b) in zip(suppliers,darts(c))),'Q disk supplied by r')
            raw=sum(1 if left[d] in black else -1 for d in darts(c))
            check(raw==(-3 if ccw else 3),'Q geometric disk sign')
            before,after=J(r,s),J(rr,s);check(after-before in (-2,2),'J change exactly two')
            check(tuple(-a for a in phases[before%4])==phases[after%4], 'phase negation')
            omega=sum(weights[t,v] for t,v in zip(A,s))
            disk={'vertices':list(c),'counterclockwise':ccw,'inside_faces':sorted(region_ids),'I':0,'B':0,'W':1,'h':3,'l':0,'delta_sum':raw,'supplier_faces':suppliers}
            row={'r_id':rid,'r_values':list(r),'image_id':image,'image_values':list(rr),'second_state_before':list(s),'second_state_after':list(s),'J_before':before,'J_after':after,'J_change':after-before,'phase_before':list(phases[before%4]),'phase_after':list(phases[after%4]),'weight_before':omega,'weight_after':omega,'oriented_cycle':list(c),'disk':disk}
            rows.append(row);transitions.append({'s':sid,'r':rid,'image':image,'J_before':before,'J_after':after,'omega':omega})
        ids=[i for i,r in partners]
        check(set(rowmap)==set(rowmap.values())==set(ids) and all(rowmap[rowmap[k]]==k for k in rowmap),'complete partner bijection/involution')
        check(all(sum(phases[J(r,s)%4][k] for i,r in partners)==0 for k in (0,1)), 'exact fixed-s cancellation')
        fibers.append({'s_id':sid,'s_values':list(s),'cycle':[0,1,2],'partner_ids':ids,'orbits':[list(x) for x in sorted({tuple(sorted((k,v))) for k,v in rowmap.items()})],'rows':rows,'fixed_state_exponential_sum':[]})
    check(fibers==records['fibers'],'full independent orbit certificate comparison')
    check(len(fibers)==1 and len(transitions)==2,'literal nonvacuous coverage')
    (OUTPUT/'independent-orbit-results.json').write_text(json.dumps({'fibers':fibers,'transitions':transitions},indent=2)+'\n')
    print('REVERSAL PASS: s=8, complete partners {0,4}, J=-3 <-> -1, omega=4, exact cancellation')

def replay(path):
    f = json.loads(path.read_text())
    cert = json.loads((PKG / 'certificates' / path.name).read_text())
    rot = {int(v): tuple(ns) for v, ns in f['rotation'].items()}
    V = set(rot); E = {edge(v, w) for v in V for w in rot[v]}
    faces = sorted(canon(t['vertices']) for t in f['faces'])
    left = {d: j for j, t in enumerate(faces) for d in darts(t)}
    check(len(left) == 3*len(faces) == 2*len(E), 'dart coverage')
    check(set(left) == {(v, w) for v in V for w in rot[v]}, 'face adjacency')
    for t in faces:
        for a, b, c in zip(t, t[1:]+t[:1], t[2:]+t[:2]):
            check(rot[b][rot[b].index(a)-1] == c, 'oriented face/vertex link')
    check(len(V)-len(E)+len(faces) == 2, 'sphere Euler')
    check(len(partition(V, E)[0]) == 1, 'connected')
    check({frozenset(t) for t in faces} ==
          {frozenset(t) for t in combinations(V, 3)
           if all(edge(a, b) in E for a, b in combinations(t, 2))}, 'all three-cliques facial')
    if f['name'].startswith('bipyramid'):
        m = len(V)-2
        expected = {edge(j, (j+1)%m) for j in range(m)} | {edge(p, j) for p in (m, m+1) for j in range(m)}
    else:
        expected = {edge(a, b) for a, b in combinations(range(6), 2) if abs(a-b) != 3}
        for u, x, y, v in ((3,6,7,1), (4,8,9,2), (5,10,11,0)):
            corners = [w for w in range(6) if w not in (u, v) and abs(w-u) != 3 and abs(w-v) != 3]
            expected.remove(edge(u, v))
            expected |= {edge(u, x), edge(x, y), edge(y, v)} | {edge(z, w) for z in (x, y) for w in corners}
    check(E == expected, 'named graph')
    colors = {canon(t['vertices']): t['color'] for t in f['faces']}
    black = {j for j, t in enumerate(faces) if colors[t] == 'black'}
    check(all((left[a, b] in black) != (left[b, a] in black) for a, b in E), 'dual coloring')
    outer = faces.index(canon(f['outer_face'])); roots = set(f['outer_face'])
    check(outer in black, 'outer black')
    A = sorted(black-{outer}); X = V-roots
    check(A == cert['A'] and sorted(X) == cert['X'], 'state domain')
    xy = verify_planar_geometry(f, E, faces, outer)
    states = [s for s in product(*(sorted(set(faces[t])-roots) for t in A)) if set(s) == X]
    check(states == [tuple(s['values']) for s in cert['states']], 'exhaustive state lists')
    qcyclic = 0
    all_Q = []
    for s, record in zip(states, cert['states']):
        q = [tuple(sorted(set(faces[t])-{v})) for t, v in zip(A, s)]
        all_Q.append(q)
        comps, cyclic = partition(V, q); qcyclic += cyclic
        check(q == [tuple(e) for e in record['Q_edges']], 'Q edges')
        check(sorted(map(sorted, comps)) == record['Q_components'], 'Q components')
        check(cyclic == bool(record['chosen_cycle']), 'Q acyclicity')
    centers = {t: len(V)+j for j, t in enumerate(A)}
    hrot = {centers[t]: faces[t] for t in A}
    for v, ns in rot.items():
        # Each black sector is immediately CCW after the dart v -> w.
        hrot[v] = tuple(centers[left[v, w]] for w in ns if left[v, w] in centers)
    check(all(hrot.values()), 'no isolated H vertex')
    for v, ns in hrot.items():
        check(canon(ns) == canon(cert['spokes']['rotation'][str(v)]), 'direct spoke rotation')
    hfaces = face_orbits(hrot)
    check(hfaces == [tuple(x) for x in cert['spokes']['faces']], 'direct spoke faces')
    # Infinity joins the three sectors surrounding the deleted outer triangle.
    houter = cert['spokes']['outer_face']
    check(all(v in hfaces[houter] for v in roots), 'spoke outer roots')
    weights = {(w['face'], w['vertex']): w['weight'] for w in cert['spokes']['weights']}
    check(set(weights) == {(t, v) for t in A for v in faces[t]}, 'weight incidences')
    check(all(type(w) is int for w in weights.values()), 'integer weights')
    wd = {(centers[t], v): w for (t, v), w in weights.items()}
    wd.update({(b, a): -w for (a, b), w in list(wd.items())})
    circ = [sum(wd[d] for d in darts(t)) for t in hfaces]
    check(circ == [-len(hfaces)+1 if j == houter else 1 for j in range(len(hfaces))], 'face circulation')
    verify_reversal(faces, outer, black, roots, A, X, states, all_Q, weights, cert, xy)
    pairs = [(r, s) for r, s in product(states, repeat=2) if all(a != b for a, b in zip(r, s))]
    check(len(pairs) == len(cert['pairs']), 'exhaustive pair count')
    groups, Z = defaultdict(list), defaultdict(lambda: [0, 0])
    phase = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for j, ((r, s), record) in enumerate(zip(pairs, cert['pairs'])):
        check((states[record['r']], states[record['s']]) == (r, s), 'pair ordering')
        raw = sum(1 if left[a, b] in black else -1 for a, b in zip(r, s))
        check(raw % 3 == 0, 'J integrality'); J = raw//3
        omega = sum(weights[t, v] for t, v in zip(A, s))
        check(J == record['J'] and list(phase[J%4]) == record['phase'] and omega == record['omega_s'], 'phase and frequency')
        D = tuple(sorted(edge(a, b) for a, b in zip(r, s)))
        groups[D].append(j)
        for k in (0, 1): Z[omega][k] += phase[J%4][k]
        nxt = dict(zip(r, s)); cycles = []; remaining = set(X)
        while remaining:
            v = min(remaining); c = [v]; w = nxt[v]
            while w != v: c.append(w); w = nxt[w]
            remaining -= set(c); cycles.append(tuple(c))
        check(len(cycles) == len(record['cycles']), 'cycle components')
        for c in cycles:
            inside, ccw = region(faces, c, outer)
            suppliers = [left[a, b] if left[a, b] in black else left[b, a] for a, b in darts(c)]
            check(all(r[A.index(t)] == a for t, (a, b) in zip(suppliers, darts(c))), 'state-directed disk')
            check(inside == geometric_inside(faces, c, outer, xy), 'independent geometric disk region')
            I = len(set().union(*(set(faces[t]) for t in inside))-set(c))
            B = len(inside & black); W = len(inside)-B; l = sum(t in inside for t in suppliers); h = len(c)
            check(B+W == 2*I+h-2 and 3*(B-W) == 2*l-h and B == I+l, 'disk equations')
            check(sum(1 if left[d] in black else -1 for d in darts(c)) == (-3 if ccw else 3), 'disk sign')
    check({D: ids for D, ids in groups.items()} == {tuple(map(tuple, g['D'])): g['member_pairs'] for g in cert['groups']}, 'literal D grouping')
    for g in cert['groups']:
        check(len(g['member_pairs']) == 2**g['cycle_count'], 'orientation fiber cardinality')
        expanded = {0: (1, 0)}
        cycle_edges=[];orientation_data=[];gap_product=1
        for c in g['cycles']:
            cycle = tuple(c['ccw_vertices']); _, ccw = region(faces, cycle, outer)
            check(ccw, 'group CCW orientation')
            suppliers=[left[a,b] if left[a,b] in black else left[b,a] for a,b in darts(cycle)]
            check(suppliers==c['supplier_faces'],'independent cycle supplier faces')
            cycle_edges.extend(edge(*d) for d in darts(cycle))
            orientation_data.append((cycle,suppliers))
            plus = sum(weights[t, b] for t, (a, b) in zip(c['supplier_faces'], darts(cycle)))
            minus = sum(weights[t, a] for t, (a, b) in zip(c['supplier_faces'], darts(cycle)))
            check((plus, minus) == (c['L_plus'], c['L_minus']), 'cycle weight sums')
            detour = tuple(v for a, t in zip(cycle, c['supplier_faces']) for v in (a, centers[t]))
            inside, ccw = region(hfaces, detour, houter)
            check(ccw and plus-minus == len(inside) == sum(wd[d] for d in darts(detour)) == c['gap'] > 0, 'positive gap')
            gap_product *= plus-minus
            acc = defaultdict(lambda: [0, 0])
            for e, (re, im) in expanded.items():
                for frequency, direction in ((plus, -1), (minus, 1)):
                    # Multiply by direction*i, using exact integer coordinates.
                    acc[e+frequency][0] -= direction*im
                    acc[e+frequency][1] += direction*re
            expanded = {e: tuple(v) for e, v in acc.items() if v != [0, 0]}
        check(sorted(cycle_edges)==[tuple(e) for e in g['D']] and len(cycle_edges)==len(set(cycle_edges)), 'full group cycle decomposition')
        check(len(orientation_data)==g['cycle_count'],'group cycle count')
        oriented=set()
        for flips in product((0,1),repeat=len(orientation_data)):
            r,s=[None]*len(A),[None]*len(A)
            for bit,(cycle,suppliers) in zip(flips,orientation_data):
                for t,(a,b) in zip(suppliers,darts(cycle)):
                    j=A.index(t);check(r[j] is None,'one edge per black face')
                    r[j],s[j]=(b,a) if bit else (a,b)
            r,s=tuple(r),tuple(s)
            check(r in states and s in states and all(a!=b for a,b in zip(r,s)),'orientation incident bijections')
            oriented.add(pairs.index((r,s)))
        check(oriented==set(g['member_pairs']), 'complete independently reconstructed orientation fiber')
        direct = defaultdict(lambda: [0, 0])
        for j in g['member_pairs']:
            r, s = pairs[j]
            omega = sum(weights[t, v] for t, v in zip(A, s))
            raw = sum(1 if left[a, b] in black else -1 for a, b in zip(r, s))
            for k in (0, 1): direct[omega][k] += phase[(raw//3)%4][k]
        direct = {e: tuple(v) for e, v in direct.items() if v != [0, 0]}
        check(direct == expanded == {p['exponent']: tuple(p['coefficient']) for p in g['exponential_sum']}, 'complete group frequency identity')
        gseries=[[sum((Fraction(c[k]*e**d,factorial(d)) for e,c in direct.items()),Fraction(0)) for k in (0,1)] for d in range(cert['taylor_cap']+1)]
        check(gseries==[[Fraction(*x) for x in coeff] for coeff in g['taylor']], 'all group rational Taylor coefficients')
        count=len(orientation_data); expected=tuple(v*gap_product for v in phase[(-count)%4])
        check(all(row==[0,0] for row in gseries[:count]) and tuple(gseries[count])==expected==tuple(g['leading_coefficient']),'group leading phase, product and order')
    Z = {e: c for e, c in Z.items() if c != [0, 0]}
    check(Z == {p['exponent']: p['coefficient'] for p in cert['Z']}, 'exact Z frequency dictionary')
    series = [[sum((Fraction(c[k]*e**d, factorial(d)) for e, c in Z.items()), Fraction(0)) for k in (0, 1)] for d in range(cert['taylor_cap']+1)]
    check(series == [[Fraction(*x) for x in coefficient] for coefficient in cert['taylor']], 'exact rational Taylor coefficients')
    result = {'fixture': f['name'], 'states': len(states), 'pairs': len(pairs), 'cyclic_Q': qcyclic, 'groups': len(groups), 'Z': Z, 'leading': str(series[1]), 'status': 'PASS'}
    print(json.dumps(result, sort_keys=True))
    return result

if __name__ == '__main__':
    results = [replay(p) for p in sorted((PKG/'fixtures').glob('*.json'))]
    (OUTPUT/'independent-results.json').write_text(json.dumps(results, indent=2)+'\n')
