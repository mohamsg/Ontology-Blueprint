import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from ..core.api_client import AnthropicAPIClient
from ..parsers.grouped_ontology_parser import OntologyGroup, GroupedOntologyParser
from ..parsers.merged_ideas_parser import MergedIdeasParser
from .template_store import TemplateStore

@dataclass
class IdeaTemplate:
    group_id: int
    group_name: str
    abstract_purpose: str
    step_structure: List[str]
    output_format: str
    abstraction_signals: List[str] = field(default_factory=list)

class TemplateBuilder:
    def __init__(self, api_client: AnthropicAPIClient, merged_parser: MergedIdeasParser, grouped_parser: GroupedOntologyParser, template_store: TemplateStore):
        self.api_client = api_client
        self.merged_parser = merged_parser
        self.grouped_parser = grouped_parser
        self.template_store = template_store

    def build_template_for_group(self, group: OntologyGroup) -> IdeaTemplate:
        idea_titles = group.idea_titles
        relevant_ideas = self.merged_parser.get_all_relevant_ideas()

        # In a real implementation, we might sample or filter relevant ideas that align with the group
        sample_patterns = []
        if relevant_ideas:
            # For simplicity, take the first 2 as samples of structural patterns
            for idea in relevant_ideas[:2]:
                sample_patterns.append(self.merged_parser.get_structural_pattern(idea, self.api_client))

        system_prompt = "You are an ontological template architect."
        user_prompt = f"Given these idea titles: {idea_titles}\nAnd these structural patterns: {sample_patterns}\nInfer the abstract procedural skeleton that all ideas in this group follow. Return only abstract steps using generic action verbs. Do not use any domain-specific words."

        schema = """
        {
          "abstract_purpose": "string",
          "step_structure": ["string"],
          "output_format": "string",
          "abstraction_signals": ["string"]
        }
        """
        data = self.api_client.call_with_structured_output(system_prompt, user_prompt, schema)

        template = IdeaTemplate(
            group_id=group.group_id,
            group_name=group.name,
            abstract_purpose=data.get("abstract_purpose", ""),
            step_structure=data.get("step_structure", []),
            output_format=data.get("output_format", ""),
            abstraction_signals=data.get("abstraction_signals", [])
        )
        self.template_store.add(template)
        return template

    def build_all_templates(self) -> Dict[int, IdeaTemplate]:
        templates = {}
        for group in self.grouped_parser.groups:
            templates[group.group_id] = self.build_template_for_group(group)
        return templates

    def _extract_abstraction_signals(self, idea_titles: List[str]) -> List[str]:
        system_prompt = "You are a cognitive scientist specializing in abstraction."
        user_prompt = f"What abstract cognitive or computational operations do these titles imply? {idea_titles}\nReturn a list of generic operation types without any domain-specific terminology."
        schema = '{"signals": ["string"]}'
        data = self.api_client.call_with_structured_output(system_prompt, user_prompt, schema)
        return data.get("signals", [])
