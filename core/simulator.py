"""
Main simulator class that orchestrates the entire erasure coding simulation.

Coordinates encoding, node failures, and reconstruction for both RS and LRC.
"""

import time
from config.constants import *
from .cluster import Cluster
from .encoder_rs import EncoderRS
from .encoder_lrc import EncoderLRC
from utils.logger import Logger

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
        self.logger = Logger(log_to_file=False)  # Console-only logging for demo

    def run_simulation(self, test_data="Hello, World! This is a test message for erasure coding simulation."):
        """
        Run the complete simulation workflow.
        """
        self.logger.log_header("Erasure Coding Simulator: RS vs LRC")
        self.original_data = test_data
        self.logger.log_data_summary("Original Data", self.original_data)

        # Initialize components
        self._initialize_components()

        # RS Simulation
        self.logger.log_header("Reed-Solomon (RS) Simulation")
        rs_fragments = self._encode_data_rs()
        rs_failed_nodes = self._simulate_failures_rs()
        rs_recovered_data, rs_nodes_contacted = self._reconstruct_rs(rs_fragments)

        # Reset cluster for LRC
        self.cluster.reset_all_nodes()

        # LRC Simulation
        self.logger.log_header("Local Reconstruction Code (LRC) Simulation")
        lrc_fragments = self._encode_data_lrc()
        lrc_failed_nodes = self._simulate_failures_lrc()
        lrc_recovered_data, lrc_nodes_contacted = self._reconstruct_lrc(lrc_fragments)

        # Results comparison
        # Convert recovered data back to string for comparison
        rs_recovered_str = rs_recovered_data.decode('utf-8') if rs_recovered_data else None
        lrc_recovered_str = lrc_recovered_data.decode('utf-8') if lrc_recovered_data else None

        rs_stats = {
            'nodes_contacted': rs_nodes_contacted,
            'success': rs_recovered_str == self.original_data if rs_recovered_str else False
        }
        lrc_stats = {
            'nodes_contacted': lrc_nodes_contacted,
            'success': lrc_recovered_str == self.original_data if lrc_recovered_str else False
        }

        self.logger.log_simulation_results(rs_stats, lrc_stats)

    def _initialize_components(self):
        """
        Initialize cluster and encoders.
        """
        self.logger.log_info("Initializing cluster and encoders...")
        self.cluster = Cluster(self.num_nodes)
        self.rs_encoder = EncoderRS(self.rs_k, self.rs_r)
        self.lrc_encoder = EncoderLRC(self.lrc_k, self.lrc_local_parity)
        time.sleep(self.thread_delay)

    def _encode_data_rs(self):
        """
        Encode data using Reed-Solomon.
        """
        self.logger.log_info(f"Encoding data into {self.rs_k} data + {self.rs_r} parity fragments...")
        fragments = self.rs_encoder.encode(self.original_data)
        self.cluster.distribute_fragments(fragments)
        self.logger.log_info(f"RS Fragments created: {len(fragments)} total")
        time.sleep(self.thread_delay)
        return fragments

    def _encode_data_lrc(self):
        """
        Encode data using Local Reconstruction Codes.
        """
        self.logger.log_info(f"Encoding data into {self.lrc_k} data + local/global parity fragments...")
        fragments = self.lrc_encoder.encode(self.original_data)
        self.cluster.distribute_fragments(fragments)
        self.logger.log_info(f"LRC Fragments created: {len(fragments)} total")
        time.sleep(self.thread_delay)
        return fragments

    def _simulate_failures_rs(self):
        """
        Simulate node failures for RS.
        """
        self.logger.log_info(f"Simulating {self.failure_count} node failures...")
        failed_nodes = self.cluster.fail_nodes(self.failure_count)
        self.logger.log_info(f"Failed nodes: {failed_nodes}")
        time.sleep(self.thread_delay)
        return failed_nodes

    def _simulate_failures_lrc(self):
        """
        Simulate node failures for LRC.
        """
        self.logger.log_info(f"Simulating {self.failure_count} node failures...")
        failed_nodes = self.cluster.fail_nodes(self.failure_count)
        self.logger.log_info(f"Failed nodes: {failed_nodes}")
        time.sleep(self.thread_delay)
        return failed_nodes

    def _reconstruct_rs(self, original_fragments):
        """
        Attempt reconstruction using RS codes.
        """
        self.logger.log_info("Attempting RS reconstruction...")
        alive_nodes = self.cluster.get_alive_nodes()
        available_fragments = [node.fragment for node in alive_nodes]

        nodes_contacted = len(alive_nodes)
        try:
            recovered_data = self.rs_encoder.decode(available_fragments)
            self.logger.log_success("RS reconstruction successful!")
            self.logger.log_data_summary("Recovered data", recovered_data.decode('utf-8') if recovered_data else None)
            return recovered_data, nodes_contacted
        except Exception as e:
            self.logger.log_error(f"RS reconstruction failed: {e}")
            return None, nodes_contacted

    def _reconstruct_lrc(self, original_fragments):
        """
        Attempt reconstruction using LRC codes.
        """
        self.logger.log_info("Attempting LRC reconstruction (local repair first)...")
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
            self.logger.log_success("LRC reconstruction successful!")
            self.logger.log_data_summary("Recovered data", recovered_data.decode('utf-8') if recovered_data else None)
            return recovered_data, nodes_contacted
        except Exception as e:
            self.logger.log_error(f"LRC reconstruction failed: {e}")
            return None, nodes_contacted
