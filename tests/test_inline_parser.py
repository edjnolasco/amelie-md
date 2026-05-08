from amelie_md.parsing.inline_parser import parse_inline


def test_plain_text():
    runs = parse_inline("Texto normal")

    assert len(runs) == 1
    assert runs[0].text == "Texto normal"


def test_bold():
    runs = parse_inline("Texto **bold**")

    assert any(run.bold for run in runs)
    assert any(run.text == "bold" for run in runs)


def test_italic():
    runs = parse_inline("Texto *italic*")

    assert any(run.italic for run in runs)
    assert any(run.text == "italic" for run in runs)


def test_inline_code():
    runs = parse_inline("Usar `amelie build`")

    assert any(run.code for run in runs)
    assert any(run.text == "amelie build" for run in runs)


def test_link():
    runs = parse_inline("[OpenAI](https://openai.com)")

    assert any(run.link for run in runs)


def test_mixed_inline():
    runs = parse_inline(
        "Texto **bold**, *italic*, `code` y [link](https://x.com)"
    )

    assert any(run.bold for run in runs)
    assert any(run.italic for run in runs)
    assert any(run.code for run in runs)
    assert any(run.link for run in runs)