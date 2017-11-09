'''This module contains a parser for regimen descriptions.

It turns a terse regimen description into structured data, suitable for
analysis or creating database records.

The grammar it parses is as follows:

    Regimen         <- RegimenPart ("," RegimenPart)*
    RegimenPart     <- DrugCombination Duration
    Duration        <- Number TimeUnit
    TimeUnit        <- "day" | "days" | "week" | "weeks"
    DrugCombination <-  Indication ("&" Indication)*
    Indication      <- DoseList Frequency
    Frequency       <- "QD" | "BID" | "TID" | "QID" | "QWK"
    DoseList        <- "("? Dose ("+" Dose)* ")"?
    Dose            <- Amount Compound
    Amount          <- Number "mg"
    Compound        <- "ASV" | "BOC" ...
    Number          <- Digit* "." Digit+ | Digit+
    Digit           <- "1" | "2" | "3" | "4" | "5"
                      | "6" | "7" | "8" | "9" | "0"

Example regimens:

    400mg SOF QD 12 weeks
    (200mg DCV + 100mg PEG) TID 2 days
    1000mg BOC QD 2 weeks, 100mg ASV 3 days
    (1mg SOF + 2mg SOF) QID 3 weeks, (4mg DCV TID + 5mg BOC) BID 6 weeks
'''

import decimal
import re

import pypeg2 as pp


_freqs = ['QD', 'BID', 'TID', 'QID', 'QWK']


class Frequency(pp.Keyword):
    grammar = pp.Enum(*[pp.Keyword(f) for f in _freqs])


_compounds = ["ASV", "BOC", "DCV", "DAS", "EBR", "GLP", "GZR", "LDV", "OMB",
              "PAR", "PEG", "PIB", "RBV", "RIT", "SIM", "SOF", "TVR", "VAN",
              "VEL", "VOX", ]


class Compound(pp.Keyword):
    grammar = pp.Enum(*[pp.Keyword(c) for c in _compounds])


class Number(pp.RegEx):
    grammar = re.compile(r"\d*\.\d+|\d+")

    def __eq__(self, other):
        type_matches = isinstance(other, type(self))
        if type_matches:
            a = decimal.Decimal(self.pattern)
            b = decimal.Decimal(other.pattern)
            return a == b
        else:
            return False

    @property
    def amount(self):
        return decimal.Decimal(self.pattern)


class Amount(pp.Concat):
    grammar = Number, "mg"

    @property
    def milligrams(self):
        number = self[0]
        if '.' in number.pattern:
            return decimal.Decimal(number.pattern)
        else:
            return int(number.pattern)

    def __eq__(self, other):
        type_matches = isinstance(other, type(self))
        if type_matches:
            return self.milligrams == other.milligrams
        else:
            return False

    @classmethod
    def of(cls, n):
        return cls([Number(str(n))])


class Dose(pp.Concat):
    # explicitly require a space between amount and compound because pypeg2's
    # automatic whitespace removal will allow the space to be omitted
    grammar = pp.contiguous(Amount, " ", Compound)


class DoseList(pp.List):
    grammar = (
        pp.optional("("),
        pp.csl(Dose, separator='+'),
        pp.optional(")"),
    )


class Indication(pp.Concat):
    grammar = DoseList, Frequency


_time_units = ['day', 'days', 'week',  'weeks']


class TimeUnit(pp.Keyword):
    grammar = pp.Enum(*[pp.Keyword(u) for u in _time_units])

    @property
    def _normed(self):
        if self.name.startswith('day'):
            return 'day'
        elif self.name.startswith('week'):
            return 'week'
        else:
            msg = "Unexpected timeunit: {}".format(self.name)
            raise SyntaxError(msg)

    def __eq__(self, other):
        type_matches = isinstance(other, type(self))
        if type_matches:
            return self._normed == other._normed
        else:
            return False

    def __hash__(self):
        return hash(self._normed)


class Duration(pp.Concat):
    grammar = Number, TimeUnit

    @property
    def days(self):
        num = self[0]
        unit = self[1]
        if unit.name.startswith('day'):
            return num.amount
        elif unit.name.startswith('week'):
            return num.amount * 7
        else:
            msg = "Unexpected timeunit value: {}".format(unit.name)
            raise SyntaxError(msg)

    def __eq__(self, other):
        type_matches = isinstance(other, type(self))
        if type_matches:
            return self.days == other.days
        else:
            return False


class DrugCombination(pp.List):
    grammar = pp.csl(Indication, separator="&")


class RegimenPart(pp.Concat):
    grammar = DrugCombination, Duration


class Regimen(pp.List):
    grammar = pp.csl(RegimenPart, separator=",")


def parse(regimen):
    return pp.parse(regimen, Regimen)
