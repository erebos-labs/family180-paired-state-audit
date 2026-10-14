#!/usr/bin/env python3
"""Nonvacuous regression and negative-certificate tests. Survive python -O."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import checker as c
import independent_check as ref
import involution as inv
import fixture_builder

ROOT=Path(__file__).resolve().parent
NAME='octahedron_three_edge_expansion_12'
BASELINE_MANIFEST_HASH='2095d84e3f9be04b449c78ed06869f74e2897cdb14b519fff06f93a759984f79'

class NonvacuousTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=json.loads((ROOT/'fixtures'/f'{NAME}.json').read_text())
        cls.a=json.loads((ROOT/'certificates'/f'{NAME}.json').read_text())
        cls.b=json.loads((ROOT/'certificates'/'reversal_fibers.json').read_text())

    def test_01_builder_is_exact_declared_fixture(self):
        self.assertEqual(fixture_builder.construction(),self.f)
        self.assertEqual(len(self.f['rotation']),12)
        self.assertEqual(self.f['outer_face'],[3,5,4])

    def test_02_primary_semantic_replay(self):
        c.verify_certificate(self.f,self.a)

    def test_03_independent_geometry_and_enumeration(self):
        result=ref.verify(self.f,self.a,self.b)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['candidate_assignments_examined'],1728)
        self.assertEqual(result['states'],9)
        self.assertEqual(result['ordered_disjoint_pairs'],10)
        self.assertEqual(result['qualifying_cyclic_state_ids'],[8])

    def test_04_nonvacuous_fiber_and_complete_orbits(self):
        result=inv.verify_certificate(self.f,self.b)
        self.assertEqual(result,{'qualifying_fibers':1,'partner_rows_checked':2,'two_element_orbits':1,'status':'PASS'})
        fresh=c.audit(self.f)
        self.assertEqual(fresh['summary']['cyclic_Q_states'],1)
        self.assertEqual(fresh['summary']['cyclic_Q_states_with_partners'],1)
        self.assertEqual(fresh['summary']['reversal_checks'],2)
        self.assertEqual([(r['pair'],r['image_pair']) for r in fresh['reversals']],[(0,4),(4,0)])

    def test_05_same_operation_is_applied_twice(self):
        T=c.Triangulation(self.f);states=T.states();s=states[8]
        for r_id,target in [(0,4),(4,0)]:
            r=states[r_id];rr=c.reverse_partner(T,r,s,(0,1,2))
            self.assertEqual(rr,states[target]);self.assertNotEqual(rr,r)
            self.assertTrue(T.state_valid(rr));self.assertTrue(all(a!=b for a,b in zip(rr,s)))
            self.assertEqual(c.reverse_partner(T,rr,s,(0,1,2)),r)

    def test_06_actual_indices_phases_and_weights(self):
        T=c.Triangulation(self.f);states=T.states();s=states[8]
        self.assertEqual((T.index(states[0],s),T.index(states[4],s)),(-3,-1))
        self.assertEqual((c.phase(-3),c.phase(-1)),((0,1),(0,-1)))
        self.assertEqual([r['J_change'] for r in self.b['fibers'][0]['rows']],[2,-2])
        self.assertEqual([r['weight_before'] for r in self.b['fibers'][0]['rows']],[4,4])
        self.assertEqual(self.b['fibers'][0]['fixed_state_exponential_sum'],[])

    def test_07_geometric_three_cycle_orientation_group(self):
        a=c.audit(self.f);groups=a['groups']
        self.assertEqual(sorted(g['cycle_count'] for g in groups),[1,3])
        triple=next(g for g in groups if g['cycle_count']==3)
        self.assertEqual(len(triple['member_pairs']),8)
        self.assertEqual([x['gap'] for x in triple['cycles']],[1,1,1])
        self.assertEqual(triple['leading_coefficient'],[0,1])
        self.assertEqual(triple['taylor'][:4],[[[0,1],[0,1]],[[0,1],[0,1]],[[0,1],[0,1]],[[0,1],[1,1]]])

    def test_08_global_exact_sum(self):
        a=c.audit(self.f)
        self.assertEqual(a['Z'],[{'exponent':k,'coefficient':[0,v]} for k,v in [(0,1),(1,-1),(2,3),(3,-3)]])
        self.assertEqual(a['summary']['first_coefficient'],[0,-4])
        self.assertEqual(a['taylor'][2],[[0,1],[-8,1]])
        self.assertEqual(a['taylor'][3],[[0,1],[-29,3]])

    def test_09_assignment_cap_enforced_before_enumeration(self):
        with patch.object(c,'MAX_LOCAL_CHOICES',1727):
            with self.assertRaisesRegex(c.Rejected,'local enumeration cap'):c.Triangulation(self.f).states()
        self.assertEqual(c.MAX_LOCAL_CHOICES,200000)

    def test_10_state_cap_enforced(self):
        with patch.object(c,'MAX_STATES',8):
            with self.assertRaisesRegex(c.Rejected,'state cap'):c.Triangulation(self.f).states()
        self.assertEqual(c.MAX_STATES,10000);self.assertEqual(c.MAX_VERTICES,20)

    def test_11_missing_fiber_rejected(self):
        b=copy.deepcopy(self.b);b['fibers']=[]
        with self.assertRaisesRegex(c.Rejected,'complete cyclic fiber'):inv.verify_certificate(self.f,b)

    def test_12_missing_partner_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['partner_ids'].pop()
        with self.assertRaisesRegex(c.Rejected,'complete partner list'):inv.verify_certificate(self.f,b)

    def test_13_missing_row_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'].pop()
        with self.assertRaisesRegex(c.Rejected,'complete reversal row domain'):inv.verify_certificate(self.f,b)

    def test_14_fixed_point_image_rejected(self):
        b=copy.deepcopy(self.b);r=b['fibers'][0]['rows'][0]
        r['image_id']=r['r_id'];r['image_values']=r['r_values'][:]
        with self.assertRaisesRegex(c.Rejected,'no fixed point'):inv.verify_certificate(self.f,b)

    def test_15_nonstate_image_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['image_values'][0]=3
        with self.assertRaisesRegex(c.Rejected,'partner closure'):inv.verify_certificate(self.f,b)

    def test_16_wrong_image_id_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['image_id']=1
        with self.assertRaisesRegex(c.Rejected,'image id'):inv.verify_certificate(self.f,b)

    def test_17_index_change_corruption_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['J_change']=0
        with self.assertRaisesRegex(c.Rejected,'index change'):inv.verify_certificate(self.f,b)

    def test_18_index_value_corruption_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['J_before']+=4
        with self.assertRaisesRegex(c.Rejected,'index values'):inv.verify_certificate(self.f,b)

    def test_19_phase_corruption_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['phase_after']=[0,1]
        with self.assertRaisesRegex(c.Rejected,'recorded phases'):inv.verify_certificate(self.f,b)

    def test_20_weight_corruption_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['weight_after']+=1
        with self.assertRaisesRegex(c.Rejected,'weight unchanged'):inv.verify_certificate(self.f,b)

    def test_21_second_state_change_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['second_state_after']=self.a['states'][0]['values'][:]
        with self.assertRaisesRegex(c.Rejected,'second state unchanged'):inv.verify_certificate(self.f,b)

    def test_22_incomplete_orbits_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['orbits']=[]
        with self.assertRaisesRegex(c.Rejected,'complete two-element orbits'):inv.verify_certificate(self.f,b)

    def test_23_fixed_state_sum_corruption_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['fixed_state_exponential_sum']=[{'exponent':4,'coefficient':[0,1]}]
        with self.assertRaisesRegex(c.Rejected,'fixed-state cancellation'):inv.verify_certificate(self.f,b)

    def test_24_cycle_changed_using_partner_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['cycle']=[0,2,1]
        with self.assertRaisesRegex(c.Rejected,'cycle chosen from fixed state'):inv.verify_certificate(self.f,b)

    def test_25_disk_sign_corruption_rejected(self):
        b=copy.deepcopy(self.b);b['fibers'][0]['rows'][0]['disk']['delta_sum']=-3
        with self.assertRaisesRegex(c.Rejected,'disk record'):inv.verify_certificate(self.f,b)

    def test_26_incidence_corruption_rejected(self):
        f=copy.deepcopy(self.f);f['faces'][0]['vertices'][0]=6
        with self.assertRaises(c.Rejected):c.audit(f)
        with self.assertRaises(ref.ReferenceRejected):ref.verify(f,self.a,self.b)

    def test_27_rotation_corruption_rejected(self):
        f=copy.deepcopy(self.f);f['rotation']['0'][0],f['rotation']['0'][1]=f['rotation']['0'][1],f['rotation']['0'][0]
        with self.assertRaises(c.Rejected):c.audit(f)
        with self.assertRaises(ref.ReferenceRejected):ref.verify(f,self.a,self.b)

    def test_28_primary_sign_record_corruption_rejected(self):
        a=copy.deepcopy(self.a);a['delta'][0]['sign']*=-1
        with self.assertRaises(c.Rejected):c.verify_certificate(self.f,a)

    def test_29_spoke_weight_corruption_rejected(self):
        a=copy.deepcopy(self.a)
        next(w for w in a['spokes']['weights'] if (w['face'],w['vertex'])==(16,8))['weight']+=1
        with self.assertRaisesRegex(c.Rejected,'circulation'):c.verify_certificate(self.f,a)
        with self.assertRaisesRegex(ref.ReferenceRejected,'circulations'):ref.verify(self.f,a,self.b)

    def test_30_three_cycle_fiber_member_omission_rejected(self):
        a=copy.deepcopy(self.a);next(g for g in a['groups'] if g['cycle_count']==3)['member_pairs'].pop()
        with self.assertRaises(c.Rejected):c.verify_certificate(self.f,a)
        with self.assertRaisesRegex(ref.ReferenceRejected,'fiber membership'):ref.verify(self.f,a,self.b)

    def test_31_independent_detects_missing_primary_reversal_records(self):
        a=copy.deepcopy(self.a);a['reversals']=[]
        with self.assertRaisesRegex(ref.ReferenceRejected,'reversal records'):ref.verify(self.f,a,self.b)

    def test_32_public_baseline_bytes_unchanged(self):
        baseline=ROOT/'baseline'/'v1.0.0'
        self.assertEqual(hashlib.sha256((baseline/'SHA256SUMS').read_bytes()).hexdigest(),BASELINE_MANIFEST_HASH)
        for line in (baseline/'SHA256SUMS').read_text().splitlines():
            expected,name=line.split('  ',1)
            self.assertEqual(hashlib.sha256((baseline/name).read_bytes()).hexdigest(),expected)

if __name__=='__main__':unittest.main(verbosity=2)
