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

    def _init_rs(self, data_len: int):
        """
        Initialize the RS codec dynamically based on data length.

        Why?
        RS works on full-byte buffers. We encode the entire data at once.
        The number of parity bytes = r * fragment_size.

        This ensures that exactly r full fragments worth of parity are created.
        """
        fragment_size = (data_len + self.k - 1) // self.k
        self.nsym = self.r * fragment_size
        self.rsc = RSCodec(self.nsym)
        return fragment_size

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

        frag_size = self._init_rs(len(data))

        # Encode full data to a single RS codeword
        codeword = self.rsc.encode(data)

        # Now split into fragments
        fragments = []
        for i in range(self.total):
            start = i * frag_size
            end = start + frag_size
            frag = codeword[start:end]
            fragments.append(frag)

        return fragments

    # -------------------------------------------------------------------------
    # DECODE
    # -------------------------------------------------------------------------
    def decode(self, fragments):
        """
        Decode original data from ANY k available fragments.

        Args:
            fragments : List of available fragments

        Returns:
            bytes : original recovered data

        Rules:
            - We reconstruct a full-length codeword by placing available
              fragments in their correct positions.
            - Missing fragments are filled with zero bytes; RSCodec can
              correct erasures if the number missing is <= r.
        """
        if len(fragments) < self.k:
            raise ValueError(
                f"Need at least {self.k} fragments for RS decoding, got {len(fragments)}"
            )

        # Each fragment is of equal size - find from first available fragment
        frag_size = None
        for frag in fragments:
            if frag is not None:
                frag_size = len(frag)
                break
        if frag_size is None:
            raise ValueError("No valid fragments available for decoding")

        # Rebuild full codeword (k+r fragments)
        # Fill missing fragments with zeros ("erasures")
        codeword = bytearray(self.total * frag_size)

        # Track erasure positions (byte-level indices)
        erasures = []

        for i in range(self.total):
            if i < len(fragments) and fragments[i] is not None:
                # Fragment available → place into codeword
                start = i * frag_size
                codeword[start:start + frag_size] = fragments[i]
            else:
                # Fragment missing → mark erasures
                start = i * frag_size
                for j in range(frag_size):
                    erasures.append(start + j)
                # leave zeros in codeword

        # Let RSCodec correct erasures
        corrected = self.rsc.decode(bytes(codeword), erase_pos=erasures)

        # decode() returns (decoded_data, parity) → we want original data only
        decoded_data = corrected[0]

        return decoded_data
