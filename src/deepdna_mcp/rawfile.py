"""Read a consumer raw DNA file on this computer.

Nothing in this module touches the network. Only the rsIDs asked for are kept
in memory, and nothing is written to disk.
"""

from __future__ import annotations

import csv
import io
import os
import zipfile
from dataclasses import dataclass

MAX_BYTES = 300 * 1024 * 1024
NO_CALLS = {"", "-", "--", "0", "00", "??", "NC"}


class UnsupportedFile(ValueError):
    """The file is not a raw DNA export this package can read."""


@dataclass(frozen=True)
class Call:
    chromosome: str
    genotype: str  # letters as written in the file ("AG", "A", "DI"); "" when the chip could not read it


@dataclass(frozen=True)
class RawFile:
    source: str
    data_lines: int
    calls: dict[str, Call]  # only the rsIDs that were asked for


def _chromosome(value: str) -> str:
    c = value.strip().upper().removeprefix("CHR")
    return {"23": "X", "24": "Y", "25": "X", "26": "MT", "M": "MT", "XY": "X"}.get(c, c)


def _genotype(value: str) -> str:
    g = value.strip().strip('"').upper().replace("/", "").replace(" ", "")
    return "" if g in NO_CALLS else g


TOO_LARGE = "The file is larger than 300 MB; a raw DNA export is usually under 30 MB."


def _text(path: str) -> str:
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No file at {path}. Pass the full path to the file, for example /Users/name/Downloads/genome.txt.")
    if os.path.getsize(path) > MAX_BYTES:
        raise UnsupportedFile(TOO_LARGE)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith((".txt", ".csv")) and not n.startswith("__MACOSX/")]
            if not names:
                raise UnsupportedFile("The zip file has no .txt or .csv inside.")
            if z.getinfo(names[0]).file_size > MAX_BYTES:
                raise UnsupportedFile(TOO_LARGE)
            with z.open(names[0]) as f:
                data = f.read(MAX_BYTES + 1)  # the declared size can lie
            if len(data) > MAX_BYTES:
                raise UnsupportedFile(TOO_LARGE)
            return data.decode("utf-8-sig", errors="replace")
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def read_raw_file(path: str, wanted: set[str]) -> RawFile:
    """Parse a 23andMe, AncestryDNA or MyHeritage/FamilyTreeDNA export, keeping only the rsIDs in `wanted`."""
    text = _text(path)
    if text.lstrip().startswith("##fileformat=VCF"):
        raise UnsupportedFile("VCF files are not supported: this package reads consumer raw data exports (23andMe, AncestryDNA, MyHeritage or FamilyTreeDNA).")
    lines = text.splitlines()
    first = next((l for l in lines if l.strip() and not l.startswith("#")), "")
    header = first.replace('"', "").replace(" ", "").lower()
    wanted = {w.lower() for w in wanted}
    calls: dict[str, Call] = {}
    data_lines = 0

    if header.startswith("rsid,chromosome,position,result"):
        source = "MyHeritage or FamilyTreeDNA (CSV)"
        rows = csv.reader(io.StringIO("\n".join(l for l in lines if l.strip() and not l.startswith("#"))))
        next(rows, None)
        for row in rows:
            if len(row) < 4:
                continue
            data_lines += 1
            rsid = row[0].strip().lower()
            if rsid in wanted:
                calls[rsid] = Call(_chromosome(row[1]), _genotype(row[3]))
    elif header.startswith("rsid\tchromosome\tposition\tallele1\tallele2"):
        source = "AncestryDNA"
        for line in lines[lines.index(first) + 1:]:
            parts = line.split("\t")
            if len(parts) < 5 or line.startswith("#"):
                continue
            data_lines += 1
            rsid = parts[0].strip().lower()
            if rsid in wanted:
                a1, a2 = parts[3].strip(), parts[4].strip()
                calls[rsid] = Call(_chromosome(parts[1]), "" if "0" in (a1, a2) else _genotype(a1 + a2))
    elif len(first.split("\t")) == 4:
        source = "23andMe" if "23andme" in text[:4000].lower() else "four-column raw data (rsid, chromosome, position, genotype)"
        for line in lines:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 4:
                continue
            data_lines += 1
            rsid = parts[0].strip().lower()
            if rsid in wanted:
                calls[rsid] = Call(_chromosome(parts[1]), _genotype(parts[3]))
    else:
        raise UnsupportedFile("Unrecognized file. Supported: 23andMe (.txt), AncestryDNA (.txt), MyHeritage or FamilyTreeDNA (.csv), or a .zip with one of them.")

    if data_lines == 0:
        raise UnsupportedFile("The file has no genotype rows.")
    return RawFile(source=source, data_lines=data_lines, calls=calls)
