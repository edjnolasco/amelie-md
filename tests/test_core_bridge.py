from amelie_md.core_bridge.pipeline import process_markdown_with_core


def test_core_bridge_processes_markdown():
    result = process_markdown_with_core("# Title\n\n## Section\nContent")

    assert result["document"].title == "Title"
    assert result["validation"].is_valid()