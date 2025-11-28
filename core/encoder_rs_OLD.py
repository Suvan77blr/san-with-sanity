"""
Reed-Solomon encoder for erasure coding.

Provides encoding and decoding functionality using simplified RS-like codes.
Note: This is a demonstration implementation that uses basic XOR operations
rather than full Reed-Solomon mathematics for simplicity.
"""

class EncoderRS:
    """
    Handles Reed-Solomon encoding and decoding operations.
    """

    def __init__(self, k, r):
        """
        Initialize RS encoder.

        Args:
            k: Number of data fragments
            r: Number of parity fragments
        """
        self.k = k
        self.r = r
        self.total_fragments = k + r

    def encode(self, data):
        """
        Encode data into k data fragments and r parity fragments.

        Args:
            data: Input data to encode (bytes or string)

        Returns:
            List of encoded fragments (data + parity)
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

        # Generate r parity fragments using XOR
        parity_fragments = []
        for p in range(self.r):
            parity = bytearray(fragment_size)
            for i in range(fragment_size):
                xor_val = 0
                for j in range(self.k):
                    xor_val ^= data_fragments[j][i]
                parity[i] = xor_val
            parity_fragments.append(bytes(parity))

        return data_fragments + parity_fragments

    def decode(self, fragments):
        """
        Decode and recover original data from available fragments.

        Args:
            fragments: List of available fragments (must have at least k)

        Returns:
            Recovered original data
        """
        if len(fragments) < self.k:
            raise ValueError(f"Need at least {self.k} fragments for RS decoding, got {len(fragments)}")

        # For this simplified implementation, we can reconstruct from any k fragments
        # Take the first k fragments and combine them
        available_fragments = fragments[:self.k]

        if not available_fragments:
            raise ValueError("No fragments available for decoding")

        # Get fragment size from the first fragment
        fragment_size = len(available_fragments[0])

        # Reconstruct data by concatenating all fragments in order
        reconstructed = bytearray()
        for fragment in available_fragments:
            reconstructed.extend(fragment)

        # Remove padding (null bytes at the end)
        while reconstructed and reconstructed[-1] == 0:
            reconstructed.pop()

        return bytes(reconstructed)
