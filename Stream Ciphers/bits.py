# bits.py
class Bits:
    
    def __init__(self, value, length=None, lsb_first=False):
        
        self.bits = []
        self.lsb_first = lsb_first  # Store bit order preference
        
        if isinstance(value, (list, tuple)):
            self.bits = [bool(bit) for bit in value]
        elif isinstance(value, int):
            if value < 0: raise ValueError("No negative integers")
            length = max(length or value.bit_length(), 1)
            if lsb_first:
                self.bits = [bool((value >> i) & 1) for i in range(length)]
            else:
                self.bits = [bool((value >> i) & 1) for i in range(length-1, -1, -1)]
        elif isinstance(value, bytes):
            for byte in value:
                if lsb_first:
                    self.bits.extend([bool((byte >> i) & 1) for i in range(8)])
                else:
                    self.bits.extend([bool((byte >> i) & 1) for i in range(7, -1, -1)])
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

    def to_int(self, lsb_first=False):
            """Convert bits to integer using specified bit order
            Args:
                lsb_first: If True, treats bits[0] as least significant bit
                        If False (default), treats bits[0] as most significant bit
            Returns:
                Integer representation of the bit sequence
            """
            if lsb_first:
                return sum(int(bit) << i for i, bit in enumerate(self.bits))
            else:
                return sum(int(bit) << (len(self)-1-i) for i, bit in enumerate(self.bits))
    def __len__(self): return len(self.bits)
    def __getitem__(self, index): return self.bits[index]
    def __setitem__(self, index, value): self.bits[index] = bool(value)
    def __str__(self): return ''.join(['1' if b else '0' for b in self.bits])
    def __repr__(self):
        if len(self) <= 10:
            return f"Bits({self.bits})"
        return f"Bits('{str(self)}')"
    
    def __xor__(self, other):
        if len(self) != len(other):
            raise ValueError("Bits must be equal length for XOR")
        return Bits([a ^ b for a, b in zip(self.bits, other.bits)])
    
    def __and__(self, other):
        if len(self) != len(other):
            raise ValueError("Bits must be equal length for AND")
        return Bits([a & b for a, b in zip(self.bits, other.bits)])
    
    def __add__(self, other): return Bits(self.bits + other.bits)
    def __mul__(self, scalar):
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Scalar must be a non-negative integer")
        return Bits(self.bits * scalar)
    
    def to_bytes(self):
        if len(self) % 8 != 0:
            raise ValueError("Bit length must be divisible by 8")
        return bytes(int(''.join('1' if bit else '0' for bit in self.bits[i:i+8]), 2) 
                for i in range(0, len(self), 8))
    
    def append(self, bit): self.bits.append(bool(bit))
    def pop(self, index=-1):  # Fix default index
        return self.bits.pop(index)
    
    def parity_bit(self): return sum(self.bits) % 2