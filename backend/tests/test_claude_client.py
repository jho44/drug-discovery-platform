"""Tests for Claude client."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.claude_client import analyze_abstracts_for_targets

SAMPLE_ABSTRACTS = [
    {
        "pmid": "12345678",
        "title": "BRAF V600E in NSCLC",
        "abstract": "BRAF V600E is a key driver mutation in non-small cell lung cancer.",
    }
]

SAMPLE_CLAUDE_RESPONSE = {
    "entities": {
        "genes_proteins": ["BRAF"],
        "diseases": ["non-small cell lung cancer", "NSCLC"],
    },
    "relations": [
        {
            "subject": "BRAF V600E",
            "relation": "is a driver mutation in",
            "object": "NSCLC",
            "pmid": "12345678",
        }
    ],
    "candidate_targets": [
        {
            "name": "BRAF",
            "type": "gene",
            "rationale": "BRAF V600E is a well-characterized oncogenic driver in NSCLC.",
            "confidence": "high",
            "evidence": [
                {
                    "pmid": "12345678",
                    "quote": "BRAF V600E is a key driver mutation",
                    "relation": "driver mutation in NSCLC",
                }
            ],
        }
    ],
    "summary": "BRAF V600E mutations are key drivers in NSCLC and represent a validated therapeutic target.",
}


@pytest.mark.asyncio
async def test_analyze_abstracts_for_targets():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(SAMPLE_CLAUDE_RESPONSE))]

    with patch("services.claude_client._client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        result = await analyze_abstracts_for_targets("BRAF NSCLC", SAMPLE_ABSTRACTS)

    assert result["candidate_targets"][0]["name"] == "BRAF"
    assert result["candidate_targets"][0]["confidence"] == "high"
    assert "BRAF" in result["entities"]["genes_proteins"]
