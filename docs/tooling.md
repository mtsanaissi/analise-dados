# Ferramentas e Fluxo Local

Este repositório ainda não adotou um stack único de tooling no estilo template novo. A referência atual deve ser o que já existe no projeto.

## Ambiente atual

- Ambiente virtual local em `.venv/`
- Dependências listadas em `requirements.txt`
- Empacotamento mínimo em `setup.py`
- Testes com `pytest`
- Configuração de testes em `pytest.ini`
- Interface gráfica com Streamlit

## Instalação local

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

## Pre-commit

Este projeto agora pode usar hooks básicos de higiene com `pre-commit`.

Instalação:

```bash
pip install pre-commit
pre-commit install
```

Execução manual em todo o repositório:

```bash
pre-commit run --all-files
```

## Comandos úteis

- Interface gráfica: `streamlit run app.py`
- Ajuda da CLI: `python3 -m src.run --help`
- Discovery: `python3 -m src.run discovery --help`
- Treatment: `python3 -m src.run treatment --help`
- Rename columns: `python3 -m src.run treatment rename_columns --help`

## Importante

- Não trate `uv`, `ruff`, `pyright` ou um `pyproject.toml` placeholder como convenções oficiais deste repositório sem uma decisão explícita.
- Antes de introduzir nova ferramenta de lint, tipagem, automação ou CI, alinhe a documentação e os comandos reais do projeto.
