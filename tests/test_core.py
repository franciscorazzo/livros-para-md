from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from livros_md.cli import writable_output
from livros_md.local import convert_local
from livros_md.mistral_ocr import extract_markdown, response_as_dict


class FakeResponse:
    def model_dump(self, *, mode: str) -> dict:
        assert mode == "json"
        return {"pages": [{"index": 0, "markdown": "Texto"}]}


class CoreTests(unittest.TestCase):
    def test_mistral_sdk_import_is_available(self) -> None:
        from mistralai.client import Mistral

        self.assertTrue(callable(Mistral))

    def test_markitdown_converts_local_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir, "sample.html")
            source.write_text(
                "<html><body><h1>Livro de teste</h1><p>Texto local.</p></body></html>",
                encoding="utf-8",
            )
            result = convert_local(source)
            self.assertIn("# Livro de teste", result)
            self.assertIn("Texto local.", result)

    def test_extract_markdown_preserves_page_markers(self) -> None:
        response = {
            "pages": [
                {"index": 0, "markdown": "# Título"},
                {"index": 1, "markdown": "Página seguinte"},
            ]
        }
        result = extract_markdown(response)
        self.assertEqual(
            result,
            "<!-- page 0 -->\n\n# Título\n\n<!-- page 1 -->\n\nPágina seguinte\n",
        )

    def test_response_as_dict_accepts_sdk_model(self) -> None:
        self.assertEqual(
            response_as_dict(FakeResponse()),
            {"pages": [{"index": 0, "markdown": "Texto"}]},
        )

    def test_output_does_not_overwrite_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir, "book.md").resolve()
            source.write_text("texto", encoding="utf-8")
            with self.assertRaises(SystemExit):
                writable_output(source, input_path=source, force=True)


if __name__ == "__main__":
    unittest.main()
