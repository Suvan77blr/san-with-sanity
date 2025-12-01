"""
Metrics collection and comparison for erasure coding schemes.

Tracks and compares performance metrics between RS and LRC approaches.
"""

import time
from dataclasses import dataclass, asdict


@dataclass
class RecoveryMetrics:
    """
    Stores metrics for a single recovery operation.
    """
    scheme_name: str
    total_fragments: int
    data_fragments: int
    parity_fragments: int
    fragments_required: int
    fragments_used: int
    failed_fragments: int
    
    # Bandwidth metrics (in bytes)
    original_data_size: int
    total_fragment_size: int
    fragments_accessed_bytes: int  # Total data read from nodes
    bandwidth_efficiency: float  # (original_data_size / total_fragment_size) * 100
    
    # Computation metrics
    xor_operations: int  # Estimated number of XOR operations
    multiplication_operations: int  # GF(256) multiplications (for RS)
    
    # I/O metrics
    nodes_contacted: int
    fragments_accessed: int  # Number of fragment objects accessed
    
    # Time metrics (in milliseconds)
    encoding_time: float
    recovery_time: float
    total_time: float
    
    # Success metrics
    reconstruction_success: bool
    data_integrity: bool


class MetricsCollector:
    """
    Collects metrics during simulation runs.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.rs_metrics = None
        self.lrc_metrics = None
        self.comparison_results = None

    def __init__(self, scenario_config=None, scenario_id=None):
        self.scenario_config = scenario_config or {}
        self.scenario_id = scenario_id
        self.rs_metrics = None
        self.lrc_metrics = None
        self.comparison_results = None
        self.timestamp = time.time()
    
    def collect_rs_metrics(self, original_data, rs_encoder, cluster, 
                          fragments_used, nodes_contacted, 
                          encoding_time, recovery_time, 
                          reconstruction_success, data_integrity):
        """
        Collect metrics for Reed-Solomon encoding/recovery.
        
        Args:
            original_data: Original data bytes
            rs_encoder: EncoderRS instance
            cluster: Cluster instance
            fragments_used: Number of fragments actually used
            nodes_contacted: Number of nodes contacted
            encoding_time: Time taken to encode (ms)
            recovery_time: Time taken to recover (ms)
            reconstruction_success: Whether recovery succeeded
            data_integrity: Whether recovered data matches original
        """
        total_fragments = rs_encoder.total
        data_fragments = rs_encoder.k
        parity_fragments = rs_encoder.r
        
        # Calculate fragment sizes
        original_size = len(original_data)
        fragment_size = (original_size + data_fragments - 1) // data_fragments
        total_fragment_size = total_fragments * fragment_size
        
        # Bandwidth accessed - RS always needs k data fragments
        # But for comparison, it accesses only k fragments, not all
        fragments_accessed_bytes = data_fragments * fragment_size
        
        # Bandwidth efficiency (original vs total system overhead)
        bandwidth_efficiency = (original_size / total_fragment_size) * 100
        
        # XOR operations (RS uses XOR for parity creation and decoding)
        # Estimation: k*fragment_size bits XOR for each parity fragment
        xor_operations = parity_fragments * fragment_size * 8
        
        # Multiplication operations (RS uses GF(256) matrix multiplication in decoding)
        # More complex decoding when fragments are missing
        multiplication_operations = data_fragments * fragment_size * 8
        
        self.rs_metrics = RecoveryMetrics(
            scheme_name="Reed-Solomon (RS)",
            total_fragments=total_fragments,
            data_fragments=data_fragments,
            parity_fragments=parity_fragments,
            fragments_required=data_fragments,
            fragments_used=fragments_used,
            failed_fragments=total_fragments - fragments_used,
            original_data_size=original_size,
            total_fragment_size=total_fragment_size,
            fragments_accessed_bytes=fragments_accessed_bytes,
            bandwidth_efficiency=bandwidth_efficiency,
            xor_operations=xor_operations,
            multiplication_operations=multiplication_operations,
            nodes_contacted=nodes_contacted,
            fragments_accessed=fragments_used,
            encoding_time=encoding_time,
            recovery_time=recovery_time,
            total_time=encoding_time + recovery_time,
            reconstruction_success=reconstruction_success,
            data_integrity=data_integrity
        )
    
    def collect_lrc_metrics(self, original_data, lrc_encoder, cluster,
                           fragments_used, nodes_contacted, 
                           encoding_time, recovery_time,
                           local_repair_used, global_repair_used,
                           reconstruction_success, data_integrity):
        """
        Collect metrics for LRC encoding/recovery.
        
        Args:
            original_data: Original data bytes
            lrc_encoder: EncoderLRC instance
            cluster: Cluster instance
            fragments_used: Number of fragments actually used
            nodes_contacted: Number of nodes contacted
            encoding_time: Time taken to encode (ms)
            recovery_time: Time taken to recover (ms)
            local_repair_used: Whether local repair was possible
            global_repair_used: Whether global repair was needed
            reconstruction_success: Whether recovery succeeded
            data_integrity: Whether recovered data matches original
        """
        total_fragments = lrc_encoder.total_fragments
        data_fragments = lrc_encoder.k
        local_parity_fragments = lrc_encoder.num_groups * lrc_encoder.local_parity
        global_parity_fragments = lrc_encoder.global_parity
        
        # Calculate fragment sizes
        original_size = len(original_data)
        fragment_size = lrc_encoder.fragment_size if lrc_encoder.fragment_size else (
            (original_size + data_fragments - 1) // data_fragments
        )
        total_fragment_size = total_fragments * fragment_size
        
        # Bandwidth accessed - only the fragments actually read
        fragments_accessed_bytes = fragments_used * fragment_size
        
        # Bandwidth efficiency (original vs total system overhead)
        bandwidth_efficiency = (original_size / total_fragment_size) * 100
        
        # XOR operations depend heavily on repair type
        if local_repair_used:
            # Local repair: only XOR within one group (very cheap!)
            # Need to XOR group_size-1 data frags + 1 local parity = group_size fragments
            xor_operations = (lrc_encoder.group_size - 1) * fragment_size * 8
        else:
            # Global repair: use all data fragments for RS encoding
            # Similar complexity to RS but less than RS due to smaller data set
            xor_operations = data_fragments * fragment_size * 8
        
        # Multiplication operations (expensive GF(256) operations)
        if local_repair_used:
            # Local repair uses ONLY XOR, no GF(256) multiplications!
            multiplication_operations = 0
        else:
            # Global repair needs GF(256) operations
            multiplication_operations = data_fragments * fragment_size * 8
        
        self.lrc_metrics = RecoveryMetrics(
            scheme_name="Local Reconstruction Code (LRC)",
            total_fragments=total_fragments,
            data_fragments=data_fragments,
            parity_fragments=local_parity_fragments + global_parity_fragments,
            fragments_required=data_fragments,
            fragments_used=fragments_used,
            failed_fragments=total_fragments - fragments_used,
            original_data_size=original_size,
            total_fragment_size=total_fragment_size,
            fragments_accessed_bytes=fragments_accessed_bytes,
            bandwidth_efficiency=bandwidth_efficiency,
            xor_operations=xor_operations,
            multiplication_operations=multiplication_operations,
            nodes_contacted=nodes_contacted,
            fragments_accessed=fragments_used,
            encoding_time=encoding_time,
            recovery_time=recovery_time,
            total_time=encoding_time + recovery_time,
            reconstruction_success=reconstruction_success,
            data_integrity=data_integrity
        )
        self.lrc_metrics.local_repair_used = local_repair_used if local_repair_used else False
        self.lrc_metrics.global_repair_used = global_repair_used if global_repair_used else False
    
    def compare_metrics(self):
        """
        Compare RS and LRC metrics and generate insights.
        
        Returns:
            dict with comparison results and advantages
        """
        if self.rs_metrics is None or self.lrc_metrics is None:
            raise ValueError("Both RS and LRC metrics must be collected first")
        
        comparison = {
            'scenario_id': self.scenario_id,
            'local_repair_used': self.lrc_metrics.local_repair_used,
            'global_repair_used': self.lrc_metrics.global_repair_used,

            'nodes_saved': {
                'value': self.rs_metrics.nodes_contacted - self.lrc_metrics.nodes_contacted,
                'unit': 'nodes',
                'percentage': ((self.rs_metrics.nodes_contacted - self.lrc_metrics.nodes_contacted) / 
                              self.rs_metrics.nodes_contacted * 100)
            },
            'bandwidth_saved': {
                'value': self.rs_metrics.fragments_accessed_bytes - self.lrc_metrics.fragments_accessed_bytes,
                'unit': 'bytes',
                'percentage': ((self.rs_metrics.fragments_accessed_bytes - self.lrc_metrics.fragments_accessed_bytes) / 
                              self.rs_metrics.fragments_accessed_bytes * 100)
            },

            'xor_reduction_ratio': round(self.lrc_metrics.xor_operations / max(self.rs_metrics.xor_operations,1), 4),
            'multiplication_reduction_ratio': round(self.lrc_metrics.multiplication_operations / max(self.rs_metrics.multiplication_operations,1), 4),
            'recovery_time_improvement': {
                'value': self.rs_metrics.recovery_time - self.lrc_metrics.recovery_time,
                'unit': 'ms',
                'percentage': ((self.rs_metrics.recovery_time - self.lrc_metrics.recovery_time) / 
                              max(self.rs_metrics.recovery_time, 0.001) * 100)
            }
        }
        
        # Earlier Version.
        # comparison = {
        #     'nodes_saved': {
        #         'value': self.rs_metrics.nodes_contacted - self.lrc_metrics.nodes_contacted,
        #         'percentage': ((self.rs_metrics.nodes_contacted - self.lrc_metrics.nodes_contacted) / 
        #                       self.rs_metrics.nodes_contacted * 100)
        #     },
        #     'bandwidth_saved': {
        #         'value': self.rs_metrics.fragments_accessed_bytes - self.lrc_metrics.fragments_accessed_bytes,
        #         'percentage': ((self.rs_metrics.fragments_accessed_bytes - self.lrc_metrics.fragments_accessed_bytes) / 
        #                       self.rs_metrics.fragments_accessed_bytes * 100)
        #     },
        #     'xor_operations_ratio': self.lrc_metrics.xor_operations / max(self.rs_metrics.xor_operations, 1),
        #     'multiplication_operations_ratio': (self.lrc_metrics.multiplication_operations / 
        #                                        max(self.rs_metrics.multiplication_operations, 1)),
        #     'recovery_time_improvement': {
        #         'value': self.rs_metrics.recovery_time - self.lrc_metrics.recovery_time,
        #         'percentage': ((self.rs_metrics.recovery_time - self.lrc_metrics.recovery_time) / 
        #                       max(self.rs_metrics.recovery_time, 0.001) * 100)
        #     }
        # }
        
        self.comparison_results = comparison
        return comparison
    
    def get_metrics_summary(self):
        """
        Get a formatted summary of collected metrics.
        
        Returns:
            dict with formatted metrics
        """
        return {
            'scenario_id': self.scenario_id,
            'timestamp': self.timestamp,
            'scenario_config': self.scenario_config,
            'rs_metrics': asdict(self.rs_metrics) if self.rs_metrics else None,
            'lrc_metrics': asdict(self.lrc_metrics) if self.lrc_metrics else None,
            'comparison': self.comparison_results
        }

        # return {
        #     'rs_metrics': asdict(self.rs_metrics) if self.rs_metrics else None,
        #     'lrc_metrics': asdict(self.lrc_metrics) if self.lrc_metrics else None,
        #     'comparison': self.comparison_results
        # }
