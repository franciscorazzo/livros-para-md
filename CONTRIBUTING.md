# Como contribuir

Obrigado pelo interesse em melhorar o Livros para Markdown.

## Antes de começar

- abra uma issue descrevendo bugs ou mudanças relevantes;
- não anexe livros, chaves de API, documentos privados ou respostas de OCR;
- preserve a confirmação explícita antes de qualquer chamada paga;
- mantenha o comportamento compatível com macOS e Windows.

## Ambiente de desenvolvimento

Execute o instalador da sua plataforma conforme o README e ative `.venv`.
Depois:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
livros-md doctor
```

## Pull requests

Mantenha mudanças pequenas e focadas. Inclua testes para o comportamento novo e
explique riscos de privacidade, custo ou compatibilidade. Os testes automáticos
não devem chamar a API da Mistral.
