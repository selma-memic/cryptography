from bits import Bits
from functools import reduce
from operator import xor

class LFSR:
    def __init__(self, poly, state=None):
        """
        Improved LFSR implementation combining both approaches
        - poly: set of polynomial degrees (e.g., {3,1} for x³ + x + 1)
        - state: initial state as Bits, int, or iterable
        """
        if not poly:
            raise ValueError("Polynomial must not be empty")
        
        self.degree = max(poly)
        self.length = self.degree
        
        # Create polynomial coefficients [p0, p1, ..., pn]
        self.poly_coeff = [int(i in poly) for i in range(self.degree + 1)]
        
        # Initialize state
        if state is None:
            self.state = Bits([True] * self.length)
        else:
            state_bits = Bits(state) if not isinstance(state, Bits) else state
            if len(state_bits) != self.length:
                raise ValueError(
                    f"Invalid state length: got {len(state_bits)} bits, "
                    f"expected {self.length} bits for polynomial degree {self.degree}"
                )
            self.state = state_bits
            
        self.output = None
        self.feedback = None
        self._update()

    def _update(self):
        """Update output and feedback bits"""
        self.output = self.state[-1]  # Rightmost bit is output
        # Calculate feedback using polynomial coefficients
        self.feedback = reduce(xor, [
            coeff & bit 
            for coeff, bit in zip(self.poly_coeff[1:], self.state.bits)
        ])

    def __iter__(self):
        return self

    def __next__(self):
        """Generate next output bit and update state"""
        output = self.output
        
        # Shift right and insert feedback
        new_state = [self.feedback] + self.state.bits[:-1]
        self.state = Bits(new_state)
        self._update()
        
        return output

    def run_steps(self, N=1, state=None):
        """Run N steps and return output bits"""
        if state is not None:
            self.state = self._initialize_state(state)
            self._update()
        return Bits([next(self) for _ in range(N)])

    def cycle(self, state=None):
        """Generate full cycle until state repeats"""
        if state is not None:
            self.state = self._initialize_state(state)
            self._update()
            
        seen = set()
        outputs = []
        while tuple(self.state.bits) not in seen:
            seen.add(tuple(self.state.bits))
            outputs.append(next(self))
        return Bits(outputs)

    def _initialize_state(self, state):
        """Validate and convert state to Bits object"""
        if isinstance(state, Bits):
            if len(state) != self.length:
                raise ValueError(f"State length must be {self.length}")
            return state
        return Bits(state, length=self.length)

    def __str__(self):
        poly_str = ' + '.join([f'x^{d}' for d in sorted(self.poly_coeff[1:], reverse=True)] + ['1'])
        return f"LFSR(poly={poly_str}, state={self.state})"

def berlekamp_massey(bits):
    """
    Finds the shortest LFSR for a given binary sequence.
    
    Args:
        bits (Bits): The input bit sequence.
        
    Returns:
        set: Set of degrees of the feedback polynomial.
    """
    N = len(bits)
    C = [1] + [0]*N  # Connection polynomial
    B = [1] + [0]*N  # Copy of previous C
    L = 0            # Current LFSR length
    m = -1           # Last update index
    for n in range(N):
        # Compute discrepancy d
        d = bits[n]
        for i in range(1, L+1):
            d ^= C[i] & bits[n-i]
        
        if d == 1:
            T = C.copy()
            for i in range(n-m, N):
                if B[i - (n - m)]:
                    C[i] ^= 1
            if 2 * L <= n:
                L = n + 1 - L
                B = T
                m = n
    # Now, C is the connection polynomial: 1 + C[1]*x + C[2]*x^2 + ... + C[N]*x^N
    # Convert C to set of degrees
    poly = {i for i, coef in enumerate(C) if coef}
    return poly
