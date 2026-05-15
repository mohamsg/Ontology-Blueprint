from typing import List, Tuple
from ..parsers.source_text_parser import SourceTextAnalysis
from ..templates.template_store import TemplateStore

class PromptBuilder:
    def __init__(self, source_analysis: SourceTextAnalysis, template_store: TemplateStore):
        self.source_analysis = source_analysis
        self.template_store = template_store

    def build_system_prompt(self, group_id: int) -> str:
        template = self.template_store.get(group_id)
        if not template:
            return "You are an ontological idea generator."

        return f"""You are an ontological idea generator.
Your purpose for this group is: {template.abstract_purpose}
You should produce ideas in the format of a {template.output_format}.
Produce ideas that are generic and applicable to any source material, not just the current one.
Follow this abstract step structure:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(template.step_structure))}
"""

    def build_user_prompt(self, group_id: int, target_idea_count: int) -> str:
        template = self.template_store.get(group_id)
        domain_context = self.source_analysis.get_domain_context()
        entities = self.source_analysis.main_entities
        processes = self.source_analysis.main_processes

        return f"""Source Material Context: {domain_context}
Relevant Entities: {entities}
Relevant Processes: {processes}

Generate exactly {target_idea_count} abstracted ideas.
Each idea must follow the abstract step structure: {template.step_structure if template else 'N/A'}
Each idea must include:
1. A name (noun phrase, singular, no verbs)
2. A one-sentence abstract purpose description
3. Numbered blueprint steps using only generic action verbs
4. An explanation of how the idea generalizes beyond the source text

Output as a JSON array of objects with keys: "idea_name", "abstract_purpose", "blueprint_steps", "generalization_note"
"""

    def build_dedup_prompt(self, existing_ideas: List[str], candidate_idea: str) -> Tuple[str, str]:
        system_prompt = "You are a semantic similarity analyzer."
        user_prompt = f"Is this candidate idea sufficiently distinct from the existing list?\nExisting: {existing_ideas}\nCandidate: {candidate_idea}\nRespond with a JSON object: " + '{"is_distinct": bool, "reason": "string"}'
        return system_prompt, user_prompt
