from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader


DEFAULT_MODEL = "mistral-ocr-latest"


def count_pdf_pages(pdf_path: Path) -> int:
    return len(PdfReader(str(pdf_path)).pages)


def response_as_dict(response: Any) -> dict[str, Any]:
    if isinstance(response, dict):
        return response
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    if hasattr(response, "model_dump_json"):
        return json.loads(response.model_dump_json())
    raise TypeError("A resposta da Mistral não pôde ser convertida para JSON.")


def extract_markdown(ocr_response: dict[str, Any]) -> str:
    chunks: list[str] = []
    for position, page in enumerate(ocr_response.get("pages") or [], start=1):
        page_number = page.get("index", position)
        markdown = (page.get("markdown") or "").strip()
        chunks.append(f"\n\n<!-- page {page_number} -->\n\n{markdown}")

    text = "".join(chunks).strip()
    if not text:
        text = json.dumps(ocr_response, ensure_ascii=False, indent=2)
    return text + "\n"


def run_mistral_ocr(
    pdf_path: Path,
    *,
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Envia um PDF à Mistral, executa OCR e remove o upload temporário."""
    from mistralai.client import Mistral

    uploaded_file_id: str | None = None
    with Mistral(api_key=api_key) as client:
        try:
            with pdf_path.open("rb") as handle:
                uploaded = client.files.upload(
                    file={"file_name": pdf_path.name, "content": handle},
                    purpose="ocr",
                )
            uploaded_file_id = uploaded.id

            signed = client.files.get_signed_url(
                file_id=uploaded_file_id,
                expiry=24,
            )
            response = client.ocr.process(
                model=model,
                document={
                    "type": "document_url",
                    "document_url": signed.url,
                },
                include_image_base64=False,
            )
            return response_as_dict(response)
        finally:
            if uploaded_file_id:
                try:
                    client.files.delete(file_id=uploaded_file_id)
                except Exception as exc:  # a extração já pode ter terminado
                    print(
                        "Aviso: não foi possível confirmar a remoção do arquivo "
                        f"temporário da Mistral: {exc}"
                    )
