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

- Interface gráfica: `streamlit run src/app_main_interface.py`
- Ajuda da CLI: `python src/run.py --help`
- Discovery: `python src/run.py discovery --help`
- Treatment: `python src/run.py treatment --help`

## Importante

- Não trate `uv`, `ruff`, `pyright` ou um `pyproject.toml` placeholder como convenções oficiais deste repositório sem uma decisão explícita.
- Antes de introduzir nova ferramenta de lint, tipagem, automação ou CI, alinhe a documentação e os comandos reais do projeto.
