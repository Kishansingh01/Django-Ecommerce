"""Gemini chat model helpers for the RAG chatbot."""
from __future__ import annotations

import logging
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI

from rag.prompts import NO_ANSWER_MESSAGE
from rag.vector_store import get_chat_model_name, get_gemini_api_key

logger = logging.getLogger(__name__)


class MockChatGemini:
    """Mock Gemini Chat Model for local development and testing without an API key."""

    def invoke(self, messages):
        """Mock invoke method that parses the catalog context and generates responses."""
        human_msg = ""
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                human_msg = msg.content
            elif isinstance(msg, tuple) and msg[0] == 'human':
                human_msg = msg[1]
            elif isinstance(msg, dict) and msg.get('type') == 'human':
                human_msg = msg.get('content', '')

        # Parse context and question
        context = ""
        question = ""
        if "Catalog context:" in human_msg:
            parts = human_msg.split("Catalog context:")
            question = parts[0].replace("Question:", "").strip()
            context = parts[1].strip()
        else:
            question = human_msg

        # Extract products from context block
        product_blocks = context.split("\n\n")
        products = []
        for block in product_blocks:
            if not block.strip():
                continue
            lines = block.strip().split("\n")
            p_name = "Unknown product"
            if lines:
                first_line = lines[0]
                if ":" in first_line:
                    p_name = first_line.split(":", 1)[-1].strip()
            price = "unknown"
            stock = "unknown"
            desc = ""
            for line in lines:
                if line.startswith("Price:"):
                    price = line.split(":", 1)[-1].strip()
                elif line.startswith("Stock availability:"):
                    stock = line.split(":", 1)[-1].strip()
                elif line.startswith("Description:"):
                    desc = line.split(":", 1)[-1].strip()

            products.append({
                "name": p_name,
                "price": price,
                "stock": stock,
                "description": desc
            })


        # Answer generation
        question_lower = question.lower()
        if not products:
            ans = NO_ANSWER_MESSAGE
        else:
            matched_product = None
            for p in products:
                if p["name"].lower() in question_lower:
                    matched_product = p
                    break

            if matched_product:
                ans = (
                    f"Yes! We have the **{matched_product['name']}** in our catalog. "
                    f"It is priced at {matched_product['price']} and is currently {matched_product['stock']}. "
                )
                if matched_product['description'] and matched_product['description'] != "unknown":
                    ans += f"Description: {matched_product['description']}."
            else:
                # General recommendation / list products
                ans = "Based on our product catalog, here are some relevant products:\n"
                for idx, p in enumerate(products[:3], 1):
                    ans += f"{idx}. **{p['name']}** - {p['price']} ({p['stock']})\n"
                ans += "\nLet me know if you would like more details about any specific product!"

        class MockResponse:
            def __init__(self, content):
                self.content = content
        return MockResponse(ans)


def get_chat_llm():
    """Create the Gemini chat model used for product-catalog answers."""

    try:
        api_key = get_gemini_api_key()
        model_name = get_chat_model_name()
        logger.info("Initializing Gemini chat model: %s", model_name)
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0,
        )
    except ValueError:
        logger.warning("GEMINI_API_KEY is not set. Falling back to MockChatGemini.")
        return MockChatGemini()

