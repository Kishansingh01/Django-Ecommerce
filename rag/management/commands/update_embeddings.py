"""Update product embeddings in ChromaDB for active catalog changes."""
from __future__ import annotations

import logging

from django.core.management.base import BaseCommand

from rag.embeddings import build_product_embedding_document, get_embedding_queryset
from rag.vector_store import delete_product_embeddings, upsert_product_documents

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Refresh product embeddings in FAISS for active products."

    def handle(self, *args, **options):
        documents = [build_product_embedding_document(product) for product in get_embedding_queryset()]
        product_ids = [document.product_id for document in documents]
        delete_product_embeddings(product_ids)
        count = upsert_product_documents(documents)
        self.stdout.write(self.style.SUCCESS(f"Updated embeddings for {count} products."))
