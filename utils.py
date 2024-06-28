
from random import *

def get_bit(value, n):
    return ((value >> n & 1) != 0)


def set_bit(value, n):
    return value | (1 << n)


def clear_bit(value, n):
    return value & ~(1 << n)


def shuffle(array):
    "Fisher–Yates shuffle"
    for i in range(len(array) - 1, 0, -1):
        j = randrange(i + 1)
        array[i], array[j] = array[j], array[i]


class ByteArray2D:
    """
    This is designed to be a drop in replacement for your nested list.
    NOTE: this data could almost certainly be shrunk even further.
    NOTE2: this assumes you dont need to store numbers larger than 1 byte.
    """


    def __init__(self, width, height):
        self.buf = bytearray(width * height)
        self.mv = memoryview(self.buf)
        self.width = width
        self.height = height


    def __len__(self):
        return self.height


    def __getitem__(self, index):
        """
        Return a memoryview of row for the given row index.
        Intended to allow syntax like: ByteArray2D[idx1][idx2] to function.
        """
        start_idx = self.width * index
        end_idx = start_idx + self.width
        return self.mv[start_idx:end_idx]


    def __setitem__(self, index, val_list):
        """Add a list to the the specified row index"""
        start_idx = self.width * index
        for idx, item in enumerate(val_list):
            self.buf[start_idx + idx] = item