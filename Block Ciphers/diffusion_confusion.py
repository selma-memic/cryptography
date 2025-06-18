import os
from aes import AES

def flip_bit(x: bytes, index: int) -> bytes:
    byte_index = index // 8
    bit_index = index % 8
    flipped_byte = x[byte_index] ^ (1 << (7 - bit_index))
    return x[:byte_index] + bytes([flipped_byte]) + x[byte_index+1:]

def hamming_distance(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count('1') for x, y in zip(a, b))

def aes_diffusion(num_rounds=None) -> int:
    key = os.urandom(16)
    plaintext = os.urandom(16)
    plaintext_flipped = flip_bit(plaintext, 0)  # flip first bit

    aes = AES(key)
    c1 = aes.partially_encrypt(plaintext, num_rounds or 10)
    c2 = aes.partially_encrypt(plaintext_flipped, num_rounds or 10)

    return hamming_distance(c1, c2)

def aes_confusion(num_rounds=None) -> int:
    key = os.urandom(16)
    key_flipped = flip_bit(key, 0)  # flip first bit
    plaintext = os.urandom(16)

    aes1 = AES(key)
    aes2 = AES(key_flipped)

    c1 = aes1.partially_encrypt(plaintext, num_rounds or 10)
    c2 = aes2.partially_encrypt(plaintext, num_rounds or 10)

    return hamming_distance(c1, c2)
