"""Retrieve relevant product context from ChromaDB embeddings."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from rag.vector_store import search_similar_products

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedProduct:
    """A single product returned by similarity search."""

    product_id: int | None
    slug: str | None
    name: str | None
    content: str
    metadata: dict[str, Any]
    score: float | None


def retrieve_products(query: str, top_k: int = 5) -> list[RetrievedProduct]:
    """Return the top matching product documents for a user query."""

    if not query.strip():
        return []

    results = search_similar_products(query, top_k=top_k)
    retrieved_products = [
        RetrievedProduct(
            product_id=int(document.metadata.get("product_id")) if document.metadata.get("product_id") else None,
            slug=document.metadata.get("slug"),
            name=document.metadata.get("name"),
            content=document.page_content,
            metadata=document.metadata,
            score=score,
        )
        for document, score in results
    ]
    logger.info("Retrieved %s products for query=%r", len(retrieved_products), query)
    return retrieved_products


def build_product_context(retrieved_products: list[RetrievedProduct]) -> str:
    """Build a compact context block for Gemini from retrieved products."""

    if not retrieved_products:
        return ""

    blocks: list[str] = []
    for index, product in enumerate(retrieved_products, start=1):
        block_lines = [
            f"Product {index}: {product.name or 'Unknown product'}",
            f"Product ID: {product.product_id if product.product_id is not None else 'unknown'}",
        ]
        if product.slug:
            block_lines.append(f"Slug: {product.slug}")
        if product.score is not None:
            block_lines.append(f"Similarity score: {product.score}")
        block_lines.append(product.content)
        blocks.append("\n".join(block_lines))

    return "\n\n".join(blocks)
