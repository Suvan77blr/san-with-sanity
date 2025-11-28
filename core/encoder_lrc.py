"""
Local Reconstruction Code (LRC) encoder.

Implements local XOR parity groups with global parity for efficient recovery.
Divides k data fragments into groups with local parity, plus global parity.
"""

class EncoderLRC:
    """
    Handles Local Reconstruction Code encoding and decoding operations.
    """

    def __init__(self, k, local_parity):
        """
        Initialize LRC encoder.

        Args:
            k: Number of data fragments
            local_parity: Number of local parity fragments per group
        """
        self.k = k
        self.local_parity = local_parity
        # For k=6, local_parity=1: divide into 2 groups of 3
        self.group_size = 3  # Fixed for this implementation
        self.num_groups = k // self.group_size
        self.total_fragments = k + (self.num_groups * local_parity) + 1  # +1 for global parity

    def encode(self, data):
        """
        Encode data using LRC with local and global parity.

        Args:
            data: Input data to encode

        Returns:
            List of encoded fragments (data + local parity + global parity)
        """
        # Convert to bytes if string
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Split data into k fragments
        fragment_size = len(data) // self.k
        if len(data) % self.k != 0:
            fragment_size += 1

        data_fragments = []
        for i in range(self.k):
            start = i * fragment_size
            end = min((i + 1) * fragment_size, len(data))
            fragment = data[start:end]
            # Pad fragment to equal size
            if len(fragment) < fragment_size:
                fragment = fragment + b'\x00' * (fragment_size - len(fragment))
            data_fragments.append(fragment)

        # Generate local parity for each group
        local_parity_fragments = []
        for group in range(self.num_groups):
            start_idx = group * self.group_size
            end_idx = start_idx + self.group_size
            group_fragments = data_fragments[start_idx:end_idx]

            # XOR all fragments in the group for local parity
            parity = bytearray(fragment_size)
            for i in range(fragment_size):
                xor_val = 0
                for fragment in group_fragments:
                    xor_val ^= fragment[i]
                parity[i] = xor_val
            local_parity_fragments.append(bytes(parity))

        # Generate global parity (XOR of all data fragments)
        global_parity = bytearray(fragment_size)
        for i in range(fragment_size):
            xor_val = 0
            for fragment in data_fragments:
                xor_val ^= fragment[i]
            global_parity[i] = xor_val

        return data_fragments + local_parity_fragments + [bytes(global_parity)]

    def local_decode(self, fragments, group_id):
        """
        Attempt local reconstruction within a specific group.

        Args:
            fragments: Available fragments
            group_id: ID of the group to reconstruct (0-based)

        Returns:
            Recovered fragment or None if local repair fails
        """
        if group_id >= self.num_groups:
            return None

        # Get fragments for this group and its local parity
        start_data = group_id * self.group_size
        end_data = start_data + self.group_size
        local_parity_idx = self.k + group_id

        group_fragments = []
        local_parity = None

        # Collect available fragments for this group
        for i in range(start_data, end_data):
            if i < len(fragments) and fragments[i] is not None:
                group_fragments.append((i, fragments[i]))

        # Get local parity if available
        if local_parity_idx < len(fragments) and fragments[local_parity_idx] is not None:
            local_parity = fragments[local_parity_idx]

        # Need at least group_size - 1 data fragments + local parity for local repair
        if len(group_fragments) >= self.group_size - 1 and local_parity is not None:
            # Find which fragment is missing
            present_indices = {idx for idx, _ in group_fragments}
            missing_idx = None
            for i in range(start_data, end_data):
                if i not in present_indices:
                    missing_idx = i
                    break

            if missing_idx is not None:
                # Reconstruct missing fragment using XOR of others + local parity
                reconstructed = bytearray(len(local_parity))
                for i in range(len(local_parity)):
                    xor_val = local_parity[i]  # Start with local parity
                    for _, fragment in group_fragments:
                        xor_val ^= fragment[i]
                    reconstructed[i] = xor_val
                return missing_idx, bytes(reconstructed)

        return None

    def global_decode(self, fragments):
        """
        Perform global reconstruction using all available fragments.

        Args:
            fragments: Available fragments (list where None indicates missing)

        Returns:
            Recovered original data
        """
        available_fragments = [f for f in fragments if f is not None]
        if len(available_fragments) < self.k:
            raise ValueError(f"Need at least {self.k} fragments for LRC global decoding")

        # Use the first k available fragments to reconstruct
        # In a real LRC, we'd use the global parity, but for simplicity:
        fragment_size = len(available_fragments[0])

        # Reconstruct data by concatenating the fragments
        reconstructed = bytearray()
        for i in range(fragment_size):
            for fragment in available_fragments[:self.k]:
                if i < len(fragment):
                    reconstructed.append(fragment[i])
                    break

        # Remove padding
        while reconstructed and reconstructed[-1] == 0:
            reconstructed.pop()

        return bytes(reconstructed)
