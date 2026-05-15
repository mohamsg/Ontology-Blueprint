import argparse
import sys
import os
from .core.config import Config
from .core.api_client import AnthropicAPIClient
from .core.logger import logger
from .parsers.grouped_ontology_parser import GroupedOntologyParser
from .parsers.merged_ideas_parser import MergedIdeasParser
from .parsers.source_text_parser import SourceTextParser
from .templates.template_builder import TemplateBuilder
from .templates.template_store import TemplateStore
from .generators.prompt_builder import PromptBuilder
from .generators.idea_generator import IdeaGenerator
from .generators.batch_generator import BatchGenerator
from .organizers.deduplicator import Deduplicator
from .organizers.idea_organizer import IdeaOrganizer
from .output.formatter import Formatter
from .output.writer import Writer

class OntologyIdeaGeneratorPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.api_client = AnthropicAPIClient(
            api_key=config.anthropic_api_key,
            model=config.model_name,
            max_tokens=config.max_tokens_per_call
        )
        self.grouped_parser = GroupedOntologyParser()
        self.merged_parser = MergedIdeasParser()
        self.source_parser = SourceTextParser()
        self.template_store = TemplateStore()
        self.template_builder = TemplateBuilder(
            self.api_client, self.merged_parser, self.grouped_parser, self.template_store
        )
        # prompt_builder will be initialized after source analysis
        self.prompt_builder = None
        self.idea_generator = None
        self.batch_generator = None
        self.deduplicator = None
        self.idea_organizer = IdeaOrganizer(self.grouped_parser)
        self.formatter = Formatter(config.output_format, self.grouped_parser)
        self.writer = Writer(config.output_path)

    def run(self) -> str:
        logger.info("Starting Ontology Idea Generator Pipeline")

        # Phase 1 - Load
        logger.info("Phase 1: Loading input files")
        self.grouped_parser.load(self.config.grouped_ontology_path)
        self.merged_parser.load(self.config.merged_ideas_path)
        self.source_parser.load(self.config.source_text_path)

        # Phase 2 - Analyze
        logger.info("Phase 2: Analyzing source text")
        source_analysis = self.source_parser.analyze(self.api_client)

        # Initialize generator components with source analysis
        self.prompt_builder = PromptBuilder(source_analysis, self.template_store)
        self.idea_generator = IdeaGenerator(
            self.api_client, self.prompt_builder, self.template_store, source_analysis
        )
        self.batch_generator = BatchGenerator(self.idea_generator, self.config)
        self.deduplicator = Deduplicator(self.api_client, self.prompt_builder)

        # Phase 3 - Build Templates
        logger.info("Phase 3: Building templates")
        self.template_builder.build_all_templates()
        self.writer.write_templates(self.template_store)

        # Phase 4 - Generate
        logger.info("Phase 4: Generating ideas")
        raw_ideas = self.batch_generator.run()

        # Phase 5 - Deduplicate
        logger.info("Phase 5: Deduplicating ideas")
        cleaned_ideas, dedup_reports = self.deduplicator.deduplicate_across_groups(raw_ideas)

        # Phase 6 - Organize
        logger.info("Phase 6: Organizing ideas")
        organized_groups = self.idea_organizer.organize(cleaned_ideas)
        coverage_summary = self.formatter.format_coverage_summary(organized_groups)

        # Phase 7 - Handle Low Coverage
        logger.info("Phase 7: Handling low coverage groups")
        low_coverage_ids = self.idea_organizer.flag_low_coverage_groups(organized_groups, threshold=0.5)
        if low_coverage_ids:
            logger.info(f"Regenerating for low coverage groups: {low_coverage_ids}")
            additional_ideas = self.batch_generator.run_for_groups(low_coverage_ids)
            if additional_ideas:
                all_ideas = cleaned_ideas + additional_ideas
                cleaned_ideas, additional_reports = self.deduplicator.deduplicate_across_groups(all_ideas)
                dedup_reports.extend(additional_reports)
                organized_groups = self.idea_organizer.organize(cleaned_ideas)
                coverage_summary = self.formatter.format_coverage_summary(organized_groups)

        # Phase 8 - Format & Write
        logger.info("Phase 8: Formatting and writing output")
        formatted_output = self.formatter.format(organized_groups, source_analysis.title)
        output_path = self.writer.write(formatted_output)
        self.writer.write_log(dedup_reports, coverage_summary, output_path)

        logger.info(f"Pipeline completed successfully. Output written to {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Ontology Idea Generator from Source Texts")
    parser.add_argument("--grouped-ontology", required=True, help="Path to grouped_ontology_ideas.md")
    parser.add_argument("--merged-ideas", required=True, help="Path to merged_ontology_ideas.md")
    parser.add_argument("--source-text", required=True, help="Path to source text file")
    parser.add_argument("--output", required=True, help="Path for output")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json", "text"], help="Output format")
    parser.add_argument("--ideas-per-group", type=int, default=10, help="Target ideas per group")
    parser.add_argument("--model", default="claude-3-5-sonnet-20240620", help="Anthropic model name")

    args = parser.parse_args()

    # Environment variables or CLI args
    config = Config(
        grouped_ontology_path=args.grouped_ontology,
        merged_ideas_path=args.merged_ideas,
        source_text_path=args.source_text,
        output_path=args.output,
        model_name=args.model,
        ideas_per_group=args.ideas_per_group,
        output_format=args.format,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    if not config.validate():
        logger.error("Invalid configuration. Check file paths and parameters.")
        sys.exit(1)

    pipeline = OntologyIdeaGeneratorPipeline(config)
    try:
        pipeline.run()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
