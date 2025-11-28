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
        self.lrc_group_size = 3  # Default group size for LRC
        self.lrc_global_parity = 1  # Number of global RS parity fragments
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
        # Compare recovered bytes with original bytes (handle length differences)
        rs_success = False
        if rs_recovered_data:
            # Trim recovered data to original length and compare
            trimmed_rs = rs_recovered_data[:len(self.original_data.encode('utf-8'))]
            rs_success = trimmed_rs == self.original_data.encode('utf-8')

        lrc_success = False
        if lrc_recovered_data:
            # Trim recovered data to original length and compare
            trimmed_lrc = lrc_recovered_data[:len(self.original_data.encode('utf-8'))]
            lrc_success = trimmed_lrc == self.original_data.encode('utf-8')

        rs_stats = {
            'nodes_contacted': rs_nodes_contacted,
            'success': rs_success
        }
        lrc_stats = {
            'nodes_contacted': lrc_nodes_contacted,
            'success': lrc_success
        }

        self.logger.log_simulation_results(rs_stats, lrc_stats)

    def _initialize_components(self):
        """
        Initialize cluster and encoders.
        """
        self.logger.log_info("Initializing cluster and encoders...")
        self.cluster = Cluster(self.num_nodes)
        self.rs_encoder = EncoderRS(self.rs_k, self.rs_r)
        self.lrc_encoder = EncoderLRC(self.lrc_k, self.lrc_group_size, self.lrc_local_parity, self.lrc_global_parity)
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
        # Create ordered fragment list (None for failed nodes)
        available_fragments = []
        alive_count = 0
        for node in self.cluster.nodes:
            if node.is_alive:
                available_fragments.append(node.fragment)
                alive_count += 1
            else:
                available_fragments.append(None)

        nodes_contacted = alive_count
        # Filter out None values for RS decoding
        valid_fragments = [f for f in available_fragments if f is not None]
        try:
            recovered_data = self.rs_encoder.decode(valid_fragments)
            self.logger.log_success("RS reconstruction successful!")
            # Log recovered data safely
            try:
                recovered_str = recovered_data.decode('utf-8', errors='replace')[:50] + "..." if len(recovered_data) > 50 else recovered_data.decode('utf-8', errors='replace')
                self.logger.log_data_summary("Recovered data", recovered_str)
            except:
                self.logger.log_data_summary("Recovered data", f"{len(recovered_data)} bytes")
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

        # For demonstration, use global repair (simplified - in practice we'd try local repair first)
        try:
            recovered_data = self.lrc_encoder.global_repair(available_fragments)
            self.logger.log_success("LRC reconstruction successful!")
            # Log recovered data safely
            try:
                recovered_str = recovered_data.decode('utf-8', errors='replace')[:50] + "..." if len(recovered_data) > 50 else recovered_data.decode('utf-8', errors='replace')
                self.logger.log_data_summary("Recovered data", recovered_str)
            except:
                self.logger.log_data_summary("Recovered data", f"{len(recovered_data)} bytes")
            return recovered_data, nodes_contacted
        except Exception as e:
            self.logger.log_error(f"LRC reconstruction failed: {e}")
            return None, nodes_contacted
