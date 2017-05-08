#encoding: utf8

import collections

import schema.util as util

# Data Parsing

entity = collections.namedtuple("entity", ["name", "description", "fields"])
field = collections.namedtuple("field", ["name", "type", "description"])


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
            targets = [util.foreign_key_target(f) for f in foreign_keys]
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
            fk_target = util.foreign_key_target(t)
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
         field("country", "string", "The collaborator's physical location (country)"),
        ]),

    entity(
        "DataBatch",
        "A study, trial, or other batch of data from a collaborator",
        [field("id", "uuid", "Unique identifier"),
         field("collaborator", "foreign key (Collaborator)", "The collaborator providing the data"),
         field("name", "string", "The name of the study or trial"),
         field("collection_start", "date", "The beginning of data collection"),
         field("collection_end", "date", "The end of data collection (if applicable)"),
        ]),


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
        "Medication",
        "",
        [field("id", "uuid", "Unique identifier"),
         field("short_name", "string", "The medication's three-letter abbreviation"),
         field("full_name", "string", "The medication's name"),
         # BLOCKED(nknight): Pharmaco-economics code?
        ]),

    entity(
        "ClinicalData",
        "Diagnostic information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant this data pertains to"),
         field("batch_id", "foreign key (DataBatch)", "The source of the data"),
         field("bmi", "float", "The participant's body mass index"),
         field("meld", "float", "MELD score"),
         field("ctp", "float", "Child-Turcotte-Pugh score"),
         field("ishak", "float", "Ishak fibrosis score"),
         field("infection_duration", "integer", "Days since likely infection"),
        ]),

    entity("ViralLoadData",
           "",
           [field("id", "uuid", "A unique identifier"),
            field("person_id", "foreign key (Person)", "The participant this data pertains to"),
            field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
            field("assay", "enum(...)", "The assay used to measure viral load"),
            field("detectable", "bool", "Was a detectable viral load present?"),
            field("viral_load", "float", "The measured viral load (if quantifiable) (units? count/mL/ IUs?)"),
           ]),

    entity(
        "TestResult",
        "The outcome of a test result (e.g. bilirubin, alt, CD4)",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", ""),
         field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
         field("name", "string", "Name of the test"),
         field("unit", "string", "Unit of the test result (e.g. ppm)"),
         field("result", "float", "The value of the test result"),
         field("date", "date", "Date the test was performed"),
        ]),

    entity(
        "EventsAndProceduresData",
        "Significant clinical events and/or procedures (e.g. diagnosed comorbid conditions, surgeries, transplants, etc.)",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "Participant this data pertains to"),
         field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
         # QUESTION(nknight): standard events and procedures coding system
         field("event_code", "string", "Standardised event coding system"),
        ]),

    entity(
        "DemographicData",
        "Demographic information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant this data pertains to"),
         field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
         field("date_collected", "date", "The date these survey responses were given"),
         field("year_of_birth", "date", "Participant's year of birth"),
         field("country_of_birth", "string", ""),
         field("gender_at_birth", "enum(male, female, other)", ""),
         # QUESTION(nknight): field for enthnicity
         field("ethnicity", "enum (...)", ""),
        ]),

    entity(
        "BehaviorData",
        "Behavioral information about a participant",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant this data pertains to"),
         field("batch_id", "foreign key (DataBatch)", "The study or trial that includes this information"),
         field("date_collected", "date", "The date this data was collected"),
         field("sexual_orientation", "enum (heterosexual,non-heterosexual)",
               "Participant's sexual orientation"),
         field("region", "string", "The participant's region of residence"),

         field("idu", "bool", "Injection drug use (narcotic)? (ever)"),
         field("idu_recent", "bool", "Recent injection drug use?"),
         field("idu_period", "enum(1month, 3months, 6months, 12months, other, unknown)",
               "Period of recall for 'idu_recent'"),

         field("opioid", "bool", "Recent opioid use (Morphine, Oxycodone, Methadone, Buprenorphine, etc."),
         field("opioid_period", "enum(1month, 3months, 6months, 12months, unknown, other)",
               "Recall period for 'opioid'"),

         field("prison", "bool", "Has the participant been in prison (ever)?"),

         field("opioid_pharm", "bool", "Has the participant recently had opioid substitution therapy?"),
        ]),

    entity(
        "NarcoticsUse",
        "Detailed data on narcotics use",
        [field("id", "uuid", "Unique identifier"),
         field("behaviourdata_id", "foreign key (BehaviorData)",
               "The behaviour data this usage was recorded with"),
         field("name", "string", "Name of the narcotic (e.g. heroin, cocaine, amphetamine"),
         field("injected", "bool", "Was the narcotic used by injection?"),
         field("prescribed", "bool", "Was the narcotic prescribed?"),
        ]),

    entity(
        "GeneticData",
        "Records relevant genetic data about participants (e.g. IL28B)",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "Person this data pertains to"),
         field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
         field("il28b", "enum(cc, non-cc, ct, tt)", "The participant's IL28B genotype"),
        ]),

    entity(
        "TreatmentData",
        "Information about a participant's treatment",
        [field("id", "uuid", "Unique identifier"),
         field("person_id", "foreign key (Person)", "The participant that this data pertains to"),
         field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
         field("first_treatment", "bool", "Is this the first treatment "),
         field("start_dt", "date", "Schedule treatment start date"),
         field("end_dt_sch", "date", "Scheduled treatment end date"),
         field("duration_sch", "float", "Schedule treatment duration (weeks)"),
         field("end_dt_act", "date", "Actual treatment end date"),
         field("end_dt_bound", "enum(<, >, =)", "Uncertainty on 'end_dt'"),
        ]),

    entity(
        "TreatmentOutcome",
        "Outcome of a participant's treatment",
        [field("id", "uuid", "Unique identifier"),
         field("treatment_id", "foreign key (TreatmentData)", "The treatment whose outcome is being described"),
         field("outcome", "enum(full-svr, partial-svr,vbt,no-response)",
               "Whether treatment caused sustained viral response(svr), virological breakthrough (vbt), or no response"),
         field("early_stop", "bool", "Did the participant discontinue treatment earlier than intended?"),
         field("stop_reason", "string", "Reason for dropping out"),
        ]),

    entity(
        "TreatmentMedicationData",
        "How much and what kind of medications were included in a treatment regimen",
        [field("treatment_id", "foreign key (TreatmentData)", "Which treatment this prescription was included in"),
         field("medication_id", "foreign key (Medication)", "Which medication was prescribed"),
         field("dosage", "float", "Dosage of the medication prescribed (in mg)"),
         field("dose_number", "float", "Number of doses taken per dose_period"),
         field("dose_period", "enum(day, week, course)", "Period over which dosage is measured"),
        ]),

    entity(
        "DeathAndLastFollowup",
        "Records data about  leaving the study",
        [field("person_id", "foreign key (Person)", ""),
         field("batch_id", "foreign key (DataBatch)", "The study or trial this data comes from"),
         field("drop", "bool", "Did the participant dropped out?"),
         field("drop_dt", "date", "Date the participant dropped out"),
         field("drop_reason", "string", "Reason for dropping out (if applicable)"),
         field("died", "bool", "Is the participant deceased?"),
         field("died_dt", "date", "The participant's date of death"),
         field("autopsy", "bool", "Was an autopsy performed?"),
         field("cause_of_death", "string", "Cause of death (e.g. ICD-10 code)"),
        ]),

    entity(
        "CauseOfDeath",
        "Primary cause of death and other underlying conditions",
        [field("ltfu_id", "foreign key (DeathAndLastFollowup)",
               "The death record this data pertains to"),
         field("cause", "enum(...)", "A code for the cause of death"),
         field("importance", "bool",
               "Was this a primary cause of death?"),
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
         field("url", "string", "URL to the reference online"),
         field("publication_dt", "date", "Null for unpublished results"),
         field("pubmed_id", "string", ""),
        ]),


    # ==================================================
    # Isolates & Sequences

    entity(
        "Isolate",
        "Virus isolate (from an individual or used in a lab experiment)",
        [field("id", "uuid", "Unique id"),
         field("isolation_date", "date", "Date the virus was isolated"),
         field("type", "enum (clinical, lab)", "The kind of isolate. (extra data available depending on kind "),
         field("entered_date", "date", "Date the isolate was entered into the database"),
         field("genbank_id", "string", "GenBank ID (if applicable)"),
         field("genotype", "enum(1,2,3,4,5,6,mixed,recombinant,indeterminate)", "The genotype of the isolate"),
         field("subgenotype", "enum(a,b,c,d,e,f,g,h,i,j)", ""),
         field("strain", "string", "The strain of the isolate"),
        ]),

    entity(
        "ClinicalIsolate",
        "Isolate information",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("person_id", "foreign key (Person)", "The participant who gave the isolate"),
         field("replicon", "bool", "Was the isolate cultured before sequencing?"),
        ]),

    entity(
        "LabIsolate",
        "Isolates created in the lab",
        [field("isolate_id", "foreign key (Isolate)", "The isolate this data pertains to"),
         field("mutations", "string", "A list of the mutations applied to the isolate"),
         field("sdm", "bool", "Was site-directed mutagenesis applied to the isolate?"),

         field("parent_sequence", "foreign key (Sequence)", "The sequence from which this isolate is derived"),
         field("kind", "enum(full-virus, full-replicon, stable-subgenomic, transient-subgenomic)",
               "The kind of isolate created (full synthetic genome, transient subgenomic replicon,"
               "or stable subgenomic cell-line)"),
         field("replicon_passage", "integer", "The passage number (for sub-cultured isolates)"),
        ]),

    entity(
        "Sequence",
        "Sequences and data needed for rapid alignment",
        [field("id", "uuid", "Unique identifier"),
         field("isolate_id", "foreign key (Isolate)", "Isolate the sequence was obtained from"),
         field("seq", "string", "nucleotide sequence"),
         field("reference", "string", "The reference genome this sequence is described with respect to"),
         field("nt_start", "integer", "The starting position of the nucleotide sequence (with respect to the reference)"),
         field("nt-end", "integer", "The end position of the nucleotide sequence (with respect to the reference)"),
         field("nucleotides", "string", "The sequence's raw nucleotide sequence"),
         field("aa_start", "integer", "The starting position of the amino acid sequence (with respect to the reference)"),
         field("aa_end", "integer", "The end position of the amino acid sequence (with respect to the reference)"),
         field("aa_derived", "bool", "Was the amino-acid sequence derived from the nucleotide sequence?"),
         field("amino_acids", "string", "The sequence's raw amino-acid sequence"),
        ]),

    entity(
        "Substitution",
        "A substitution, insertion, or deletion in an RNA sequence",
        [field("id", "uuid", "Unique identifier"),
         field("name", "string", "Name of the substitution"),
         field("reference_sequence", "string", "Name of the consensus wild-type reference sequence"),
         field("position", "integer", "Nucleotide position (with respect to the reference sequence)"),
         field("length", "integer", "Length of the substitution"),
         field("content", "string", "The nucleotide content of the substitution"),
         field("resistance_associated", "bool", "Is this a resistance associated substitution observed in virologic failures in the clinic?"),
        ]),

    entity(
        "SequenceSubstitution",
        "Indicates that the attached sequence has the attached substitution",
        [field("sequence_id", "foreign key (Sequence)", "The sequence being tagged"),
         field("substitution_id", "foreign key (Substitution)", "The substitution identified in the tagged sequence"),
        ]),


    # ==================================================
    # Susceptibility results

    entity(
        "SusceptibilityResult",
        "Susceptibility test results",
        [field("id", "uuid", "Unique id"),
         field("isolate_id", "foreign key (Isolate)", "The isolate being tested"),
         field("reference_id", "foreign key (Reference)", "Source (if applicable)"),
         field("medication_id", "foreign key (Medication)", "The medication being tested"),
         field("method_id", "foreign key (SusceptibilityMethod)", "Name of the susceptibility test method"),
         field("result", "float", "Concentration of medication required for inhibition (in nM)"),
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
