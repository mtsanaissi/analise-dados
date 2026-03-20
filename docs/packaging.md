# Empacotamento e Execução

O objetivo principal deste repositório é oferecer um toolkit executável para análise de dados, não um pacote distribuído com convenções de fresh repo.

## Estado atual

- A base de dependências está em `requirements.txt`.
- O empacotamento atual é mínimo e usa `setup.py`.
- O ponto de entrada operacional da linha de comando é `src/run.py`.
- A interface gráfica é executada via Streamlit em `src/app_main_interface.py`.

## O que isso implica

- `requirements.txt` continua sendo a fonte prática de instalação até que o projeto decida migrar deliberadamente para outro padrão.
- Mudanças em nome de pacote, backend de build ou fonte de verdade de dependências não devem ser feitas incidentalmente.
- Se houver necessidade futura de migrar para `pyproject.toml`, isso deve ser tratado como uma mudança de arquitetura, com atualização coordenada de documentação, comandos locais e CI.

## Aspectos do domínio que importam mais aqui

- Compatibilidade com arquivos de dados reais e diretórios `data/<projeto>/`
- Geração de relatórios e artefatos intermediários por fase
- Reprodutibilidade de execuções CLI e GUI
- Conectores, YAMLs de configuração e notebooks de apoio

## Antes de mudar a estrutura de execução

Revise estes pontos:

- comandos documentados em `LEIAME.md` e `COMO_USAR.md`
- efeitos sobre `tests/`
- expectativas registradas em `AGENTS.md`
- impacto sobre usuários em Windows 11
