'''Test the hashable, equable, canonical regimen data object'''

import decimal
import unittest

import pypeg2 as pp

import shared_schema.regimens.grammar as rg
import shared_schema.regimens.regimen as regimen


# ---------------------------------------------------------------------
# Helpers

def methods_exist(obj):
    '''Verify that __eq__ and __hash__ exist on an object'''
    method_names = ('__eq__', '__hash__')
    obj_methods = dir(obj)
    msg = "Expected '{}' to have {} method"
    msg.format(obj, ", ".join(method_names))
    return (all(nm in obj_methods for nm in method_names), msg)


def equivalent(a, b):
    '''Verify that two objects are equal and have the same hash'''
    if a != b:
        msg = "Expected {} == {}"
        return (False, msg.format(a, b))
    if hash(a) != hash(b):
        msg = "Expected hash({}) == hash({})"
        return (False, msg.format(a, b))
    return True, ""


def parse_from_source(src, grammar_node):
    grammar_obj = pp.parse(src, grammar_node)
    parsed = regimen.parse(grammar_obj)
    return parsed


# ---------------------------------------------------------------------
# Example Data
dcv_dose = regimen._dose(amount=decimal.Decimal(1), compound='DCV')
sof_dose = regimen._dose(amount=decimal.Decimal(2), compound='SOF')
boc_dose = regimen._dose(amount=decimal.Decimal(3), compound='BOC')

duration_12wks = decimal.Decimal(12 * 7)
duration_24wks = decimal.Decimal(24 * 7)


# ---------------------------------------------------------------------
# Test Cases

class TestParsingCompoundObjects(unittest.TestCase):

    def test_dose(self):
        src = "1mg DCV"
        parsed = parse_from_source(src, rg.Dose)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(parsed, dcv_dose)

    def test_indication(self):
        src = "1mg DCV + 2mg SOF QD"
        parsed = parse_from_source(src, rg.Indication)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            regimen._indication(
                frequency="QD",
                doselist=frozenset([dcv_dose, sof_dose]),
            ),
        )

    def test_regimenpart(self):
        src = "2mg SOF QD 12 weeks"
        parsed = parse_from_source(src, rg.RegimenPart)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            regimen._regimen_part(
                duration=duration_12wks,
                drug_combination=frozenset([
                    regimen._indication(
                        frequency='QD',
                        doselist=frozenset([sof_dose]),
                    )
                ]),
            )
        )


class TestParsingCollections(unittest.TestCase):

    def test_doselist_parses(self):
        src = "1mg DCV + 3mg BOC"
        parsed = parse_from_source(src, rg.DoseList)
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset([dcv_dose, boc_dose]),
        )

    def test_doselist_canonical(self):
        dl1 = parse_from_source("2mg DCV", rg.DoseList)
        dl2 = parse_from_source("1mg DCV + 1mg DCV", rg.DoseList)
        self.assertTrue(*methods_exist(dl1))
        self.assertTrue(*methods_exist(dl2))
        self.assertTrue(*equivalent(dl1, dl2))

    def test_drugcombination(self):
        parsed = parse_from_source(
            "1mg DCV QD & 3mg BOC TID",
            rg.DrugCombination,
        )
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset([
                regimen._indication(
                    doselist=frozenset([dcv_dose]),
                    frequency="QD",
                ),
                regimen._indication(
                    doselist=frozenset([boc_dose]),
                    frequency="TID",
                ),
            ]),
        )

    def test_regimen(self):
        parsed = parse_from_source(
            "(1mg DCV + 2mg SOF) QD 12 week, 3mg BOC QD 24 weeks",
            rg.Regimen,
        )
        self.assertIsInstance(parsed, frozenset)
        self.assertTrue(*methods_exist(parsed))
        self.assertEqual(
            parsed,
            frozenset([
                regimen._regimen_part(
                    duration=duration_12wks,
                    drug_combination=frozenset([
                        regimen._indication(
                            frequency='QD',
                            doselist=frozenset([dcv_dose, sof_dose]),
                        )
                    ]),
                ),
                regimen._regimen_part(
                    duration=duration_24wks,
                    drug_combination=frozenset([
                        regimen._indication(
                            frequency='QD',
                            doselist=frozenset([boc_dose]),
                        )
                    ]),
                )
            ]),
        )


class TestMonoidalOperations(unittest.TestCase):

    # NOTE(nknight): Skip testing regimen.key, as it's just an accessor

    dose_a1 = regimen._dose(amount=1, compound='test')
    dose_a2 = regimen._dose(amount=2, compound='test')
    dose_b1 = regimen._dose(amount=1, compound='other test')

    druglist_a = frozenset([dose_a1])
    druglist_b = frozenset([dose_b1])
    druglist_ab = frozenset([dose_a1, dose_b1])

    def test_dose_add(self):
        self.assertEqual(
            regimen.add(self.dose_a1, self.dose_a2),
            regimen._dose(amount=3, compound='test'),
        )
        with self.assertRaises(ValueError):
            regimen.add(self.dose_a1, self.dose_b1)

    def test_dose_consolidating_insert(self):
        xs = frozenset([self.dose_a1, self.dose_b1])
        new_xs = regimen.consolidating_insert(xs, self.dose_a1)
        self.assertEqual(
            new_xs,
            frozenset([
                regimen._dose(amount=2, compound='test'),
                self.dose_b1
            ]),
        )

    def test_indication_consolidating_insert(self):
        self.assertEqual(
            regimen.consolidating_insert(
                self.druglist_a,
                self.dose_b1,
            ),
            self.druglist_ab,
        )
        self.assertEqual(
            regimen.consolidating_insert(
                self.druglist_a,
                self.dose_a1,
            ),
            frozenset([self.dose_a2]),
        )
        self.assertEqual(
            regimen.consolidating_insert(
                self.druglist_ab,
                self.dose_a1,
            ),
            frozenset([self.dose_a2, self.dose_b1]),
        )
