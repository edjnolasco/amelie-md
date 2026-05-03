from pathlib import Path

from amelie_md.exporters.docx import DocxExporter, DocxMetadata
from amelie_md.importers.docx import DocxImporter


input_path = Path("examples/input.docx")
output_path = Path("examples/output_reformatted.docx")

importer = DocxImporter()
amelie_document = importer.import_file(input_path)

markdown = amelie_document.to_markdown()

metadata = DocxMetadata(
    title="Documento reformateado",
    author="Edwin José Nolasco",
)

exporter = DocxExporter(metadata=metadata, style="academic")

exporter.export(
    markdown_text=markdown,
    output_path=output_path,
)