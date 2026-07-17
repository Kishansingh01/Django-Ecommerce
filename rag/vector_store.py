"""Persistent FAISS storage for product embeddings."""
from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from django.conf import settings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from rag.embeddings import ProductEmbeddingDocument

logger = logging.getLogger(__name__)

INDEX_DIR_NAME = "product_catalog_faiss"
MANIFEST_FILE_NAME = "documents.json"


def get_gemini_api_key() -> str:
    """Return the Gemini API key from the environment."""

    api_key = getattr(settings, "GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required for the RAG chatbot")
    return api_key


def get_chat_model_name() -> str:
    """Return the configured Gemini chat model name."""

    return getattr(settings, "CHAT_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"


def get_embedding_model_name() -> str:
    """Return the configured Gemini embedding model name."""

    return getattr(settings, "EMBEDDING_MODEL", "gemini-embedding-001").strip() or "gemini-embedding-001"


def get_faiss_db_path() -> Path:
    """Return the persistent FAISS storage path."""

    configured_path = getattr(settings, "FAISS_INDEX_PATH", "").strip()
    if configured_path:
        return Path(configured_path)
    return Path(settings.BASE_DIR) / "faiss_db"


def get_embeddings_client():
    """Create the Gemini embeddings client used by LangChain."""
    from langchain_core.embeddings import FakeEmbeddings

    try:
        api_key = get_gemini_api_key()
        return GoogleGenerativeAIEmbeddings(
            model=get_embedding_model_name(),
            google_api_key=api_key,
        )
    except ValueError:
        logger.warning("GEMINI_API_KEY is not set. Falling back to FakeEmbeddings.")
        return FakeEmbeddings(size=768)



def get_faiss_index_directory() -> Path:
    """Return the directory that stores the FAISS index files."""

    return get_faiss_db_path() / INDEX_DIR_NAME


def get_manifest_path() -> Path:
    """Return the manifest path used to rebuild the FAISS index."""

    return get_faiss_index_directory() / MANIFEST_FILE_NAME


def _document_to_payload(document: ProductEmbeddingDocument) -> dict[str, object]:
    payload = asdict(document)
    payload["product_id"] = int(document.product_id)
    return payload


def _payload_to_document(payload: dict[str, object]) -> ProductEmbeddingDocument:
    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = dict(metadata)
    return ProductEmbeddingDocument(
        product_id=int(payload["product_id"]),
        slug=str(payload.get("slug") or ""),
        title=str(payload.get("title") or ""),
        content=str(payload.get("content") or ""),
        metadata=metadata,
    )


def _read_document_manifest() -> list[ProductEmbeddingDocument]:
    manifest_path = get_manifest_path()
    if not manifest_path.exists():
        return []

    try:
        with manifest_path.open("r", encoding="utf-8") as manifest_file:
            payload = json.load(manifest_file)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to read FAISS manifest at %s: %s", manifest_path, exc)
        return []

    if not isinstance(payload, list):
        logger.warning("Ignoring malformed FAISS manifest at %s", manifest_path)
        return []

    documents: list[ProductEmbeddingDocument] = []
    for item in payload:
        if isinstance(item, dict) and "product_id" in item:
            documents.append(_payload_to_document(item))
    return documents


def _write_document_manifest(documents: Sequence[ProductEmbeddingDocument]) -> None:
    index_directory = get_faiss_index_directory()
    index_directory.mkdir(parents=True, exist_ok=True)

    with get_manifest_path().open("w", encoding="utf-8") as manifest_file:
        json.dump([
            _document_to_payload(document) for document in documents
        ], manifest_file, ensure_ascii=False, indent=2)


def _clear_index_files() -> None:
    index_directory = get_faiss_index_directory()
    if not index_directory.exists():
        return

    for child in index_directory.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)


def _build_vector_store(documents: Sequence[ProductEmbeddingDocument]) -> FAISS | None:
    index_directory = get_faiss_index_directory()
    index_directory.mkdir(parents=True, exist_ok=True)

    if not documents:
        _clear_index_files()
        _write_document_manifest([])
        return None

    lc_documents = [
        Document(page_content=document.content, metadata=document.metadata)
        for document in documents
    ]
    vector_store = FAISS.from_documents(documents=lc_documents, embedding=get_embeddings_client())
    vector_store.save_local(str(index_directory))
    _write_document_manifest(documents)
    return vector_store


def get_vector_store() -> FAISS | None:
    """Open the persistent FAISS vector store for product documents."""

    index_directory = get_faiss_index_directory()
    if not index_directory.exists():
        documents = _read_document_manifest()
        if documents:
            return _build_vector_store(documents)
        return None

    try:
        return FAISS.load_local(
            str(index_directory),
            get_embeddings_client(),
            allow_dangerous_deserialization=True,
        )
    except Exception as exc:  # pragma: no cover - defensive recovery path
        logger.warning("Failed to load FAISS index from %s: %s", index_directory, exc)
        documents = _read_document_manifest()
        if documents:
            logger.info("Rebuilding FAISS index from %s documents", len(documents))
            return _build_vector_store(documents)
        return None


def upsert_product_documents(documents: Sequence[ProductEmbeddingDocument]) -> int:
    """Insert or update product documents in FAISS."""

    if not documents:
        logger.info("No product documents were provided for embedding upsert")
        return 0

    existing_documents = {document.product_id: document for document in _read_document_manifest()}
    for document in documents:
        existing_documents[document.product_id] = document

    _build_vector_store(sorted(existing_documents.values(), key=lambda item: item.product_id))
    logger.info("Upserted %s product embeddings into FAISS", len(documents))
    return len(documents)


def delete_product_embeddings(product_ids: Sequence[int]) -> None:
    """Delete embeddings for the provided product identifiers."""

    if not product_ids:
        return

    product_id_set = {int(product_id) for product_id in product_ids}
    remaining_documents = [
        document for document in _read_document_manifest() if document.product_id not in product_id_set
    ]
    _build_vector_store(remaining_documents)
    logger.info("Deleted %s product embeddings from FAISS", len(product_id_set))


def search_similar_products(query: str, top_k: int = 5) -> list[tuple[object, float]]:
    """Return the top matching persisted embeddings for a user query."""

    query = (query or "").strip()
    if not query:
        return []

    vector_store = get_vector_store()
    if vector_store is None:
        return []

    return vector_store.similarity_search_with_score(query, k=top_k)
