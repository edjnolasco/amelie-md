from amelie_md.core.semantic_pipeline import prepare_semantic_blocks


def test_prepare_semantic_blocks_normalizes_numbers_references_and_indexes():
    blocks = [
        {"type": "heading", "level": 1, "text": "Capítulo"},
        {"type": "paragraph", "text": "[[LIST_OF_FIGURES]]"},
        {"type": "paragraph", "text": ":::figure arch-main Arquitectura"},
        {"type": "paragraph", "text": "Diagrama."},
        {"type": "paragraph", "text": ":::"},
        {"type": "paragraph", "text": "Ver {{ref:arch-main}}."},
    ]

    prepared = prepare_semantic_blocks(
        blocks,
        html_links=True,
        inject_indexes=True,
    )

    assert prepared[1]["type"] == "semantic_index"
    assert prepared[1]["items"][0]["label"] == "Figure 1.1"
    assert prepared[2]["type"] == "figure"
    assert prepared[2]["label"] == "Figure 1.1"
    assert prepared[3]["text"] == 'Ver <a class="semantic-reference" href="#arch-main">Figure 1.1</a>.'


def test_prepare_semantic_blocks_can_skip_index_injection():
    blocks = [
        {"type": "paragraph", "text": "[[LIST_OF_FIGURES]]"},
    ]

    prepared = prepare_semantic_blocks(
        blocks,
        inject_indexes=False,
    )

    assert prepared == blocks
