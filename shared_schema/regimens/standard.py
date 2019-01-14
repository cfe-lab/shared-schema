"""Record standard compounds and treatment regimens"""

_compounds = [
    ("asunaprevir", "asv"),
    ("boceprevir", "boc"),
    ("daclatasvir", "dcv"),
    ("dasabuvir", "das"),
    ("elbasvir", "ebr"),
    ("glecaprevir", "glp"),
    ("grazoprevir", "gzr"),
    ("ledipasvir", "ldv"),
    ("ombitasvir", "omb"),
    ("paritaprevir", "par"),
    ("pegylated interferon", "peg"),
    ("pibrentasvir", "pib"),
    ("ribavirin", "rbv"),
    ("ritonavir", "rit"),
    ("simeprevir", "sim"),
    ("sofosbuvir", "sof"),
    ("telaprevir", "tvr"),
    ("vaniprevir", "van"),
    ("velpatasvir", "vel"),
    ("voxilaprevir", "vox"),
]
compounds = {cmpnd: abbr for cmpnd, abbr in _compounds}
compound_keys = ("compound", "abbreviation")

_freqs = [
    ("qd", "once daily"),
    ("bid", "twice daily"),
    ("tid", "three times daily"),
    ("qid", "four times daily"),
    ("qwk", "weekly"),
]
freqs = {abbr: desc for abbr, desc in _freqs}
freq_keys = ("abbreviation", "description")

_regimens = [
    ("DAKLINZA", "60mg dcv qd 12 weeks"),
    ("EPCLUSA", "(400mg sof + 100mg vel) qd 12 weeks"),
    ("HARVONI", "(90mg ldv + 400mg sof) qd 12 weeks"),
    ("INCIVEK", "750mg tvr tid 12 weeks"),
    ("MAVYRET", "(300mg glp + 120mg pib) qd 12 weeks"),
    ("OLYSIO", "150mg sim qd 12 weeks"),
    ("SOVALDI", "400mg sof qd 12 weeks"),
    ("SUNVEPRA", "100mg asv bid 24 weeks"),
    ("TECHNIVIE", "(25mg omb + 150mg par + 100mg rit) qd 12 weeks"),
    ("VICTRELIS", "800mg boc tid 32 weeks"),
    (
        "VIEKIRA PAK",
        "250mg das bid & (250mg omb + 150mg par + 100mg rit) qd 12 weeks",
    ),
    (
        "VIEKIRA XR",
        "(600mg das + 25mg omb + 150mg par +100mg rit) qd 12 weeks",
    ),
    ("VOSEVI", "(400mg sof + 100mg vel + 100mg vox) qd 12 weeks"),
    ("ZEPATIER", "(50mg ebr + 100mg gzr) qd 12 weeks"),
    ("PEGASYS", "0.180mg peg qwk 48 weeks"),
    ("COPEGUS1000", "500mg rbv bid 48 weeks"),
    ("COPEGUS1200", "600mg rbv bid 48 weeks"),
]
regimens = {name: reg for name, reg in _regimens}
regimen_keys = ("name", "regimen")


def expand(src):
    """Replace standard regimen names with their contents.

    This function searchs a regimen source string for standard regimen
    names and replaces them with the long form of their contents, as
    understood by the grammar.
    """
    for name, explicit in regimens.items():
        if name in src:
            src = src.replace(name, explicit)
    return src
