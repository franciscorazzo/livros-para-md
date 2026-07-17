from __future__ import annotations

from pathlib import Path


def default_local_output(input_path: Path) -> Path:
    return input_path.with_suffix(".md")


def convert_local(input_path: Path) -> str:
    """Converte um arquivo local com o Microsoft MarkItDown."""
    from markitdown import MarkItDown

    converter = MarkItDown(enable_plugins=False)
    result = converter.convert_local(input_path)
    text = result.text_content or ""
    return text.rstrip() + "\n"
