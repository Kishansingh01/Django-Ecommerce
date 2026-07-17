"""Application configuration for the RAG chatbot app."""
from django.apps import AppConfig


class RagConfig(AppConfig):
    """Django app configuration for the RAG chatbot."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "rag"
    verbose_name = "RAG Chatbot"

    def ready(self) -> None:
        import rag.signals  # noqa