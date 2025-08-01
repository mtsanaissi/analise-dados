# Tarefas do Projeto

## Backlog

*   **ID:** T028
    **Título:** Corrigir Lógica de Exclusão de Diretórios na Busca de Arquivos
    **Descrição:** A função `find_files` foi criada para ignorar diretórios padrão como `fad-metadados`, `fad-config` e `fad-bkp*`, mas os scripts orquestradores estão sobrescrevendo essa lista padrão ao passar seus próprios diretórios de exclusão (como o diretório de backup da execução atual). Isso faz com que as pastas `fad-bkp*` de execuções anteriores sejam processadas incorretamente. A lógica precisa ser ajustada para adicionar exclusões em vez de sobrescrevê-las.
    **Critérios de Aceitação:**
    - [ ] A função `find_files` em `src/utils.py` deve ser modificada para sempre usar sua lista de exclusão padrão (`fad-metadados`, `fad-config`, `fad-bkp*`) e adicionar a ela quaisquer diretórios extras passados através do argumento `exclude_dirs`.
    - [ ] Todas as chamadas para `find_files` nos arquivos orquestradores (ex: `phase01_orchestrator.py`, `phase02_orchestrator.py`) devem ser revisadas e, se necessário, ajustadas para garantir que não sobrescrevam mais a lista padrão.
    - [ ] **Testes:** Um teste de integração deve ser criado ou atualizado para validar este cenário. O teste deve:
        1. Criar uma estrutura de diretórios que inclua uma pasta de backup de uma execução anterior (ex: `fad-bkp-treatment-123`).
        2. Executar uma fase (como a Fase 2) que também cria seu próprio diretório de backup.
        3. Verificar se a função `find_files` ignora corretamente AMBOS os diretórios de backup (o antigo e o novo).

## Em Andamento

## Concluído

*   **ID:** T027
    **Título:** Criar Funcionalidade para Remover Espaços em Branco (Whitespace)
    **Descrição:** Implementar uma nova operação na Fase 2, ativada pela flag `--strip-whitespace`, que remove espaços em branco do início e do fim de todos os valores em todas as colunas.

*   **ID:** T026
    **Título:** Corrigir e Aprimorar Verificação de Consistência de Tipos
    **Descrição:** Corrigir um bug no orquestrador da Fase 1 onde a verificação de tipos para arquivos Excel só é executada se existirem arquivos CSV. Além disso, aprimorar os testes da funcionalidade para cobrir mais cenários e tipos de arquivo.

*   **ID:** T024
    **Título:** Implementar Verificação de Consistência de Tipos de Dados
    **Descrição:** Adicionar uma nova funcionalidade na Fase 1 para comparar os tipos de dados (dtypes) de colunas com o mesmo nome entre diferentes arquivos do mesmo tipo (ex: CSVs).

*   **ID:** T025
    **Título:** Adicionar `case_sensitive` ao `find-and-replace-text` e Atualizar Documentação
    **Descrição:** Padronizar as funcionalidades de substituição, adicionando a opção `case_sensitive` à operação `--find-and-replace-text` e atualizando a documentação para ambas as operações.

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