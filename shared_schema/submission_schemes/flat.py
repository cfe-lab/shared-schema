'''Definition of the flat data submission scheme.

This scheme is designed for simpler data sets where the flexibility of
relational data isn't required.
'''

from shared_schema import data
from shared_schema.submission_schemes import field

schema = data.schema_data
field = field.Field


def from_schema(entity_name, field_name, **kwargs):
    schema_field = schema.find_field(entity_name, field_name)
    return field.from_schema_field(schema_field, **kwargs)


scheme = {
    'flat': [
        field('id', 'string', req=True,
              descr="A participant's anonymous id"),
        from_schema('Person', 'country'),
        from_schema('Person', 'sex'),
        from_schema('Person', 'ethnicity'),
        from_schema('Person', 'year_of_birth'),
        field('ltfu', 'bool', req=False,
              descr="Has this participant been lost to follow up?"),
        from_schema('LossToFollowUp', 'ltfu_year'),
        from_schema('LossToFollowUp', 'died'),
        from_schema('LossToFollowUp', 'cod'),
        from_schema('BehaviorData', 'sex_ori'),
        from_schema('BehaviorData', 'idu'),
        from_schema('BehaviorData', 'idu_recent'),
        from_schema('BehaviorData', 'ndu'),
        from_schema('BehaviorData', 'ndu_recent'),
        from_schema('BehaviorData', 'prison'),
        from_schema("ClinicalData", "hiv"),
        from_schema("ClinicalData", "hbv"),
        from_schema("ClinicalData", "ost"),
        from_schema("ClinicalData", "chir"),
        from_schema("ClinicalData", "metavir"),
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
        field(
            'bl_seq_file',
            'string',
            descr=("The name of sequence file in the ``sequences`` folder "
                   "containing the participants baseline sample sequence.")
        ),
        field(
            'bl_genotype',
            'enum(1, 2, 3, 4, 5, 6, mixed, recombinant, indeterminate)',
            descr="The baseline sample's genotype",
        ),
        field(
            'bl_subgenotype',
            'string',
            descr="The baseline sample's subgenotype",
        ),
        field(
            'bl_cutoff',
            'float',
            descr=("The cutoff percentage used to generate the baseline "
                   "sample consensus sequence."),
        ),
        field(
            'fu_seq_file',
            'string',
            descr=("The name of sequence file in the ``sequences`` folder "
                   "containing the participants follow-up sample sequence.")
        ),
        field(
            'fu_kind',
            'enum(eot, fw4, fw12, fw23)',
            descr=("The kind of follow up sample provided (end-of-treatment "
                   "or up to 4, 12, or 24 weeks after end-of-treatment)."),
        ),
        field(
            'fu_genotype',
            'enum(1, 2, 3, 4, 5, 6, mixed, recombinant, indeterminate)',
            descr="The follow-up sample's genotype",
        ),
        field(
            'fu_subgenotype',
            'string',
            descr="The follow-up sample's subgenotype",
        ),
        field(
            'fu_cutoffb',
            'float',
            descr=("The cutoff percentage used to generate the follow-up "
                   "sample consensus sequence."),
        ),
        from_schema('TreatmentData', 'first_treatment'),
        from_schema('TreatmentData', 'duration_sch'),
        from_schema('TreatmentData', 'duration_act'),
        field(
            'regimen',
            'string',
            descr="What drug regimens was the participant taking?",
            possible_values="See :ref:`treatment_regimens`.",
        ),
        field(
            'prev_regimen',
            'string',
            descr=("If the participant has been treated before, what "
                   "treatment regimen were they taking previously?"),
            possible_values="See :ref:`treatment_regimens`.",
        ),
        field(
            'pprev_regimen',
            'string',
            descr=("If the participant has had two previous treatments, "
                   "what regimen were they taking before-last?"),
            possible_values="See :ref:`treatment_regimens`.",
        ),
        from_schema('TreatmentData', 'response'),
        from_schema('TreatmentData', 'notes'),
    ]
}
