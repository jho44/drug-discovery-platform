"""Anthropic Claude client for NER, relation extraction, and summarization."""

import json
import anthropic

from config.settings import settings

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


LITERATURE_MINING_PROMPT = """\
You are an expert biomedical researcher performing literature analysis for drug target identification.

You are given a set of PubMed abstracts retrieved for the query: "{query}"

Your tasks:
1. **Named Entity Recognition**: Extract all mentioned genes, proteins, and diseases.
2. **Relation Extraction**: Identify relationships such as "Gene X is upregulated in Disease Y", "Protein A inhibits pathway B", "Drug C targets Protein D".
3. **Target Summarization**: Based on the evidence, identify the top candidate drug targets. For each target, provide:
   - The target name (gene/protein)
   - Why it is a candidate (mechanism, evidence strength)
   - Supporting evidence quotes from the abstracts (include PMID)
   - Confidence level: high / medium / low

Return your response as a JSON object with this exact structure:
{{
  "entities": {{
    "genes_proteins": ["list of unique gene/protein names mentioned"],
    "diseases": ["list of unique disease names mentioned"]
  }},
  "relations": [
    {{
      "subject": "gene or protein name",
      "relation": "short description of relationship",
      "object": "gene, protein, disease, or pathway",
      "pmid": "PMID where this was found"
    }}
  ],
  "candidate_targets": [
    {{
      "name": "target name",
      "type": "gene | protein | pathway",
      "rationale": "why this is a candidate target",
      "confidence": "high | medium | low",
      "evidence": [
        {{
          "pmid": "PMID",
          "quote": "relevant excerpt from the abstract",
          "relation": "brief description of what this evidence shows"
        }}
      ]
    }}
  ],
  "summary": "2-3 sentence overview of the landscape based on the abstracts"
}}

Abstracts:
{abstracts}
"""


async def analyze_abstracts_for_targets(
    query: str,
    abstracts: list[dict],
) -> dict:
    """Send abstracts to Claude for NER, relation extraction, and target identification."""
    formatted_abstracts = "\n\n".join(
        f"[PMID: {a['pmid']}] {a['title']}\n{a['abstract']}"
        for a in abstracts
    )

    prompt = LITERATURE_MINING_PROMPT.format(
        query=query,
        abstracts=formatted_abstracts,
    )

    message = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text

    # Extract JSON from the response (handles markdown code fences if present)
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())
