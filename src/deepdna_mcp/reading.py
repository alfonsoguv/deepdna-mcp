"""What a raw DNA file shows at each curated position, read on this computer.

The rules come from the genomics review in alfonsoguv/deepdna#591:
- a position missing from the file, or a no-call, is unknown, never "normal";
- only positions whose record says `countable` are counted, and only single bases;
- A/T and C/G positions are counted only when the file's strand is confirmed;
- chromosome X needs the person's sex unless the letters settle it;
- a count is per position: never a star allele, diplotype, metabolizer status or risk.
"""

from __future__ import annotations

from typing import Any

from .rawfile import Call

COMPLEMENT = str.maketrans("ACGT", "TGCA")

POSITION_NOTE = (
    "Counts are per position. They are not a star-allele, diplotype, metabolizer status or risk: phasing, "
    "other variants in the gene and copy-number changes are not considered. A missing or unreadable position "
    "is unknown, not normal. A chip call of a rare pathogenic variant needs a validated clinical test."
)


def _single_bases(r: dict[str, Any]) -> tuple[str, str] | None:
    ref, var = r.get("reference_allele"), r.get("variant_allele")
    if isinstance(ref, str) and isinstance(var, str) and len(ref) == 1 and len(var) == 1:
        return ref, var
    return None


def file_orientation(calls: dict[str, Call], variants: list[dict[str, Any]]) -> dict[str, Any]:
    """Check the file's strand on the non-ambiguous positions: plus, minus, or unconfirmed."""
    plus = minus = 0
    for v in variants:
        r = v["reading"]
        bases = _single_bases(r)
        call = calls.get(v["rsid"].lower())
        if not bases or r.get("strand_ambiguous") or not call or not call.genotype or not set(call.genotype) <= set("ACGT"):
            continue
        ref, var = bases
        letters = set(call.genotype)
        if letters <= {ref, var}:
            plus += 1
        elif letters <= {ref.translate(COMPLEMENT), var.translate(COMPLEMENT)}:
            minus += 1
    strand = "plus" if plus >= 3 and minus == 0 else "minus" if minus >= 3 and plus == 0 else "unconfirmed"
    return {"strand": strand, "positions_checked": plus + minus, "matching_plus": plus, "matching_minus": minus}


def read_position(v: dict[str, Any], call: Call | None, strand: str, sex: str | None) -> dict[str, Any]:
    """One curated variant as the file shows it."""
    r = v["reading"]
    out: dict[str, Any] = {"rsid": v["rsid"], "gene": v["gene"], "name": v.get("name")}

    def done(**fields: Any) -> dict[str, Any]:
        out.update(fields)
        out.update(record_alleles=v.get("alleles"), effect=v.get("effect"), sources=v.get("sources", []))
        return out

    if call is None:
        return done(state="not_in_file", counted=False, note="This position is not in the file: unknown, not normal.")
    if not call.genotype:
        return done(state="no_call", counted=False, note="The chip could not read this position: unknown, not normal.")
    letters = call.genotype
    out.update(state="read", letters=letters)
    bases = _single_bases(r)
    if not r.get("countable") or not bases:
        return done(counted=False, note="Not counted: this position can't be read on its own (see record_alleles).")
    if not set(letters) <= set("ACGT"):
        return done(counted=False, note="Not counted: the file reports an insertion or deletion here, not single bases.")
    ref, var = bases
    plus_fit = set(letters) <= {ref, var}
    minus_fit = set(letters) <= {ref.translate(COMPLEMENT), var.translate(COMPLEMENT)}
    if r.get("strand_ambiguous"):
        if strand == "unconfirmed":
            return done(counted=False, note="Not counted: an A/T or C/G position, and the file's strand could not be confirmed.")
        seen = letters if strand == "plus" else letters.translate(COMPLEMENT)
    elif plus_fit and strand != "minus":
        seen = letters
    elif minus_fit and strand != "plus":
        seen = letters.translate(COMPLEMENT)
    else:
        return done(state="unexpected_letters", counted=False,
                    note=f"Not counted: the file's letters do not match this record ({ref}>{var} on the plus strand of GRCh37).")
    out.update(reference_allele=ref, variant_allele=var)

    if r.get("chromosome") == "X":
        if len(seen) == 1 or (sex == "male" and seen[0] == seen[-1]):
            return done(counted=True, variant_allele_copies=int(seen[0] == var), x_copies=1,
                        note="Chromosome X, one copy.")
        if sex == "male":
            return done(counted=False, note="Not counted: two different letters on chromosome X for a male. Check the file.")
        if seen[0] != seen[1] or sex == "female":
            return done(counted=True, variant_allele_copies=seen.count(var), x_copies=2, note="Chromosome X, two copies.")
        return done(counted=False, note="Not counted: on chromosome X two identical letters can mean one copy or two. Pass sex to count it.")
    if len(seen) != 2:
        return done(counted=False, note="Not counted: expected two letters at this position.")
    return done(counted=True, variant_allele_copies=seen.count(var))
