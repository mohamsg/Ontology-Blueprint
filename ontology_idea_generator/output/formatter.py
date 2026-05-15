import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from datetime import datetime
from ..organizers.idea_organizer import OrganizedGroup
from ..parsers.grouped_ontology_parser import GroupedOntologyParser

@dataclass
class FormattedOutput:
    format: str
    content: str
    data: Dict[str, Any]
    group_count: int
    total_idea_count: int
    source_document: str
    generation_timestamp: str

class Formatter:
    def __init__(self, output_format: str, grouped_parser: GroupedOntologyParser):
        self.output_format = output_format
        self.grouped_parser = grouped_parser

    def format(self, organized_groups: List[OrganizedGroup], source_document: str) -> FormattedOutput:
        total_ideas = sum(len(g.ideas) for g in organized_groups)
        timestamp = datetime.now().isoformat()

        if self.output_format == "markdown":
            content = self.format_as_markdown(organized_groups, source_document, timestamp)
            data = {}
        elif self.output_format == "json":
            data = self._build_data_dict(organized_groups, source_document, timestamp)
            content = json.dumps(data, indent=2)
        else: # text
            content = self.format_as_plain_text(organized_groups, source_document, timestamp)
            data = {}

        return FormattedOutput(
            format=self.output_format,
            content=content,
            data=data,
            group_count=len(organized_groups),
            total_idea_count=total_ideas,
            source_document=source_document,
            generation_timestamp=timestamp
        )

    def format_as_markdown(self, organized_groups: List[OrganizedGroup], source_doc: str, timestamp: str) -> str:
        lines = [f"# Generated Ontological Ideas", f"Source: {source_doc}", f"Generated at: {timestamp}", ""]
        lines.append("## Table of Contents")
        for g in organized_groups:
            lines.append(f"- [{g.group_name}](#group-{g.group_id}) ({len(g.ideas)} ideas)")
        lines.append("")

        for g in organized_groups:
            lines.append(f"## <a name='group-{g.group_id}'></a>{g.group_id}. {g.group_name}")
            lines.append(f"Generated {len(g.ideas)} / Original {g.original_idea_count}")
            lines.append("")
            for idea in g.ideas:
                lines.append(f"### {idea.idea_name}")
                lines.append(f"**Purpose:** {idea.abstract_purpose}")
                lines.append("")
                lines.append("**Blueprint Steps:**")
                for i, step in enumerate(idea.blueprint_steps):
                    lines.append(f"{i+1}. {step}")
                lines.append("")
                lines.append(f"> {idea.generalization_note}")
                lines.append("")
        return "\n".join(lines)

    def format_as_plain_text(self, organized_groups: List[OrganizedGroup], source_doc: str, timestamp: str) -> str:
        # Simplified plain text
        return self.format_as_markdown(organized_groups, source_doc, timestamp)

    def _build_data_dict(self, organized_groups: List[OrganizedGroup], source_doc: str, timestamp: str) -> Dict[str, Any]:
        return {
            "metadata": {
                "source_document": source_doc,
                "timestamp": timestamp,
                "total_ideas": sum(len(g.ideas) for g in organized_groups)
            },
            "groups": [asdict(g) for g in organized_groups]
        }

    def format_coverage_summary(self, organized_groups: List[OrganizedGroup]) -> str:
        lines = ["| Group | Original | Generated | Ratio |", "|---|---|---|---|"]
        for g in organized_groups:
            lines.append(f"| {g.group_name} | {g.original_idea_count} | {g.generated_idea_count} | {g.coverage_ratio:.2%} |")
        return "\n".join(lines)
