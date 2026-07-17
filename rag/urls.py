"""URL routes for the RAG chatbot API."""
from __future__ import annotations

from django.urls import path

from rag.views import ChatAPIView, ChatbotPageView

app_name = "rag"

urlpatterns = [
    path('', ChatbotPageView.as_view(), name='chatbot_page'),
    path("chat/", ChatAPIView.as_view(), name="chat"),
]
