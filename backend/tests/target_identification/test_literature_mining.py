"""Integration-style tests for the literature mining pipeline."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from pipeline.target_identification.models import LitMiningRequest
from pipeline.target_identification.literature_mining import run_literature_mining


MOCK_ABSTRACTS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>99999999</PMID>
      <Article>
        <Journal>
          <Title>Cancer Cell</Title>
          <JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue>
        </Journal>
        <ArticleTitle>BRAF inhibition in NSCLC</ArticleTitle>
        <Abstract>
          <AbstractText>Vemurafenib targets BRAF V600E in non-small cell lung cancer patients.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author><LastName>Jones</LastName><ForeName>Alice</ForeName></Author>
        </AuthorList>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>"""

MOCK_CLAUDE_OUTPUT = {
    "entities": {"genes_proteins": ["BRAF"], "diseases": ["NSCLC"]},
    "relations": [{"subject": "BRAF", "relation": "targeted by", "object": "Vemurafenib", "pmid": "99999999"}],
    "candidate_targets": [
        {
            "name": "BRAF",
            "type": "gene",
            "rationale": "Oncogenic driver targeted by approved inhibitors.",
            "confidence": "high",
            "evidence": [{"pmid": "99999999", "quote": "Vemurafenib targets BRAF V600E", "relation": "drug-target"}],
        }
    ],
    "summary": "BRAF V600E is a validated target in NSCLC.",
}


@pytest.mark.asyncio
async def test_run_literature_mining():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(MOCK_CLAUDE_OUTPUT))]

    with (
        patch("pipeline.target_identification.literature_mining.search_pubmed", AsyncMock(return_value=["99999999"])),
        patch(
            "pipeline.target_identification.literature_mining.fetch_abstracts",
            AsyncMock(return_value=_make_abstracts()),
        ),
        patch("services.claude_client._client") as mock_client,
    ):
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        result = await run_literature_mining(LitMiningRequest(query="BRAF-V600E NSCLC"))

    assert result.abstracts_fetched == 1
    assert result.candidate_targets[0].name == "BRAF"
    assert result.candidate_targets[0].confidence == "high"
    assert result.query == "BRAF-V600E NSCLC"


@pytest.mark.asyncio
async def test_run_literature_mining_no_results():
    with patch("pipeline.target_identification.literature_mining.search_pubmed", AsyncMock(return_value=[])):
        result = await run_literature_mining(LitMiningRequest(query="xyznonexistent"))

    assert result.abstracts_fetched == 0
    assert result.candidate_targets == []


def _make_abstracts():
    from services.pubmed_client import Abstract
    return [Abstract(
        pmid="99999999",
        title="BRAF inhibition in NSCLC",
        abstract="Vemurafenib targets BRAF V600E in non-small cell lung cancer patients.",
        authors=["Alice Jones"],
        journal="Cancer Cell",
        year="2024",
    )]
