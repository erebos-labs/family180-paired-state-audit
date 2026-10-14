#!/usr/bin/env python3
"""The one predeclared 12-vertex fixture. No state or partner search.
Original Erebos Labs audit code, 2026; see LICENSE.md.
"""
from itertools import product
from pathlib import Path
import json

NAME = 'octahedron_three_edge_expansion_12'
POINTS = [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)]
PATHS = [(3,6,7,1),(4,8,9,2),(5,10,11,0)]
OUTER = (3,5,4)

def determinant(a,b,c):
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def construction():
    faces = []
    for a,b,c in product((0,3),(1,4),(2,5)):
        if determinant(POINTS[a],POINTS[b],POINTS[c]) < 0: b,c=c,b
        faces.append((a,b,c))
    refined = []
    for f in faces:
        hits = [p for p in PATHS if p[0] in f and p[-1] in f]
        if not hits:
            refined.append(f); continue
        if len(hits)!=1: raise ValueError('the selected edges must share no old face')
        p=hits[0]
        for j in range(3):
            a,b,c=f[j],f[(j+1)%3],f[(j+2)%3]
            if {a,b}=={p[0],p[-1]}:
                q=p if a==p[0] else p[::-1]
                refined.extend((q[k],q[k+1],c) for k in range(3))
                break
    canonical=lambda f:min(f[j:]+f[:j] for j in range(len(f)))
    outer=canonical(OUTER)
    refined=sorted(canonical(f) for f in refined)
    refined=[outer]+[f for f in refined if f!=outer]
    coordinates={str(v):[3*x for x in q] for v,q in enumerate(POINTS)}
    for u,x,y,v in PATHS:
        coordinates[str(x)]=[2*a+b for a,b in zip(POINTS[u],POINTS[v])]
        coordinates[str(y)]=[a+2*b for a,b in zip(POINTS[u],POINTS[v])]
    nxt={}; left={}
    for f,tri in enumerate(refined):
        for j in range(3):
            a,b,c=tri[j],tri[(j+1)%3],tri[(j+2)%3]
            nxt.setdefault(b,{})[c]=a
            left[a,b]=f
    rotation={}
    for v,successor in sorted(nxt.items()):
        start=min(successor); seq=[start]
        while successor[seq[-1]]!=start:
            seq.append(successor[seq[-1]])
            if len(seq)>len(successor):raise ValueError('invalid vertex link')
        if len(seq)!=len(successor):raise ValueError('disconnected vertex link')
        rotation[str(v)]=seq
    color={0:0}; queue=[0]
    for f in queue:
        for j in range(3):
            a,b=refined[f][j],refined[f][(j+1)%3]
            g=left[b,a]
            if g not in color:color[g]=1-color[f];queue.append(g)
            if color[g]==color[f]:raise ValueError('not face-colorable')
    return {'schema':'family180-fixture-v1','name':NAME,'size_cap':20,
            'rotation_convention':'counterclockwise','rotation':rotation,
            'outer_face':list(OUTER),
            'faces':[{'vertices':list(f),'color':'black' if color[i]==0 else 'white'} for i,f in enumerate(refined)],
            'construction':{'old_antipodal_pairs':[[0,3],[1,4],[2,5]],'expanded_paths':[list(p) for p in PATHS],
                            'coordinates_scale':3,'integer_coordinates':coordinates}}

if __name__=='__main__':
    dest=Path(__file__).resolve().parent/'fixtures'/f'{NAME}.json'
    dest.write_text(json.dumps(construction(),indent=2,sort_keys=True)+'\n')
    print(f'Wrote the single declared fixture: {dest.name}')
