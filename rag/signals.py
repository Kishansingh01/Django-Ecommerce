import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from products.models import Product, Review
from rag.embeddings import build_product_embedding_document
from rag.vector_store import upsert_product_documents, delete_product_embeddings

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def product_post_save(sender, instance, **kwargs):
    """Automatically update the vector store when a product is saved."""
    try:
        if instance.is_active:
            logger.info("Automatically updating vector store embedding for Product ID: %s", instance.id)
            document = build_product_embedding_document(instance)
            upsert_product_documents([document])
        else:
            # If product is deactivated, remove it from vector store
            logger.info("Deactivated Product ID: %s. Removing from vector store.", instance.id)
            delete_product_embeddings([instance.id])
    except Exception as exc:
        logger.warning("Failed to auto-update vector store for product %s: %s", instance.id, exc)

@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
    """Automatically remove the product from vector store when deleted."""
    try:
        logger.info("Deleted Product ID: %s. Removing from vector store.", instance.id)
        delete_product_embeddings([instance.id])
    except Exception as exc:
        logger.warning("Failed to auto-delete vector store for product %s: %s", instance.id, exc)

@receiver(post_save, sender=Review)
def review_post_save(sender, instance, **kwargs):
    """Automatically update the product vector embedding when a review changes."""
    try:
        product = instance.product
        if product.is_active:
            logger.info("Review updated/created for Product ID: %s. Rebuilding product embedding.", product.id)
            document = build_product_embedding_document(product)
            upsert_product_documents([document])
    except Exception as exc:
        logger.warning("Failed to update vector store for review %s: %s", instance.id, exc)

@receiver(post_delete, sender=Review)
def review_post_delete(sender, instance, **kwargs):
    """Automatically update the product vector embedding when a review is deleted."""
    try:
        product = instance.product
        if product.is_active:
            logger.info("Review deleted for Product ID: %s. Rebuilding product embedding.", product.id)
            document = build_product_embedding_document(product)
            upsert_product_documents([document])
    except Exception as exc:
        logger.warning("Failed to update vector store for deleted review: %s", exc)
