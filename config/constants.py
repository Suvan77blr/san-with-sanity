"""
Configuration constants for the Erasure Coding Simulator.

All adjustable parameters are centralized here.
Modify these values to change simulation behavior.
"""

# Simulation parameters
NUM_NODES = 10          # Total number of storage nodes
FAILURE_COUNT = 1      # Number of nodes that will fail during simulation (set to 1 to always trigger local repair for LRC)
THREAD_DELAY_MS = 10    # Delay between thread operations (milliseconds)

# Reed-Solomon parameters
RS_K = 6                # Number of data fragments
RS_R = 3                # Number of parity fragments (total 9 nodes needed)

# Local Reconstruction Code parameters
LRC_K = 6               # Number of data fragments (same as RS for fair comparison)
LRC_LOCAL_PARITY = 1    # Number of local parity fragments per group
LRC_GROUP_SIZE = 3      # Default group size for LRC (6 data → 2 groups of 3)
LRC_GLOBAL_PARITY = 2   # Number of global RS parity fragments

# LRC structure: 6 data + 2 local (3+3) + 2 global = 10 total
# RS structure: 6 data + 3 parity = 9 total

# Data parameters
BLOCK_SIZE = 1024  # Size of data blocks in bytes

# Adding a default config for the simulator.
DEFAULT_CONFIG = {
    "NUM_NODES": NUM_NODES,
    "FAILURE_COUNT": FAILURE_COUNT,
    "RS_K": RS_K,
    "RS_R": RS_R,
    "LRC_K": LRC_K,
    "LRC_LOCAL_PARITY": LRC_LOCAL_PARITY,
    "LRC_GROUP_SIZE": LRC_GROUP_SIZE,
    "LRC_GLOBAL_PARITY": LRC_GLOBAL_PARITY,
    "THREAD_DELAY_MS": THREAD_DELAY_MS
}

# SCENARIOS = [

#     # 1️⃣ Local Repair Demonstration
#     {
#         **DEFAULT_CONFIG,
#         "FAILURE_COUNT": 1,
#         "LRC_GROUP_SIZE": 3,
#     },

#     # 2️⃣ Increasing global parity (LRC more robust)
#     {
#         **DEFAULT_CONFIG,
#         "LRC_GLOBAL_PARITY": 3,
#     },

#     # 3️⃣ Larger groups (LRC loses locality)
#     {
#         **DEFAULT_CONFIG,
#         "LRC_GROUP_SIZE": 6,  # becomes RS-like
#     },

#     # 4️⃣ Small groups (LRC extremely efficient)
#     {
#         **DEFAULT_CONFIG,
#         "LRC_GROUP_SIZE": 2,
#     }
# ]


# BASE = {
#     "NUM_NODES": 10,
#     "FAILURE_COUNT": 1,
#     "RS_K": 6,
#     "RS_R": 3,
#     "LRC_K": 6,
#     "LRC_LOCAL_PARITY": 1,
#     "LRC_GROUP_SIZE": 3,
#     "LRC_GLOBAL_PARITY": 2,
#     "THREAD_DELAY_MS": 10,
# }
