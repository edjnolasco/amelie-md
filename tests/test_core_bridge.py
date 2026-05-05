from amelie_md.core_bridge.pipeline import process_markdown_with_core


def test_core_bridge_processes_markdown():
    result = process_markdown_with_core("# Title\n\n## Section\nContent")

    document = result["document"]

    assert hasattr(document, "blocks")
    assert document.blocks[0]["type"] == "heading"
    assert document.blocks[0]["level"] == 1
    assert document.blocks[0]["text"] == "Title"

    assert document.blocks[1]["type"] == "heading"
    assert document.blocks[1]["level"] == 2
    assert document.blocks[1]["text"] == "Section"

    assert document.blocks[2]["type"] == "paragraph"
    assert document.blocks[2]["text"] == "Content"

    assert "validation" in result
    assert "style" in result
