from dataclasses import dataclass
from typing import List, Dict, Any
from ..core.api_client import AnthropicAPIClient
from .prompt_builder import PromptBuilder
from ..templates.template_store import TemplateStore
from ..parsers.source_text_parser import SourceTextAnalysis
from ..core.logger import logger

@dataclass
class GeneratedIdea:
    group_id: int
    group_name: str
    idea_name: str
    abstract_purpose: str
    blueprint_steps: List[str]
    generalization_note: str
    source_domain: str
    generation_index: int

class IdeaGenerator:
    def __init__(self, api_client: AnthropicAPIClient, prompt_builder: PromptBuilder, template_store: TemplateStore, source_analysis: SourceTextAnalysis):
        self.api_client = api_client
        self.prompt_builder = prompt_builder
        self.template_store = template_store
        self.source_analysis = source_analysis

    def generate_for_group(self, group_id: int, target_count: int) -> List[GeneratedIdea]:
        template = self.template_store.get(group_id)
        group_name = template.group_name if template else f"Group {group_id}"

        system_prompt = self.prompt_builder.build_system_prompt(group_id)
        user_prompt = self.prompt_builder.build_user_prompt(group_id, target_count)

        schema = """
        {
          "ideas": [
            {
              "idea_name": "string",
              "abstract_purpose": "string",
              "blueprint_steps": ["string"],
              "generalization_note": "string"
            }
          ]
        }
        """

        try:
            response = self.api_client.call_with_structured_output(system_prompt, user_prompt, schema)
            raw_ideas = response.get("ideas", [])
            return self._parse_response_to_ideas(raw_ideas, group_id, group_name)
        except Exception as e:
            logger.error(f"Generation failed for group {group_id}: {e}")
            return []

    def _parse_response_to_ideas(self, raw_ideas: List[Dict[str, Any]], group_id: int, group_name: str) -> List[GeneratedIdea]:
        ideas = []
        for i, raw in enumerate(raw_ideas):
            idea = GeneratedIdea(
                group_id=group_id,
                group_name=group_name,
                idea_name=raw.get("idea_name", ""),
                abstract_purpose=raw.get("abstract_purpose", ""),
                blueprint_steps=raw.get("blueprint_steps", []),
                generalization_note=raw.get("generalization_note", ""),
                source_domain=self.source_analysis.title,
                generation_index=i
            )
            if self._validate_idea(idea):
                ideas.append(idea)
        return ideas

    def _validate_idea(self, idea: GeneratedIdea) -> bool:
        if not idea.idea_name or not idea.abstract_purpose:
            return False
        if len(idea.blueprint_steps) < 3:
            return False
        return True
