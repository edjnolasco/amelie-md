from pathlib import Path

from docx import Document

from amelie_md.exporters.docx import DocxExporter, DocxMetadata


def test_docx_exporter_creates_docx_with_core_elements(tmp_path: Path) -> None:
    markdown = """# Main Title

## Section

This is a paragraph.

- First item
- Second item

| Name | Value |
| ---- | ----- |
| A    | 1     |

```python
print("hello")

"""
    output_path = tmp_path / "output.docx"

    exporter = DocxExporter(
        metadata=DocxMetadata(
            title="Test Document",
            author="Amelie Suite",
            date="2026-04-28",
        )
    )

    exporter.export(markdown, output_path)

    assert output_path.exists()

    document = Document(output_path)
    paragraphs = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "Test Document" in paragraphs
    assert "Main Title" in paragraphs
    assert "Section" in paragraphs
    assert "This is a paragraph." in paragraphs
    assert "First item" in paragraphs
    assert "Second item" in paragraphs
    assert 'print("hello")' in paragraphs

    assert len(document.tables) == 1
    assert document.tables[0].cell(0, 0).text == "Name"
    assert document.tables[0].cell(1, 1).text == "1"