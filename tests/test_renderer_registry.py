import pytest

from amelie_md.renderers.registry import RendererRegistry


def test_register_and_get_renderer():
    registry = RendererRegistry()

    def render(block):
        return f"<p>{block['text']}</p>"

    registry.register("paragraph", render)

    renderer = registry.get("paragraph")

    assert renderer({"text": "Hola"}) == "<p>Hola</p>"


def test_register_duplicate_renderer_raises_error():
    registry = RendererRegistry()

    def render(block):
        return ""

    registry.register("paragraph", render)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("paragraph", render)


def test_get_missing_renderer_raises_error():
    registry = RendererRegistry()

    with pytest.raises(ValueError, match="No renderer registered"):
        registry.get("unknown")


def test_has_renderer():
    registry = RendererRegistry()

    def render(block):
        return ""

    registry.register("heading", render)

    assert registry.has("heading") is True
    assert registry.has("paragraph") is False