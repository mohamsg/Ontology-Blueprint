import os
import json
from .formatter import FormattedOutput
from ..templates.template_store import TemplateStore

class Writer:
    def __init__(self, output_path: str, overwrite: bool = True):
        self.output_path = output_path
        self.overwrite = overwrite

    def write(self, formatted_output: FormattedOutput) -> str:
        # If output_path is a directory, append filename
        path = self.output_path
        if os.path.isdir(path):
            ext = "md" if formatted_output.format == "markdown" else formatted_output.format
            filename = f"generated_ideas_{formatted_output.generation_timestamp.replace(':', '-')}.{ext}"
            path = os.path.join(path, filename)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(formatted_output.content)

        return path

    def write_log(self, deduplication_report: list, coverage_summary: str, output_filepath: str) -> None:
        log_path = output_filepath + ".log"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Output File: {output_filepath}\n\n")
            f.write("Coverage Summary:\n")
            f.write(coverage_summary)
            f.write("\n\nDeduplication Report:\n")
            for report in deduplication_report:
                f.write(f"- {report.original_idea_name} <-> {report.duplicate_idea_name}: {report.similarity_score} ({report.reason})\n")

    def write_templates(self, template_store: TemplateStore) -> None:
        template_path = self.output_path + ".templates.json"
        if os.path.isdir(self.output_path):
             template_path = os.path.join(self.output_path, "templates.json")

        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_store.export_to_dict(), f, indent=2)
