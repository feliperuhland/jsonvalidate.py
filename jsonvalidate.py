# -*- coding: utf8 -*-
'''Utility function to generate json from a schema.

Scalar values represent that a value of the same type can be generated, in the
integer and float case the value represents the allowed boundaries
'''
import random
import simplejson as json

from multidispatch import multifunction, DispatchError

Any = type('Any', (), {})


class Repeat(object):
    def __init__(self, schema, minimum, maximum):
        self.schema = schema
        self.minimum = minimum
        self.maximum = maximum

    def __hash__(self):
        return 37 * hash(self.schema) * hash(self.minimum) + hash(self.maximum)

    def __repr__(self):
        return 'Repeat({})'.format(self.schema)


class ZeroOrMore(Repeat):
    def __init__(self, schema):
        super(ZeroOrMore, self).__init__(schema, 0, float('inf'))

    def __repr__(self):
        return 'ZeroOrMore({})'.format(self.schema)


class OneOfThese(object):
    def __init__(self, *posibilities):
        self.posibilities = posibilities

    def __hash__(self):
        result = 17

        for value in self.posibilities:
            result *= hash(value)

        return result

    def __repr__(self):
        return 'OneOfThese({})'.format(self.posibilities)


class Optional(object):
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return 'Optional({})'.format(self.value)


class Error(object):
    def __init__(self, erro):
        self.erro = erro

    # Error is always falsy
    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

    def __repr__(self):
        return 'Error({})'.format(self.erro)


def validate_json(jsonstring, schema):
    try:
        data = json.loads(jsonstring)
    except:
        return Error('invalid json')

    try:
        return is_valid(data, schema)
    except DispatchError as e:
        # XXX: improve this
        data_type = e.message[e.message.find('(')+1:e.message.find(',')]
        expected_type = e.message[e.message.find(',')+2:e.message.find(')')]

        return Error('excpected type {} got {}'.format(expected_type, data_type))


def validate_type(data, schema):
    if schema in (dict, set, list):
        return Error('invalid schema: {} has no meaning, use a instance of this type'.format(schema))

    # raw types: bool, int, float, etc.
    if type(data) is not schema:
        return Error('excpected type {} got {}'.format(schema, type(data)))

    return True


def validate_list(data, schema):
    if len(schema) != 1:
        return Error('invalid schema: list must have one value')

    # validate every sub element with the same schema
    subschema = schema[0]

    for value in data:
        error = is_valid(value, subschema)

        if not error:
            return error

    return True


def validate_tuple(data, schema):
    if len(data) != len(schema):
        return Error('wrong number of arguments, expected {} got {}'.format(len(schema), len(data)))

    for subdata, subschema in zip(data, schema):
        error = not is_valid(subdata, subschema)

        if error:
            return error

    return True


def validate_dict(data, schema):
    unknow = set(data.keys()) - set(key.value if isinstance(key, Optional) else key for key in schema.keys())
    if unknow:
        return Error('unknow keys: {}'.format(unknow))

    required = set(key for key in schema.keys() if not isinstance(key, Optional)) - set(data.keys())
    if required:
        return Error('missing required keys: {}'.format(required))

    for key, subschema in schema.items():
        optional = isinstance(key, Optional)
        key = key.value if optional else key

        if key in data:
            error = is_valid(data[key], subschema)

            if not error:
                return error
        elif not optional:
            return Error('missing required key: {}'.format(key))

    return True


def validate_any(data, schema):
    return True


def validate_optional(data, schema):
    if data is None:
        return True

    try:
        return is_valid(data, schema.value)
    except DispatchError:
        return Error('{} is not a valid {}'.format(data, schema.value))


def validate_oneofthese(data, schema):
    for subschema in schema.posibilities:
        try:
            if is_valid(data, subschema):  # stop at the first
                return True
        except DispatchError:
            pass

    list_types = [getattr(type_, '__name__', str(type_)) for type_ in schema.posibilities]
    return Error('value must be one of these types: {}'.format(list_types))


def validate_set(data, schema):
    # validate_set is a short-cut
    return validate_oneofthese(data, OneOfThese(*schema))


def validate_repeat(data, schema):
    if schema.maximum < len(data) < schema.minimum:
        return Error('wrong number of elements, must be {}<x<{}'.format(schema.minimum, schema.maximum))

    subschema = schema.schema
    return all(is_valid(subdata, subschema) for subdata in data)


def generate_bool(schema):
    return random.choice((True, False))


def generate_none(schema):
    return None


def generate_int(schema):
    '''integers and floats are used as lower/upper boundary'''
    return random.randint(-schema, schema)


def generate_float(schema):
    return random.uniform(-schema, schema)


def generate_type(schema):
    if schema is int:
        return random.randint(-10000, 10000)

    if schema is float:
        random.uniform(-10000.0, 10000.0)

    if schema is bool:
        return random.choice((True, False))

    if schema is None:
        return None


def generate_set(schema):
    '''sets represents possible types'''
    return generate(random.choice(schema))


def generate_list(schema):
    '''lists have zero or more repetitions of the types it contains (in order)'''
    return [
        generate(subschema)
        for subschema in schema * random.randint(0, 10)
    ]


def generate_tuple(schema):
    '''tuples represent fixed size lists with each element type defined'''
    return [generate(subschema) for subschema in schema]


def generate_dict(schema):
    '''dicts represents objects'''
    return dict(
        (key, generate(subschema))
        for (key, subschema) in schema.items()
    )

is_valid = multifunction.new(
    'validate',
    doc='validate data following schema, stop on the first error, erros are reported with a Error instance',
)
generate_scalar = multifunction.new(
    'generate_scalar',
    doc='generate random data for a given schema',
)

is_valid[object, type] = validate_type
is_valid[object, Any] = validate_any
is_valid[object, Optional] = validate_optional
is_valid[object, Repeat] = validate_repeat
is_valid[object, OneOfThese] = validate_oneofthese
is_valid[object, set] = validate_set

is_valid[dict, dict] = validate_dict
is_valid[list, list] = validate_list
is_valid[list, tuple] = validate_tuple

generate_scalar[bool] = generate_bool
generate_scalar[None] = generate_none
generate_scalar[int] = generate_int
generate_scalar[float] = generate_float

generate = multifunction.new('generate')
generate[type] = generate_type
generate[set] = generate_set
generate[list] = generate_list
generate[tuple] = generate_tuple
generate[tuple] = generate_dict
