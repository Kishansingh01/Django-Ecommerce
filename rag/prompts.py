"""Prompt templates for the product-catalog RAG chatbot."""
from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

NO_ANSWER_MESSAGE = "I couldn't find that information in the product catalog."


def build_rag_prompt() -> ChatPromptTemplate:
    """Create the strict catalog-only prompt used by Gemini."""

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a product catalog assistant for an ecommerce website. "
                "Answer only using the provided context from the product catalog. "
                "Do not use outside knowledge, do not guess, and do not mention policies. "
                f"If the answer is not clearly supported by the context, respond exactly with: {NO_ANSWER_MESSAGE}",
            ),
            (
                "human",
                "Question: {question}\n\nCatalog context:\n{context}\n\n"
                "Return a concise helpful answer. If the answer is not present in the context, use the exact fallback sentence.",
            ),
        ]
    )
