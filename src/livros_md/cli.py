from __future__ import annotations

import argparse
import getpass
import importlib.metadata
import os
import platform
import sys
from pathlib import Path

from .local import convert_local, default_local_output
from .mistral_ocr import (
    DEFAULT_MODEL,
    count_pdf_pages,
    extract_markdown,
    run_mistral_ocr,
)


def existing_file(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"arquivo não encontrado: {path}")
    return path


def writable_output(path: Path, *, input_path: Path, force: bool) -> Path:
    output = path.expanduser().resolve()
    if output == input_path:
        raise SystemExit("A saída não pode sobrescrever o arquivo de entrada.")
    if output.exists() and not force:
        raise SystemExit(
            f"A saída já existe: {output}\nUse --force para substituí-la."
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def command_local(args: argparse.Namespace) -> int:
    output = writable_output(
        args.output or default_local_output(args.input),
        input_path=args.input,
        force=args.force,
    )
    print(f"Convertendo localmente: {args.input}")
    output.write_text(convert_local(args.input), encoding="utf-8")
    print(f"Markdown salvo em: {output}")
    return 0


def command_ocr(args: argparse.Namespace) -> int:
    if args.input.suffix.lower() != ".pdf":
        raise SystemExit("O comando ocr aceita somente arquivos PDF.")

    output = writable_output(
        args.output or args.input.with_suffix(".ocr.md"),
        input_path=args.input,
        force=args.force,
    )
    raw_json = writable_output(
        args.raw_json or args.input.with_suffix(".ocr.json"),
        input_path=args.input,
        force=args.force,
    )
    if raw_json == output:
        raise SystemExit("O Markdown e o JSON bruto precisam de caminhos diferentes.")

    pages = count_pdf_pages(args.input)
    size_mb = args.input.stat().st_size / 1_048_576
    print(f"PDF: {args.input}")
    print(f"Páginas: {pages}")
    print(f"Tamanho: {size_mb:.1f} MB")
    print(f"Modelo: {args.model}")
    print(f"Saída: {output}")

    if not args.yes:
        confirmation = input(
            "\nIsso enviará o PDF à Mistral e poderá consumir créditos. "
            "Digite PROCESSAR para continuar: "
        ).strip()
        if confirmation != "PROCESSAR":
            print("Cancelado antes de chamar a API.")
            return 1

    api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not api_key:
        api_key = getpass.getpass(
            "Cole sua MISTRAL_API_KEY. Ela não será salva nem exibida: "
        ).strip()
    if not api_key:
        raise SystemExit("Chave Mistral ausente.")

    print("Enviando e processando o PDF na Mistral...")
    response = run_mistral_ocr(args.input, api_key=api_key, model=args.model)
    import json

    raw_json.write_text(
        json.dumps(response, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    output.write_text(extract_markdown(response), encoding="utf-8")
    print(f"Markdown salvo em: {output}")
    print(f"JSON bruto salvo em: {raw_json}")
    return 0


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "NÃO INSTALADO"


def command_doctor(_: argparse.Namespace) -> int:
    print(f"Sistema: {platform.system()} {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print(f"Executável: {sys.executable}")
    print(f"MarkItDown: {package_version('markitdown')}")
    print(f"Mistral SDK: {package_version('mistralai')}")
    print(f"pypdf: {package_version('pypdf')}")
    configured = bool(os.getenv("MISTRAL_API_KEY", "").strip())
    print(f"MISTRAL_API_KEY configurada: {'sim' if configured else 'não'}")

    supported = (3, 12) <= sys.version_info[:2] < (3, 14)
    packages_ok = all(
        package_version(name) != "NÃO INSTALADO"
        for name in ("markitdown", "mistralai", "pypdf")
    )
    if supported and packages_ok:
        print("Diagnóstico: ambiente pronto.")
        return 0
    print("Diagnóstico: ambiente incompleto; execute o instalador novamente.")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="livros-md",
        description="Converte livros e documentos para Markdown.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    local = subparsers.add_parser(
        "local",
        help="Converte localmente com MarkItDown (sem custo de API).",
    )
    local.add_argument("input", type=existing_file, help="Arquivo de entrada.")
    local.add_argument("-o", "--output", type=Path, help="Markdown de saída.")
    local.add_argument("--force", action="store_true", help="Substitui a saída.")
    local.set_defaults(handler=command_local)

    ocr = subparsers.add_parser(
        "ocr",
        help="Executa OCR de PDF escaneado com a API paga da Mistral.",
    )
    ocr.add_argument("input", type=existing_file, help="PDF de entrada.")
    ocr.add_argument("-o", "--output", type=Path, help="Markdown de saída.")
    ocr.add_argument("--raw-json", type=Path, help="JSON bruto da Mistral.")
    ocr.add_argument("--model", default=DEFAULT_MODEL, help="Modelo OCR.")
    ocr.add_argument("--yes", action="store_true", help="Pula confirmação de custo.")
    ocr.add_argument("--force", action="store_true", help="Substitui as saídas.")
    ocr.set_defaults(handler=command_ocr)

    doctor = subparsers.add_parser("doctor", help="Confere a instalação.")
    doctor.set_defaults(handler=command_doctor)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.handler(args))
    except KeyboardInterrupt:
        print("\nCancelado.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
