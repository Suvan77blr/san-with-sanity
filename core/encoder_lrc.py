"""
Real Local Reconstruction Codes (LRC) encoder with:

  • Local parity groups (XOR)
  • Global Reed–Solomon parity over GF(256)

This mirrors Azure-LRC and HDFS LRC behavior:
    - Fast local repair: 1 missing → repair via XOR within group
    - Slow global repair: multi-missing → global RS-based repair

Author: ChatGPT (2025)
"""

from reedsolo import RSCodec


class EncoderLRC:
    """
    Full Azure-style LRC encoder with:
        - k data fragments
        - g local parity groups
        - 1 global RS parity set
    """

    def __init__(self, k: int, group_size: int, local_parity: int = 1, global_parity: int = 2):
        """
        Args:
            k            : number of data fragments
            group_size   : number of data fragments per group
            local_parity : number of local parity fragments per group
            global_parity: number of RS global parity fragments
        """

        self.k = k
        self.group_size = group_size
        self.local_parity = local_parity
        self.global_parity = global_parity

        # Number of data groups (rounded up)
        self.num_groups = (k + group_size - 1) // group_size

        # Total fragments: data + local + global
        self.total_fragments = (
            k + (self.num_groups * local_parity) + global_parity
        )

        self.rsc = None  # RS object
        self.fragment_size = None

    # ----------------------------------------------------------------------
    # ENCODE
    # ----------------------------------------------------------------------
    def encode(self, data: bytes | str):
        """
        Encode data into data + local parity + global RS parity.
        """

        if isinstance(data, str):
            data = data.encode("utf-8")

        # Compute fragment size (pad last fragment)
        self.fragment_size = (len(data) + self.k - 1) // self.k

        # Split into k data fragments
        data_fragments = []
        for i in range(self.k):
            start = i * self.fragment_size
            end = start + self.fragment_size
            frag = data[start:end]
            frag = frag + b"\x00" * (self.fragment_size - len(frag))
            data_fragments.append(frag)

        # ------------------------
        # Generate Local Parity
        # ------------------------
        local_parities = []
        for grp in range(self.num_groups):
            start = grp * self.group_size
            end = min(start + self.group_size, self.k)
            group_frags = data_fragments[start:end]

            # XOR of all group fragments for L1 parity
            parity = bytearray(self.fragment_size)
            for i in range(self.fragment_size):
                v = 0
                for frag in group_frags:
                    v ^= frag[i]
                parity[i] = v
            local_parities.append(bytes(parity))

        # ------------------------
        # Generate Global RS Parity
        # ------------------------
        nsym = self.global_parity * self.fragment_size
        self.rsc = RSCodec(nsym)

        # Encode entire data-region at once
        codeword = self.rsc.encode(b"".join(data_fragments))

        # Extract RS parity (last bytes)
        rs_parity = codeword[-nsym:]

        # Split RS parity into fragments
        global_parity_frags = []
        for i in range(self.global_parity):
            start = i * self.fragment_size
            end = start + self.fragment_size
            global_parity_frags.append(rs_parity[start:end])

        return data_fragments + local_parities + global_parity_frags

    # ----------------------------------------------------------------------
    # LOCAL REPAIR
    # ----------------------------------------------------------------------
    def local_repair(self, fragments, missing_index):
        """
        Fast local XOR-based recovery for a *single* missing data fragment.
        Returns bytes or None.
        """

        group_id = missing_index // self.group_size
        start = group_id * self.group_size
        end = min(start + self.group_size, self.k)

        local_parity_idx = self.k + group_id  # index of that group's local parity

        # If local parity is missing, local repair impossible
        if fragments[local_parity_idx] is None:
            return None

        # Collect available fragments
        available = []
        for i in range(start, end):
            if fragments[i] is not None and i != missing_index:
                available.append(fragments[i])

        # Need group_size - 1 data frags + local parity
        if len(available) != (end - start - 1):
            return None

        # XOR them back
        reconstructed = bytearray(self.fragment_size)

        for i in range(self.fragment_size):
            v = fragments[local_parity_idx][i]
            for frag in available:
                v ^= frag[i]
            reconstructed[i] = v

        return bytes(reconstructed)

    # ----------------------------------------------------------------------
    # GLOBAL REPAIR (RS)
    # ----------------------------------------------------------------------
    def global_repair(self, fragments):
        """
        Perform RS-based global recovery of the full data stream.

        Missing fragments (data+local parity) are treated as erasures.
        """

        # Check if all fragments are present
        missing_count = sum(1 for f in fragments if f is None)

        if missing_count == 0:
            # All fragments present - extract data fragments directly
            data = []
            for i in range(self.k):
                data.append(fragments[i])

            # Combine into final data
            out = bytearray()
            for frag in data:
                out.extend(frag)

            # Remove zero padding
            while out and out[-1] == 0:
                out.pop()

            return bytes(out)

        # Some fragments missing - use RS correction
        # Construct full codeword
        full_len = self.total_fragments * self.fragment_size
        codeword = bytearray(full_len)
        erasures = []

        for idx in range(self.total_fragments):
            start = idx * self.fragment_size
            if fragments[idx] is None:
                for b in range(self.fragment_size):
                    erasures.append(start + b)
                continue
            codeword[start:start + self.fragment_size] = fragments[idx]

        # Decode with erasures
        decoded = self.rsc.decode(bytes(codeword), erase_pos=erasures)

        # decoded = (data, parity)
        data_bytes = decoded[0]

        # Extract the k original data fragments
        data = []
        for i in range(self.k):
            start = i * self.fragment_size
            end = start + self.fragment_size
            data.append(data_bytes[start:end])

        # Combine into final data
        out = bytearray()
        for frag in data:
            out.extend(frag)

        # Remove zero padding
        while out and out[-1] == 0:
            out.pop()

        return bytes(out)
