import unittest

import pypeg2 as pp

import shared_schema.regimens.grammar as rg


def check_parser_good_cases(test_case, parser, cases):
    for case in cases:
        test_case.assertEqual(
            pp.parse(case, parser),
            parser(case),
            "Parsed and constructed objects don't match",
        )


def check_parser_bad_cases(test_case, parser, cases, exc=SyntaxError):
    for case in cases:
        with test_case.assertRaises(exc):
            pp.parse(case, parser)


class TestNumber(unittest.TestCase):

    def test_rich_equality(self):
        self.assertEqual(
            rg.Number('1'),
            rg.Number('1'),
        )

        class DummyOne(object):
            pattern = '1'

        not_equals = [1, '1', DummyOne()]

        for n in not_equals:
            self.assertNotEqual(rg.Number('1'), n)

    good_cases = ['1', '2', '1.5', '0.3', '.9']
    bad_cases = ['1.2.3', 'a', '1.a', '1.6e3', '-1']

    def test_parsing_numbers(self):
        check_parser_good_cases(self, rg.Number, self.good_cases)

    def test_parsing_not_numbers(self):
        check_parser_bad_cases(self, rg.Number, self.bad_cases)


class TestAmount(unittest.TestCase):

    good_cases = ['1', '200', '3.5', '.7']

    def test_good_cases(self):
        for case in self.good_cases:
            src = case + 'mg'
            parsed = pp.parse(src, rg.Amount)
            constructed = rg.Amount.of(case)
            self.assertEqual(
                parsed,
                constructed,
                "Parsed and constructed Numbers don't match",
            )
            self.assertEqual(
                parsed.milligrams,
                float(case),
                "Expected amount.milligrams to be {}".format(case),
            )

    bad_cases = ['150', '120ug', '150kg' '150 mg']

    def test_bad_units(self):
        check_parser_bad_cases(self, rg.Amount, self.bad_cases)

    def test_rich_equality(self):
        self.assertEqual(rg.Amount.of(100), rg.Amount.of(100.0))
        not_equals = [100, '100']
        for n in not_equals:
            self.assertNotEqual(n, rg.Amount.of(100))


class TestDose(unittest.TestCase):

    good_cases = [
        ('100mg SOF', rg.Dose([rg.Amount.of(100), rg.Compound('SOF')])),
        ('200mg DCV', rg.Dose([rg.Amount.of(200), rg.Compound('DCV')])),
    ]

    def test_good_case(self):
        for src, expected in self.good_cases:
            parsed = pp.parse(src, rg.Dose)
            self.assertEqual(parsed, expected)


class TestIndication(unittest.TestCase):

    good_cases = [
        ("100mg DCV QID", [[('100', 'DCV')], 'QID']),
        ("1mg SOF + 2mg DCV TID", [[('1', 'SOF'), ('2', 'DCV')], 'TID']),
    ]

    def test_good_cases(self):
        for src, (doses, freq) in self.good_cases:
            parsed = pp.parse(src, rg.Indication)

            drug_list = rg.DoseList([
                rg.Dose([rg.Amount.of(d), rg.Compound(c)])
                for d, c in doses
            ])
            expected = rg.Indication([drug_list, rg.Frequency(freq)])

            self.assertEqual(parsed, expected)

    bad_cases = ["100 DCV QD", "100mgDCV QID", "100mg DCV FFF"]

    def test_bad_cases(self):
        for src in self.bad_cases:
            with self.assertRaises(SyntaxError):
                pp.parse(src, rg.Indication)


class TestDuration(unittest.TestCase):

    in_days_cases = [
        ('12 days', 12),
        ('2 weeks', 14),
        ('1 day', 1),
        ('1 week', 7),
    ]

    def test_duration_in_days(self):
        for src, expected in self.in_days_cases:
            duration = pp.parse(src, rg.Duration)
            self.assertEqual(duration.days, expected)

    equal_cases = [
        ('1 week', '7 days'),
        ('2 weeks', '14 days'),
        ('7 day', '1 week'),
    ]

    def test_equality(self):
        for src_left, src_right in self.equal_cases:
            left = pp.parse(src_left, rg.Duration)
            right = pp.parse(src_right, rg.Duration)
            self.assertEqual(
                left,
                right,
                'Same durations in days & weeks not equal',
            )


class TestTimeUnit(unittest.TestCase):

    match_cases = [
        ('day', 'day'),
        ('day', 'days'),
        ('week', 'week'),
        ('week', 'weeks'),
    ]

    not_match_cases = [
        ('day', 'week'),
        ('weeks', 'days'),
    ]

    def test_equality(self):
        for x, y in self.match_cases:
            tu_x = rg.TimeUnit(x)
            tu_y = rg.TimeUnit(y)
            self.assertEqual(tu_x, tu_y)
        for x, y in self.not_match_cases:
            tu_x = rg.TimeUnit(x)
            tu_y = rg.TimeUnit(y)
            self.assertNotEqual(tu_x, tu_y)


class TestDrugCombination(unittest.TestCase):

    cases = [
        ('1mg DCV BID', rg.DrugCombination([
            pp.parse('1mg DCV BID', rg.Indication)
        ])),
        ('(1mg SOF QD & 2mg DCV + 3mg GLP) TID', rg.DrugCombination([
            pp.parse('1mg SOF QD', rg.Indication),
            pp.parse('2mg DCV + 3mg GLP TID', rg.Indication),
        ])),
    ]

    def test_parsing_works_as_expected(self):
        for src, expected in self.cases:
            parsed = pp.parse(src, rg.DrugCombination)
            self.assertEqual(parsed, expected)


class TestRegimen(unittest.TestCase):

    def test_simple_parsing(self):
        src = "1mg SOF QD 1 day"
        parsed = pp.parse(src, rg.Regimen)

        indication = pp.parse('1mg SOF QD', rg.Indication)
        duration = rg.Duration([rg.Number('1'), rg.TimeUnit('day')])
        expected = rg.Regimen([
            rg.RegimenPart([
                rg.DrugCombination([indication]),
                duration
            ])
        ])

        self.assertEqual(parsed, expected)

    def test_multiple_drugs(self):
        src = "1mg SOF QD & 2mg DCV TID 2 weeks"
        parsed = pp.parse(src, rg.Regimen)

        indications = rg.DrugCombination([
            pp.parse("1mg SOF QD", rg.Indication),
            pp.parse("2mg DCV TID", rg.Indication),
        ])
        duration = pp.parse("2 weeks", rg.Duration)
        expected = rg.Regimen([rg.RegimenPart([indications, duration])])

        self.assertEqual(parsed, expected)

    def test_multiple_regimen_parts(self):
        src = ("1mg SOF TID 2 weeks, 2mg DCV QD 3 days,"
               " 0.180mg PEG QWK 48 weeks")
        parsed = pp.parse(src, rg.Regimen)

        expected = rg.Regimen([
            rg.RegimenPart([
                pp.parse("1mg SOF TID", rg.DrugCombination),
                pp.parse("2 weeks", rg.Duration),
            ]),
            rg.RegimenPart([
                pp.parse("2mg DCV QD", rg.DrugCombination),
                pp.parse("3 days", rg.Duration),
            ]),
            rg.RegimenPart([
                pp.parse("0.180mg PEG QWK", rg.DrugCombination),
                pp.parse("48 weeks", rg.Duration),
            ]),
        ])

        self.assertEqual(parsed, expected)
