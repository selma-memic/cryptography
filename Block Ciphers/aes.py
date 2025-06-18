from typing import List

# AES S-box
S_BOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

RCON = [
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
]

class AES:
    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("Invalid key size: AES-128 requires a 16-byte (128-bit) key.")
        self.key = key
        self.round_keys = self.key_expansion()


    @staticmethod
    def add_round_key(state: bytes, round_key: bytes) -> bytes:
        return bytes([b ^ k for b, k in zip(state, round_key)])

    @staticmethod
    def byte_substitution(state: bytes) -> bytes:
        return bytes([S_BOX[b] for b in state])

    @staticmethod
    def shift_rows(state: bytes) -> bytes:
        # Convert to 4x4 matrix, column-major
        matrix = [[state[r + 4 * c] for c in range(4)] for r in range(4)]
        # Shift rows
        for r in range(1, 4):
            matrix[r] = matrix[r][r:] + matrix[r][:r]
        # Flatten back to bytes (column-major)
        return bytes([matrix[r][c] for c in range(4) for r in range(4)])


    @staticmethod
    def mul_by_02(b: int) -> int:
        return ((b << 1) ^ 0x1B) & 0xFF if b & 0x80 else (b << 1) & 0xFF

    @staticmethod
    def mul_by_03(b: int) -> int:
        return AES.mul_by_02(b) ^ b  # Since 3*b = 2*b ⊕ b

    @staticmethod
    def mul_by_01(b: int) -> int:
        return b  # Multiplication by 1 is the identity
    
    @staticmethod
    def mix_single_column(column: List[int]) -> List[int]:
        a = column
        return [
            AES.mul_by_02(a[0]) ^ AES.mul_by_03(a[1]) ^ a[2] ^ a[3],
            a[0] ^ AES.mul_by_02(a[1]) ^ AES.mul_by_03(a[2]) ^ a[3],
            a[0] ^ a[1] ^ AES.mul_by_02(a[2]) ^ AES.mul_by_03(a[3]),
            AES.mul_by_03(a[0]) ^ a[1] ^ a[2] ^ AES.mul_by_02(a[3])
        ]


    @staticmethod
    def mix_column(state: bytes) -> bytes:
        # Proper column-major interpretation
        matrix = [[state[r + 4 * c] for r in range(4)] for c in range(4)]
        mixed = [AES.mix_single_column(col) for col in matrix]
        return bytes([mixed[c][r] for c in range(4) for r in range(4)])


    def key_expansion(self) -> List[bytes]:
        key_columns = [list(self.key[i:i+4]) for i in range(0, 16, 4)]
        i = 4
        while len(key_columns) < 44:
            word = list(key_columns[-1])
            if i % 4 == 0:
                word = word[1:] + word[:1]
                word = [S_BOX[b] for b in word]
                word[0] ^= RCON[(i//4)-1]
            word = [a ^ b for a, b in zip(word, key_columns[i - 4])]
            key_columns.append(word)
            i += 1
        round_keys = [sum(key_columns[i:i+4], []) for i in range(0, 44, 4)]
        return [bytes(rk) for rk in round_keys]

    @staticmethod
    def round(state: bytes, round_key: bytes) -> bytes:
        state = AES.byte_substitution(state)
        state = AES.shift_rows(state)
        state = AES.mix_column(state)
        state = AES.add_round_key(state, round_key)
        return state

    @staticmethod
    def final_round(state: bytes, round_key: bytes) -> bytes:
        state = AES.byte_substitution(state)
        state = AES.shift_rows(state)
        state = AES.add_round_key(state, round_key)
        return state

    def partially_encrypt(self, plaintext: bytes, num_rounds: int = 10) -> bytes:
        """
        Encrypts a 16-byte block of plaintext using the specified number of AES rounds.
        """
        state = self.add_round_key(plaintext, self.round_keys[0])
        
        for i in range(1, num_rounds):
            state = self.round(state, self.round_keys[i])
        
        if num_rounds == 10:
            state = self.final_round(state, self.round_keys[10])
        
        return state

    def encrypt(self, plaintext):
        state = self.add_round_key(plaintext, self.round_keys[0])
        for i in range(1, 10):
            state = self.round(state, self.round_keys[i])
        state = self.final_round(state, self.round_keys[10])
        return state 
    
   

