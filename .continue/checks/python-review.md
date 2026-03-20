# Review Python do Repositório

Use este check para mudanças substanciais neste toolkit de análise de dados.

Foque em:

- Aderência ao `AGENTS.md`, incluindo docstrings em português, identificadores em inglês, resiliência por arquivo e uso de `logging`.
- Compatibilidade com o fluxo real do projeto: CLI em `src/run.py`, interface Streamlit em `src/app_main_interface.py` e módulos por fase em `src/phases/`.
- Fronteiras de IO e tratamento de erro ao ler ou escrever CSV, XLSX, JSON, TXT, YAML e relatórios gerados em `data/<projeto>/`.
- Preservação de artefatos e convenções de dados, incluindo relatórios `discovery_report.*`, saídas `fad-*`, backups de tratamento e arquivos de exemplo em `data/sample/`.
- Impacto em notebooks, conectores, YAMLs de configuração e reprodutibilidade local quando a mudança altera fluxos de análise ou tratamento.
- Cobertura de testes e validação realista para caminhos de sucesso e falha, sem presumir stacks placeholder como `uv`, `ruff` ou `pyright` como se já fossem padrão do repositório.
- Drift de documentação entre `LEIAME.md`, `COMO_USAR.md`, `docs/` e o comportamento implementado no código.
