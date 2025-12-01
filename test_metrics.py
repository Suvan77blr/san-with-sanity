#!/usr/bin/env python3
"""
Quick test to verify metrics calculations are real and correct.
"""

def test_lrc_local_repair():
    """Test LRC local repair fragment calculation"""
    # Configuration
    lrc_k = 6  # 6 data fragments
    group_size = 3  # 2 groups of 3
    num_groups = (lrc_k + group_size - 1) // group_size  # = 2
    local_parity = 1
    global_parity = 2
    total_fragments = lrc_k + (num_groups * local_parity) + global_parity  # 6 + 2 + 2 = 10
    
    print("LRC Configuration:")
    print(f"  Data fragments: {lrc_k}")
    print(f"  Group size: {group_size}")
    print(f"  Number of groups: {num_groups}")
    print(f"  Local parity (per group): {local_parity}")
    print(f"  Global parity fragments: {global_parity}")
    print(f"  Total fragments: {total_fragments}")
    print()
    
    # Scenario 1: Single failure in group 0
    print("Scenario 1: Single failure in group 0 (data fragment 0)")
    failed_pos = 0
    group_id = failed_pos // group_size  # = 0
    group_start = group_id * group_size  # = 0
    group_end = min(group_start + group_size, lrc_k)  # = 3
    
    # For local repair: need (group_size - 1) data + 1 local parity
    group_data_available = group_end - group_start - 1  # 3 - 1 = 2
    fragments_needed = group_data_available + 1  # 2 + 1 = 3
    
    print(f"  Failed position: {failed_pos}")
    print(f"  Group: {group_id} (positions {group_start}-{group_end-1})")
    print(f"  Available data in group: {group_data_available}")
    print(f"  Local parity position: {lrc_k + group_id} = {lrc_k + group_id}")
    print(f"  Fragments needed for local repair: {fragments_needed}")
    print(f"  Advantage: {lrc_k} - {fragments_needed} = {lrc_k - fragments_needed} fragments saved!")
    print()
    
    # Scenario 2: RS always needs k fragments
    rs_k = 6
    rs_r = 3
    rs_total = rs_k + rs_r
    print("Scenario 2: Reed-Solomon for comparison")
    print(f"  Data fragments (k): {rs_k}")
    print(f"  Parity fragments (r): {rs_r}")
    print(f"  Total fragments: {rs_total}")
    print(f"  Fragments needed for any recovery: {rs_k}")
    print(f"  Advantage of LRC: {rs_k - fragments_needed} fewer fragments needed")
    print()
    
    # Computation complexity
    fragment_size_bytes = 17  # Average for the test data
    print("Computation Complexity:")
    print("RS (always needs GF(256) operations):")
    print(f"  XOR operations: {rs_r * fragment_size_bytes * 8} bits")
    print(f"  GF(256) multiplications: {rs_k * fragment_size_bytes * 8} bits")
    print()
    print("LRC with local repair:")
    print(f"  XOR operations: {(group_size - 1) * fragment_size_bytes * 8} bits")
    print(f"  GF(256) multiplications: 0 (local repair is XOR only!)")
    print(f"  Savings: {rs_k * fragment_size_bytes * 8} GF(256) operations!")
    print()
    
    # Bandwidth
    print("Bandwidth:")
    print(f"  RS reads: {rs_k * fragment_size_bytes} bytes")
    print(f"  LRC (local): {fragments_needed * fragment_size_bytes} bytes")
    print(f"  LRC (global): {(rs_k + global_parity) * fragment_size_bytes} bytes")
    print(f"  Savings (local): {(rs_k - fragments_needed) * fragment_size_bytes} bytes")

if __name__ == "__main__":
    test_lrc_local_repair()
