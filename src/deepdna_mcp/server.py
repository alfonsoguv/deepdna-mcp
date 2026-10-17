"""DeepDNA local MCP server (stdio): the raw DNA file is read on this computer and never sent anywhere."""

from __future__ import annotations

from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import __version__
from .knowledge import KnowledgeUnavailable, curated_variants, drug_gene
from .rawfile import UnsupportedFile, read_raw_file
from .reading import POSITION_NOTE, file_orientation, read_position

INSTRUCTIONS = (
    "DeepDNA local reads a user's raw DNA file (23andMe, AncestryDNA, MyHeritage or FamilyTreeDNA) on this computer and "
    "reports, for the variants DeepDNA curates, what the file shows at each position, with cited records. The file never "
    "leaves this computer: to read it, the package downloads the same public records for every user, and lookup_drug_gene "
    "sends only the gene and drug names. A count at one "
    "position is never a metabolizer status, diplotype, diagnosis or dose, and a missing or unreadable position is "
    "unknown, not normal. Educational information only, not medical advice."
)
PRIVACY = (
    "Read on this computer. deepdna.ai received only the public records it serves to every user, nothing from this file."
)

server = MCPServer(
    name="deepdna-local",
    title="DeepDNA (local file reader)",
    version=__version__,
    instructions=INSTRUCTIONS,
    website_url="https://github.com/alfonsoguv/deepdna-mcp",
)


@server.tool(
    title="Read a raw DNA file on this computer",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
)
def read_dna_file(
    path: str,
    genes: list[str] | None = None,
    sex: Literal["female", "male"] | None = None,
) -> dict[str, Any]:
    """Read the user's raw DNA file (23andMe, AncestryDNA, MyHeritage or FamilyTreeDNA; .txt, .csv or .zip) on this
    computer and report, for each variant DeepDNA curates, what the file shows: read, no-call or not in the file, and,
    for positions that can be read on their own, how many copies of the variant allele, with the record's text and
    sources. The file never leaves this computer. Use `genes` to keep the answer short (for example ["CYP2C19"] before
    discussing clopidogrel). Pass `sex` only if the user gives it: some chromosome X positions (G6PD) need it. A count
    at one position is not a metabolizer status, diplotype, diagnosis or dose: say so, and refer anything that could
    matter for health to a clinician and a validated test."""
    try:
        variants, disclaimer = curated_variants()
    except KnowledgeUnavailable as e:
        raise ToolError(f"{e} The file was not read.") from e
    if genes:
        asked = {g.strip().upper() for g in genes}
        selected = [v for v in variants if v["gene"].upper() in asked]
        unknown = sorted(asked - {v["gene"].upper() for v in variants})
    else:
        selected, unknown = variants, []
    try:
        raw = read_raw_file(path, {v["rsid"] for v in variants})
    except (FileNotFoundError, UnsupportedFile) as e:
        raise ToolError(str(e)) from e
    strand = file_orientation(raw.calls, variants)
    positions = [read_position(v, raw.calls.get(v["rsid"].lower()), strand["strand"], sex) for v in selected]
    states = [p["state"] for p in positions]
    result: dict[str, Any] = {
        "file": {"format": raw.source, "data_lines": raw.data_lines, "orientation": strand},
        "summary": {
            "positions": len(positions),
            "read": states.count("read"),
            "counted": sum(1 for p in positions if p.get("counted")),
            "no_call": states.count("no_call"),
            "not_in_file": states.count("not_in_file"),
        },
        "positions": positions,
        "note": POSITION_NOTE,
        "privacy": PRIVACY,
        "disclaimer": disclaimer,
    }
    if unknown:
        result["genes_not_curated"] = unknown
    return result


@server.tool(
    title="Look up drug-gene guidance",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True),
)
def lookup_drug_gene(gene: str, drug: str | None = None) -> dict[str, Any]:
    """Cited pharmacogenomic guidance for a gene, optionally for one drug, from DeepDNA's public API: the guideline
    (CPIC or DPWG where one exists, otherwise a drug label or the primary literature), a summary and sources. Sends
    only the gene and drug names. Educational information, not a dose or a prescription."""
    try:
        data = drug_gene(gene, drug)
    except KnowledgeUnavailable as e:
        raise ToolError(str(e)) from e
    if not data:
        raise ToolError(f"No curated record for {gene}{' and ' + drug if drug else ''}. Use read_dna_file without genes to see which genes are curated.")
    return data


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
