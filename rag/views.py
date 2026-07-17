"""REST API views for the RAG chatbot."""
from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView

from rag.services import answer_product_question

logger = logging.getLogger(__name__)


class ChatbotPageView(TemplateView):
    """Render the public chatbot page."""

    template_name = "rag/chatbot.html"


class ChatAPIView(APIView):
    """POST endpoint for product-catalog questions."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        query = request.data.get("query", "")
        if not isinstance(query, str):
            return Response(
                {"detail": "query must be a string"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = answer_product_question(query=query)
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.exception("Chat request failed: %s", exc)
            return Response(
                {"detail": "Unable to process the chat request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"answer": result.answer, "sources": result.sources},
            status=status.HTTP_200_OK,
        )
