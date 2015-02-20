# -*- coding: utf8 -*-
from decimal import Decimal

import pytest
from jsonvalidate import is_valid, Any, DispatchError, Optional, ZeroOrMore, OneOfThese


def test_schema_with_single_type():
    msg = 'the schema can use a type to define the category of values that are allowed'
    assert is_valid(1, int), msg
    assert is_valid(1.0, float), msg
    assert is_valid(Decimal(), Decimal), msg
    assert is_valid('', str), msg
    assert is_valid('str', str), msg


def test_type_schema():
    msg = 'cant use compound types as schema'
    assert not is_valid({}, dict), msg
    assert not is_valid([], list), msg
    assert not is_valid(set(), set), msg


def test_type_objects():
    assert not is_valid(int, {int, float, dict, Decimal})
    assert not is_valid(int, {int, float})
    assert not is_valid(int, set())

    assert not is_valid(float, {int, float, dict, Decimal})
    assert not is_valid(float, {int, float})
    assert not is_valid(float, set())

    assert not is_valid(list, {int, float, dict, Decimal})
    assert not is_valid(list, {int, float})
    assert not is_valid(list, set())

    assert not is_valid(dict, {int, float, dict, Decimal})
    assert not is_valid(dict, {int, float})
    assert not is_valid(dict, set())

    assert not is_valid(Decimal, {int, float, dict, Decimal})
    assert not is_valid(Decimal, {int, float})
    assert not is_valid(Decimal, set())


def test_is_valid_value_of_different_type():
    msg = 'a value of a different type is not valid'
    assert not is_valid(1.0, int), msg
    assert not is_valid(Decimal(), int), msg
    assert not is_valid('', int), msg
    assert not is_valid('str', int), msg
    assert not is_valid(1, float), msg
    assert not is_valid(Decimal(), float), msg
    assert not is_valid('', float), msg
    assert not is_valid('str', float), msg
    assert not is_valid(1, Decimal), msg
    assert not is_valid(1.0, Decimal), msg
    assert not is_valid('', Decimal), msg
    assert not is_valid('str', Decimal), msg
    assert not is_valid(1, str), msg
    assert not is_valid(1.0, str), msg
    assert not is_valid(Decimal(), str), msg


def test_any_accepts_any_value():
    msg = 'Any() must accept any value'
    assert is_valid(None, Any()), msg
    assert is_valid(1, Any()), msg
    assert is_valid(1.0, Any()), msg
    assert is_valid(True, Any()), msg
    assert is_valid([], Any()), msg
    assert is_valid({}, Any()), msg
    assert is_valid(object(), Any()), msg
    assert is_valid(object, Any()), msg


def test_optional():
    msg = 'Optional() must accept None'
    assert is_valid(None, Optional(int)), msg
    assert is_valid(None, Optional(float)), msg
    assert is_valid(None, Optional({})), msg

    msg = 'Optional() must accept the intend value'
    assert is_valid(1, Optional(int)), msg
    assert is_valid(1.0, Optional(float)), msg
    assert is_valid({}, Optional({})), msg

    msg = 'Optional() must reject values of the wrong type'
    assert not is_valid({1: None}, Optional({})), msg
    assert not is_valid({'1': None}, Optional({})), msg
    assert not is_valid({None: None}, Optional({})), msg
    assert not is_valid(1.0, Optional(int)), msg
    assert not is_valid('1', Optional(int)), msg
    assert not is_valid({1: 1}, Optional(int)), msg
    assert not is_valid([1], Optional(int)), msg
    assert not is_valid(1, Optional(float)), msg
    assert not is_valid('1', Optional(float)), msg
    assert not is_valid({1: 1}, Optional(float)), msg
    assert not is_valid([1], Optional(float)), msg
    assert not is_valid(1, Optional({})), msg
    assert not is_valid('1', Optional({})), msg
    assert not is_valid({1: 1}, Optional({})), msg
    assert not is_valid([1], Optional({})), msg


def test_one_of_these():
    '''One of these allow any of the given values to be used, it can be represented with a set'''
    assert is_valid(1, {int}) == is_valid(1, int)
    assert is_valid(1.0, {float}) == is_valid(1.0, float)
    assert is_valid(Decimal('1'), {Decimal}) == is_valid(Decimal('1'), Decimal)

    assert is_valid(1, OneOfThese(int, float, {}))
    assert is_valid(1.0, OneOfThese(int, float, {}))

    assert not is_valid(1, OneOfThese(float, {}))
    assert not is_valid(1.0, OneOfThese(int, {}))

    assert not is_valid(None, set())
    assert not is_valid(1, set())
    assert not is_valid(1.0, set())


def test_set_complex():
    '''complex types can be nested within the sets'''
    assert is_valid([1, 2, 3], {ZeroOrMore(int), ZeroOrMore(float)})
    assert is_valid([1.0, 2.0, 3.0], {ZeroOrMore(int), ZeroOrMore(float)})
    assert is_valid([1, 2.0, Decimal('1')], [{int, float, Decimal}])

    assert not is_valid([1.0, 2.0, 3.0], {ZeroOrMore(int)})
    assert not is_valid([1, 2, 3], {ZeroOrMore(float)})
    assert not is_valid([1.0, 2, 3.0], {ZeroOrMore(int), ZeroOrMore(float)})
    assert not is_valid([1, 2.0, Decimal('1')], [{float, Decimal}])
    assert not is_valid([1, 2.0, Decimal('1')], [{int, Decimal}])
    assert not is_valid([1, 2.0, Decimal('1')], [{int, float}])


def test_dict():
    with pytest.raises(DispatchError):
        is_valid({}, [])

    assert is_valid({}, {})

    assert not is_valid({'a': 1}, {})
    assert not is_valid({'a': 1, 'b': 2}, {'a': int})
    assert not is_valid({'a': 1, 'b': 2}, {'b': int})


def test_dict_optional():
    assert is_valid(None, Optional({})), 'Optional() must accept None'
    assert is_valid({}, Optional({})), 'Optional() must accept None'

    assert is_valid({}, {Optional('a'): int}), 'Optional() can be used in dictionary keys'
    assert is_valid({'a': 1}, {Optional('a'): int}), 'Optional() can be used in dictionary keys'

    assert is_valid({}, {Optional('a'): Optional(int)}), 'Optional() can be used in dictionary keys'
    assert is_valid({'a': None}, {Optional('a'): Optional(int)}), 'Optional() can be used in dictionary keys'
    assert is_valid({'a': 1}, {Optional('a'): Optional(int)}), 'Optional() can be used in dictionary keys'

    assert not is_valid({'a': None}, {Optional('a'): int}), 'An optional *key* does not make a value optinal'
    assert not is_valid({}, {'a': Optional(int)}), 'An optional *value* does not make a key optinal'


def test_list():
    msg = 'list must have one value'
    assert not is_valid([], []), msg

    assert is_valid([1], [int])
    assert is_valid([1, 2, 3, 4], [int])

    assert is_valid([1.0], [float])
    assert is_valid([1.0, 2.0, 3.0, 4.0], [float])
    assert is_valid([1, 2.0, 3.0, 4], [{int, float}])

    msg = 'list are zero or more itens'
    assert is_valid([], [int]), msg
    assert is_valid([], [float]), msg
    assert is_valid([], [{}]), msg
    assert is_valid([], [None]), msg
    assert is_valid([], [set()]), msg
