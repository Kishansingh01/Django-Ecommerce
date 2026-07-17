"""Database models for persisted RAG embeddings."""
from __future__ import annotations

from django.db import models

from products.models import Product


class ProductEmbedding(models.Model):
    """Persist the embedding and document text for a product catalog entry."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="rag_embedding",
    )
    content = models.TextField()
    embedding = models.JSONField()
    metadata = models.JSONField(default=dict)
    embedding_model = models.CharField(max_length=100)
    content_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product_id"]

    def __str__(self) -> str:
        return f"Embedding for {self.product_id} - {self.product.name}"
