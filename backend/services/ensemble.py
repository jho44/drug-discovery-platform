"""Ensemble/consensus scoring across multiple pipeline methods.

When a user runs multiple methods at the same stage, this module merges their
outputs and ranks candidates by how consistently they appear across methods.
"""

from dataclasses import dataclass, field


@dataclass
class ScoredCandidate:
    name: str
    appearances: int          # how many methods surfaced this candidate
    total_methods: int
    consensus_score: float    # appearances / total_methods
    method_results: list[dict] = field(default_factory=list)


def compute_consensus(
    method_outputs: list[list[dict]],
    name_key: str = "name",
) -> list[ScoredCandidate]:
    """Merge candidate lists from multiple methods into a consensus ranking.

    Args:
        method_outputs: List of candidate lists, one per method.
        name_key: The dict key that holds the candidate name.

    Returns:
        Candidates sorted by consensus_score descending.
    """
    total_methods = len(method_outputs)
    counts: dict[str, list[dict]] = {}

    for method_result in method_outputs:
        seen_in_method: set[str] = set()
        for candidate in method_result:
            name = candidate.get(name_key, "").strip().upper()
            if name and name not in seen_in_method:
                counts.setdefault(name, []).append(candidate)
                seen_in_method.add(name)

    scored = []
    for name, results in counts.items():
        appearances = len(results)
        scored.append(ScoredCandidate(
            name=name,
            appearances=appearances,
            total_methods=total_methods,
            consensus_score=appearances / total_methods,
            method_results=results,
        ))

    scored.sort(key=lambda c: c.consensus_score, reverse=True)
    return scored
