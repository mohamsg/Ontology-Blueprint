import re
from dataclasses import dataclass, field
from typing import List, Optional
from ..core.api_client import AnthropicAPIClient

@dataclass
class MergedIdea:
    idea_name: str
    source_document: str = ""
    blueprint_steps: List[str] = field(default_factory=list)
    relevance_label: str = ""
    relevance_explanation: str = ""

class MergedIdeasParser:
    def __init__(self):
        self.raw_text: str = ""
        self.ideas: List[MergedIdea] = []

    def load(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_text = f.read()

        # Split on ## or ### headings
        sections = re.split(r'\n#{2,3}\s+', '\n' + self.raw_text)
        self.ideas = []

        for section in sections:
            section = section.strip()
            if not section or section.startswith('#'):
                continue

            lines = section.strip().split('\n')
            idea_name = lines[0].strip()

            # Source
            source_match = re.search(r'<!--\s*Source:\s*(.*?)\s*-->', section)
            source_document = source_match.group(1) if source_match else ""

            # Blueprint steps
            steps = []
            steps_found = False
            for i, line in enumerate(lines):
                if "**Blueprint Steps:**" in line or "**Algorithmic Steps:**" in line:
                    steps_found = True
                    continue
                if steps_found:
                    # Look for numbered steps
                    step_match = re.match(r'\d+\.\s+(.*)', line.strip())
                    if step_match:
                        steps.append(step_match.group(1))
                    elif line.strip() and not line.strip().startswith('('):
                        # End of steps if we see other content
                        if steps: # only break if we already found some steps
                             pass
                    elif line.strip().startswith('('):
                        break # Relevance line

            # Relevance
            relevance_match = re.search(r'\((relevant|irrelevant):\s*(.*?)\)', section)
            relevance_label = relevance_match.group(1) if relevance_match else ""
            relevance_explanation = relevance_match.group(2) if relevance_match else ""

            self.ideas.append(MergedIdea(
                idea_name=idea_name,
                source_document=source_document,
                blueprint_steps=steps,
                relevance_label=relevance_label,
                relevance_explanation=relevance_explanation
            ))

    def get_all_relevant_ideas(self) -> List[MergedIdea]:
        return [i for i in self.ideas if i.relevance_label == "relevant"]

    def get_ideas_by_step_count(self, min_steps: int, max_steps: int) -> List[MergedIdea]:
        return [i for i in self.ideas if min_steps <= len(i.blueprint_steps) <= max_steps]

    def get_structural_pattern(self, idea: MergedIdea, api_client: AnthropicAPIClient) -> List[str]:
        system_prompt = "You are a structural analyst extracting procedural skeletons."
        # No more hardcoded model names here if we use the api_client's built-in model
        user_prompt = f"Extract the abstract procedural structure from these steps, using generic action verbs and stripping all domain-specific nouns:\n\n" + "\n".join(idea.blueprint_steps)
        schema = '{"steps": ["string"]}'
        response = api_client.call_with_structured_output(system_prompt, user_prompt, schema)
        return response.get("steps", [])
