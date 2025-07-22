import pytest
from unittest.mock import patch, MagicMock
from slack_mcp import search_channel, search_group, search_dm  # replace with actual import

@pytest.fixture
def mock_slack_client(monkeypatch):
    mock_client = MagicMock()

    # Mock conversations_list
    mock_client.conversations_list.return_value = {
        "channels": [{"id": "C123", "name": "general"}]
    }

    # Mock conversations_history
    mock_client.conversations_history.return_value = {
        "messages": [{"text": "This is a timeout error", "ts": "123.456"}]
    }

    # Mock replies
    mock_client.conversations_replies.return_value = {
        "messages": [{"text": "This is a timeout error"}, {"text": "Increase timeout in config"}]
    }

    # Mock permalink
    mock_client.chat_getPermalink.return_value = {
        "permalink": "https://slack.com/archives/C123/p123456"
    }

    monkeypatch.setattr("slack_mcp.client", mock_client)
    return mock_client


def test_search_channel(mock_slack_client):
    result = search_channel(keyword="timeout", channel_name="general")
    assert isinstance(result, list)
    assert "permalink" in result[0]
    assert "summary" in result[0]


def test_search_group(mock_slack_client):
    mock_slack_client.conversations_list.return_value = {
        "channels": [{"id": "G123", "name": "secret-group"}]
    }
    result = search_group(keyword="timeout", group_name="secret-group")
    assert isinstance(result, list)
    assert result[0]["summary"].startswith("This is a timeout")


def test_search_dm(mock_slack_client):
    mock_slack_client.users_list.return_value = {
        "members": [{"id": "U123", "name": "tyler"}]
    }
    mock_slack_client.conversations_list.return_value = {
        "channels": [{"id": "D123", "user": "U123"}]
    }
    result = search_dm(keyword="timeout", username="tyler")
    assert isinstance(result, list)
    assert result[0]["summary"].startswith("This is a timeout")

MCP_URL = "http://localhost:8000/"

@pytest.fixture
def test_search_dm(monkeypatch):
    payload = {
        "tool": "slack.search_dm",
        "params": {
            "keyword": "test 12345",
            "username": "Kevin Ren"
        }
    }
    response = requests.post(MCP_URL, json=payload)
    assert response.status_code == 200
    data = response.json()
    # Adjust these assertions based on your actual response structure
    assert isinstance(data, list)
    assert len(data) == 1
    assert "test 12345" in data[0]["summary"]
    assert "permalink" in data[0]