> Authoring record from the verified input. Publication and independent review
> status are updated in PUBLIC_REVIEW.md; original private ZIPs are not distributed.

# Implementation fault-injection coverage

These twelve mutants were defined and run locally. The three Atlas mutant definitions were not supplied; none is claimed reproduced.

The control passed all 32 tests. Each mutant was applied to isolated temporary source copies, compiled syntactically, and run against the unchanged semantic suite. Hash mismatch alone was not a detection criterion. A nonzero exit without identified failing tests is an infrastructure error, not a kill.

| Mutant | Result | Detecting tests |
|---|---|---|
| `M01_identity_reversal` | KILLED_BY_SEMANTIC_TESTS | `test_02_primary_semantic_replay`, `test_04_nonvacuous_fiber_and_complete_orbits`, `test_05_same_operation_is_applied_twice`, `test_07_geometric_three_cycle_orientation_group`, `test_08_global_exact_sum` |
| `M02_skip_all_cyclic_fibers` | KILLED_BY_SEMANTIC_TESTS | `test_02_primary_semantic_replay`, `test_04_nonvacuous_fiber_and_complete_orbits` |
| `M03_corrupt_index_difference` | KILLED_BY_SEMANTIC_TESTS | `test_02_primary_semantic_replay`, `test_04_nonvacuous_fiber_and_complete_orbits`, `test_07_geometric_three_cycle_orientation_group`, `test_08_global_exact_sum` |
| `M04_disable_entire_fiber_validator` | KILLED_BY_SEMANTIC_TESTS | `test_11_missing_fiber_rejected`, `test_12_missing_partner_rejected`, `test_13_missing_row_rejected`, `test_14_fixed_point_image_rejected`, `test_15_nonstate_image_rejected`, `test_16_wrong_image_id_rejected`, `test_17_index_change_corruption_rejected`, `test_18_index_value_corruption_rejected`, `test_19_phase_corruption_rejected`, `test_20_weight_corruption_rejected`, `test_21_second_state_change_rejected`, `test_22_incomplete_orbits_rejected`, `test_23_fixed_state_sum_corruption_rejected`, `test_24_cycle_changed_using_partner_rejected`, `test_25_disk_sign_corruption_rejected` |
| `M05_disable_phase_record_validation` | KILLED_BY_SEMANTIC_TESTS | `test_19_phase_corruption_rejected` |
| `M06_disable_weight_record_validation` | KILLED_BY_SEMANTIC_TESTS | `test_20_weight_corruption_rejected` |
| `M07_disable_index_change_validation` | KILLED_BY_SEMANTIC_TESTS | `test_17_index_change_corruption_rejected` |
| `M08_disable_orbit_record_validation` | KILLED_BY_SEMANTIC_TESTS | `test_22_incomplete_orbits_rejected` |
| `M09_disable_fixed_second_state_validation` | KILLED_BY_SEMANTIC_TESTS | `test_21_second_state_change_rejected` |
| `M10_ignore_claimed_cancellation_sum` | KILLED_BY_SEMANTIC_TESTS | `test_23_fixed_state_sum_corruption_rejected` |
| `M11_truncate_cycle_decomposition` | KILLED_BY_SEMANTIC_TESTS | `test_02_primary_semantic_replay`, `test_04_nonvacuous_fiber_and_complete_orbits`, `test_07_geometric_three_cycle_orientation_group`, `test_08_global_exact_sum` |
| `M12_omit_reverse_orientations` | KILLED_BY_SEMANTIC_TESTS | `test_02_primary_semantic_replay`, `test_04_nonvacuous_fiber_and_complete_orbits`, `test_07_geometric_three_cycle_orientation_group`, `test_08_global_exact_sum` |

## Particularly important negative controls

M04 replaces the complete fiber validator with a fabricated PASS result containing the correct coverage counts. Positive data can no longer reveal that bypass, but fifteen malformed-certificate tests fail because it accepts them. This is the principal guard against an apparently successful but disabled validator.

M05, M06, M07, M08, M09 and M10 each remove a specific recorded phase, weight, index-change, orbit, fixed-second-state or sum check. The corresponding negative record is then accepted and its rejection test fails. M01, M02 and M03 break the actual reversal operation/coverage/index computation. M11 and M12 break the now nonvacuous multi-cycle and orientation handling.

All twelve are detected. This is bounded mutation coverage, not a proof that every bug or every logically redundant check deletion is detectable. In particular no claim is made about unidentified Atlas code.

Exact replacements and expected source-match counts are in mutations/definitions.json, individual unified patches in mutations/, actual unittest output in logs/mutations/, and machine-readable outcomes with hashes in mutation_results.json.

For a fresh replay without overwriting delivered evidence:

```sh
python3 run_mutations.py --output replay_output/mutations
```
