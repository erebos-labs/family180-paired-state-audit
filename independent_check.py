#!/usr/bin/env python3
"""Second exact implementation for the ONE declared fixture.

No imports from checker.py, involution.py or fixture_builder.py. Reconstructs
geometry by rational Schlegel projection, tests edges for crossings, obtains
rotations by rational angular sorting, exhausts the Cartesian assignment space,
and reconstructs all partners, cycle sets, weights, phases and reversal maps.
Written/reviewed by the same assistant, NOT an independent worker or Lean proof.
"""
from collections import defaultdict
from fractions import Fraction as F
from functools import cmp_to_key
from itertools import combinations, product
from math import factorial, prod
import json
from pathlib import Path

class ReferenceRejected(ValueError):pass

def need(ok,message):
    if not ok:raise ReferenceRejected(message)

def edge(a,b):return tuple(sorted((a,b)))
def canon(c):
    c=tuple(c)
    return min(c[i:]+c[:i] for i in range(len(c)))
def uncycle(c):return min(canon(c),canon(tuple(c)[::-1]))
def darts(c):return list(zip(c,c[1:]+c[:1]))
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def area(c,xy):return sum(xy[a][0]*xy[b][1]-xy[a][1]*xy[b][0] for a,b in darts(c))
def between(a,b,p):return cross(a,b,p)==0 and all(min(a[k],b[k])<=p[k]<=max(a[k],b[k]) for k in (0,1))

def angle_order(v,neighbors,xy):
    def compare(a,b):
        p=(xy[a][0]-xy[v][0],xy[a][1]-xy[v][1])
        q=(xy[b][0]-xy[v][0],xy[b][1]-xy[v][1])
        hp=0 if p[1]>0 or (p[1]==0 and p[0]>0) else 1
        hq=0 if q[1]>0 or (q[1]==0 and q[0]>0) else 1
        if hp!=hq:return -1 if hp<hq else 1
        z=p[0]*q[1]-p[1]*q[0]
        need(z!=0,'collinear rays at a vertex')
        return -1 if z>0 else 1
    return tuple(sorted(neighbors,key=cmp_to_key(compare)))

def faces_from_angles(rot):
    permutation={}
    for v,ns in rot.items():
        for k,u in enumerate(ns):permutation[u,v]=(v,ns[k-1])
    remaining=set(permutation);faces=[]
    while remaining:
        start=min(remaining);d=start;face=[]
        while True:
            need(d in remaining,'dart permutation overlaps')
            remaining.remove(d);face.append(d[0]);d=permutation[d]
            if d==start:break
        faces.append(canon(face))
    return sorted(faces)

def check_segments(xy,edges):
    tests=0
    for a,b in edges:
        for v in xy:
            if v not in (a,b):need(not between(xy[a],xy[b],xy[v]),'vertex in edge interior')
    for (a,b),(c,d) in combinations(edges,2):
        if {a,b}&{c,d}:continue
        tests+=1
        s=[cross(xy[a],xy[b],xy[x]) for x in (c,d)]
        t=[cross(xy[c],xy[d],xy[x]) for x in (a,b)]
        need(not(s[0]*s[1]<0 and t[0]*t[1]<0),'nonincident edge crossing')
        need(not any((between(xy[a],xy[b],xy[c]),between(xy[a],xy[b],xy[d]),
                      between(xy[c],xy[d],xy[a]),between(xy[c],xy[d],xy[b]))),'nonincident edge touching')
    return tests

def components(n,edges):
    parent=list(range(n))
    def root(v):
        while parent[v]!=v:v=parent[v]
        return v
    for a,b in edges:parent[root(a)]=root(b)
    out=defaultdict(list)
    for v in range(n):out[root(v)].append(v)
    return sorted(sorted(v) for v in out.values())

def cycles_by_edge_subsets(edges):
    """All simple undirected cycles, including completeness, by edge subsets.
    There are exactly 9 Q or D edges here, hence only 512 subsets per graph.
    This deliberately does not reuse the primary DFS or cycle-union code.
    """
    out=set();edges=sorted(edges)
    for mask in range(1<<len(edges)):
        if mask.bit_count()<3:continue
        adj=defaultdict(list)
        for j,(a,b) in enumerate(edges):
            if mask>>j&1:adj[a].append(b);adj[b].append(a)
        if any(len(ns)!=2 for ns in adj.values()):continue
        start=min(adj);walk=[start];prev=None;v=start
        while True:
            w=next(x for x in sorted(adj[v]) if x!=prev)
            if w==start:break
            if w in walk:break
            walk.append(w);prev,v=v,w
        if w==start and len(walk)==len(adj):out.add(uncycle(walk))
    return sorted(out)

def inside(point,polygon,xy):
    winding=0
    for a,b in darts(polygon):
        u,v=xy[a],xy[b]
        need(not between(u,v,point),'interior sample is on polygon boundary')
        if u[1]<=point[1]<v[1] and cross(u,v,point)>0:winding+=1
        if v[1]<=point[1]<u[1] and cross(u,v,point)<0:winding-=1
    return winding!=0

def gadd(a,b):return a[0]+b[0],a[1]+b[1]
def gmul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def phase(j):
    # Repeated Gaussian multiplication, not the primary four-entry lookup.
    value=(1,0)
    for _ in range(j%4):value=(-value[1],value[0])
    return value

def exp_sum(terms):
    p=defaultdict(lambda:(0,0))
    for w,c in terms:p[w]=gadd(p[w],c)
    return {w:c for w,c in sorted(p.items()) if c!=(0,0)}
def exp_json(p):return [{'exponent':w,'coefficient':list(c)} for w,c in sorted(p.items())]
def series_json(p,cap):
    return [[[z.numerator,z.denominator] for z in
             (sum((F(c[k]*w**d,factorial(d)) for w,c in p.items()),F(0)) for k in (0,1))]
            for d in range(cap+1)]

def verify(fixture,full,orbit_certificate):
    need(fixture['name']=='octahedron_three_edge_expansion_12','wrong declared fixture')
    # Independent expected graph and coordinates, not assertions from builder.
    p3={0:(3,0,0),1:(0,3,0),2:(0,0,3),3:(-3,0,0),4:(0,-3,0),5:(0,0,-3)}
    paths=((3,6,7,1),(4,8,9,2),(5,10,11,0))
    edges={edge(a,b) for a,b in combinations(range(6),2) if abs(a-b)!=3}
    for u,x,y,v in paths:
        # Original antipodal rule gives the two opposite corners even after edits.
        opp=[w for w in range(6) if w not in (u,v) and abs(w-u)!=3 and abs(w-v)!=3]
        need(len(opp)==2,'two opposite old corners')
        edges.remove(edge(u,v));edges.update((edge(u,x),edge(x,y),edge(y,v)))
        edges.update(edge(z,w) for z in (x,y) for w in opp)
        p3[x]=tuple((2*a+b)//3 for a,b in zip(p3[u],p3[v]))
        p3[y]=tuple((a+2*b)//3 for a,b in zip(p3[u],p3[v]))
    need(len(p3)==12 and len(edges)==30,'construction size')
    need(fixture['construction']['integer_coordinates']=={str(v):list(p) for v,p in p3.items()},'coordinate claims')
    # Schlegel view from P=(-4/3,-4/3,-4/3), onto x+y+z=-3.
    # P violates only that octahedral facet inequality. Use x,y on the plane.
    xy={v:tuple(F(-4,3)+(F(p[k])+F(4,3))/(sum(p)+4) for k in (0,1)) for v,p in p3.items()}
    need(len(set(xy.values()))==12,'projected vertices distinct')
    adj={v:[] for v in p3}
    for a,b in edges:adj[a].append(b);adj[b].append(a)
    angles={v:angle_order(v,ns,xy) for v,ns in adj.items()}
    rot={int(v):tuple(ns) for v,ns in fixture['rotation'].items()}
    need(set(rot)==set(p3),'rotation vertices')
    need(all(canon(rot[v])==canon(angles[v]) for v in p3),'rotation matches exact geometric angle order')
    segment_tests=check_segments(xy,sorted(edges))
    faces=faces_from_angles(angles)
    need(len(faces)==20 and all(len(f)==3 for f in faces),'twenty triangular face orbits')
    need(12-30+len(faces)==2,'sphere Euler count')
    outer=faces.index(canon((3,5,4)));roots={3,4,5}
    need(canon(tuple(fixture['outer_face']))==faces[outer],'root face')
    need(area(faces[outer],xy)<0 and all(area(f,xy)>0 for i,f in enumerate(faces) if i!=outer),'geometric outer/bounded orientations')
    need(sum(area(f,xy) for f in faces)==0,'signed facial area sum')
    left={d:i for i,f in enumerate(faces) for d in darts(f)}
    color={outer:0};todo=[outer]
    for i in todo:
        for a,b in darts(faces[i]):
            j=left[b,a]
            if j not in color:color[j]=1-color[i];todo.append(j)
            need(color[j]!=color[i],'face coloring contradiction')
    need(len(color)==20,'complete face coloring')
    claims={canon(tuple(f['vertices'])):f['color'] for f in fixture['faces']}
    need(len(claims)==20 and claims=={f:'black' if color[i]==0 else 'white' for i,f in enumerate(faces)},'face incidence/color claims')
    A=[i for i in range(20) if color[i]==0 and i!=outer];X=sorted(set(p3)-roots)
    choices=[tuple(v for v in X if v in faces[t]) for t in A]
    candidates=prod(map(len,choices));need(candidates<=200000,'candidate cap')
    seen=0;states=[]
    for values in product(*choices):
        seen+=1
        if len(set(values))==len(values) and set(values)==set(X):states.append(values)
    need(seen==candidates and len(states)<=10000,'complete capped Cartesian enumeration')
    need(full['A']==A and full['X']==X and full['roots']==sorted(roots),'domains and roots')
    need([tuple(s['values']) for s in full['states']]==states,'exact state list agreement')
    need([s['id'] for s in full['states']]==list(range(len(states))),'state identifiers')
    pairs=[(i,j) for i,r in enumerate(states) for j,s in enumerate(states) if all(a!=b for a,b in zip(r,s))]
    need([(p['r'],p['s']) for p in full['pairs']]==pairs,'all ordered disjoint partners')
    need([p['id'] for p in full['pairs']]==list(range(len(pairs))),'pair identifiers')
    Q=[tuple(edge(*[v for v in faces[t] if v!=s[k]]) for k,t in enumerate(A)) for s in states]
    qcycles=[cycles_by_edge_subsets(q) for q in Q]
    for j,s in enumerate(states):
        need(full['states'][j]['Q_edges']==[list(e) for e in Q[j]],'Q edge reconstruction')
        need(full['states'][j]['Q_components']==components(12,Q[j]),'union-find Q components')
        chosen=list(qcycles[j][0]) if qcycles[j] else None
        need(full['states'][j]['chosen_cycle']==chosen,'exhaustive edge-subset Q cycles')
    # Geometric reconstruction of H0 from straight center spokes in each black face.
    centers={t:12+k for k,t in enumerate(A)}
    hxy=dict(xy);hadj={v:[] for v in xy}
    for t,k in centers.items():
        hxy[k]=tuple(sum(xy[v][a] for v in faces[t])/3 for a in (0,1))
        hadj[k]=list(faces[t])
        for v in faces[t]:hadj[v].append(k)
    need(all(hadj.values()),'connected nonisolated spoke scope')
    hrot={v:angle_order(v,ns,hxy) for v,ns in hadj.items()}
    hf=faces_from_angles(hrot);ho=[i for i,f in enumerate(hf) if area(f,hxy)<0]
    need(len(ho)==1 and all(area(f,hxy)>0 for i,f in enumerate(hf) if i not in ho),'spoke geometric faces')
    ho=ho[0]
    need([list(f) for f in hf]==full['spokes']['faces'] and ho==full['spokes']['outer_face'],'spoke face reconstruction agreement')
    weights={(w['face'],w['vertex']):w['weight'] for w in full['spokes']['weights']}
    need(set(weights)=={(t,v) for t in A for v in faces[t]} and all(type(w)is int for w in weights.values()),'complete integer spoke weights')
    wd={}
    for (t,v),w in weights.items():wd[centers[t],v]=w;wd[v,centers[t]]=-w
    circulation=[sum(wd[d] for d in darts(f)) for f in hf]
    need(circulation==[-(len(hf)-1) if i==ho else 1 for i in range(len(hf))],'geometric spoke face circulations')
    omega=[sum(weights[t,s[k]] for k,t in enumerate(A)) for s in states]
    need([s['omega'] for s in full['states']]==omega,'state weights')
    def delta(a,b):return 1 if color[left[a,b]]==0 else -1
    def index(r,s):
        raw=sum(delta(a,b) for a,b in zip(r,s));need(raw%3==0,'exact index divisibility')
        return raw//3
    def supplier(a,b):return left[a,b] if color[left[a,b]]==0 else left[b,a]
    def disk(cycle,r):
        bounded=[i for i,f in enumerate(faces) if i!=outer and inside(tuple(sum(xy[v][k] for v in f)/3 for k in (0,1)),cycle,xy)]
        vertices=[v for v in xy if v not in cycle and inside(xy[v],cycle,xy)]
        bs=sum(color[t]==0 for t in bounded);ws=len(bounded)-bs
        suppliers=[supplier(a,b) for a,b in darts(cycle)]
        need(all(t in A and r[A.index(t)]==a for t,(a,b) in zip(suppliers,darts(cycle))),'geometric cycle tails incident')
        l=sum(t in bounded for t in suppliers);h=len(cycle);iv=len(vertices)
        ccw=area(cycle,xy)>0;raw=sum(delta(a,b) for a,b in darts(cycle))
        need(not (roots & set(cycle)) and not (roots & set(vertices)),'root avoidance')
        need(bs+ws==2*iv+h-2 and 3*(bs-ws)==2*l-h and bs==iv+l,'geometric disk equations')
        need(raw==(-3 if ccw else 3),'geometric signed disk identity')
        return {'vertices':list(cycle),'counterclockwise':ccw,'inside_faces':bounded,'I':iv,'B':bs,'W':ws,'h':h,'l':l,'delta_sum':raw,'supplier_faces':suppliers}
    group_members=defaultdict(list);all_terms=[]
    for pid,(ri,si) in enumerate(pairs):
        r,s=states[ri],states[si];J=index(r,s);rec=full['pairs'][pid]
        need(rec['J']==J and rec['phase']==list(phase(J)) and rec['omega_s']==omega[si],'pair phase/index/weight')
        D=tuple(sorted(edge(a,b) for a,b in zip(r,s)));need(len(set(D))==len(X),'distinct D edges')
        cs=cycles_by_edge_subsets(D);need(sum(len(x) for x in cs)==len(X) and len(set(v for C in cs for v in C))==len(X),'D cycle cover')
        directed=dict(zip(r,s));disks=[]
        for C in cs:
            if directed[C[0]]!=C[1]:C=canon(C[::-1])
            need(all(directed[a]==b for a,b in darts(C)),'D cycle orientation')
            disks.append(disk(C,r))
        need(disks==rec['cycles'],'independent geometric D disks')
        group_members[D].append(pid);all_terms.append((omega[si],phase(J)))
    qualifying=[j for j,C in enumerate(qcycles) if C and any(si==j for ri,si in pairs)]
    need(qualifying,'nonvacuous independent Q coverage')
    reference_reversals=[];reference_orbits=[]
    for si in qualifying:
        s=states[si];C=qcycles[si][0];boundary={edge(*d) for d in darts(C)}
        pp=[ri for ri,sj in pairs if sj==si];mapping={};rows=[]
        for ri in pp:
            r=states[ri];image=list(r)
            for k,t in enumerate(A):
                if Q[si][k] in boundary:image[k]=next(v for v in faces[t] if v not in (r[k],s[k]))
            image=tuple(image);need(image in states,'reference reversal is a state');ii=states.index(image)
            need(ii in pp and ii!=ri,'reference partner closure and no fixed points');mapping[ri]=ii
            before=index(r,s);after=index(image,s)
            need(after-before in (-2,2) and phase(after)==tuple(-x for x in phase(before)),'reference phase change')
            changed={r[k]:image[k] for k in range(len(A)) if r[k]!=image[k]}
            oriented=C if changed[C[0]]==C[1] else canon(C[::-1])
            need(all(changed[a]==b for a,b in darts(oriented)),'reference Q orientation')
            dd=disk(oriented,r)
            pid=pairs.index((ri,si));iid=pairs.index((ii,si))
            reference_reversals.append({'pair':pid,'image_pair':iid,'cycle':list(C),'disk':dd,'J_change':after-before,'unchanged_exponent':omega[si]})
            rows.append((ri,ii))
        need(set(mapping)==set(mapping.values()) and all(mapping[mapping[x]]==x for x in mapping),'reference bijection/involution')
        need(exp_sum([(omega[si],phase(index(states[r],s))) for r in pp])=={},'reference fixed-state cancellation')
        reference_orbits.append({'s_id':si,'partner_ids':pp,'orbits':[list(x) for x in sorted({tuple(sorted(x)) for x in rows})]})
    need(full['reversals']==reference_reversals,'complete primary reversal records match independent construction')
    need([{'s_id':f['s_id'],'partner_ids':f['partner_ids'],'orbits':f['orbits']} for f in orbit_certificate['fibers']]==reference_orbits,'complete orbit certificate')
    # Reconstruct orientation products, including the genuine three-cycle fiber.
    counts={};leading=[]
    for rec,(D,members) in zip(full['groups'],sorted(group_members.items())):
        need(rec['D']==[list(e) for e in D] and rec['member_pairs']==members,'D fiber membership')
        cs=cycles_by_edge_subsets(D);counts[len(cs)]=counts.get(len(cs),0)+1
        options=[];gaps=[];assignments=[]
        for C in cs:
            if area(C,xy)<0:C=canon(C[::-1])
            suppliers=[supplier(a,b) for a,b in darts(C)]
            lp=sum(weights[t,b] for t,(a,b) in zip(suppliers,darts(C)))
            lm=sum(weights[t,a] for t,(a,b) in zip(suppliers,darts(C)))
            need(lp>lm,'positive cycle gap independently checked')
            gaps.append(lp-lm);options.append([(lp,(0,-1)),(lm,(0,1))]);assignments.append((C,suppliers))
        orientations=set();terms=[]
        for bits in product((0,1),repeat=len(cs)):
            rr=[None]*len(A);ss=[None]*len(A);w=0;ph=(1,0)
            for bit,(C,suppliers),opt in zip(bits,assignments,options):
                exponent,p=opt[bit];w+=exponent;ph=gmul(ph,p)
                for t,(a,b) in zip(suppliers,darts(C)):
                    k=A.index(t);rr[k],ss[k]=(b,a) if bit else (a,b)
            need(tuple(rr) in states and tuple(ss) in states,'reference orientation state validity')
            orientations.add((states.index(tuple(rr)),states.index(tuple(ss))));terms.append((w,ph))
        need(orientations=={pairs[p] for p in members} and len(members)==2**len(cs),'all independent cycle orientations')
        direct=exp_sum([(omega[pairs[p][1]],phase(index(states[pairs[p][0]],states[pairs[p][1]]))) for p in members])
        need(direct==exp_sum(terms) and rec['exponential_sum']==exp_json(direct),'reference cycle-product identity')
        need(rec['taylor']==series_json(direct,full['taylor_cap']),'reference group rational Taylor coefficients')
        lead=tuple(z*prod(gaps) for z in phase(-len(cs)))
        need(rec['leading_coefficient']==list(lead),'reference cycle leading product');leading.append((len(cs),lead))
    need(len(full['groups'])==len(group_members),'all D groups')
    Z=exp_sum(all_terms)
    need(full['Z']==exp_json(Z) and full['taylor']==series_json(Z,full['taylor_cap']),'reference total rational Taylor series')
    report={'status':'PASS','method':'exact rational geometry + Cartesian states + edge-subset cycles',
            'candidate_assignments_examined':seen,'states':len(states),'ordered_disjoint_pairs':len(pairs),
            'qualifying_cyclic_state_ids':qualifying,'reversal_rows':len(reference_reversals),'reversal_orbits':reference_orbits,
            'D_group_cycle_counts':{str(k):v for k,v in sorted(counts.items())},'bounded_spoke_faces':len(hf)-1,
            'spoke_circulations':circulation,'nonincident_segment_pair_tests':segment_tests,
            'projected_coordinates':{str(v):[[p.numerator,p.denominator] for p in xy[v]] for v in sorted(xy)}}
    return report

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    fixture=json.loads(next((root/'fixtures').glob('*.json')).read_text())
    full=json.loads((root/'certificates'/f"{fixture['name']}.json").read_text())
    orbit=json.loads((root/'certificates'/'reversal_fibers.json').read_text())
    print(json.dumps(verify(fixture,full,orbit),indent=2,sort_keys=True))
