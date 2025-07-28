# Tarefas do Projeto

## Backlog

*   **ID:** T001
    **Título:** Revisar e Implementar Testes para a Fase 1
    **Descrição:** Revisar os módulos existentes em `src/phases/phase01_discovery/` e seus subdiretórios. Implementar testes unitários e de integração para garantir a robustez e a correção das funcionalidades de descoberta de dados.
    **Critérios de Aceitação:**
    - [ ] Cobertura de testes para os módulos em `src/phases/phase01_discovery/core/`.
    - [ ] Cobertura de testes para os módulos em `src/phases/phase01_discovery/file_type_specific/`.
    - [ ] Testes para o orquestrador `src/phases/phase01_discovery/phase01_orchestrator.py`.

## Em Andamento

*   **ID:** T002
    **Título:** Implementar Funcionalidade de Concatenação de Arquivos
    **Descrição:** Criar uma nova ferramenta para consolidar dados de múltiplos arquivos (CSV e XLSX) de uma pasta de entrada em um único arquivo de saída, mantendo o formato original e unindo todas as colunas.
    **Critérios de Aceitação:**
    - [ ] Criar o arquivo `src/phases/phase02_treatment/core/data_concatenator.py`.
    - [ ] Implementar a classe `DataConcatenator` (ou função `concatenate_files`) que recebe um dicionário de configuração.
    - [ ] A configuração deve incluir `input_folder`, `output_file` e `file_type`.
    - [ ] A ferramenta deve validar a configuração e listar os arquivos do tipo especificado.
    - [ ] Ler arquivos CSV usando `CsvConnector` e arquivos XLSX usando `pd.read_excel`.
    - [ ] Concatenar os DataFrames lidos em um único DataFrame mestre.
    - [ ] Escrever o DataFrame mestre no arquivo de saída, mantendo o formato original.
    - [ ] Adicionar logs informativos sobre o progresso da concatenação.
    - [ ] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py` para aceitar um novo argumento `--concatenate-data` que aponta para um arquivo de configuração JSON.
    - [ ] Implementar tratamento de erros para `FileNotFoundError`, `json.JSONDecodeError`, etc.
    - [ ] Adicionar docstrings completas e comentários conforme as convenções do projeto.