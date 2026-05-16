from amelie_md.core.semantic_contract import (
    get_semantic_contract,
    is_semantic_block_type,
    validate_semantic_block,
)


def test_get_definition_contract():
    contract = get_semantic_contract("definition")

    assert contract is not None
    assert contract.numbered is True
    assert contract.referenceable is True
    assert contract.indexable is True


def test_is_semantic_block_type():
    assert is_semantic_block_type("figure") is True
    assert is_semantic_block_type("paragraph") is False


def test_validate_valid_definition_block():
    errors = validate_semantic_block(
        {
            "type": "definition",
            "title": "Concepto",
            "text": "Contenido",
            "id": "concept",
        }
    )

    assert errors == []


def test_validate_missing_required_field():
    errors = validate_semantic_block(
        {
            "type": "figure",
            "title": "Figura",
        }
    )

    assert "Missing required field 'text' for 'figure' block." in errors


def test_validate_empty_reference_id():
    errors = validate_semantic_block(
        {
            "type": "figure",
            "title": "Figura",
            "text": "Contenido",
            "id": "   ",
        }
    )

    assert "Empty optional field 'id' for referenceable 'figure' block." in errors


def test_unknown_block_has_no_contract_errors():
    errors = validate_semantic_block(
        {
            "type": "paragraph",
            "text": "Texto",
        }
    )

    assert errors == []
