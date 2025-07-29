# Tarefas do Projeto

## Backlog

*   **ID:** T010
    **Título:** Refatorar Saída de Artefatos para Diretório Dedicado
    **Descrição:** Atualmente, as fases 1 e 2 geram arquivos de saída (relatórios, dados tratados) no diretório principal do projeto de dados, exigindo regras de exclusão frágeis. Esta tarefa visa centralizar todos os artefatos gerados em um subdiretório dedicado chamado `fad-metadados` para aumentar a robustez e a organização.
    **Critérios de Aceitação:**
    - [ ] Definir uma constante global ou uma função utilitária para o nome do diretório de metadados, `fad-metadados`.
    - [ ] Em `src/phases/phase01_discovery/phase01_orchestrator.py`:
        - [ ] Modificar a lógica para que os relatórios (`discovery_report.json`, `discovery_report.html`) sejam salvos dentro de `[data_project_path]/fad-metadados/`.
        - [ ] O diretório `fad-metadados` deve ser criado automaticamente se não existir.
        - [ ] Simplificar a lógica de descoberta de arquivos (`find_files`) para excluir qualquer arquivo contido no diretório `fad-metadados`, em vez de usar padrões de nome de arquivo.
    - [ ] Em `src/phases/phase02_treatment/phase02_orchestrator.py`:
        - [ ] Modificar a lógica para que os relatórios (`treatment_report.json`, `treatment_report.html`) e os arquivos tratados (`*_treated.csv`) sejam salvos dentro de `[data_project_path]/fad-metadados/`.
        - [ ] O diretório `fad-metadados` deve ser criado automaticamente se não existir.
        - [ ] Simplificar a lógica de descoberta de arquivos para excluir o diretório `fad-metadados`.
    - [ ] Validar que, após a execução das fases 1 e 2, a pasta `fad-metadados` é criada corretamente dentro do projeto de dados (ex: `data/beneficios-qualireg/fad-metadados/`).
    - [ ] Validar que todos os artefatos gerados estão localizados exclusivamente dentro da pasta `fad-metadados`.
    - [ ] Confirmar que os pipelines rodam sem erros de `ParserError` ou loops de processamento, provando que a nova lógica de exclusão é eficaz.

*   **ID:** T009
    **Título:** Melhorar Relatório da Fase 1 com Saída HTML
    **Descrição:** O relatório de descoberta da Fase 1 atualmente é gerado apenas em JSON. Para facilitar a análise humana, é necessário adicionar uma opção de saída em formato HTML, similar à funcionalidade planejada para a Fase 2.
    **Critérios de Aceitação:**
    - [ ] Criar um novo módulo `src/phases/phase01_discovery/core/reporting.py` para a lógica de renderização de relatórios.
    - [ ] Implementar uma função `generate_html_report(report_data, output_path)` no novo módulo que converte a estrutura de dados do relatório de descoberta em um arquivo HTML bem formatado.
    - [ ] Modificar `src/phases/phase01_discovery/phase01_orchestrator.py` para adicionar o argumento `--report-output {json,html}`, com `json` como padrão.
    - [ ] No final do orquestrador da Fase 1, com base no argumento, gerar ou `discovery_report.json` (comportamento atual) ou `discovery_report.html` usando a nova função.
    - [ ] Garantir que a Fase 1 ignore arquivos `*_report.html` ao buscar arquivos para análise.
    - [ ] Adicionar testes unitários para a função `generate_html_report` para validar a correta geração do HTML.

## Em Andamento

## Concluído

*   **ID:** T008
    **Título:** Implementar Relatório Detalhado para a Fase 2
    **Descrição:** Criar um relatório abrangente para a fase de tratamento que detalhe todas as operações executadas. O formato do relatório deve ser configurável (JSON ou HTML), e a fase deve ser atualizada para ignorar seus próprios arquivos de relatório em execuções subsequentes.
    **Critérios de Aceitação:**
    - [x] Criar um novo módulo, por exemplo, `src/phases/phase02_treatment/core/reporting.py`, para encapsular a lógica de geração de relatórios.
    - [x] A estrutura de dados do relatório deve capturar: um resumo geral (total de arquivos processados, sucessos, falhas), e um log por arquivo detalhando as ações (valores extraídos, correções aplicadas, transformações) e quaisquer erros encontrados.
    - [x] Implementar uma função no novo módulo para renderizar os dados do relatório como um arquivo JSON.
    - [x] Implementar uma função para renderizar os dados do relatório como um arquivo HTML de fácil leitura.
    - [x] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py` para adicionar um novo argumento de linha de comando: `--report-output {json,html}`. O valor padrão deve ser `json`.
    - [x] O orquestrador deve agregar os dados ao longo do processo e, no final, chamar o módulo de relatório para gerar `treatment_report.json` ou `treatment_report.html` no diretório de saída.
    - [x] Ajustar a lógica de descoberta de arquivos na Fase 2 para ignorar explicitamente os padrões `*_report.json` e `*_report.html`.
    - [x] Adicionar testes unitários para o novo módulo de relatórios para validar a geração de JSON e HTML.

*   **ID:** T007
    **Título:** Corrigir Leitura de Arquivos XLSX na Fase 2
    **Descrição:** O `XlsxConnector` está retornando um dicionário de DataFrames (um por planilha) em vez de um único DataFrame, causando um `AttributeError` no pipeline da Fase 2. É necessário ajustar o conector para ler apenas a primeira planilha por padrão.
    **Critérios de Aceitação:**
    - [x] Modificar o método `read` em `src/connectors/xlsx_connector.py`.
    - [x] Garantir que, se nenhum `sheet_name` for especificado, o conector leia a *primeira* planilha do arquivo Excel (índice 0) por padrão.
    - [x] O método `read` deve sempre retornar um objeto `pd.DataFrame`, e não um dicionário.
    - [x] Validar que a Fase 2 (`python src/run.py -d data/beneficios-qualireg -p treatment`) executa sem erros para arquivos `.xlsx`.

*   **ID:** T003
    **Título:** Implementar Testes para Componentes Principais
    **Descrição:** Criar testes unitários para os módulos centrais do projeto, garantindo a robustez das funcionalidades de base.
    **Critérios de Aceção:**
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