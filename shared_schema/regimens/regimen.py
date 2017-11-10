'''A hashable, eq'able, canonical representation of drug regimens'''
import collections
import decimal
import functools

from . import grammar

# NOTE(nknight): We don't consider grammar.TimeUnit or grammar.Number
# because we canonicalise the things that contain them direcly
# (Durations and Amounts); they're required for parsing, but don't
# contain extra information.


# ---------------------------------------------------------------------
# Helpers

def types_match(f):
    "Ensures that the types of the decorated binary function's arguments match"
    @functools.wraps(f)
    def wrapped(x, y):
        if type(x) is not type(y):
            msg = "Can't combine '{}' and '{}"
            raise ValueError(msg.format(x, y))
        return f(x, y)
    return wrapped


# ---------------------------------------------------------------------
# Canonicalizing Collections
'''These functions operate on collections and objects that can
*sometimes* be consolidated, e.g. Doses of the same compound.

- `key` accesses the attribute of an object that must match in order
  to consolidate
- `add` combines to objects that can be consolidated
'''

_dose = collections.namedtuple('Dose', ['amount', 'compound'])
_indication = collections.namedtuple('Indication', ['doselist', 'frequency'])
_regimen_part = collections.namedtuple(
    'RegimenPart',
    ['drug_combination', 'duration'],
)


@functools.singledispatch
def key(x):
    '''Consolidatable types with the same key can be consolidated.

    E.g: For a Dose, the key is the compound type. Doses of the same
    compound can be consolidated, but doses of different compounds
    must be kept separate.
    '''
    msg = "key: {}"
    raise NotImplemented(msg.format(x))


@functools.singledispatch
def add(x, other):
    '''Binary operation for combining two consolidatable types that have
    the same key.

    E.g: For two Doses with the same compound, return a new dose with
    the same compound, adding the amounts together.
    '''
    msg = "add: {}"
    raise NotImplemented(msg.format(x))


# TODO(nknight): Hypothesis testing for this function's postconditions:
#  - each `key` value is unique
#  - total for each `key` is the same before and after
#  - etc.

def consolidating_insert(collection, newobj):
    '''Insert an object into a collection, consolidating if possible.

    Implemented in terms of `key` and `add` and iterability of
    collection.

    Returns a new collection (specifically, a frozenset) of objects
    with the given newobj added. If any objects in this new collection
    have a `key` value that matches newobj, they will all be
    consolidated in the new collection.

    The collection should contain only instances of the same class as
    newobj.
    '''
    maybe_obj = next(iter(collection), None)
    if maybe_obj is not None:
        if type(maybe_obj) is not type(newobj):
            msg = "Can't insert {} into a set of {}"
            raise ValueError(msg.format(newobj, maybe_obj))
    matches = [obj for obj in collection if key(obj) == key(newobj)]
    others = [obj for obj in collection if key(obj) != key(newobj)]
    consolidated = functools.reduce(add, matches, newobj)
    return frozenset([consolidated] + others)


def consolidating_merge(xs, ys):
    return functools.reduce(consolidating_insert, xs, ys)


def consolidate(xs):
    return consolidating_merge(xs, [])


@key.register(_dose)
def _(dose):
    return dose.compound


@add.register(_dose)
@types_match
def _(dose, other):
    if key(dose) != key(other):
        msg = "Can't add doses of different compounds: {} + {}"
        raise ValueError(msg.format(dose, other))
    return _dose(
        compound=dose.compound,
        amount=dose.amount + other.amount,
    )


@key.register(_indication)
def _(indication):
    return indication.frequency


@add.register(_indication)
@types_match
def _(indication, other):
    if key(indication) != key(other):
        msg = "Can't add indications of different frequencies: {} + {}"
        raise ValueError(msg.format(indication, other))
    new_doselist = consolidating_merge(indication.doselist, other.doselist)
    return _indication(
        doselist=new_doselist,
        frequency=indication.frequency,
    )


@key.register(_regimen_part)
def _(regimen_part):
    return regimen_part.duration


@add.register(_regimen_part)
@types_match
def _(regimen_part, other):
    if key(regimen_part) != key(other):
        msg = "Can't add regimen parts with different durations: {} + {}"
        raise ValueError(msg.format(regimen_part, other))
    new_drug_combination = consolidating_merge(
        regimen_part.drug_combination,
        other.drug_combination,
    )
    return _regimen_part(
        duration=regimen_part.duration,
        drug_combination=new_drug_combination,
    )


# ---------------------------------------------------------------------
# Converter

@functools.singledispatch
def parse(src):
    '''Parse a grammar object into a hashable, eq'able object

    This multi-method should turn each node that's parsed by the
    regimen grammar into a tuple or frozenset of builtin scalar
    datatypes. This ensures that two identical regimens will parse to
    the same object, even when they're expressed differently.
    '''
    msg = "Unhandled object of type '{} : '{}'"
    raise ValueError(msg.format(type(src), src))


@parse.register(grammar.Frequency)
def _(src):
    return str(src)


@parse.register(grammar.Compound)
def _(src):
    return str(src)


@parse.register(grammar.Amount)
def _(src):
    return src.milligrams


@parse.register(grammar.Dose)
def _(src):
    amount, compound = src
    return _dose(amount=parse(amount), compound=parse(compound))


@parse.register(grammar.DoseList)
def _(src):
    doses = [parse(dose) for dose in src]
    return frozenset(consolidate(doses))


@parse.register(grammar.Indication)
def _(src):
    doselist, frequency = src
    return _indication(
        doselist=parse(doselist),
        frequency=parse(frequency),
    )


@parse.register(grammar.Duration)
def _(src):
    days = src.days
    return decimal.Decimal(days)


@parse.register(grammar.DrugCombination)
def _(src):
    indications = consolidate(parse(ind) for ind in iter(src))
    return frozenset(indications)


@parse.register(grammar.RegimenPart)
def _(src):
    drug_combination, duration = src
    return _regimen_part(
        drug_combination=parse(drug_combination),
        duration=parse(duration),
    )


@parse.register(grammar.Regimen)
def _(src):
    parts = consolidate(parse(part) for part in iter(src))
    return frozenset(parts)


# ---------------------------------------------------------------------

class Regimen(object):
    '''A hashable, eq'able object representing a drug regimen.'''

    def __init__(self):
        pass

    def __hash__(self):
        pass

    @classmethod
    def from_grammar_object(cls, grammar_obj):
        return parse(grammar_obj)
