"""Anthropic Claude client for NER, relation extraction, and summarization."""

from __future__ import annotations
import json
import anthropic

from config.settings import settings

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


ENRICHMENT_SYNTHESIS_PROMPT = """\
You are an expert drug discovery scientist synthesizing multi-source evidence to evaluate candidate drug targets.

Original research query: "{query}"

For each candidate target below, you have three evidence sources:
1. Literature evidence (PubMed + AI extraction)
2. Genetic evidence from OpenTargets (association scores, tractability, mouse knockouts)
3. Expression evidence from Human Protein Atlas (tissue levels, cancer pathology)

Your task: synthesize ALL three sources for each target. Explain HOW they corroborate or contradict each other — do not just restate the data.

Confidence scoring:
- "high": strong lit mining confidence AND at least one external source provides supporting evidence (genetic association > 0.5 OR disease-relevant high expression)
- "medium": lit evidence present but external data weak, absent, or mixed
- "low": weak lit evidence and external data does not support

Targets and evidence:
{evidence_text}

Return valid JSON (no markdown fences) with this exact structure:
{{
  "enriched_targets": [
    {{
      "name": "target name — must match input exactly",
      "integrated_confidence": "high | medium | low",
      "integrated_rationale": "2-4 sentences synthesizing how the three sources align or conflict",
      "validation_summary": "1-sentence plain-language conclusion"
    }}
  ],
  "enrichment_summary": "3-5 sentences summarizing the target landscape across all evidence sources"
}}
"""

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


def _extract_json(raw: str) -> dict:
    """Pull JSON from a response that may be wrapped in markdown code fences."""
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


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

    return _extract_json(message.content[0].text)


def _format_evidence_bundle(bundle: dict) -> str:
    lit = bundle.get("literature", {})
    ot = bundle.get("opentargets")
    hpa = bundle.get("hpa")

    lines = [f"TARGET: {bundle['name']}"]

    lines.append(
        f"LITERATURE: confidence={lit.get('confidence', 'unknown')}, "
        f"rationale=\"{lit.get('rationale', '')[:200]}\", "
        f"evidence_count={len(lit.get('evidence', []))}"
    )

    if ot:
        assoc_str = ", ".join(
            f"{a['disease_name']}:{a['score']:.2f}"
            for a in (ot.get("top_genetic_associations") or [])
        )
        lines.append(
            f"OPENTARGETS: ensembl={ot.get('ensembl_id', 'N/A')}, "
            f"tractability_sm={ot.get('tractability', {}).get('small_molecule_score')}, "
            f"tractability_ab={ot.get('tractability', {}).get('antibody_score')}, "
            f"top_associations=[{assoc_str}], "
            f"mouse_phenotypes={ot.get('mouse_phenotypes', [])[:5]}, "
            f"safety_liabilities={ot.get('safety_liabilities', [])}"
        )
    else:
        lines.append("OPENTARGETS: not found")

    if hpa:
        high_tissues = [
            f"{e['tissue']}:{e['rna_level']}"
            for e in (hpa.get("tissue_expression") or [])
            if e.get("rna_level") in ("High", "Medium")
        ][:6]
        cancer_str = ", ".join(
            f"{c['cancer_type']}:high_in_{int(c['high_expression_percent'])}%"
            f"{'(' + c['survival_correlation'] + ')' if c.get('survival_correlation') else ''}"
            for c in (hpa.get("cancer_pathology") or [])[:4]
        )
        lines.append(
            f"HPA: protein_class={hpa.get('protein_class', [])}, "
            f"expressed_tissues=[{', '.join(high_tissues)}], "
            f"cancer_pathology=[{cancer_str}]"
        )
    else:
        lines.append("HPA: not found")

    return "\n".join(lines)


async def synthesize_enriched_targets(
    query: str,
    evidence_bundles: list[dict],
) -> dict:
    """Send multi-source evidence to Claude for integrated target validation synthesis."""
    evidence_text = "\n\n".join(_format_evidence_bundle(b) for b in evidence_bundles)

    prompt = ENRICHMENT_SYNTHESIS_PROMPT.format(
        query=query,
        evidence_text=evidence_text,
    )

    message = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )

    return _extract_json(message.content[0].text)
