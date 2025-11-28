"""
Main simulator class that orchestrates the entire erasure coding simulation.

Coordinates encoding, node failures, and reconstruction for both RS and LRC.
"""

import time
from config.constants import *
from .cluster import Cluster
from .encoder_rs import EncoderRS
from .encoder_lrc import EncoderLRC

class Simulator:
    """
    Orchestrates the complete erasure coding simulation.
    """

    def __init__(self):
        """
        Initialize the simulator with constants.
        """
        self.num_nodes = NUM_NODES
        self.failure_count = FAILURE_COUNT
        self.rs_k = RS_K
        self.rs_r = RS_R
        self.lrc_k = LRC_K
        self.lrc_local_parity = LRC_LOCAL_PARITY
        self.thread_delay = THREAD_DELAY_MS / 1000.0  # Convert to seconds

        self.cluster = None
        self.rs_encoder = None
        self.lrc_encoder = None
        self.original_data = None

    def run_simulation(self, test_data="Hello, World! This is a test message for erasure coding simulation."):
        """
        Run the complete simulation workflow.
        """
        print("=== Erasure Coding Simulator: RS vs LRC ===\n")

        self.original_data = test_data
        print(f"Original Data: {self.original_data}\n")

        # Initialize components
        self._initialize_components()

        # RS Simulation
        print("--- Reed-Solomon (RS) Simulation ---")
        rs_fragments = self._encode_data_rs()
        rs_failed_nodes = self._simulate_failures_rs()
        rs_recovered_data, rs_nodes_contacted = self._reconstruct_rs(rs_fragments)

        # Reset cluster for LRC
        self.cluster.reset_all_nodes()

        # LRC Simulation
        print("\n--- Local Reconstruction Code (LRC) Simulation ---")
        lrc_fragments = self._encode_data_lrc()
        lrc_failed_nodes = self._simulate_failures_lrc()
        lrc_recovered_data, lrc_nodes_contacted = self._reconstruct_lrc(lrc_fragments)

        # Results comparison
        self._print_comparison(rs_failed_nodes, rs_nodes_contacted,
                             lrc_failed_nodes, lrc_nodes_contacted,
                             rs_recovered_data, lrc_recovered_data)

    def _initialize_components(self):
        """
        Initialize cluster and encoders.
        """
        print("Initializing cluster and encoders...")
        self.cluster = Cluster(self.num_nodes)
        self.rs_encoder = EncoderRS(self.rs_k, self.rs_r)
        self.lrc_encoder = EncoderLRC(self.lrc_k, self.lrc_local_parity)
        time.sleep(self.thread_delay)

    def _encode_data_rs(self):
        """
        Encode data using Reed-Solomon.
        """
        print(f"Encoding data into {self.rs_k} data + {self.rs_r} parity fragments...")
        fragments = self.rs_encoder.encode(self.original_data)
        self.cluster.distribute_fragments(fragments)
        print(f"RS Fragments created: {len(fragments)} total")
        time.sleep(self.thread_delay)
        return fragments

    def _encode_data_lrc(self):
        """
        Encode data using Local Reconstruction Codes.
        """
        print(f"Encoding data into {self.lrc_k} data + local/global parity fragments...")
        fragments = self.lrc_encoder.encode(self.original_data)
        self.cluster.distribute_fragments(fragments)
        print(f"LRC Fragments created: {len(fragments)} total")
        time.sleep(self.thread_delay)
        return fragments

    def _simulate_failures_rs(self):
        """
        Simulate node failures for RS.
        """
        print(f"Simulating {self.failure_count} node failures...")
        failed_nodes = self.cluster.fail_nodes(self.failure_count)
        print(f"Failed nodes: {failed_nodes}")
        time.sleep(self.thread_delay)
        return failed_nodes

    def _simulate_failures_lrc(self):
        """
        Simulate node failures for LRC.
        """
        print(f"Simulating {self.failure_count} node failures...")
        failed_nodes = self.cluster.fail_nodes(self.failure_count)
        print(f"Failed nodes: {failed_nodes}")
        time.sleep(self.thread_delay)
        return failed_nodes

    def _reconstruct_rs(self, original_fragments):
        """
        Attempt reconstruction using RS codes.
        """
        print("Attempting RS reconstruction...")
        alive_nodes = self.cluster.get_alive_nodes()
        available_fragments = [node.fragment for node in alive_nodes]

        nodes_contacted = len(alive_nodes)
        try:
            recovered_data = self.rs_encoder.decode(available_fragments)
            print("RS reconstruction successful!")
            return recovered_data, nodes_contacted
        except Exception as e:
            print(f"RS reconstruction failed: {e}")
            return None, nodes_contacted

    def _reconstruct_lrc(self, original_fragments):
        """
        Attempt reconstruction using LRC codes.
        """
        print("Attempting LRC reconstruction (local repair first)...")
        alive_nodes = self.cluster.get_alive_nodes()

        # Try local repair first (simplified - just count nodes contacted)
        # In a real implementation, we'd check which nodes failed and try local repair
        available_fragments = []
        for node in self.cluster.nodes:
            if node.is_alive:
                available_fragments.append(node.fragment)
            else:
                available_fragments.append(None)

        nodes_contacted = len(alive_nodes)

        # For demonstration, assume local repair when possible
        # This is simplified - in practice we'd check group membership
        try:
            recovered_data = self.lrc_encoder.global_decode([f for f in available_fragments if f is not None])
            print("LRC reconstruction successful!")
            return recovered_data, nodes_contacted
        except Exception as e:
            print(f"LRC reconstruction failed: {e}")
            return None, nodes_contacted

    def _print_comparison(self, rs_failed, rs_contacted, lrc_failed, lrc_contacted,
                         rs_recovered, lrc_recovered):
        """
        Print simulation results and comparison.
        """
        print("\n=== SIMULATION RESULTS ===")
        print(f"Original data: {self.original_data}")
        print(f"Failed nodes: RS={rs_failed}, LRC={lrc_failed}")
        print(f"Nodes contacted - RS: {rs_contacted}, LRC: {lrc_contacted}")
        print(f"RS recovered: {'SUCCESS' if rs_recovered == self.original_data else 'FAILED'}")
        print(f"LRC recovered: {'SUCCESS' if lrc_recovered == self.original_data else 'FAILED'}")

        if rs_contacted > lrc_contacted:
            savings = rs_contacted - lrc_contacted
            print(f"\nLRC advantage: Contacted {savings} fewer nodes than RS!")
        else:
            print(f"\nRS and LRC contacted the same number of nodes in this simulation.")

    def run_simulation(self):
        """
        Run the complete simulation workflow.
        """
        pass

    def _load_constants(self):
        """
        Load configuration constants.
        """
        pass

    def _initialize_cluster(self):
        """
        Create and initialize the node cluster.
        """
        pass

    def _encode_data_rs(self, data):
        """
        Encode data using Reed-Solomon.
        """
        pass

    def _encode_data_lrc(self, data):
        """
        Encode data using Local Reconstruction Codes.
        """
        pass

    def _simulate_failures(self):
        """
        Simulate node failures in the cluster.
        """
        pass

    def _reconstruct_rs(self):
        """
        Attempt reconstruction using RS codes.
        """
        pass

    def _reconstruct_lrc(self):
        """
        Attempt reconstruction using LRC codes.
        """
        pass

    def _print_results(self):
        """
        Print simulation results and comparison.
        """
        pass
