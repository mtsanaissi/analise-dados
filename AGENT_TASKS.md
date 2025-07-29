# Tarefas do Projeto

## Backlog

*   **ID:** T007
    **Título:** Corrigir Leitura de Arquivos XLSX na Fase 2
    **Descrição:** O `XlsxConnector` está retornando um dicionário de DataFrames (um por planilha) em vez de um único DataFrame, causando um `AttributeError` no pipeline da Fase 2. É necessário ajustar o conector para ler apenas a primeira planilha por padrão.
    **Critérios de Aceitação:**
    - [ ] Modificar o método `read` em `src/connectors/xlsx_connector.py`.
    - [ ] Garantir que, se nenhum `sheet_name` for especificado, o conector leia a *primeira* planilha do arquivo Excel (índice 0) por padrão.
    - [ ] O método `read` deve sempre retornar um objeto `pd.DataFrame`, e não um dicionário.
    - [ ] Validar que a Fase 2 (`python src/run.py -d data/beneficios-qualireg -p treatment`) executa sem erros para arquivos `.xlsx`.

## Em Andamento

## Concluído

*   **ID:** T003
    **Título:** Implementar Testes para Componentes Principais
    **Descrição:** Criar testes unitários para os módulos centrais do projeto, garantindo a robustez das funcionalidades de base.
    **Critérios de Aceitação:**
    - [x] Cobertura de testes para `src/utils.py`.
    - [x] Cobertura de testes para os conectores em `src/connectors/`.
    - [x] Cobertura de testes para o orquestrador principal `src/main/orchestrator.py`.

*   **ID:** T004
    **Título:** Implementar Testes para a Fase 2 (Tratamento)
    **Descrição:** Desenvolver testes para todos os módulos do núcleo da fase de tratamento de dados.
    **Critérios de Aceitação:**
    - [x] Cobertura de testes para `src/phases/phase02_treatment/core/column_transformer.py`.
    - [x] Cobertura de testes para `src/phases/phase02_treatment/core/data_enricher.py`.
    - [x] Cobertura de testes para `src/phases/phase02_treatment/core/problematic_value_extractor.py`.
    - [x] Cobertura de testes para `src/phases/phase02_treatment/core/value_corrector.py`.
    - [x] Testes para o orquestrador `src/phases/phase02_treatment/phase02_orchestrator.py`.

*   **ID:** T005
    **Título:** Implementar Testes para a Fase 3 (Exploratória)
    **Descrição:** Criar testes para os scripts da fase de análise exploratória.
    **Critérios de Aceitação:**
    - [x] Cobertura de testes para `src/phases/phase03_exploratory/p3_01_explore_distinct_values.py`.
    - [x] Cobertura de testes para `src/phases/phase03_exploratory/p3_02_preprocess_filter_batch.py`.
    - [x] Cobertura de testes para `src/phases/phase03_exploratory/p3_03_transform_denormalize_rows.py`.

*   **ID:** T006
    **Título:** Implementar Testes para a Fase 4 (Visualização)
    **Descrição:** Desenvolver testes para as aplicações de visualização e ferramentas de geração de relatórios.
    **Critérios de Aceitação:**
    - [x] Cobertura de testes para `src/phases/phase04_visualization/app_explore_aggregated_profiles.py`.
    - [x] Cobertura de testes para `src/phases/phase04_visualization/app_explore_single_profile.py`.
    - [x] Cobertura de testes para `src/phases/phase04_visualization/app_generic_data_analyzer.py`.
    - [x] Cobertura de testes para `src/phases/phase04_visualization/tool_generate_html_profiles.py`.
