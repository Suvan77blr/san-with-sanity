"""
Cluster class for managing a collection of storage nodes.

Handles distribution of fragments across nodes and failure simulation.
"""

import random
from .node import Node


class Cluster:
    """
    Manages a collection of Node objects in the distributed system.
    """

    def fail_nodes_by_indices(self, indices):
        """
        Fail nodes by their indices (node_id).

        Args:
            indices: List of node indices to fail

        Returns:
            List of node IDs that were failed
        """
        failed_ids = []
        for idx in indices:
            if 0 <= idx < len(self.nodes):
                self.nodes[idx].fail()
                failed_ids.append(self.nodes[idx].node_id)
        return failed_ids

    def __init__(self, num_nodes):
        """
        Initialize a cluster with the specified number of nodes.

        Args:
            num_nodes: Number of nodes to create in the cluster
        """
        self.nodes = []
        self._create_nodes(num_nodes)

    def _create_nodes(self, num_nodes):
        """
        Create the specified number of nodes.

        Args:
            num_nodes: Number of nodes to create
        """
        for i in range(num_nodes):
            self.nodes.append(Node(i))

    def distribute_fragments(self, fragments):
        """
        Distribute fragments across available nodes.

        Args:
            fragments: List of fragments to distribute
        """
        if len(fragments) > len(self.nodes):
            raise ValueError("Cannot distribute more fragments than available nodes")

        for i, fragment in enumerate(fragments):
            self.nodes[i].store_fragment(fragment)

    def fail_nodes(self, failure_count):
        """
        Randomly fail a specified number of nodes.

        Args:
            failure_count: Number of nodes to fail

        Returns:
            List of node IDs that were failed
        """
        available_nodes = [node for node in self.nodes if node.is_alive]
        if failure_count > len(available_nodes):
            failure_count = len(available_nodes)

        failed_nodes = random.sample(available_nodes, failure_count)
        failed_ids = []

        for node in failed_nodes:
            node.fail()
            failed_ids.append(node.node_id)

        return failed_ids

    def get_alive_nodes(self):
        """
        Get list of currently alive nodes.

        Returns:
            List of alive Node objects
        """
        return [node for node in self.nodes if node.is_alive]

    def get_dead_nodes(self):
        """
        Get list of currently failed nodes.

        Returns:
            List of failed Node objects
        """
        return [node for node in self.nodes if not node.is_alive]

    def reset_all_nodes(self):
        """
        Reset all nodes to alive state (for testing).
        """
        for node in self.nodes:
            node.recover()
