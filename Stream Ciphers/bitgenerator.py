from lfsr import LFSR
from bits import Bits

class AlternatingStep:
    def __init__(self, seed=None, polyC=None, poly0=None, poly1=None):
        # Set default polynomials as per PDF
        self.polyC = {5, 2, 0} if polyC is None else polyC  # x⁵ + x² + 1
        self.poly0 = {3, 1, 0} if poly0 is None else poly0  # x³ + x + 1
        self.poly1 = {4, 1, 0} if poly1 is None else poly1  # x⁴ + x + 1

        # Initialize with all 1s if no seed
        if seed is None:
            seed = Bits([1]*12)  # 5 (C) + 3 (0) + 4 (1) = 12 bits
        else:
            seed = Bits(seed)
            if len(seed) < 12:
                raise ValueError("Seed needs 12 bits (5+3+4)")

        # Split seed into components
        self.lfsrC = LFSR(self.polyC, Bits(seed.bits[:5]))
        self.lfsr0 = LFSR(self.poly0, Bits(seed.bits[5:8]))
        self.lfsr1 = LFSR(self.poly1, Bits(seed.bits[8:12]))

    def __iter__(self):
        return self

    def __next__(self):
        control_bit = next(self.lfsrC)
        
        # Get current outputs before clocking
        out0 = self.lfsr0.output
        out1 = self.lfsr1.output
        
        # Clock the appropriate LFSR
        if control_bit == 0:
            next(self.lfsr0)
        else:
            next(self.lfsr1)
        
        # Return XOR of current outputs (matches PDF)
        return not (out0 ^ out1)  # Inverted to match PDF's notation