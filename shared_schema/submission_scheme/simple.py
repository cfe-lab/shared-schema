'''Definition of the simple data submission scheme.

This scheme is designed for simpler data sets where the flexibility of
relational data isn't required.
'''

from shared_schema import data

from . import field as scm_field

schema = data.schema_data
Field = scm_field.Field  # A re-export to avoid importing the field module.
field = scm_field.Field


def from_schema(entity_name, schema_field_name, **kwargs):
    schema_field = schema.find_field(entity_name, schema_field_name)
    schema_path = (entity_name, schema_field_name)
    return field.from_schema_field(
        schema_field, schema_path=schema_path, **kwargs)


scheme = {
    'simple': [
        field(
            'id',
            'string',
            req=True,
            descr="A participant's anonymous id",
            schema_path='not applicable'),
        from_schema('Person', 'country'),
        from_schema('Person', 'sex'),
        from_schema('Person', 'ethnicity'),
        from_schema('Person', 'year_of_birth'),
        field(
            'ltfu',
            'bool',
            req=False,
            descr="Has this participant been lost to follow up?",
            schema_path='not applicable',
        ),
        from_schema('LossToFollowUp', 'ltfu_year'),
        from_schema('LossToFollowUp', 'died'),
        from_schema(
            'LossToFollowUp',
            'cod',
            new_possible_values="See :ref:`tbl_cause_of_death`.",
        ),
        from_schema('BehaviorData', 'sex_ori'),
        from_schema('BehaviorData', 'idu'),
        from_schema('BehaviorData', 'idu_recent'),
        from_schema('BehaviorData', 'ndu'),
        from_schema('BehaviorData', 'ndu_recent'),
        from_schema('BehaviorData', 'prison'),
        field(
            'kind',
            'enum(bl, eot, fw4, fw12, fw24)',
            descr=("Does this row contain baseline, end-of-treatment, or "
                   "follow-up results?"),
            schema_path="not applicable",
            req=True,
        ),
        from_schema("ClinicalData", "hiv"),
        from_schema("ClinicalData", "hbv"),
        from_schema("ClinicalData", "ost"),
        from_schema("ClinicalData", "cirr"),
        from_schema("ClinicalData", "fibrosis"),
        from_schema("ClinicalData", "inflamation"),
        from_schema("ClinicalData", "metavir_by"),
        from_schema("ClinicalData", "stiff"),
        from_schema("ClinicalData", "alt"),
        from_schema("ClinicalData", "ast"),
        from_schema("ClinicalData", "crt"),
        from_schema("ClinicalData", "egfr"),
        from_schema("ClinicalData", "ctp"),
        from_schema("ClinicalData", "meld"),
        from_schema("ClinicalData", "ishak"),
        from_schema("ClinicalData", "bil"),
        from_schema("ClinicalData", "hemo"),
        from_schema("ClinicalData", "alb"),
        from_schema("ClinicalData", "inr"),
        from_schema("ClinicalData", "phos"),
        from_schema("ClinicalData", "urea"),
        from_schema("ClinicalData", "plate"),
        from_schema("ClinicalData", "CD4"),
        from_schema("ClinicalData", "crp"),
        from_schema("ClinicalData", "il28b"),
        from_schema("ClinicalData", "asc"),
        from_schema("ClinicalData", "var_bleed"),
        from_schema("ClinicalData", "hep_car"),
        from_schema("ClinicalData", "transpl"),
        from_schema("ClinicalData", "vl"),
        from_schema('TreatmentData', 'first_treatment'),
        from_schema('TreatmentData', 'duration_act'),
        field(
            'regimen',
            'string',
            descr="What drug regimens was the participant taking?",
            possible_values="See :ref:`treatment_regimens`.",
            schema_path='not applicable',
            req=True,
        ),
        field(
            'prev_regimen',
            'string',
            descr=("If the participant has been treated before, what "
                   "treatment regimen were they taking previously?"),
            possible_values="See :ref:`treatment_regimens`.",
            schema_path='not applicable',
        ),
        field(
            'pprev_regimen',
            'string',
            descr=("If the participant has had two previous treatments, "
                   "what regimen were they taking before-last?"),
            possible_values="See :ref:`treatment_regimens`.",
            schema_path='not applicable',
        ),
        from_schema('TreatmentData', 'response'),
        from_schema('TreatmentData', 'notes', new_name='treatment_notes'),
        field(
            "seq_kind",
            'enum(bl, eot, fw4, fw12, fw24, fw+)',
            descr=("The kind of sequence in this record: (baseline, "
                   "end-of-treatment, or follo-up at up to 4, 12, 24, or more"
                   "weeks."),
            schema_path="not applicable",
        ),
        field(
            'genotype',
            'enum(1, 2, 3, 4, 5, 6, mixed, recombinant, indeterminate)',
            descr="The sequence's clinically determined genotype.",
            schema_path='not applicable',
        ),
        field(
            "subgenotype",
            'string',
            descr="The sequence's clinically determined subgenotype",
            schema_path='not applicable',
        ),
        field(
            'strain',
            'string',
            descr="The isolate's strain (if applicable/known)",
            schema_path='not applicable',
        ),
        field(
            "seq_id",
            "string",
            descr="The id of a sequence in the FASTA files directory.",
            schema_path='not applicable',
        ),
        field(
            "gene",
            "enum(ns3, ns5a, ns5b)",
            descr="The gene contained in this record's sequence.",
            schema_path="not applicable",
        ),
        field(
            'seq_method',
            'string',
            descr="The sequencing method used to obtain this sequence.",
            possible_values="``sanger``, ``ngs``",
            schema_path='not applicable',
        ),
        field(
            'cutoff',
            'float',
            descr=("The cutoff percentage used to generate the consensus "
                   "sequence; 5% should be entered as '5' or '5.0'."),
            schema_path='not applicable',
        ),
        field(
            'seq_notes',
            'string',
            descr="Notes on the baseline sequence, if applicable",
            schema_path='not applicable',
        ),
    ]
}

fields = scheme['simple']
