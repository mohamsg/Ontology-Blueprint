from dataclasses import dataclass
from typing import List, Dict
from ..generators.idea_generator import GeneratedIdea
from ..parsers.grouped_ontology_parser import GroupedOntologyParser

@dataclass
class OrganizedGroup:
    group_id: int
    group_name: str
    original_idea_count: int
    generated_idea_count: int
    ideas: List[GeneratedIdea]
    coverage_ratio: float

class IdeaOrganizer:
    def __init__(self, grouped_parser: GroupedOntologyParser):
        self.grouped_parser = grouped_parser

    def organize(self, ideas: List[GeneratedIdea]) -> List[OrganizedGroup]:
        grouped_ideas: Dict[int, List[GeneratedIdea]] = {}
        for idea in ideas:
            if idea.group_id not in grouped_ideas:
                grouped_ideas[idea.group_id] = []
            grouped_ideas[idea.group_id].append(idea)

        organized_groups = []
        for group in self.grouped_parser.groups:
            ideas_in_group = grouped_ideas.get(group.group_id, [])
            coverage = len(ideas_in_group)

            organized_groups.append(OrganizedGroup(
                group_id=group.group_id,
                group_name=group.name,
                original_idea_count=group.idea_count,
                generated_idea_count=coverage,
                ideas=ideas_in_group,
                coverage_ratio=coverage / group.idea_count if group.idea_count > 0 else 0
            ))
        return organized_groups

    def get_coverage_summary(self, organized_groups: List[OrganizedGroup]) -> Dict[str, float]:
        return {g.group_name: g.coverage_ratio for g in organized_groups}

    def flag_low_coverage_groups(self, organized_groups: List[OrganizedGroup], threshold: float) -> List[int]:
        return [g.group_id for g in organized_groups if g.coverage_ratio < threshold]
