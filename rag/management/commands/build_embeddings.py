"""Build the full product embedding index in ChromaDB."""
from __future__ import annotations

import logging

from django.core.management.base import BaseCommand

from rag.embeddings import iter_product_embedding_documents
from rag.vector_store import upsert_product_documents

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Build product embeddings and store them in FAISS."

    def handle(self, *args, **options):
        documents = iter_product_embedding_documents()
        count = upsert_product_documents(documents)
        self.stdout.write(self.style.SUCCESS(f"Built embeddings for {count} products."))
