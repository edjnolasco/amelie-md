from amelie_md.core.semantic_types import (
    DEFINITION_TYPE,
    FIGURE_TYPE,
    INDEXABLE_SEMANTIC_TYPES,
    NUMBERED_SEMANTIC_TYPES,
    REFERENCEABLE_SEMANTIC_TYPES,
    SEMANTIC_BLOCK_TYPES,
)


def test_semantic_block_types_include_academic_primitives():
    assert DEFINITION_TYPE in SEMANTIC_BLOCK_TYPES
    assert FIGURE_TYPE in SEMANTIC_BLOCK_TYPES


def test_numbered_referenceable_and_indexable_types_are_aligned():
    assert NUMBERED_SEMANTIC_TYPES == REFERENCEABLE_SEMANTIC_TYPES
    assert NUMBERED_SEMANTIC_TYPES == INDEXABLE_SEMANTIC_TYPES
