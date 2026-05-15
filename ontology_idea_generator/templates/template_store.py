from typing import List, Dict, Optional, Any
from dataclasses import asdict

class TemplateStore:
    def __init__(self):
        self._store: Dict[int, Any] = {} # Storing as IdeaTemplate objects

    def add(self, template: Any) -> None:
        self._store[template.group_id] = template

    def get(self, group_id: int) -> Optional[Any]:
        return self._store.get(group_id)

    def get_all(self) -> List[Any]:
        return list(self._store.values())

    def get_step_structure(self, group_id: int) -> List[str]:
        template = self.get(group_id)
        return template.step_structure if template else []

    def get_output_format(self, group_id: int) -> str:
        template = self.get(group_id)
        return template.output_format if template else ""

    def export_to_dict(self) -> Dict[int, Any]:
        return {group_id: asdict(template) for group_id, template in self._store.items()}

    def populate(self, templates: Dict[int, Any]) -> None:
        self._store.update(templates)
