"""PubMed E-utilities client for searching abstracts."""
from __future__ import annotations
import httpx
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from config.settings import settings


@dataclass
class Abstract:
    pmid: str
    title: str
    abstract: str
    authors: list[str]
    journal: str
    year: str


async def search_pubmed(query: str, max_results: int | None = None) -> list[str]:
    """Run esearch and return a list of PMIDs."""
    limit = max_results or settings.max_abstracts_per_query
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": limit,
        "retmode": "json",
        "sort": "relevance",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.pubmed_base_url}/esearch.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
    return data["esearchresult"]["idlist"]


async def fetch_abstracts(pmids: list[str]) -> list[Abstract]:
    """Fetch full abstract records for a list of PMIDs via efetch."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.pubmed_base_url}/efetch.fcgi", params=params)
        response.raise_for_status()
        xml_content = response.text

    return _parse_abstracts_xml(xml_content)


def _parse_abstracts_xml(xml_content: str) -> list[Abstract]:
    root = ET.fromstring(xml_content)
    abstracts = []

    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None else ""

        title_el = article.find(".//ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else ""

        # Abstract may have multiple sections (structured abstracts)
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join("".join(el.itertext()) for el in abstract_texts)

        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName", "")
            fore = author.findtext("ForeName", "")
            if last:
                authors.append(f"{fore} {last}".strip())

        journal_el = article.find(".//Journal/Title")
        journal = journal_el.text if journal_el is not None else ""

        year_el = article.find(".//PubDate/Year")
        year = year_el.text if year_el is not None else ""

        if abstract:  # skip articles with no abstract
            abstracts.append(Abstract(
                pmid=pmid,
                title=title,
                abstract=abstract,
                authors=authors,
                journal=journal,
                year=year,
            ))

    return abstracts
