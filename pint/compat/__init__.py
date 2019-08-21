# -*- coding: utf-8 -*-
"""
    pint.compat
    ~~~~~~~~~~~

    Compatibility layer.

    :copyright: 2013 by Pint Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import sys

import warnings
from io import BytesIO
from numbers import Number
from decimal import Decimal

from . import tokenize

ENCODING_TOKEN = tokenize.ENCODING

PYTHON3 = sys.version >= '3'

def tokenizer(input_string):
    for tokinfo in tokenize.tokenize(BytesIO(input_string.encode('utf-8')).readline):
        if tokinfo.type == ENCODING_TOKEN:
            continue
        yield tokinfo


if PYTHON3:
    string_types = str

    def u(x):
        return x

    maketrans = str.maketrans

    long_type = int
else:
    string_types = basestring

    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]

    maketrans = lambda f, t: dict((ord(a), b) for a, b in zip(f, t))

    long_type = long

try:
    from collections import Chainmap
except ImportError:
    from .chainmap import ChainMap

try:
    from functools import lru_cache
except ImportError:
    from .lrucache import lru_cache

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

# TODO: remove this warning after v0.10
class BehaviorChangeWarning(UserWarning):
    pass
_msg = ('The way pint handles numpy operations has changed with '
'the implementation of NEP 18. Unimplemented numpy operations '
'will now fail instead of making assumptions about units. Some '
'functions, eg concat, will now return Quanties with units, '
'where they returned ndarrays previously. See '
'https://github.com/hgrecco/pint/pull/764. '
'To hide this warning use the following code to import pint:'
"""

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pint

To disable the new behavior, see
https://www.numpy.org/neps/nep-0018-array-function-protocol.html#implementation
---    
""")

try:
    import numpy as np
    from numpy import ndarray

    HAS_NUMPY = True
    NUMPY_VER = np.__version__
    NUMERIC_TYPES = (Number, Decimal, ndarray, np.number)
    
    if "dev" in NUMPY_VER:
        NUMPY_VER = NUMPY_VER[:NUMPY_VER.index("dev")-1]

    def _to_magnitude(value, force_ndarray=False):
        if isinstance(value, (dict, bool)) or value is None:
            raise TypeError('Invalid magnitude for Quantity: {0!r}'.format(value))
        elif isinstance(value, string_types) and value == '':
            raise ValueError('Quantity magnitude cannot be an empty string.')
        elif isinstance(value, (list, tuple)):
            return np.asarray(value)
        if force_ndarray:
            return np.asarray(value)
        return value

    def _test_array_function_protocol():
        # Test if the __array_function__ protocol is enabled
        try:
            class FakeArray:
                def __array_function__(self, *args, **kwargs):
                    return

            np.concatenate([FakeArray()])
            return True
        except ValueError:
            return False

    HAS_NUMPY_ARRAY_FUNCTION = _test_array_function_protocol()

    if HAS_NUMPY_ARRAY_FUNCTION:
        warnings.warn(_msg, BehaviorChangeWarning)

except ImportError:

    np = None

    class ndarray(object):
        pass

    HAS_NUMPY = False
    NUMPY_VER = '0'
    NUMERIC_TYPES = (Number, Decimal)
    HAS_NUMPY_ARRAY_FUNCTION = False

    def _to_magnitude(value, force_ndarray=False):
        if isinstance(value, (dict, bool)) or value is None:
            raise TypeError('Invalid magnitude for Quantity: {0!r}'.format(value))
        elif isinstance(value, string_types) and value == '':
            raise ValueError('Quantity magnitude cannot be an empty string.')
        elif isinstance(value, (list, tuple)):
            raise TypeError('lists and tuples are valid magnitudes for '
                             'Quantity only when NumPy is present.')
        return value

try:
    from uncertainties import ufloat
    HAS_UNCERTAINTIES = True
except ImportError:
    ufloat = None
    HAS_UNCERTAINTIES = False

try:
    from babel import Locale as Loc
    from babel import units as babel_units
    HAS_BABEL = True
    HAS_PROPER_BABEL = hasattr(babel_units, 'format_unit')
except ImportError:
    HAS_PROPER_BABEL = HAS_BABEL = False

if not HAS_PROPER_BABEL:
    Loc = babel_units = None

try:
    import pandas as pd
    HAS_PANDAS = True
    # pin Pandas version for now
    HAS_PROPER_PANDAS = pd.__version__.startswith("0.25")
except ImportError:
    HAS_PROPER_PANDAS = HAS_PANDAS = False

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
