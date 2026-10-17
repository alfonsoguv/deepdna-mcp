"""DeepDNA local MCP server (stdio): the raw DNA file is read on this computer and nothing from it is sent to deepdna.ai."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from . import __version__
from .knowledge import KnowledgeUnavailable, curated_genes, curated_variants, drug_gene
from .rawfile import UnsupportedFile, read_raw_file
from .reading import POSITION_NOTE, file_orientation, read_position

# Disease-risk genes, not pharmacogenes: read only when the user names them (the right not to know).
ONLY_WHEN_NAMED = {"APOE", "BRCA1", "HFE"}

INSTRUCTIONS = (
    "DeepDNA local reads a user's raw DNA file (23andMe, AncestryDNA, MyHeritage or FamilyTreeDNA) on this computer and "
    "reports, for the variants DeepDNA curates, what the file shows at each position, with cited records. Nothing from "
    "the file is sent to deepdna.ai: the package downloads the same public records for every user, and lookup_drug_gene "
    "sends only the gene and drug names. What read_dna_file returns becomes part of this conversation with the AI model, "
    "so do not tell the user their genetic data stays on their computer. A count at one position is never a metabolizer "
    "status, diplotype, diagnosis or dose, and a missing or unreadable position is unknown, not normal. Never place the "
    "user in a metabolizer or phenotype group, and never suggest starting, stopping, switching or changing the dose of a "
    "medication: that is for the prescriber, with a validated test. Educational information only, not medical advice."
)
PRIVACY = (
    "Read on this computer. deepdna.ai was asked only for the public records it serves to every user; nothing from this "
    "file was sent to it. This result is part of the conversation with the AI model."
)
SOURCE = "DeepDNA knowledge API, https://deepdna.ai/docs/"

server = MCPServer(
    name="deepdna-local",
    title="DeepDNA local",
    version=__version__,
    instructions=INSTRUCTIONS,
    website_url="https://github.com/alfonsoguv/deepdna-mcp",
)


@server.tool(
    title="Read a raw DNA file on this computer",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True),
)
def read_dna_file(
    path: Annotated[str, Field(description="Full path to the raw DNA file on this computer, e.g. /Users/name/Downloads/genome.txt")],
    genes: Annotated[list[str] | None, Field(description='Gene symbols the user asked about, e.g. ["CYP2C19"]')] = None,
    sex: Annotated[Literal["female", "male"] | None, Field(description="Only if the user gives it: some chromosome X positions (G6PD) need it")] = None,
) -> dict[str, Any]:
    """Read the user's raw DNA file (23andMe, AncestryDNA, MyHeritage or FamilyTreeDNA; .txt, .csv or .zip) on this
    computer and report, for each curated variant, one of four states: read, no_call, not_in_file, or unexpected_letters
    (the file's letters fit neither the record nor its complement). For positions the record marks as countable it gives
    how many copies of the variant allele the file shows, with the record's text and sources. Pass `genes` for what the
    user asked about (for example ["CYP2C19"] before discussing clopidogrel). APOE, BRCA1 and HFE are disease-risk
    genes: they are read only when named in `genes`, so do not offer or report them unless the user asks for them by
    name. A count at one position is not a metabolizer status, diplotype, diagnosis or dose: say so, and refer anything
    that could matter for health to a clinician and a validated test."""
    try:
        variants, disclaimer = curated_variants()
    except KnowledgeUnavailable as e:
        raise ToolError(f"The file was not read. {e}") from e
    asked = {g.strip().upper() for g in genes or []}
    pool = [v for v in variants if v["gene"].upper() not in ONLY_WHEN_NAMED or v["gene"].upper() in asked]
    selected = [v for v in pool if v["gene"].upper() in asked] if asked else pool
    unknown = sorted(asked - {v["gene"].upper() for v in variants})
    try:
        raw = read_raw_file(path, {v["rsid"] for v in pool})
    except (FileNotFoundError, UnsupportedFile) as e:
        raise ToolError(str(e)) from e
    strand = file_orientation(raw.calls, pool)
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
            "unexpected_letters": states.count("unexpected_letters"),
        },
        "positions": positions,
        "note": POSITION_NOTE,
        "privacy": PRIVACY,
        "source": SOURCE,
        "disclaimer": disclaimer,
    }
    not_read = sorted(ONLY_WHEN_NAMED - asked)
    if not_read:
        result["not_read"] = {"genes": not_read, "why": "Disease-risk genes are read only when the user names them. "
                              "Do not mention them unless the user asks about them."}
    if unknown:
        result["genes_not_curated"] = unknown
    return result


@server.tool(
    title="Look up drug-gene guidance",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True),
)
def lookup_drug_gene(
    gene: Annotated[str, Field(description='Gene symbol, e.g. "CYP2C19"')],
    drug: Annotated[str | None, Field(description='Generic drug name, e.g. "clopidogrel"')] = None,
) -> dict[str, Any]:
    """Cited pharmacogenomic guidance for a gene, optionally for one drug, from DeepDNA's public API: the guideline
    (CPIC or DPWG where one exists, otherwise a drug label or the primary literature), a summary and sources. Sends
    only the gene and drug names. The phenotype groups it lists are the guideline's own: do not place the user in one
    from read_dna_file counts. Educational information, not a dose or a prescription."""
    try:
        data = drug_gene(gene, drug)
        if data:
            return data
        curated = curated_genes()
    except KnowledgeUnavailable as e:
        raise ToolError(str(e)) from e
    if gene.strip().upper() not in curated:
        raise ToolError(f"{gene} is not one of the genes DeepDNA curates: {', '.join(curated)}.")
    if drug:
        raise ToolError(f"DeepDNA has no curated record for {drug} with {gene}. Call lookup_drug_gene with only the gene to see the drugs it covers.")
    raise ToolError(f"DeepDNA has no curated drug-gene record for {gene}.")


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
