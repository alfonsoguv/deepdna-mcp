# DeepDNA local

Reads a raw DNA file on your own computer and reports what it shows at the pharmacogenomic positions DeepDNA curates, with the cited record for each one. It adds one local MCP server, `deepdna-local`, to Claude Code and to Cowork sessions that run on your computer. Chat on claude.ai does not start local servers; for chat, use the DeepDNA connector (`https://deepdna.ai/mcp`), which looks up genes, variants and drugs but never reads a DNA file.

> Educational information only, not medical advice. A count at one position is not a metabolizer status, a diplotype, a diagnosis or a dose. Decisions about a medication stay with the prescriber, with a validated test.

## What it runs

The plugin starts the open-source package [`deepdna-mcp`](https://pypi.org/project/deepdna-mcp/) 0.1.1 from PyPI with `uvx deepdna-mcp==0.1.1`. It needs [uv](https://docs.astral.sh/uv/) on your computer. The source is in this repository, under `src/deepdna_mcp/`, MIT licensed.

## Use it

Ask Claude, for example: *"My 23andMe file is at /Users/me/Downloads/genome.txt. What does it show at the CYP2C19 positions DeepDNA curates, and what do the sources say about clopidogrel?"*

| Tool | What it returns |
|---|---|
| `read_dna_file` | What a 23andMe, AncestryDNA or MyHeritage/FamilyTreeDNA export (.txt, .csv or .zip) shows at each curated position |
| `lookup_drug_gene` | Guidance for a gene, optionally for one drug, from DeepDNA's public API, with sources |

- Each position is `read`, `no_call`, `not_in_file` or `unexpected_letters`. A missing or unreadable position is unknown, never normal.
- APOE, BRCA1 and HFE are disease-risk genes: they are read only when you name them, so you choose what to learn.
- The file's strand is checked before any A/T or C/G position is counted.
- VCF files are not supported.

## Data

- **Your DNA file stays on your computer.** The package reads it locally and sends nothing from it to DeepDNA or anyone else. It writes nothing to disk.
- **What it fetches:** at the start of each session it downloads the same public records for every user from `https://deepdna.ai/api/v1` (the list of curated genes, each gene's record and each curated variant's record). `lookup_drug_gene` sends only a gene symbol and a drug name. These requests carry the user-agent `deepdna-mcp-local/0.1.1` and are counted like any other request to the public API, as the [privacy policy](https://deepdna.ai/privacy/) describes.
- **What reaches the AI model:** what `read_dna_file` returns (the letters and counts at the curated positions) becomes part of your conversation with Claude, under Anthropic's terms.

## Links

- Step-by-step walkthrough: <https://deepdna.ai/blog/read-23andme-file-with-claude/>
- Terms: <https://deepdna.ai/terms/> · Privacy: <https://deepdna.ai/privacy/>
- Issues: <https://github.com/alfonsoguv/deepdna-mcp/issues> (please don't post a DNA file, genotypes or medications there)
