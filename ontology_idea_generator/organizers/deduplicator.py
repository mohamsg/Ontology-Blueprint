from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from ..generators.idea_generator import GeneratedIdea
from ..core.api_client import AnthropicAPIClient
from ..generators.prompt_builder import PromptBuilder
from ..core.logger import logger

@dataclass
class DuplicationReport:
    original_idea_name: str
    duplicate_idea_name: str
    similarity_score: float
    reason: str
    recommendation: str

class Deduplicator:
    def __init__(self, api_client: AnthropicAPIClient, prompt_builder: PromptBuilder, similarity_threshold: float = 0.8):
        self.api_client = api_client
        self.prompt_builder = prompt_builder
        self.similarity_threshold = similarity_threshold

    def deduplicate_across_groups(self, all_ideas: List[GeneratedIdea]) -> Tuple[List[GeneratedIdea], List[DuplicationReport]]:
        if not all_ideas:
            return [], []

        logger.info(f"Starting deduplication for {len(all_ideas)} ideas")

        # Batching approach: Group ideas and send to LLM to identify duplicates
        # To avoid context window issues, we might still need some chunking if there are hundreds
        # But for 20-100 ideas, we can likely do it in one or a few calls.

        system_prompt = "You are a semantic duplication detector. Your goal is to identify near-duplicate ideas from a provided list."

        ideas_text = "\n".join([f"{i}. {idea.idea_name}: {idea.abstract_purpose}" for i, idea in enumerate(all_ideas)])

        user_prompt = f"""Review the following list of generated ontological ideas and identify any pairs that are near-duplicates (semantically very similar in purpose and scope).

Ideas:
{ideas_text}

Respond with a JSON object containing a list of duplicate pairs found. For each pair, provide the indices of the duplicate ideas, a similarity score (0.0 to 1.0), and a reason.
"""
        schema = """
        {
          "duplicates": [
            {
              "index_a": 0,
              "index_b": 1,
              "similarity_score": 0.9,
              "reason": "Both ideas describe the same hierarchical structure validator.",
              "recommendation": "drop_second"
            }
          ]
        }
        """

        try:
            data = self.api_client.call_with_structured_output(system_prompt, user_prompt, schema)
            duplicate_info = data.get("duplicates", [])

            indices_to_remove = set()
            reports = []
            for item in duplicate_info:
                idx_a = item.get("index_a")
                idx_b = item.get("index_b")
                score = item.get("similarity_score", 0.0)

                if score > self.similarity_threshold:
                    # By default, we keep index_a and remove index_b (the one later in the list)
                    indices_to_remove.add(max(idx_a, idx_b))
                    reports.append(DuplicationReport(
                        original_idea_name=all_ideas[idx_a].idea_name,
                        duplicate_idea_name=all_ideas[idx_b].idea_name,
                        similarity_score=score,
                        reason=item.get("reason", ""),
                        recommendation=item.get("recommendation", "drop_second")
                    ))

            cleaned_ideas = [idea for i, idea in enumerate(all_ideas) if i not in indices_to_remove]
            logger.info(f"Deduplication complete. Removed {len(indices_to_remove)} duplicates.")
            return cleaned_ideas, reports

        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            return all_ideas, []

    def _assess_pair_similarity(self, idea_a: GeneratedIdea, idea_b: GeneratedIdea) -> DuplicationReport:
        # Keeping this for potential granular checks if needed, but the main logic is batched now.
        return DuplicationReport(idea_a.idea_name, idea_b.idea_name, 0.0, "Skipped by batched logic", "keep_both")
