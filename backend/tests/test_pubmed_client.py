"""Tests for PubMed client."""

import pytest
from unittest.mock import AsyncMock, patch
from services.pubmed_client import search_pubmed, fetch_abstracts, _parse_abstracts_xml

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <Journal>
          <Title>Nature Medicine</Title>
          <JournalIssue>
            <PubDate><Year>2023</Year></PubDate>
          </JournalIssue>
        </Journal>
        <ArticleTitle>BRAF V600E mutations in NSCLC</ArticleTitle>
        <Abstract>
          <AbstractText>BRAF V600E is a driver mutation in non-small cell lung cancer.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>Smith</LastName>
            <ForeName>John</ForeName>
          </Author>
        </AuthorList>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


def test_parse_abstracts_xml():
    results = _parse_abstracts_xml(SAMPLE_XML)
    assert len(results) == 1
    assert results[0].pmid == "12345678"
    assert results[0].title == "BRAF V600E mutations in NSCLC"
    assert "BRAF V600E" in results[0].abstract
    assert results[0].authors == ["John Smith"]
    assert results[0].journal == "Nature Medicine"
    assert results[0].year == "2023"


@pytest.mark.asyncio
async def test_search_pubmed_returns_pmids():
    mock_response = {
        "esearchresult": {"idlist": ["12345678", "87654321"]}
    }
    with patch("services.pubmed_client.httpx.AsyncClient") as mock_client_cls:
        mock_resp = AsyncMock()
        mock_resp.json.return_value = mock_response
        mock_resp.raise_for_status = lambda: None
        mock_client_cls.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)

        pmids = await search_pubmed("BRAF NSCLC", max_results=5)

    assert pmids == ["12345678", "87654321"]
