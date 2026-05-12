from __future__ import annotations

from dataclasses import dataclass

from amelie_md.core.semantic_types import (
    ADMONITION_TYPE,
    DEFINITION_TYPE,
    FIGURE_TYPE,
    QUOTE_TYPE,
    SEMANTIC_INDEX_TYPE,
)


@dataclass(frozen=True)
class SemanticBlockContract:
    block_type: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    numbered: bool = False
    referenceable: bool = False
    indexable: bool = False


SEMANTIC_BLOCK_CONTRACTS: dict[str, SemanticBlockContract] = {
    ADMONITION_TYPE: SemanticBlockContract(
        block_type=ADMONITION_TYPE,
        required_fields=("type", "kind", "text"),
        optional_fields=("title",),
    ),
    DEFINITION_TYPE: SemanticBlockContract(
        block_type=DEFINITION_TYPE,
        required_fields=("type", "title", "text"),
        optional_fields=("id", "kind", "number", "chapter", "label"),
        numbered=True,
        referenceable=True,
        indexable=True,
    ),
    FIGURE_TYPE: SemanticBlockContract(
        block_type=FIGURE_TYPE,
        required_fields=("type", "title", "text"),
        optional_fields=("id", "kind", "number", "chapter", "label"),
        numbered=True,
        referenceable=True,
        indexable=True,
    ),
    QUOTE_TYPE: SemanticBlockContract(
        block_type=QUOTE_TYPE,
        required_fields=("type", "text"),
        optional_fields=("title", "kind"),
    ),
    SEMANTIC_INDEX_TYPE: SemanticBlockContract(
        block_type=SEMANTIC_INDEX_TYPE,
        required_fields=("type", "kind", "title", "items"),
        optional_fields=(),
    ),
}


def get_semantic_contract(block_type: str) -> SemanticBlockContract | None:
    return SEMANTIC_BLOCK_CONTRACTS.get(block_type)


def is_semantic_block_type(block_type: str) -> bool:
    return block_type in SEMANTIC_BLOCK_CONTRACTS


def validate_semantic_block(block: dict) -> list[str]:
    block_type = str(block.get("type", "")).strip()
    contract = get_semantic_contract(block_type)

    if contract is None:
        return []

    errors: list[str] = []

    for field in contract.required_fields:
        value = block.get(field)

        if value is None:
            errors.append(f"Missing required field '{field}' for '{block_type}' block.")
            continue

        if isinstance(value, str) and not value.strip():
            errors.append(f"Empty required field '{field}' for '{block_type}' block.")

    if contract.referenceable and block.get("id") is not None:
        identifier = str(block.get("id", "")).strip()

        if not identifier:
            errors.append(f"Empty optional field 'id' for referenceable '{block_type}' block.")

    return errors
