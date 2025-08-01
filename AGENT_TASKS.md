# Tarefas do Projeto

## Backlog

*   **ID:** T024
    **Título:** Implementar Verificação de Consistência de Tipos de Dados
    **Descrição:** Adicionar uma nova funcionalidade na Fase 1 para comparar os tipos de dados (dtypes) de colunas com o mesmo nome entre diferentes arquivos do mesmo tipo (ex: CSVs). O objetivo é identificar inconsistências que possam causar problemas na concatenação ou análise, como uma coluna ser `int64` em um arquivo e `object` em outro.
    **Critérios de Aceitação:**
    - [ ] A funcionalidade deve ser acionada por um novo argumento no orquestrador da Fase 1: `--compare-types`.
    - [ ] A verificação deve agrupar arquivos por tipo e comparar os tipos de dados das colunas correspondentes.
    - [ ] O `data_profiler.py` deve ser usado ou estendido para inferir os tipos de dados de cada coluna.
    - [ ] O relatório final da Fase 1 (JSON e HTML) deve conter uma nova seção, `type_consistency_analysis`, que lista as inconsistências encontradas.
    - [ ] A implementação deve lidar de forma graciosa com arquivos que não possuem colunas em comum com a referência.
    - [ ] **Testes:** Um novo teste deve ser criado em `tests/phases/phase01_discovery/` para validar a lógica de comparação de tipos. O teste deve usar arquivos de exemplo com tipos consistentes e inconsistentes e verificar se o relatório gerado está correto.
    - [ ] **Documentação:** O arquivo `COMO_USAR.md` deve ser atualizado para incluir a descrição e o exemplo de uso do novo argumento `--compare-types` na seção da Fase 1.

## Em Andamento

## Concluído

*   **ID:** T023
    **Título:** Ignorar Pastas Específicas na Busca de Arquivos
    **Descrição:** Aperfeiçoar o mecanismo de busca de arquivos de dados para que ignore explicitamente os diretórios `fad-metadados`, `fad-config` e `fad-bkp*`.

*   **ID:** T022
    **Título:** Configurar Sensibilidade de Caso na Substituição de Valores
    **Descrição:** Permitir que a operação `--replace-values` da Fase 2 ignore diferenças de maiúsculas e minúsculas (case-insensitive) durante a busca por valores a serem substituídos.

*   **ID:** T021
    **Título:** Criar Operação de Substituição de Texto e Padrões (Regex)
    **Descrição:** Adicionar uma nova operação na Fase 2, focada em substituição de substrings e padrões (regex) dentro do conteúdo das células, para lidar com casos de limpeza mais complexos que a substituição de valores inteiros não cobre.

*   **ID:** T020
    **Título:** Aprimorar Operação de Substituição de Valores com Múltiplos Valores
    **Descrição:** Evoluir a operação `--replace-values` para permitir que uma lista de múltiplos valores existentes (`existing_value`) seja mapeada para um único `new_value`, tornando as regras de padronização mais concisas e eficientes.
