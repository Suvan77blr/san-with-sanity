"""
Configuration constants for the Erasure Coding Simulator.

All adjustable parameters are centralized here.
Modify these values to change simulation behavior.
"""

# Simulation parameters
NUM_NODES = 12          # Total number of storage nodes (increased for more fragments)
FAILURE_COUNT = 3       # Number of nodes that will fail during simulation (increased tolerance)
THREAD_DELAY_MS = 100   # Delay between thread operations (milliseconds)

# Reed-Solomon parameters
RS_K = 8  # Number of data fragments (increased)
RS_R = 4  # Number of parity fragments (increased for more fault tolerance)

# Local Reconstruction Code parameters
LRC_K = 4               # Number of data fragments
LRC_LOCAL_PARITY = 1    # Number of local parity fragments per group
LRC_GROUP_SIZE = 4      # Default group size for LRC
LRC_GLOBAL_PARITY = 2   # Number of global RS parity fragments (increased for 2 failure tolerance)

# Data parameters
BLOCK_SIZE = 1024  # Size of data blocks in bytes
