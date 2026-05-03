from amelie_core.pipeline.document_pipeline import process_document


def process_markdown_with_core(markdown_text: str, style_text: str | None = None):
    return process_document(markdown_text, style_text)