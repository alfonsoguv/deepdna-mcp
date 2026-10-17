"""DeepDNA's public knowledge API, read-only.

The requests are the same for every user: the gene list, each gene's record and
each curated variant's record. Nothing about the user's file is ever sent.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Any
from urllib.parse import quote

import httpx

from . import __version__

API = "https://deepdna.ai/api/v1"
USER_AGENT = f"deepdna-mcp-local/{__version__} (+https://github.com/alfonsoguv/deepdna-mcp)"


class KnowledgeUnavailable(RuntimeError):
    """deepdna.ai could not be reached or answered with an error."""


def _get(client: httpx.Client, path: str) -> dict[str, Any]:
    try:
        r = client.get(API + path)
    except httpx.HTTPError as e:
        raise KnowledgeUnavailable("Could not reach deepdna.ai to download the public records. "
                                   "Check the internet connection and try again.") from e
    if r.status_code == 404:
        return {}
    if r.status_code != 200:
        raise KnowledgeUnavailable(f"deepdna.ai answered {r.status_code} for {path}.")
    return r.json()


def _client() -> httpx.Client:
    return httpx.Client(timeout=20, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})


@lru_cache(maxsize=1)
def curated_genes() -> list[str]:
    """The gene symbols DeepDNA curates. Fetched once per session."""
    with _client() as client:
        return [g["symbol"] for g in _get(client, "/genes").get("genes", [])]


@lru_cache(maxsize=1)
def curated_variants() -> tuple[list[dict[str, Any]], str]:
    """Every curated variant with its reading block, and the API's disclaimer. Fetched once per session."""
    genes = curated_genes()
    with _client() as client:
        with ThreadPoolExecutor(max_workers=6) as pool:
            gene_records = list(pool.map(lambda s: _get(client, f"/genes/{quote(s)}"), genes))
            rsids = sorted({k["rsid"] for g in gene_records for k in g.get("gene", {}).get("key_variants", []) if k.get("rsid")})
            records = list(pool.map(lambda rs: _get(client, f"/variants/{quote(rs)}"), rsids))
    variants = [r["variant"] for r in records if r.get("variant", {}).get("reading")]
    disclaimer = next((r["meta"]["disclaimer"] for r in records if r.get("meta", {}).get("disclaimer")), "")
    if not variants:
        raise KnowledgeUnavailable("deepdna.ai returned no curated variants.")
    return variants, disclaimer


def drug_gene(gene: str, drug: str | None) -> dict[str, Any]:
    """CPIC or DPWG guidance for a gene, optionally for one drug, as the public API returns it."""
    if not any(c.isalnum() for c in gene) or (drug is not None and not any(c.isalnum() for c in drug)):
        return {}  # ".." would otherwise be resolved as a path segment
    path = f"/pgx/{quote(gene.strip().upper(), safe='')}" + (f"/{quote(drug.strip().lower(), safe='')}" if drug else "")
    with _client() as client:
        return _get(client, path)
