"""
original: https://github.com/frederickjansen/polyline/blob/0c81e0ddd29d4dcaed6cb036c40120e63f3bee9c/src/polyline/polyline.py

Modified to more easily deal with xctrack's task polyline format. Mostly just not assuming that the encoded string
is a set of pairs. XCTrack task turnpoints uses polyline encoded lat, long, altitude, and radius. Most polyline
libraries assume you are only ever dealing with pairs of coordinates.

reference: https://xctrack.org/Competition_Interfaces.html
"""
import io
import itertools
import math
from typing import List

METER_FACTOR = 100000

def _pcitr(iterable):
    return zip(iterable, itertools.islice(iterable, 1, None))


def _py2_round(x):
    # The polyline algorithm uses Python 2's way of rounding
    return int(math.copysign(math.floor(math.fabs(x) + 0.5), x))


def _write(output, value, factor):
    value = _py2_round(value * factor)
    it = value - 0
    it <<= 1
    it = it if it >= 0 else ~it

    while it >= 0x20:
        output.write(chr((0x20 | (it & 0x1f)) + 63))
        it >>= 5

    output.write(chr(it + 63))

def _trans(value, index):
    byte, result, shift = None, 0, 0

    comp = None
    while byte is None or byte >= 0x20:
        byte = ord(value[index]) - 63
        index += 1
        result |= (byte & 0x1f) << shift
        shift += 5
        comp = result & 1

    return ~(result >> 1) if comp else (result >> 1), index

def decode(expression: str, precision: int = 5) -> List[float]:
    """
    Decode a polyline string into a list of floats

    :param expression: Polyline string, e.g. 'u{~vFvyys@fS]'.
    :param precision: Precision of the encoded coordinates. The default value is 5.
    :return: List of decoded floats
    """
    rv, index, length, factor = [], 0, len(expression), float(10 ** precision)

    while index < length:
        change, index = _trans(expression, index)
        rv.append(change / factor)

    return rv

def encode(lat: float, long: float, radius_meters: int, altitude: float = 0.0, precision: int = 5) -> str:
    """encode lat, long, altitude, and radius into a polyline string"""
    rv, factor = io.StringIO(), int(10 ** precision)

    _write(rv, lat, factor)
    _write(rv, long, factor)
    _write(rv, altitude, factor)
    _write(rv, radius_meters / METER_FACTOR, factor)

    return rv.getvalue()
