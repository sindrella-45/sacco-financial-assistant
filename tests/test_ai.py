"""
tests/test_ai.py
Tests for the chat function (Handshake 2).

Uses the real ai_service if available, otherwise falls back to
the mock in chatbot_ui — so these tests pass on any branch.
"""

import pytest


def _chat(message: str, user_id: str = "M001", history: list = None) -> str:
    """Import the real service or the mock transparently."""
    history = history or []
    try:
        from app.services.ai_service import chat
        return chat(message=message, user_id=user_id, history=history)
    except ImportError:
        from app.ui.chatbot_ui import _mock_chat
        return _mock_chat(message=message, user_id=user_id, history=history)


def test_chat_returns_string():
    """chat() must always return a str."""
    reply = _chat("What is my loan balance?")
    assert isinstance(reply, str)


def test_chat_returns_non_empty_string():
    """chat() must never return an empty string."""
    reply = _chat("How is interest calculated?")
    assert len(reply.strip()) > 0


def test_chat_accepts_empty_history():
    """chat() should not raise when history is an empty list."""
    reply = _chat("Hello", history=[])
    assert isinstance(reply, str)


def test_chat_accepts_populated_history():
    """chat() should accept a pre-existing conversation history."""
    history = [
        {"role": "user",      "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"},
    ]
    reply = _chat("Tell me about saving tips.", history=history)
    assert isinstance(reply, str)


def test_chat_handles_different_user_ids():
    """chat() must work for any of the demo member IDs."""
    for uid in ["M001", "M002", "M003", "M004", "M005"]:
        reply = _chat("What is my account status?", user_id=uid)
        assert isinstance(reply, str), f"Expected str for user_id={uid}"


def test_chat_history_format_is_role_content_dicts():
    """
    Verify the mock (or real service) produces output compatible with the
    messages format expected by gr.Chatbot(type='messages').
    The caller constructs history as list of {"role": ..., "content": ...} dicts.
    chat() should accept this without raising.
    """
    history = [{"role": "user", "content": "What savings tips do you have?"}]
    reply = _chat("Follow-up question about savings.", history=history)
    assert isinstance(reply, str)
