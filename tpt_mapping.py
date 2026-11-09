"""Case 3 - illustrative versioned mapping (NOT a compliant TPT implementation)."""

# V8 codes as stated in the FinDatEx V8 technical annex.
# V7: only the meaning of code 9 ("none") is taken from the annex; other V7 codes
# must be copied from the official V7 template, not guessed.
ISSUER_ID_CODE_TYPE = {
    "V7": {"NONE": "9"},
    "V8": {"LEI": "1", "EXTERNAL": "2", "INTERNAL": "9"},
}
VERSION_LABEL = {"V8": "V8.0 dated 8 October 2026"}   # field 1000 content in V8


def issuer_code_type(id_kind: str, version: str) -> str:
    """Return the code type for the issuer identifier, or fail loudly."""
    table = ISSUER_ID_CODE_TYPE[version]
    if id_kind not in table:
        raise ValueError(f"No {version} code for identifier kind '{id_kind}' - "
                         "check the specification before producing the file")
    return table[id_kind]


def pick_issuer_identifier(lei=None, external=None, internal=None):
    """V8 priority order: LEI, then external identifier, then internal identifier."""
    for kind, value in (("LEI", lei), ("EXTERNAL", external), ("INTERNAL", internal)):
        if value:
            return kind, value
    return "NONE", None
