import re
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class OntologyGroup:
    group_id: int
    name: str
    idea_count: int = 0
    idea_titles: List[str] = field(default_factory=list)

class GroupedOntologyParser:
    def __init__(self):
        self.raw_text: str = ""
        self.groups: List[OntologyGroup] = []

    def load(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_text = f.read()

        # Split by ## headings. Prepend newline to catch the first heading if it's ##
        # but usually the file starts with # Title
        sections = re.split(r'\n##\s+', '\n' + self.raw_text)
        self.groups = []

        for section in sections:
            section = section.strip()
            if not section or section.startswith('#'):
                continue

            lines = section.strip().split('\n')
            header = lines[0]

            # Extract ID and Name: "1. Ontological Architecture & Core Structure"
            match = re.match(r'(\d+)\.\s+(.*)', header)
            if match:
                group_id = int(match.group(1))
                name = match.group(2).strip()

                # Extract titles: "- **Title**"
                idea_titles = []
                for line in lines[1:]:
                    title_match = re.search(r'\*\*(.*?)\*\*', line)
                    if title_match:
                        idea_titles.append(title_match.group(1))
                    elif line.strip().startswith('- '):
                        # Fallback if not bolded
                        idea_titles.append(line.strip()[2:].strip())

                self.groups.append(OntologyGroup(
                    group_id=group_id,
                    name=name,
                    idea_count=len(idea_titles),
                    idea_titles=idea_titles
                ))

    def get_group_by_id(self, group_id: int) -> Optional[OntologyGroup]:
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    def get_all_group_names(self) -> List[str]:
        return [g.name for g in self.groups]

    def get_idea_titles_for_group(self, group_id: int) -> List[str]:
        group = self.get_group_by_id(group_id)
        return group.idea_titles if group else []
