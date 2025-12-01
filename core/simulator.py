"""
Main simulator class that orchestrates the entire erasure coding simulation.

Coordinates encoding, node failures, and reconstruction for both RS and LRC.
"""

import time
from config.constants import *
from .cluster import Cluster
from .encoder_rs import EncoderRS
from .encoder_lrc import EncoderLRC
from .metrics import MetricsCollector
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
        self.lrc_group_size = LRC_GROUP_SIZE
        self.lrc_global_parity = LRC_GLOBAL_PARITY
        self.thread_delay = THREAD_DELAY_MS / 1000.0  # Convert to seconds

        self.cluster = None
        self.rs_encoder = None
        self.lrc_encoder = None
        self.original_data = None
        self.logger = Logger(log_to_file=False)  # Console-only logging for demo
        self.metrics_collector = MetricsCollector()

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
        rs_start_time = time.time()
        rs_fragments = self._encode_data_rs()
        rs_encoding_time = (time.time() - rs_start_time) * 1000  # Convert to ms
        
        rs_failed_nodes = self._simulate_failures_rs()
        
        rs_recovery_start = time.time()
        rs_result = self._reconstruct_rs(rs_fragments)
        rs_recovery_time = (time.time() - rs_recovery_start) * 1000  # Convert to ms
        rs_recovered_data, rs_nodes_contacted, rs_fragments_accessed = rs_result

        # Reset cluster for LRC
        self.cluster.reset_all_nodes()

        # LRC Simulation
        self.logger.log_header("Local Reconstruction Code (LRC) Simulation")
        lrc_start_time = time.time()
        lrc_fragments = self._encode_data_lrc()
        lrc_encoding_time = (time.time() - lrc_start_time) * 1000  # Convert to ms
        
        lrc_failed_nodes = self._simulate_failures_lrc()
        
        lrc_recovery_start = time.time()
        lrc_result = self._reconstruct_lrc(lrc_fragments)
        lrc_recovery_time = (time.time() - lrc_recovery_start) * 1000  # Convert to ms
        lrc_recovered_data, lrc_nodes_contacted, lrc_fragments_accessed, lrc_local_repair_used = lrc_result

        # Results comparison
        # Compare recovered bytes with original bytes (handle length differences)
        rs_success = False
        if rs_recovered_data:
            # Trim recovered data to original length and compare
            original_bytes = self.original_data.encode('utf-8')
            trimmed_rs = rs_recovered_data[:len(original_bytes)]
            rs_success = trimmed_rs == original_bytes

        lrc_success = False
        if lrc_recovered_data:
            # Trim recovered data to original length and compare, ignoring trailing zero padding
            original_bytes = self.original_data.encode('utf-8')
            trimmed_lrc = lrc_recovered_data[:len(original_bytes)]
            # Remove trailing zeros from both for fair comparison
            def strip_trailing_zeros(data):
                return data.rstrip(b'\x00')
            lrc_success = strip_trailing_zeros(trimmed_lrc) == strip_trailing_zeros(original_bytes)

        rs_stats = {
            'nodes_contacted': rs_nodes_contacted,
            'success': rs_success
        }
        lrc_stats = {
            'nodes_contacted': lrc_nodes_contacted,
            'success': lrc_success
        }

        self.logger.log_simulation_results(rs_stats, lrc_stats)
        
        # Collect and display metrics
        self._collect_and_display_metrics(
            rs_recovered_data, lrc_recovered_data,
            rs_nodes_contacted, lrc_nodes_contacted,
            rs_fragments_accessed, lrc_fragments_accessed,
            rs_encoding_time, rs_recovery_time,
            lrc_encoding_time, lrc_recovery_time,
            rs_success, lrc_success,
            lrc_local_repair_used
        )

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
        Simulate node failures for LRC, guaranteeing at least one single data failure (for local repair).
        """
        import random
        self.logger.log_info(f"Simulating {self.failure_count} node failures (guaranteed single data failure)...")
        # Always fail one data node (position 0 to k-1)
        data_failure = random.randint(0, self.lrc_k - 1)
        # Remaining failures: choose from all other nodes except the chosen data node
        all_nodes = list(range(len(self.cluster.nodes)))
        remaining_candidates = [i for i in all_nodes if i != data_failure]
        remaining_failures = random.sample(remaining_candidates, self.failure_count - 1)
        failed_nodes = [data_failure] + remaining_failures
        self.cluster.fail_nodes_by_indices(failed_nodes)
        self.logger.log_info(f"Failed nodes: {failed_nodes} (data failure at {data_failure})")
        time.sleep(self.thread_delay)
        return failed_nodes

    def _reconstruct_rs(self, original_fragments):
        """
        Attempt reconstruction using RS codes.
        """
        self.logger.log_info("Attempting RS reconstruction...")
        # Create ordered fragment list (None for failed nodes)
        available_fragments = []
        accessed_fragments = []  # Track which fragments are actually used
        alive_count = 0
        for i, node in enumerate(self.cluster.nodes):
            if node.is_alive:
                available_fragments.append(node.fragment)
                accessed_fragments.append(i)
                alive_count += 1
            else:
                available_fragments.append(None)

        nodes_contacted = alive_count
        # RS always needs exactly k fragments for decoding (first k data fragments)
        fragments_accessed = self.rs_k
        
        # Pass the full ordered list with None values for missing fragments
        try:
            recovered_data = self.rs_encoder.decode(available_fragments)
            self.logger.log_success("RS reconstruction successful!")
            # Log recovered data safely
            try:
                recovered_str = recovered_data.decode('utf-8', errors='replace')
                self.logger.log_info(f"Recovered data: {recovered_str}")
            except:
                self.logger.log_data_summary("Recovered data", f"{len(recovered_data)} bytes")
            return recovered_data, nodes_contacted, fragments_accessed
        except Exception as e:
            self.logger.log_error(f"RS reconstruction failed: {e}")
            return None, nodes_contacted, fragments_accessed

    def _reconstruct_lrc(self, original_fragments):
        """
        Attempt reconstruction using LRC codes with smart local repair.
        """
        self.logger.log_info("Attempting LRC reconstruction (local repair first)...")
        alive_nodes = self.cluster.get_alive_nodes()

        # Build fragment list with positions
        available_fragments = []
        failed_positions = []
        for i, node in enumerate(self.cluster.nodes):
            if node.is_alive:
                available_fragments.append(node.fragment)
            else:
                available_fragments.append(None)
                failed_positions.append(i)

        nodes_contacted = len(alive_nodes)  # All alive nodes are available
        fragments_accessed = len(alive_nodes)  # Default: could need all
        local_repair_used = False
        repair_strategy = "Default"
        
        # Try local repair if only one failure
        if len(failed_positions) == 1:
            failed_pos = failed_positions[0]
            # Check if failure is in data fragments (positions 0 to k-1)
            if failed_pos < self.lrc_k:
                group_id = failed_pos // self.lrc_encoder.group_size
                group_start = group_id * self.lrc_encoder.group_size
                group_end = min(group_start + self.lrc_encoder.group_size, self.lrc_k)
                local_parity_idx = self.lrc_k + group_id
                
                self.logger.log_info(f"Single data failure at position {failed_pos} (group {group_id})")
                self.logger.log_info(f"Local parity at position {local_parity_idx}")
                
                # Check if local parity is available
                if local_parity_idx < len(available_fragments) and available_fragments[local_parity_idx] is not None:
                    # LOCAL REPAIR IS POSSIBLE!
                    # Need: (group_size - 1) surviving data fragments + 1 local parity
                    surviving_data = group_end - group_start - 1
                    fragments_accessed = surviving_data + 1  # data + local parity
                    local_repair_used = True
                    repair_strategy = "LOCAL"
                    self.logger.log_success(f"✓✓✓ LOCAL REPAIR POSSIBLE ✓✓✓")
                    self.logger.log_success(f"✓ Using ONLY {fragments_accessed} fragments ({surviving_data} data + 1 local parity)")
                    self.logger.log_success(f"✓ No GF(256) operations needed!")
                else:
                    # Local parity not available, must use global
                    fragments_accessed = self.lrc_k + self.lrc_encoder.global_parity
                    repair_strategy = "GLOBAL (parity unavailable)"
                    self.logger.log_info(f"Local parity missing: falling back to global repair ({fragments_accessed} fragments)")
            else:
                # Failure is in parity fragments, need global repair
                fragments_accessed = self.lrc_k + self.lrc_encoder.global_parity
                repair_strategy = "GLOBAL (parity fragment failed)"
                self.logger.log_info(f"Parity fragment failure: using global repair ({fragments_accessed} fragments)")
        elif len(failed_positions) > 1:
            # Multiple failures: must use global repair
            fragments_accessed = self.lrc_k + self.lrc_encoder.global_parity
            repair_strategy = "GLOBAL (multiple failures)"
            self.logger.log_info(f"Multiple failures: using global repair ({fragments_accessed} fragments)")
        
        # Perform reconstruction
        try:
            if local_repair_used:
                # Use local repair for the missing data fragment
                repaired_fragment = self.lrc_encoder.local_repair(available_fragments, failed_positions[0])
                if repaired_fragment is None:
                    self.logger.log_error("Local repair failed unexpectedly!")
                    return None, nodes_contacted, fragments_accessed, local_repair_used
                # Reconstruct full data from all data fragments (replace missing with repaired)
                data_fragments = []
                for i in range(self.lrc_k):
                    if i == failed_positions[0]:
                        data_fragments.append(repaired_fragment)
                    else:
                        data_fragments.append(available_fragments[i])
                out = bytearray()
                for frag in data_fragments:
                    out.extend(frag)
                # Remove padding
                while out and out[-1] == 0:
                    out.pop()
                recovered_data = bytes(out)
            else:
                recovered_data = self.lrc_encoder.global_repair(available_fragments)
            self.logger.log_success(f"LRC reconstruction successful! (Strategy: {repair_strategy})")
            # Log recovered data safely
            try:
                recovered_str = recovered_data.decode('utf-8', errors='replace')
                self.logger.log_info(f"Recovered data: {recovered_str}")
            except:
                self.logger.log_data_summary("Recovered data", f"{len(recovered_data)} bytes")
            return recovered_data, nodes_contacted, fragments_accessed, local_repair_used
        except Exception as e:
            self.logger.log_error(f"LRC reconstruction failed: {e}")
            return None, nodes_contacted, fragments_accessed, local_repair_used

    def _collect_and_display_metrics(self, rs_recovered_data, lrc_recovered_data,
                                     rs_nodes_contacted, lrc_nodes_contacted,
                                     rs_fragments_accessed, lrc_fragments_accessed,
                                     rs_encoding_time, rs_recovery_time,
                                     lrc_encoding_time, lrc_recovery_time,
                                     rs_success, lrc_success,
                                     lrc_local_repair_used):
        """
        Collect metrics for both schemes and display comparison.
        """
        # Use actual fragments accessed
        rs_fragments_used = rs_fragments_accessed
        lrc_fragments_used = lrc_fragments_accessed
        
        original_bytes = self.original_data.encode('utf-8')
        
        # Collect RS metrics
        self.metrics_collector.collect_rs_metrics(
            original_data=original_bytes,
            rs_encoder=self.rs_encoder,
            cluster=self.cluster,
            fragments_used=rs_fragments_used,
            nodes_contacted=rs_nodes_contacted,
            encoding_time=rs_encoding_time,
            recovery_time=rs_recovery_time,
            reconstruction_success=rs_success,
            data_integrity=rs_success
        )
        
        # Collect LRC metrics (track whether local repair was actually used)
        self.metrics_collector.collect_lrc_metrics(
            original_data=original_bytes,
            lrc_encoder=self.lrc_encoder,
            cluster=self.cluster,
            fragments_used=lrc_fragments_used,
            nodes_contacted=lrc_nodes_contacted,
            encoding_time=lrc_encoding_time,
            recovery_time=lrc_recovery_time,
            local_repair_used=lrc_local_repair_used,
            global_repair_used=not lrc_local_repair_used,
            reconstruction_success=lrc_success,
            data_integrity=lrc_success
        )
        
        # Compare metrics and display results
        try:
            self.metrics_collector.compare_metrics()
            metrics_summary = self.metrics_collector.get_metrics_summary()
            self.logger.log_metrics_comparison(metrics_summary)
        except Exception as e:
            self.logger.log_error(f"Error displaying metrics: {e}")
