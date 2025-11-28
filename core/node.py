"""
Node class for simulating storage nodes in the erasure coding system.

Each node represents a storage unit that can store a fragment and
experience failures.
"""

class Node:
    """
    Represents a storage node in the distributed system.
    """

    def __init__(self, node_id):
        """
        Initialize a new node.

        Args:
            node_id: Unique identifier for this node
        """
        self.node_id = node_id
        self.fragment = None
        self.is_alive = True

    def store_fragment(self, fragment):
        """
        Store a data fragment on this node.

        Args:
            fragment: The data fragment to store
        """
        self.fragment = fragment

    def fail(self):
        """
        Mark this node as failed (unavailable).
        """
        self.is_alive = False

    def recover(self):
        """
        Mark this node as recovered (available again).
        """
        self.is_alive = True

    def __str__(self):
        """
        String representation of the node.

        Returns:
            String showing node status
        """
        status = "ALIVE" if self.is_alive else "FAILED"
        return f"Node {self.node_id}: {status}"
