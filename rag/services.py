"""High-level orchestration for the product-catalog RAG chatbot."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from rag.prompts import NO_ANSWER_MESSAGE, build_rag_prompt
from rag.retriever import build_product_context, retrieve_products
from rag.llm import get_chat_llm

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChatResponse:
    """Structured response returned by the chatbot service."""

    answer: str
    sources: list[dict[str, object]]


def _build_sources(retrieved_products) -> list[dict[str, object]]:
    """Serialize retrieved products into a response-friendly structure."""

    sources: list[dict[str, object]] = []
    for product in retrieved_products:
        sources.append(
            {
                "product_id": product.product_id,
                "slug": product.slug,
                "name": product.name,
                "score": product.score,
                "metadata": product.metadata,
            }
        )
    return sources


def answer_product_question(query: str, top_k: int = 5) -> ChatResponse:
    """Answer a user question using only product catalog retrieval context."""

    query = (query or "").strip()
    if not query:
        return ChatResponse(answer=NO_ANSWER_MESSAGE, sources=[])

    retrieved_products = retrieve_products(query, top_k=top_k)
    sources = _build_sources(retrieved_products)
    if not retrieved_products:
        return ChatResponse(answer=NO_ANSWER_MESSAGE, sources=sources)

    context = build_product_context(retrieved_products)
    prompt = build_rag_prompt()
    messages = prompt.format_messages(question=query, context=context)

    logger.info("Sending RAG prompt for query=%r with %s sources", query, len(sources))
    llm = get_chat_llm()
    response = llm.invoke(messages)
    answer = (response.content or "").strip()

    if not answer or answer == NO_ANSWER_MESSAGE:
        return ChatResponse(answer=NO_ANSWER_MESSAGE, sources=sources)

    return ChatResponse(answer=answer, sources=sources)
