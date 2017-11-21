'''Definition of a multi-table data submission scheme

This submission scheme is designed for researchers or other
contributors with a moderate quantity of data in an existing
database. It's mostly derived in part from the database schema.
'''

from shared_schema import data
from shared_schema.submission_schemes import field


schema = data.schema_data
field = field.Field


def from_schema(entity_name, field_name, **kwargs):
    schema_field = schema.find_field(entity_name, field_name)
    schema_path = (entity_name, field_name)
    return field.from_schema_field(
        schema_field,
        schema_path=schema_path,
        **kwargs
    )


scheme = {
    'ltfu': [
        field(
            'person',
            'string',
            req=True,
            descr="The ID of a person in the ``participants`` file",
            schema_path=('LossToFollowUp', 'person_id'),
        ),
        from_schema('LossToFollowUp', 'ltfu_year'),
        from_schema('LossToFollowUp', 'died'),
        from_schema(
            'LossToFollowUp',
            'cod',
            new_possible_values="See :ref:`tbl_cause_of_death`.",
        ),
    ],
    'participants': [
        field(
            'id',
            'string',
            req=True,
            descr="A participant's anonymous id",
            schema_path='not applicable',
        ),
        from_schema('Person', 'country'),
        from_schema('Person', 'sex'),
        from_schema('Person', 'ethnicity'),
        from_schema('Person', 'year_of_birth'),
    ],
    'behavior': [
        field(
            'person',
            'string',
            req=True,
            descr="The ID of a peson in the ``participants`` file",
            schema_path=('BehaviorData', 'person_id'),
        ),
        from_schema('BehaviorData', 'sex_ori'),
        from_schema('BehaviorData', 'idu'),
        from_schema('BehaviorData', 'idu_recent'),
        from_schema('BehaviorData', 'ndu'),
        from_schema('BehaviorData', 'ndu_recent'),
        from_schema('BehaviorData', 'prison'),
    ],
    'clinical': [
        field(
            'person',
            'string',
            req=True,
            descr="The ID of a person in the ``participants`` file",
            schema_path=('ClinicalData', 'person_id'),
        ),
        from_schema('ClinicalData', 'kind'),
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
    ],
    'isolates': [
        field(
            'person',
            'string',
            req=True,
            descr="The ID of a person in the ``participants`` file",
            schema_path=('ClinicalIsolate', 'person_id'),
        ),
        field(
            'seq_file',
            'string',
            req=True,
            descr="The name of a sequence file in the ``sequences`` folder",
            schema_path='not applicable',
        ),
        from_schema('Isolate', 'genotype'),
        from_schema('Isolate', 'subgenotype'),
        from_schema('Isolate', 'seq_method'),
        from_schema('Isolate', 'strain'),
        from_schema('Isolate', 'cutoff'),
        from_schema('ClinicalIsolate', 'sample_kind'),
    ],
    'treatment': [
        field(
            'person',
            'string',
            req=True,
            descr="The ID of a person in the ``participants`` file",
            schema_path=('TreatmentData', 'person_id'),
        ),
        from_schema('TreatmentData', 'first_treatment'),
        from_schema('TreatmentData', 'duration_act'),
        field(
            'regimen',
            'string',
            descr="What drug regimens was the participant taking?",
            possible_values="See :ref:`treatment_regimens`.",
            schema_path='not applicable',
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
        from_schema('TreatmentData', 'notes'),
    ],
}
