SCENARIOS = [
    # Scenario 1 – Good locality, 1 failure
    {
        "FAILURE_COUNT": 1,
        "LRC_GROUP_SIZE": 3,
        "LRC_GROUP_PARITY": 2
    },

    # Scenario 2 – Larger global parity => (LRC has stronger cross-group protection)
    {
        "FAILURE_COUNT": 1,
        "LRC_GLOBAL_PARITY": 3,    # More global parity improves multi-failure tolerance
        "LRC_GROUP_SIZE": 3,       # Keep locality same
        "NUM_NODES": 11
    },

    # Scenario 3 – Stress test: bigger groups (reduced locality)
    {
        "FAILURE_COUNT": 1,
        "LRC_GROUP_SIZE": 6,       # 1 group of 6 → worst locality
        "LRC_GLOBAL_PARITY": 2,    # Keep global parity default
    },

    # Scenario 4 – 2 failures (tests global parity’s benefit)
    {
        "FAILURE_COUNT": 2,
        "LRC_GROUP_SIZE": 3,       # Good locality
        "LRC_GLOBAL_PARITY": 2,    # Default global parity helps recovering 2 failures
    }
]
