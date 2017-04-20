#encoding: utf8
import collections
import re

# Data Parsing

entity = collections.namedtuple("entity", ["name", "description", "fields"])
field = collections.namedtuple("field", ["name", "type", "description"])


def foreign_key_target(field_type):
    '''What entity does a foreign key target?'''
    matches = re.findall("\((.+)\)", field_type)
    return matches[0]


class Schema(object):

    types = {"integer", "float", "string", "foreign key", "date",
             "uuid", "enum", "bool"}

    def __init__(self, raw_entities):
        self.raw_entities = raw_entities
        self.entities = {e.name: e for e in raw_entities}
        err_msg = "Duplicate entities?"
        assert len(self.entities) == len(self.raw_entities), err_msg
        types = (f.type for e in self.entities.values() for f in e.fields)
        for t in types:
            err_msg = "invalid type: {}".format(t)
            assert self.type_is_valid(t, self.entities), err_msg

    @property
    def relationships(self):
        rels = set()
        for ename, entity in self.entities.items():
            types = (f.type for f in entity.fields)
            foreign_keys = [t for t in types if "foreign key" in t]
            targets = [foreign_key_target(f) for f in foreign_keys]
            for target in targets:
                rel = (entity.name, target)
                rels.add(rel)
        return rels

    @classmethod
    def type_is_valid(cls, t, entities):
        known_type = t in cls.types
        fk = "foreign key" in t
        enum = "enum" in t
        if not (known_type or fk or enum):
            return False
        elif fk:
            fk_target = foreign_key_target(t)
            err_msg = "invalid foreign key target: {}".format(fk_target)
            assert  fk_target in entities, err_msg
            return True
        else:
            return True




schema_data = Schema([

    entity(
        "Collaborator",
        "A collaborating site (provides participant data)",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "Name of the collaborating entity"),
         field("location", "string", "The collaborator's physical location"),
        ]),

    # QUESTION(nknight): Location? How do we represent geographical data (how accurate do we need to be?)
    # QUESTION(nknight): Treatment/Contact Centre? (as distinct from collaborator; could be useful for geographic data)


    # ==================================================
    # Participant Data

    entity(
        "Person",
        "A study participant",
        [field("id", "uuid", "Unique identifier"),
         field("date_entered", "date", "Date the participant entered the study"),
         field("region", "enum(america, europe, asia, africa, other)",
               "Country or region of origin"),
        ]),

    entity(
        "Drug",
        "An HCV drug",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "The drug's name"),
         # QUESTION(nknight): some kind of key to a drug database?
         # QUESTION(nknight): other drug info?
        ]),

    entity(
        "ClinicalData",
        "Diagnostic information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant to whom this data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "The source of the data"),
         field("height", "float", "Participant's height (in m)"),
         field("weight", "float", "Participant's weight (in kg)"),
         field("seroconverted", "bool", ""),
         field("meld", "float", "MELD score"),
         field("ctp", "float", "Child-Turcotte-Pugh score"),
         field("ishak", "float", "Ishak fibrosis score"),
         field("q_life_global", "float", "Global quality of life score"),
         field("q_life_phys", "float", "Physical quality of life score"),
         field("q_life_ment", "float", "Mental quality of life score"),
         field("q_life_instrument", "string", "Quality of life instrument and version"),
         field("depression", "bool", "Has the participant ever been diagnosed with depression"),
         field("viral_load", "float", "Viral load"),
         # QUESTION(nknight): exposure?
         # QUESTION(nknight): separate test results table?
        ]),

    entity(
        "EventsAndProceduresData",
        "Significant clinical events and/or procedures (e.g. diagnoses, surgeries, etc.)",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "Participant to whom this data pertains"),
         # QUESTION(nknight): standard events and procedures coding system?
         field("event_code", "string", "Standardised event coding system"),
         field("event_date", "date", "Date of procedure or diagnosis"),
        ]),

    entity(
        "DemographicData",
        "Demographic information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant to whom this data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "The source of the data"),
         field("date_collected", "date", "The date this data was collected"),
         field("date_of_birth", "date", "Participant's date of birth"),
         field("country_of_birth", "string", ""),
         # QUESTION(nknight): what are the possible/useful values here?
         field("ethnicity", "enum (...)", ""),
        ]),

    entity(
        "BehaviorData",
        "Behavioral information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant to whom this data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "The collaborator who provided the data"),
         field("date_collected", "date", "The date this data was collected"),
         field("sexual_orientation", "enum (heterosexual, non-heterosexual)",
               "Participant's sexual orientation"),
         field("gender", "enum (cis-male, cis-female, trans-male, trans-female, intersex, other)", ""),
         field("highest_education", "enum(...)", "Participant's highest level of education to date"),
         field("employed", "enum(employed, unemployed, other)", "Employment status"),
         field("housing", "enum(stable, unstable, prison, other)", "Housing status"),

         field("idu", "bool", "Injection drug use? (ever)"),
         field("idu_recent", "bool", "Recent injection drug use?"),
         field("idu_period", "enum(1month, 3months, 6months, 12months, other, unknown)",
               "Period of recall for 'idu_recent'"),
         field("idu_min_freq", "enum(daily, weekly, rarely)",
               "Minimum frequency of recent drug use (daily: once or more every day; weekly: not every day, but more than once a week; rarely: less than once a week)"),
         field("idu_min_freq_period", "enum(1month, 3months, 6months, 12months, other, unknown)",
               "Period of recall for idu_min_freq"),
         field("idu_syr_borrowed", "bool",
               "Recent receptive syringe sharing (i.e. using a syringe that has previously been used by someone else)"),
         field("idu_syr_borrowed_period", "enum(1month, 3months, 6months, 12months, other, unknown)",
               "Period of recall for 'idu_syr_borrowed'"),
         field("idu_syr_borrowed_min_freq", "enum(daily, weekly, rarely)",
               "Minimum frequency of receptive syringe sharing"),
         field("idu_syr_borrowed_min_freq_period", "enum(1month, 3months, 6months, 12months, other, unknown)",
               "Period of recall for 'idu_syr_borrowed_min_freq'"),
         field("idu_eqp_borrowed", "bool",
               "Recent receptive sharing of other injecting equipment (cookers, containers, cottons, etc.) that "),
         field("idu_eqp_borrowed_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Period of recall for 'idu_eqp_borrowed'"),
         field("idu_eqp_borrowed_min_freq", "enum(daily, weekly, rarely)",
               "Minimum frequency for 'idu_eqp_borrowed_min_freq'"),
         field("idu_shared_partners", "integer",
               "Number of people shared with recently (including use before and after)"),
         field("idu_shared_partners_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Period of recall for 'idu_shared_partners'"),

         field("prison", "bool", "Recent prison"),
         field("prison_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Period of recall for 'prison'"),

         field("alcohol", "bool", "Recent alcohol use"),
         field("alcohol_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Period of recall for 'alcohol'"),
         field("alcohol_min_freq", "enum(daily, weekly, rarely)",
               "Minimum frequency of alcohol use"),
         field("alcohol_min_freq_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Period of recall for 'alcohol_min_freq'"),
         field("alcohol_drinks", "float", "Average number of drinks per session"),
         field("alcohol_amount", "float", "Average amount of alcohol per drink (in grams)"),

         field("sex_hcv", "bool", "Recent sexual partner known to be HCV positive?"),
         field("sex_hcv_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Period of recall for 'sex_hcv'"),
         field("sex_idu", "bool", "Recent sexual partner who injects drugs?"),
         field("sex_idu_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Recall period for 'sex_idu'"),
         field("inj_sexpart", "bool",
               "Recent injecting with sex partner (in the same space, not necessarily sharing"),
         field("inj_sexpart_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Recall period for 'sex_inj'"),
         field("inj_sexpart_min_freq", "enum(daily, weekly, rarely)",
               "Frequency of recent injecting with sex partner"),
         field("inj_sexpart_min_freq_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Recall period for 'inj_sexpart_min_freq'"),

         field("sexpart_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Recall period for sexual partner & condom use"),
         field("sexpart", "integer", "Total number of recent sexual partners (regular or casual)"),
         field("sexpart_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with all sex partners"),
         field("sexpart_cm", "integer", "Total number of cis-male sexual partners"),
         field("sexpart_cm_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with cis-male sexual partners"),
         field("sexpart_cf", "integer", "Total number of cis-female sexual partners"),
         field("sexpart_cf_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with cis-female sexual partners"),
         field("sexpart_tm", "integer", "Total number of trans-male sexual partners"),
         field("sexpart_tm_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with trans-male sexual partners"),
         field("sexpart_tf", "integer", "Total number of trans-female sexual partners"),
         field("sexpart_tf_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with trans-female sexual partners"),
         field("sexpart_is", "integer", "Total number of intersex sexual partners"),
         field("sexpart_is_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with intersex sexual partners"),
         field("sexpart_inj", "integer", "Total number of sex partners they injected with"),
         field("sexpart_inj_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with sexual partners they injected with"),
         field("sexpart_comm", "integer",
               "Total number of partner with whom they traded sex for money, housing, goods, favours, etc."),
         field("sexpart_comm_condom", "enum(always, usually, sometimes, rarely, never, unknown, refused)",
               "Condom use with sex partners they traded sex to"),

         field("opiate_pharm", "bool", "Recent opiate pharmacotherapy"),
         field("opiod", "bool", "Recent opiod use (Morphine, Oxycodone, Methadone, Buprenorphine, etc."),
         field("opiod_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Recall period for 'opiod'"),
        ]),

    entity(
        "DrugUse",
        "Detailed data on drug use",
        [field("id", "uuid", "Unique identifier"),
         field("behaviourdata_id", "foreign key (BehaviorData)",
               "The behaviour data this usage was recorded with"),
         field("drug", "string", "Name of the drug"),
         field("injected", "bool", "Whether the drug was injected"),
         field("prescribed", "bool", "Whether the drug was prescribed"),
         field("period", "enum(1month, 3months, 6months, 12months, other, unknown)",
               "Recall period for this drug"),
        ]),

    entity(
        "GeneticData",
        "Records relevant genetic data about participants (e.g. IL28B)",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "Person to whom this data pertains"),
         field("gene", "string", "Name of the relevant gene"),
         field("snp", "string", "Single nucleotide polymorphism"),
         field("snp_genotype", "string", "Genotype of 'snp'"),
        ]),

    entity(
        "TreatmentData",
        "Information about a participant's treatment",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant to whom this data pertains"),
         field("collaborator_id", "foreign key (Collaborator)", "Collaborator who collected this data"),
         field("start_dt", "date", "Schedule treatment start date"),
         field("end_dt", "date", "Scheduled treatment end date"),
         field("end_dt_bound", "enum(<, >, =)", "Uncertainty on 'end_dt'"),
        ]),

    entity(
        "TreatmentOutcome",
        "Outcome of a participant's treatment",
        [field("id", "uuid", "Unique identifier"),
         field("treatment_id", "foreign key (TreatmentData)", "The treatment whose outcome is being described"),
         field("outcome", "enum(svr, vbt, relapse)",
               "Sustained viral response(svr), virological breakthrough (vbt), or relapse"),
         field("early_stop", "bool", "Did the participant discontinue treatment earlier than intended?"),
         field("stop_reason", "string", "Reason for dropping out"),
         # QUESTION(nknight): Site?
        ]),

    entity(
        "TreatmentDrugData",
        "How much and what kind of a drug was included in a treatment regimen",
        [field("treatment_id", "foreign key (TreatmentData)", "Which treatment this prescription was included in"),
         field("drug_id", "foreign key (Drug)", "Which drug was prescribed"),
         field("dosage", "float", "Dosage of the drug prescribed (in μg)"),
         field("dose_number", "float", "Number of doses taken per dose_period"),
         field("dose_period", "enum(day, week, course)", "Period over which dosage is measured"),
        ]),

    entity(
        "DeathAndLastFollowup",
        "Records data about  leaving the study",
        [field("person_id", "foreign key (Person)", ""),
         field("drop", "bool", "The participant dropped out"),
         field("drop_dt", "date", "Date the participant dropped out"),
         field("drop_reason", "string", "Reason for dropping out (if applicable)"),
         field("died", "bool", "Is the participant deceased?"),
         field("died_dt", "date", "The participant's date of death"),
         field("autopsy", "bool", "Was an autopsy performed?"),
         # QUESTION(nknight): split cause into separate table?
         field("cause_of_death", "string", "Cause of death (e.g. ICD-10 code)"),
        ]),


    # ==================================================
    # References

    entity(
        "Reference",
        "A reference to a publication",
        [field("id", "uuid", "Unique id"),
         field("author", "string", ""),
         field("title", "string", ""),
         field("journal", "string", ""),
         field("publication_dt", "date", "Null for unpublished results"),
         field("pubmed_id", "string", ""),
        ]),

    # QUESTION(nknight): other kinds of reference? (other than pubmed)


    # ==================================================
    # Isolates & Sequences

    entity(
        "Isolate",
        "Virus isolate (from an individual or used in a lab experiment)",
        [field("id", "uuid", "Unique id"),
         field("isolation_date", "date", "Date the virus was isolated"),
         field("type", "enum (clinical, lab)", "The kind of isolate. (extra data available depending on kind "),
         field("isolate_date", "date", "Date the virus was isolated"),
         field("entered_date", "date", "Date the isolate was entered into the database"),
        ]),
    # QUESTION(nknight): generic isolate fields? (hicdep additionally has "gene")
    # QUESTION(nknight): external references for isolates (e.g. to GenBank)?
    # QUESTION(nknight): Do isolates have a single viral component (e.g. do we need to handle multiple genotypes per isolate)?
    # QUESTION(nknight): How do we record genotype/subtype information? (per isolate, per participant, per what?)

    entity(
        "ClinicalIsolate",
        "Isolate information",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("person_id", "foreign key (Person)", "The participant who gave the isolate"),
         field("cultured", "bool", "Whether or not the isolate was cultured before sequencing"),
        ]),
    # QUESTION(nknight): clinical isolate fields (hicdep has template, clone method, and seq method"
    # QUESTION(nknight): Do lab isolates come from participants? Do we want a third kind that are purely synthetic?

    entity(
        "LabIsolate",
        "Isolates created in the lab",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("mutations", "string", "A list of the mutations applied to the isolate"),
        ]),
    # QUESTION(nknight): lab isolate fields? (hicdep has + parent, mutation list, sdm, passage)

    entity(
        "Sequence",
        "Sequences and data needed for rapid alignment",
        [field("id", "uuid", "Unique identifier"),
         field("isolate_id", "foreign key (Isolate)", "Isolate the sequence was obtained from"),
         field("seq", "string", "nucleotide sequence"),
         # QUESTION(nknight): sequence fields (hicdep has + clonename, naseq, aaseq, firstaa, lastaa)
         # QUESTION(nknight): sequence length? should be 19Kb or less, no?
         # QUESTION(nknight): How many sequences will we be storing (millions, billions)?

        ]),

    entity(
        "Substitution",
        "A substitution, insertion, or deletion in an RNA sequence",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "Name of the substitution"),
         field("reference_sequence", "string", "Name of the consensus wild-type reference sequence"),
         field("position", "integer", "Nucleotide position (with respect to the reference sequence)"),
         field("length", "integer", "Length of the substitution"),
         field("resistance_associated", "bool", "True if this is a resistance associated substitution"),
        ]),

    entity(
        "SequenceSubstitution",
        "Indicates that the attached sequence has the attached substitution",
        [field("sequence_id", "foreign key (Sequence)", "The sequence being tagged"),
         field("substitution_id", "foreign key (Substitution)",
               "The substitution identified in the tagged sequence"),
        ]),



    # ==================================================
    # Susceptibility results

    entity(
        "SusceptibilityResult",
        "Drug susceptibility test results",
        [field("id", "uuid", "Unique id"),
         field("isolate_id", "foreign key (Isolate)", "The isolate being tested"),
         field("reference_id", "foreign key (Reference)", "Source (if applicable)"),
         field("drug_id", "foreign key (Drug)", "The drug being tested"),
         field("method_id", "foreign key (SusceptibilityMethod)", "Name of the susceptibility test method"),
         # QUESTION(nknight): precision?
         field("result", "float", "Drug concentration required for inhibition (in nM)"),
         field("result_bound", "enum (<, =, >)", ""),
         field("IC", "enum (50, 90, 95)", "% inhibition"),
         field("fold", "float", "Fold-change compared to wild type"),
         field("fold_bound", "enum (<, =, >)", "Represents uncertainty in the fold-change measurement"),
        ]),

    entity(
        "SusceptibilityMethod",
        "Susceptibility testing methods",
        [field("id", "uuid", "Unique id"),
         field("name", "string", "Name of the method"),
         field("reference_id", "foreign key (Reference)", "Reference describing the method"),
         field("notes", "string", "Free-text notes about the testing method"),
        ]),

])
