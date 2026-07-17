"""Build embedding-ready product documents from the existing catalog."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable

from django.db.models import Prefetch, QuerySet

from products.models import Product, Review

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProductEmbeddingDocument:
    """Normalized product payload used for embedding and retrieval."""

    product_id: int
    slug: str
    title: str
    content: str
    metadata: dict[str, Any]


def _format_price(value: Any) -> str:
    """Render a price consistently for text embedding."""

    if value is None:
        return "unknown"
    if isinstance(value, Decimal):
        return f"₹{value:.2f}"
    return str(value)


def _optional_value(obj: Any, candidate_names: Iterable[str]) -> Any:
    """Return the first non-empty attribute found on an object."""

    for name in candidate_names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value not in (None, "", [], {}, ()):
                return value
    return None


def _format_review(review: Review) -> str:
    """Turn a review into a compact text fragment."""

    title = review.title.strip() if review.title else ""
    comment = review.comment.strip() if review.comment else ""
    author = review.user.username if review.user_id else "anonymous"
    parts = [f"rating={review.rating}", f"author={author}"]
    if title:
        parts.append(f"title={title}")
    if comment:
        parts.append(f"comment={comment}")
    return "; ".join(parts)


def build_product_content(product: Product) -> str:
    """Build the canonical text block used to create embeddings for a product."""

    brand = _optional_value(product, ("brand", "manufacturer", "maker"))
    specifications = _optional_value(product, ("specifications", "specs", "technical_specs", "features"))
    category_name = product.category.name if product.category_id and product.category else "unknown"
    availability = "in stock" if product.is_available() else "out of stock"

    parts = [
        f"Product name: {product.name}",
        f"Description: {product.description}",
        f"Category: {category_name}",
        f"Price: {_format_price(product.price)}",
        f"Stock availability: {availability}",
    ]

    if brand:
        parts.append(f"Brand: {brand}")
    if specifications:
        parts.append(f"Specifications: {specifications}")

    reviews = [review for review in product.reviews.all() if review.is_approved]
    if reviews:
        parts.append("Reviews: " + " | ".join(_format_review(review) for review in reviews[:5]))

    return "\n".join(parts)


def get_embedding_queryset() -> QuerySet[Product]:
    """Return products with the related data needed to build embeddings."""

    approved_reviews = Review.objects.filter(is_approved=True).select_related("user")
    return (
        Product.objects.select_related("category")
        .prefetch_related(Prefetch("reviews", queryset=approved_reviews))
        .filter(is_active=True)
    )


def build_product_embedding_document(product: Product) -> ProductEmbeddingDocument:
    """Convert a product into a text document plus metadata for ChromaDB."""

    content = build_product_content(product)
    metadata: dict[str, Any] = {
        "product_id": product.id,
        "slug": product.slug,
        "name": product.name,
        "category": product.category.name if product.category_id and product.category else None,
        "price": str(product.price),
        "stock": product.stock,
        "is_active": product.is_active,
        "is_featured": product.is_featured,
        "source": "django_orm",
    }

    brand = _optional_value(product, ("brand", "manufacturer", "maker"))
    specifications = _optional_value(product, ("specifications", "specs", "technical_specs", "features"))
    if brand is not None:
        metadata["brand"] = brand
    if specifications is not None:
        metadata["specifications"] = specifications

    return ProductEmbeddingDocument(
        product_id=product.id,
        slug=product.slug,
        title=product.name,
        content=content,
        metadata=metadata,
    )


def iter_product_embedding_documents() -> list[ProductEmbeddingDocument]:
    """Load all products and convert them into embedding documents."""

    documents: list[ProductEmbeddingDocument] = []
    for product in get_embedding_queryset():
        documents.append(build_product_embedding_document(product))
    logger.info("Prepared %s product documents for embedding", len(documents))
    return documents