from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from ..core.api_client import AnthropicAPIClient

@dataclass
class SourceTextAnalysis:
    raw_text: str
    title: str = ""
    summary: str = ""
    main_entities: List[str] = field(default_factory=list)
    main_processes: List[str] = field(default_factory=list)
    main_qualities: List[str] = field(default_factory=list)
    main_relationships: List[str] = field(default_factory=list)
    hierarchies: List[Tuple[str, str]] = field(default_factory=list)
    temporal_sequences: List[str] = field(default_factory=list)
    causal_chains: List[str] = field(default_factory=list)
    functional_descriptions: List[str] = field(default_factory=list)
    named_fields: List[str] = field(default_factory=list)
    definitions_present: List[str] = field(default_factory=list)

    def get_domain_context(self) -> str:
        return f"{self.title}: {self.summary}"

    def get_entity_process_pairs(self) -> List[Tuple[str, str]]:
        # This could be more sophisticated based on API analysis
        return []

class SourceTextParser:
    def __init__(self):
        self.raw_text: str = ""

    def load(self, filepath: str) -> None:
        with open(filepath, 'r', encoding='utf-8') as f:
            self.raw_text = f.read()

    def analyze(self, api_client: AnthropicAPIClient) -> SourceTextAnalysis:
        system_prompt = "You are a semantic text analyzer. Decompose the provided text into key ontological components."
        user_prompt = f"Analyze the following text and extract its concepts:\n\n{self.raw_text}"
        schema = """
        {
          "title": "string",
          "summary": "string",
          "main_entities": ["string"],
          "main_processes": ["string"],
          "main_qualities": ["string"],
          "main_relationships": ["string"],
          "hierarchies": [["string", "string"]],
          "temporal_sequences": ["string"],
          "causal_chains": ["string"],
          "functional_descriptions": ["string"],
          "named_fields": ["string"],
          "definitions_present": ["string"]
        }
        """
        data = api_client.call_with_structured_output(system_prompt, user_prompt, schema)

        return SourceTextAnalysis(
            raw_text=self.raw_text,
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            main_entities=data.get("main_entities", []),
            main_processes=data.get("main_processes", []),
            main_qualities=data.get("main_qualities", []),
            main_relationships=data.get("main_relationships", []),
            hierarchies=[tuple(h) for h in data.get("hierarchies", [])],
            temporal_sequences=data.get("temporal_sequences", []),
            causal_chains=data.get("causal_chains", []),
            functional_descriptions=data.get("functional_descriptions", []),
            named_fields=data.get("named_fields", []),
            definitions_present=data.get("definitions_present", [])
        )
