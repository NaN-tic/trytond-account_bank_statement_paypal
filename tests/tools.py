# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

__all__ = ['read_file']


def read_file(filename):
    with open(filename) as f:
        data = f.read()
        # On python3 we must cast to bytes with valid encoding
        if bytes != str:
            data = bytes(data, encoding=f.encoding)
    return data
