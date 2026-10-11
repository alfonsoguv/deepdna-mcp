# DeepDNA MCP server

A remote [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI agents cited pharmacogenomic and gene-variant lookups, so the model quotes CPIC and DPWG guidance instead of recalling it from memory.

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
| `lookup_variant` | One variant by dbSNP rsID: gene, star-allele or common name, alleles, functional effect, population frequency note and sources. Optionally takes the genotype at that position and counts copies of the variant allele; it never turns that into a phenotype, metabolizer status or risk, and the genotype is not stored |
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

## What it is not

- **It does not read DNA files.** Parsing consumer raw data (23andMe, AncestryDNA, MyHeritage) is specified in the API but is in private beta and not deployed. A lookup carries a gene symbol, an rsID, a drug name or one genotype.
- **It does not call phenotypes or doses.** Turning a genotype into a metabolizer status needs phasing and the other variants in the gene, which a single lookup does not have. Tools such as PharmCAT do that from a VCF.
- **Usage is counted, people are not.** Each request is counted (method, tool, the gene, rsID or drug looked up, whether there was an answer, the client's name and user-agent, a country code). IP addresses, request bodies, medication lists and genotypes are not stored; the one exception is `request_beta_access`, which keeps the email and use case the user agrees to send, and a hashed IP for one hour to limit abuse.
- **A consumer chip is not a clinical test.** Arrays are reliable for common variants and much less so for rare ones; anything that could affect a health decision needs a validated test and a clinician.

## Links

- Docs: <https://deepdna.ai/docs/#mcp>
- Walkthrough with real outputs: <https://deepdna.ai/blog/pharmacogenomics-mcp-server/>
- Worked example in Python, where your own code goes from a raw DNA file to CPIC phenotypes (the server does not do this step): <https://deepdna.ai/blog/pharmacogenomics-raw-dna-python/>
- Terms: <https://deepdna.ai/terms/> · Privacy: <https://deepdna.ai/privacy/>

This repository holds documentation and examples only; the server is hosted by DeepDNA. Issues and questions about the tools are welcome here.

<sub>Written with AI assistance.</sub>
