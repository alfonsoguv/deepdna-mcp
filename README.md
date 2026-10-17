# DeepDNA MCP server

A remote [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI agents cited pharmacogenomic and gene-variant lookups, so the model quotes CPIC and DPWG guidance instead of recalling it from memory. This repository also holds a [local package](#read-a-raw-dna-file-on-your-own-computer) that reads a raw DNA file on the user's own computer; nothing from the file is sent to DeepDNA.

```text
https://deepdna.ai/mcp
```

Streamable HTTP, stateless, no API key, no account. Listed in the official MCP registry as `ai.deepdna/knowledge`.

> Educational information only, not medical advice. The server reports what curated sources and guidelines say about a gene, a variant or a drug–gene pair. It does not diagnose, prescribe or recommend a dose.

## Tools

| Tool | What it returns |
|---|---|
| `list_genes` | The genes in the knowledge base, with a one-line summary and category for each |
| `lookup_gene` | Everything curated about one gene: function, key variants with rsIDs, phenotypes, drug interactions, what a consumer genotyping array can and cannot tell you, and sources |
| `lookup_variant` | One variant by dbSNP rsID: gene, star-allele or common name, alleles, effect, frequency note, sources, and a `reading` block (plus-strand GRCh37 alleles, `countable`, `strand_ambiguous`). Takes the rsID only, never a genotype |
| `lookup_drug_gene` | Guidance for a gene, optionally for one drug: guideline (CPIC or DPWG where one exists), summary, phenotype groups and sources |
| `check_medications` | Splits a list of generic drug names into drugs with a curated record (gene, and a `basis` field: CPIC or DPWG guideline, drug label, or primary literature) and drugs not covered. Needs no genotype |
| `request_beta_access` | The only tool that writes: registers the user's interest in the private beta (email and optional use case). The agent must ask the user first and set `user_consent: true`. See the [privacy policy](https://deepdna.ai/privacy/) |

Two prompts, `medication_review` and `explain_variant`, package the common questions for clients that show MCP prompts.

Coverage today is 12 genes: CYP2C19, CYP2C9, CYP2D6, SLCO1B1, VKORC1, UGT1A1, G6PD, MTHFR, COMT, HFE, APOE and BRCA1, with 51 curated drug–gene pairs across 11 of them: 40 cite a CPIC or DPWG guideline, the rest a drug label or the primary literature; the `basis` field in `check_medications` says which (`guideline` is null when no guideline exists). It is a small, reviewed set, not a mirror of PharmGKB/ClinPGx. Every record lists its sources. The `level` field (the guideline's evidence grade) is `null` for every pair today.

## Connect

**Claude Code**

```bash
claude mcp add --transport http deepdna https://deepdna.ai/mcp
```

**Cursor** (`~/.cursor/mcp.json`) and other clients that use an `mcpServers` file:

```json
{
  "mcpServers": {
    "deepdna": { "type": "http", "url": "https://deepdna.ai/mcp" }
  }
}
```

**VS Code** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "deepdna": { "type": "http", "url": "https://deepdna.ai/mcp" }
  }
}
```

**Claude Desktop and claude.ai:** add `https://deepdna.ai/mcp` as a custom connector.

## Try it without a client

```bash
curl -s https://deepdna.ai/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"lookup_drug_gene","arguments":{"gene":"CYP2C19","drug":"clopidogrel"}}}'
```

The answer carries the CPIC recommendation for clopidogrel by CYP2C19 metabolizer group, the sources it was written from, and the disclaimer. The same data is available as plain REST, documented in the [API docs](https://deepdna.ai/docs/) and the [OpenAPI spec](https://deepdna.ai/openapi.json):

```text
GET https://deepdna.ai/api/v1/pgx/CYP2C19/clopidogrel
GET https://deepdna.ai/api/v1/variants/rs4244285
```

## Read a raw DNA file on your own computer

The remote server takes no genotype: its tools have no field for one. For a raw DNA file there is a local package in this repository. It reads the file on the user's computer and reports what it shows at each position DeepDNA curates, with the cited records. Nothing from the file is sent to deepdna.ai: the package downloads the same public records for every user, and `lookup_drug_gene` sends only the gene and drug names. What `read_dna_file` returns (the letters and counts at the curated positions) becomes part of the conversation with the AI model your client uses, under that provider's terms.

**Claude Code** (needs [uv](https://docs.astral.sh/uv/) and git):

```bash
claude mcp add deepdna-local -- uvx --from git+https://github.com/alfonsoguv/deepdna-mcp@v0.1.0 deepdna-mcp
```

Clients that use an `mcpServers` file (if the client cannot find `uvx`, put its full path, from `which uvx`, in `command`):

```json
{
  "mcpServers": {
    "deepdna-local": { "command": "uvx", "args": ["--from", "git+https://github.com/alfonsoguv/deepdna-mcp@v0.1.0", "deepdna-mcp"] }
  }
}
```

| Tool | What it returns |
|---|---|
| `read_dna_file` | What a 23andMe, AncestryDNA or MyHeritage/FamilyTreeDNA export (.txt, .csv or .zip) shows at each curated position |
| `lookup_drug_gene` | Guidance for a gene, optionally for one drug, from the public API. Sends only the gene and drug names |

- Each position gets one of four states: `read`, `no_call`, `not_in_file`, or `unexpected_letters` (letters that fit neither the record nor its complement). A missing or unreadable position is unknown, never normal.
- For positions the record marks as `countable` (one chip call is enough to read them), it gives how many copies of the variant allele the file shows, with the record's text and sources.
- `genes` limits the answer to what the user asked about. APOE, BRCA1 and HFE are disease-risk genes: they are read only when named in `genes`.
- `sex` is needed only for some chromosome X positions (G6PD).
- It checks the file's strand first: at least three positions that are not A/T or C/G must agree, and none disagree. A/T and C/G positions, whose two letters look the same on either strand, are counted only on a confirmed strand.

A count at one position is not a metabolizer status, a diplotype, a diagnosis or a dose. The tools tell the model never to suggest starting, stopping or changing a medication: that stays with the prescriber. VCF files are not supported.

Try it with: *"My 23andMe file is at /Users/me/Downloads/genome.txt. What does it show at the CYP2C19 positions DeepDNA curates, and what do the sources say about clopidogrel?"*

## What it is not

- **The remote server does not read DNA files.** Parsing on DeepDNA's servers is specified in the API but is in private beta and not deployed. A remote lookup carries a gene symbol, an rsID or a drug name. Its tools have no genotype field, and an undeclared argument is refused and not used. An agent that reads a raw DNA file itself compares the user's genotype with the `reading` block, outside DeepDNA. The `reading` block gives the reference and variant alleles on the plus strand of GRCh37, as 23andMe raw data reports it.
- **Neither server calls phenotypes or doses.** Turning a genotype into a metabolizer status needs phasing and the other variants in the gene, which a single lookup or a chip file does not give. Tools such as PharmCAT do that from a VCF.
- **Remote usage is counted, people are not.** Each request to the remote server is counted (method, tool, the lookup label described below, whether there was an answer, the client's name and version, its user-agent, a country code). IP addresses, request bodies and medication lists are not stored. A value typed into a declared field is recorded only as a short lookup label: an rsID in the form rs123, a gene from a fixed list of known pharmacogenes, or a drug DeepDNA covers; anything else, whatever it is, is recorded as "(other)". Please don't type a personal genetic result into these fields. The one exception is `request_beta_access`: it keeps the email and use case the user agrees to send, the signup metadata listed in the [privacy policy](https://deepdna.ai/privacy/) (time, source, country code and the client's name), and a hashed IP for one hour to limit abuse. The local package's downloads are ordinary requests to the public API, with the user-agent `deepdna-mcp-local/<version>`.
- **A consumer chip is not a clinical test.** Arrays are reliable for common variants and much less so for rare ones; anything that could affect a health decision needs a validated test and a clinician.

## Links

- Docs: <https://deepdna.ai/docs/#mcp>
- Walkthrough with real outputs: <https://deepdna.ai/blog/pharmacogenomics-mcp-server/>
- Worked example in Python, where your own code goes from a raw DNA file to CPIC phenotypes (neither server does this step): <https://deepdna.ai/blog/pharmacogenomics-raw-dna-python/>
- Terms: <https://deepdna.ai/terms/> · Privacy: <https://deepdna.ai/privacy/>

This repository holds the documentation and the local package; the remote server is hosted by DeepDNA. Questions and bug reports go in the issues; please don't post a raw DNA file, genotypes or medications there.

<sub>Written with AI assistance.</sub>
