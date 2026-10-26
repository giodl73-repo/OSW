"""Compare browser JSON values while keeping booleans distinct from numbers."""
import math
import eicc_reference_query_v1 as context


def normalized(value):
    if type(value) is float:
        if not math.isfinite(value): raise ValueError('Nonfinite browser evidence value')
        return int(value) if value.is_integer() else value
    if isinstance(value, list): return [normalized(item) for item in value]
    if isinstance(value, dict): return {key: normalized(item) for key, item in value.items()}
    return value


def same(actual, expected):
    return context.encoded(normalized(actual)) == context.encoded(normalized(expected))
