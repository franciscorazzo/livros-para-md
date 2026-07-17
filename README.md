# Livros para Markdown

[![Testes](https://github.com/franciscorazzo/livros-para-md/actions/workflows/tests.yml/badge.svg)](https://github.com/franciscorazzo/livros-para-md/actions/workflows/tests.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE)

Converta livros e documentos para Markdown por extração local ou OCR. O projeto
combina o [Microsoft MarkItDown](https://github.com/microsoft/markitdown) para
arquivos que já contêm texto com o
[Mistral Document AI](https://docs.mistral.ai/studio-api/document-processing/basic_ocr)
para PDFs escaneados.

## O que o projeto faz

- converte localmente PDF, EPUB, DOCX, PPTX, XLSX, HTML e outros formatos;
- reconhece PDFs escaneados com `mistral-ocr-latest`;
- preserva marcadores de página no Markdown produzido pelo OCR;
- salva a resposta bruta da Mistral em JSON para auditoria e reaproveitamento;
- remove da Mistral o arquivo temporário após o processamento;
- pede confirmação explícita antes de uma chamada que pode consumir créditos;
- funciona em macOS e Windows com dependências reproduzíveis.

## Onde o programa fica instalado?

O comando `git clone` cria uma pasta normal chamada `livros-para-md` no
computador. Tudo fica dentro dela:

```text
livros-para-md/
├── .venv/       # Python e bibliotecas isolados
├── entrada/     # documentos do usuário; ignorados pelo Git
├── saida/       # Markdown e JSON gerados; ignorados pelo Git
├── scripts/     # instaladores para macOS e Windows
└── src/         # código do programa
```

O instalador não substitui o Python do sistema nem instala as bibliotecas
globalmente. Para desinstalar, feche o Terminal e mova a pasta
`livros-para-md` para o Lixo. Documentos que devam ser preservados precisam ser
retirados antes das pastas `entrada/` e `saida/`.

## Qual método escolher?

| Situação | Comando | Envia o arquivo? | Custo de API |
|---|---|---:|---:|
| PDF ou documento com texto selecionável | `livros-md local` | Não | Não |
| PDF escaneado ou fotografado | `livros-md ocr` | Sim, à Mistral | Pode haver |

Comece pelo método local. Recorra ao OCR apenas se o Markdown vier vazio,
incompleto ou ilegível.

## Instalação no macOS

### 1. Pré-requisitos

Abra o aplicativo **Terminal**. O instalador usa, nesta ordem:

- `uv`, caso já esteja disponível; ou
- Python 3.12; ou
- [Homebrew](https://brew.sh/) para instalar Python 3.12.

O Git pode ser instalado pelas Command Line Tools do próprio macOS quando o
sistema solicitar.

### 2. Baixar e instalar

```bash
git clone https://github.com/franciscorazzo/livros-para-md.git
cd livros-para-md
chmod +x scripts/setup-macos.sh
./scripts/setup-macos.sh
source .venv/bin/activate
livros-md doctor
```

O diagnóstico deve terminar com `Diagnóstico: ambiente pronto.`

### 3. Usar novamente em outro dia

Em uma nova janela do Terminal:

```bash
cd caminho/para/livros-para-md
source .venv/bin/activate
```

## Instalação no Windows

Abra o PowerShell dentro da pasta clonada e execute:

```powershell
.\scripts\setup-windows.ps1
.\.venv\Scripts\Activate.ps1
livros-md doctor
```

## Conversão local com MarkItDown

Coloque o documento na pasta `entrada` e execute:

```bash
livros-md local "entrada/meu-livro.pdf" -o "saida/meu-livro.md"
```

Outro exemplo:

```bash
livros-md local "entrada/meu-livro.epub" -o "saida/meu-livro.md"
```

O arquivo original permanece intacto. Uma saída existente só será substituída
se o usuário acrescentar `--force`.

## PDF escaneado com Mistral OCR

### 1. Obter uma chave

Crie uma conta no [Mistral AI Studio](https://console.mistral.ai/) e gere sua
própria API key. Não publique nem compartilhe essa chave.

### 2. Processar o PDF

Sem configurar nenhum arquivo de segredo:

```bash
livros-md ocr "entrada/livro-escaneado.pdf" \
  -o "saida/livro-escaneado.md" \
  --raw-json "saida/livro-escaneado.ocr.json"
```

O programa solicitará a chave sem exibi-la ou salvá-la. Em seguida, mostrará
caminho, número de páginas, tamanho e modelo. A chamada só ocorrerá depois que
o usuário digitar `PROCESSAR`.

Também é possível definir a chave apenas na sessão atual do macOS:

```bash
export MISTRAL_API_KEY="sua-chave"
```

No PowerShell:

```powershell
$env:MISTRAL_API_KEY="sua-chave"
```

## Privacidade, custos e direitos autorais

- `livros-md local` trabalha no computador e não envia o documento à Mistral.
- `livros-md ocr` envia o PDF à Mistral e pode consumir créditos da conta.
- O upload temporário é removido ao final; se a remoção não puder ser
  confirmada, o programa mostra um aviso.
- `.gitignore` exclui documentos, saídas, chaves e ambientes locais.
- O usuário é responsável por ter autorização para processar, armazenar e
  compartilhar cada documento.

Consulte também os termos e a política de privacidade do serviço Mistral antes
de processar material confidencial ou dados pessoais.

## Comandos

```bash
livros-md --help
livros-md local --help
livros-md ocr --help
livros-md doctor
```

## Desenvolvimento

As dependências diretas estão em `pyproject.toml`; o conjunto completo de
versões está congelado em `requirements.lock`.

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
livros-md doctor
```

Os testes não acessam a API da Mistral nem consomem créditos. O GitHub Actions
repete a verificação em macOS e Windows.

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para contribuir e
[SECURITY.md](SECURITY.md) para relatar vulnerabilidades.

## Limitações

- a qualidade depende do arquivo original e, no OCR, do serviço da Mistral;
- diagramas, notas marginais e layouts complexos podem exigir revisão manual;
- o projeto não revisa, corrige ou normaliza automaticamente o conteúdo;
- cada comando processa um arquivo por vez nesta versão.

## Licença

Código distribuído sob a [licença MIT](LICENSE). MarkItDown, Mistral SDK e
demais dependências possuem licenças e termos próprios.
