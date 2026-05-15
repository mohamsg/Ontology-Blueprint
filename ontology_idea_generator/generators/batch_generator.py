from typing import List
from .idea_generator import IdeaGenerator, GeneratedIdea
from ..core.config import Config

class BatchGenerator:
    def __init__(self, idea_generator: IdeaGenerator, config: Config):
        self.idea_generator = idea_generator
        self.config = config
        self.all_generated_ideas: List[GeneratedIdea] = []

    def run(self) -> List[GeneratedIdea]:
        group_ids = [g.group_id for g in self.idea_generator.template_store.get_all()]
        return self.run_for_groups(group_ids)

    def run_for_groups(self, group_ids: List[int]) -> List[GeneratedIdea]:
        new_ideas = []
        for group_id in group_ids:
            ideas = self.idea_generator.generate_for_group(group_id, self.config.ideas_per_group)
            new_ideas.extend(ideas)
            self.all_generated_ideas.extend(ideas)
        return new_ideas
