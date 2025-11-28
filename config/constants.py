"""
Configuration constants for the Erasure Coding Simulator.

All adjustable parameters are centralized here.
Modify these values to change simulation behavior.
"""

# Simulation parameters
NUM_NODES = 10          # Total number of storage nodes (must be >= max(RS total, LRC total))
FAILURE_COUNT = 2       # Number of nodes that will fail during simulation
THREAD_DELAY_MS = 100   # Delay between thread operations (milliseconds)

# Reed-Solomon parameters
RS_K = 6  # Number of data fragments
RS_R = 4  # Number of parity fragments (total fragments = k + r = 10)

# Local Reconstruction Code parameters
LRC_K = 6               # Number of data fragments
LRC_LOCAL_PARITY = 1    # Number of local parity fragments per group

# Data parameters
BLOCK_SIZE = 1024  # Size of data blocks in bytes
