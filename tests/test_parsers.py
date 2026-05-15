import pytest
import os
from ontology_idea_generator.parsers.grouped_ontology_parser import GroupedOntologyParser
from ontology_idea_generator.parsers.merged_ideas_parser import MergedIdeasParser

def test_grouped_ontology_parser(tmp_path):
    content = """# Grouped Ontology Ideas

## 1. Ontological Architecture & Core Structure
- **Title 1.1**
- **Title 1.2**

## 2. Disposition, Capability & Function Modeling
- **Title 2.1**
- **Title 2.2**
"""
    d = tmp_path / "data"
    d.mkdir()
    f = d / "grouped.md"
    f.write_text(content)

    parser = GroupedOntologyParser()
    parser.load(str(f))

    assert len(parser.groups) == 2
    assert parser.groups[0].group_id == 1
    assert parser.groups[0].name == "Ontological Architecture & Core Structure"
    assert parser.groups[0].idea_titles == ["Title 1.1", "Title 1.2"]
    assert parser.groups[1].group_id == 2
    assert parser.groups[1].idea_titles == ["Title 2.1", "Title 2.2"]

def test_merged_ideas_parser(tmp_path):
    content = """# Merged Ontology Ideas

## Idea 1
<!-- Source: Document A -->
**Blueprint Steps:**
1. Step one
2. Step two
(relevant: explanation)

## Idea 2
<!-- Source: Document B -->
**Algorithmic Steps:**
1. Action one
2. Action two
(irrelevant: explanation)
"""
    d = tmp_path / "data"
    d.mkdir()
    f = d / "merged.md"
    f.write_text(content)

    parser = MergedIdeasParser()
    parser.load(str(f))

    assert len(parser.ideas) == 2
    assert parser.ideas[0].idea_name == "Idea 1"
    assert parser.ideas[0].source_document == "Document A"
    assert parser.ideas[0].blueprint_steps == ["Step one", "Step two"]
    assert parser.ideas[0].relevance_label == "relevant"
    assert parser.ideas[1].relevance_label == "irrelevant"
