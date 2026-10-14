#!/usr/bin/env python3
"""Explicit partner-fiber certificates and a rejection-oriented validator.

The primary audit is inherited and extended in checker.py. This module adds a
public certificate validation boundary for targeted negative and fault tests.
It never accepts a PASS flag as evidence. Standard library and checker only.
"""
from collections import defaultdict
from itertools import product
import checker as c


def make_certificate(fixture: dict, full: dict) -> dict:
    """Package primary records. Validation below reconstructs their content."""
    states={s['id']:s for s in full['states']}
    pairs={p['id']:p for p in full['pairs']}
    fibers=[]
    for s in full['states']:
        if s['chosen_cycle'] is None or not s['partner_count']:continue
        rows=[]; partner_ids=[]
        for rv in full['reversals']:
            p=pairs[rv['pair']]
            if p['s']!=s['id']:continue
            q=pairs[rv['image_pair']]
            partner_ids.append(p['r'])
            rows.append({'r_id':p['r'],'r_values':states[p['r']]['values'],
                         'image_id':q['r'],'image_values':states[q['r']]['values'],
                         'second_state_before':s['values'],'second_state_after':s['values'],
                         'J_before':p['J'],'J_after':q['J'],'J_change':rv['J_change'],
                         'phase_before':p['phase'],'phase_after':q['phase'],
                         'weight_before':p['omega_s'],'weight_after':q['omega_s'],
                         'oriented_cycle':rv['disk']['vertices'],'disk':rv['disk']})
        orbit=sorted({tuple(sorted((r['r_id'],r['image_id']))) for r in rows})
        fibers.append({'s_id':s['id'],'s_values':s['values'],
                       'cycle':s['chosen_cycle'],'partner_ids':sorted(partner_ids),
                       'orbits':[list(p) for p in orbit],'rows':rows,
                       'fixed_state_exponential_sum':[]})
    return {'schema':'family180-reversal-fibers-v1','fixture':fixture['name'],
            'upstream_pin':c.PIN,'fibers':fibers}


def verify_certificate(fixture: dict, certificate: dict) -> dict:
    """Re-enumerate all states/partners and check every complete reversal orbit.

    Separate checks for recorded index, phase, weight, support, etc. permit
    precise data mutations. A metadata mismatch is not repaired or ignored.
    This function intentionally does not call make_certificate or c.audit.
    """
    c.require(certificate.get('schema')=='family180-reversal-fibers-v1','fiber schema')
    c.require(certificate.get('fixture')==fixture['name'] and certificate.get('upstream_pin')==c.PIN,'fiber provenance')
    T=c.Triangulation(fixture)
    states=T.states(); ids={s:i for i,s in enumerate(states)}
    partners={s:[r for r in states if all(a!=b for a,b in zip(r,s))] for s in states}
    cycles={s:c.find_cycle(T.q_edges(s)) for s in states}
    qualifying=[s for s in states if cycles[s] is not None and partners[s]]
    c.require(bool(qualifying),'nonvacuous partnered cyclic fiber required')
    fibers=certificate['fibers']
    c.require([f['s_id'] for f in fibers]==[ids[s] for s in qualifying],'complete cyclic fiber list')
    H,outer,centers=c.spoke_embedding(T)
    weights,_=c.make_weights(H,outer,centers)
    c.check_weights(H,outer,centers,weights)
    checks=0;orbit_count=0
    for s,f in zip(qualifying,fibers):
        cycle=cycles[s]
        c.require(f['s_values']==list(s),'fixed state values')
        c.require(f['cycle']==list(cycle),'cycle chosen from fixed state')
        expected_partner_ids=[ids[r] for r in partners[s]]
        c.require(f['partner_ids']==expected_partner_ids,'complete partner list')
        rows=f['rows']
        c.require([row['r_id'] for row in rows]==expected_partner_ids,'complete reversal row domain')
        mapping={}
        for r,row in zip(partners[s],rows):
            c.require(row['r_values']==list(r),'row source values')
            rr=tuple(row['image_values'])
            c.require(T.state_valid(rr) and rr in partners[s],'image incident-bijection partner closure')
            c.require(row['image_id']==ids[rr],'image id and values agree')
            c.require(rr!=r,'no fixed point')
            # Independently evaluate the definition at every bounded black face.
            boundary={c.edge(*d) for d in c.darts(cycle)}
            expected=[];outgoing={};local=[]
            for j,t in enumerate(T.A):
                opposite=set(T.faces[t])-{s[j]}
                if tuple(sorted(opposite)) in boundary:
                    third=next(iter(set(T.faces[t])-{r[j],s[j]}))
                    expected.append(third);outgoing[r[j]]=third
                    local.append(T.delta[third,s[j]]-T.delta[r[j],s[j]]==2*T.delta[r[j],third])
                else:expected.append(r[j])
            c.require(rr==tuple(expected),'exact first-state reversal support and values')
            c.require(all(local),'local triangle sign identity')
            oriented=cycle if outgoing[cycle[0]]==cycle[1] else c.canonical(reversed(cycle))
            c.require(all(outgoing[a]==b for a,b in c.darts(oriented)),'directed opposite-edge cycle')
            disk=T.disk_check(oriented,r)
            c.require(row['oriented_cycle']==list(oriented) and row['disk']==disk,'oriented cycle and disk record')
            before=T.index(r,s);after=T.index(rr,s)
            c.require(row['J_before']==before and row['J_after']==after,'index values recomputed')
            c.require(after-before in (-2,2) and row['J_change']==after-before,'index change plus or minus two')
            c.require(row['phase_before']==list(c.phase(before)) and row['phase_after']==list(c.phase(after)),'recorded phases recomputed')
            c.require(c.phase(after)==c.scale(c.phase(before),-1),'actual phase negation')
            c.require(row['second_state_before']==list(s) and row['second_state_after']==list(s),'second state unchanged')
            weight=sum(weights[t,v] for t,v in zip(T.A,s))
            c.require(row['weight_before']==weight and row['weight_after']==weight,'fixed-state weight unchanged')
            mapping[ids[r]]=ids[rr];checks+=1
        c.require(set(mapping)==set(expected_partner_ids) and set(mapping.values())==set(expected_partner_ids),'fiber bijectivity')
        c.require(all(mapping[mapping[r]]==r for r in mapping),'fiber involutivity')
        orbits=sorted({tuple(sorted((r,image))) for r,image in mapping.items()})
        c.require(f['orbits']==[list(o) for o in orbits] and all(len(set(o))==2 for o in orbits),'complete two-element orbits')
        c.require(len(orbits)*2==len(expected_partner_ids),'orbit partition coverage')
        total=c.exponential_sum([(c.phase(T.index(r,s)),sum(weights[t,v] for t,v in zip(T.A,s))) for r in partners[s]])
        c.require(total=={} and f['fixed_state_exponential_sum']==c.serialize_exp(total),'exact fixed-state cancellation')
        orbit_count+=len(orbits)
    return {'qualifying_fibers':len(qualifying),'partner_rows_checked':checks,'two_element_orbits':orbit_count,'status':'PASS'}
