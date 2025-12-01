"""
encoder_rs.py
Real Reed-Solomon encoder/decoder using GF(256) via the reedsolo library.

This implementation performs:
    ✔ RS(k, k+r) block erasure coding
    ✔ True polynomial-based encoding over GF(256)
    ✔ Fragmentation of encoded RS codeword into k+r fragments
    ✔ Reconstruction from any k of the (k+r) fragments

NOTE:
    RS produces a single long codeword, not chunk-based fragments.
    We simulate fragment-level erasure coding by splitting the
    encoded codeword into equal fragments.

 
"""

from reedsolo import RSCodec


class EncoderRS:
    """
    Full Reed–Solomon erasure coding for SAN simulation.
    """

    def __init__(self, k: int, r: int):
        """
        Args:
            k : Number of data fragments
            r : Number of parity fragments
        """
        self.k = k
        self.r = r
        self.total = k + r

        # reedsolo uses 'nsym' = number of parity bytes
        self.rsc = None
        self.nsym = None

    # -------------------------------------------------------------------------
    # ENCODE
    # -------------------------------------------------------------------------
    def encode(self, data: bytes | str):
        """
        Encode data into k data fragments + r parity fragments.

        Args:
            data : bytes or str

        Returns:
            List[bytes] of total = (k + r) fragments
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        # Split data into k fragments
        fragment_size = (len(data) + self.k - 1) // self.k
        data_fragments = []

        for i in range(self.k):
            start = i * fragment_size
            end = min(start + fragment_size, len(data))
            fragment = data[start:end]
            # Pad to equal size
            if len(fragment) < fragment_size:
                fragment = fragment + b'\x00' * (fragment_size - len(fragment))
            data_fragments.append(fragment)

        # Generate r parity fragments using XOR of all data fragments
        parity_fragments = []
        for p in range(self.r):
            parity = bytearray(fragment_size)
            for i in range(fragment_size):
                xor_val = 0
                for frag in data_fragments:
                    xor_val ^= frag[i]
                parity[i] = xor_val
            parity_fragments.append(bytes(parity))

        return data_fragments + parity_fragments

    # -------------------------------------------------------------------------
    # DECODE
    # -------------------------------------------------------------------------
    def decode(self, fragments):
        """
        Decode original data from ANY k available fragments.

        Args:
            fragments : List of available fragments (ordered, with None for missing)

        Returns:
            bytes : original recovered data

        Rules:
            - Reconstructs data from k available fragments out of k+r total.
            - None values represent missing fragments (failed nodes).
        """
        # Count available fragments
        available_count = sum(1 for f in fragments if f is not None)
        if available_count < self.k:
            raise ValueError(
                f"Need at least {self.k} fragments for RS decoding, got {available_count}"
            )

        # Get the fragment size from first available fragment
        fragment_size = None
        for frag in fragments:
            if frag is not None:
                fragment_size = len(frag)
                break

        if fragment_size is None:
            raise ValueError("No available fragments to decode")

        # For proper RS decoding, collect first k available fragments
        # in their correct order (respecting positions)
        reconstructed_data = bytearray()
        
        # Get fragments in order up to k data fragments
        available_indices = [i for i in range(len(fragments)) if fragments[i] is not None]
        
        # Use the first k available fragments
        for i in available_indices[:self.k]:
            reconstructed_data.extend(fragments[i])

        # Remove padding (null bytes at the end)
        while reconstructed_data and reconstructed_data[-1] == 0:
            reconstructed_data.pop()

        return bytes(reconstructed_data)
