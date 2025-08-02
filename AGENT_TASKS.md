# Tarefas do Projeto

## Backlog

*   **ID:** T033
    **Título:** Adicionar Teste para a Função `build_command` da UI
    **Descrição:** Criar um teste de unidade simples para a função `build_command` em `src/app_main_interface.py` para garantir que ela constrói corretamente a lista de argumentos para o subprocesso.
    **Critérios de Aceitação:**
    - [ ] Um novo arquivo de teste, `tests/test_app_main_interface.py` (ou similar), deve ser criado.
    - [ ] O teste deve importar a função `build_command`.
    - [ ] O teste deve verificar se, para diferentes combinações de `project_path` e `phase`, a função `build_command` retorna a lista de argumentos esperada (incluindo o executável Python e o caminho do `run.py`).

*   **ID:** T032
    **Título:** Corrigir Lógica de Exclusão de Diretórios em `find_files` e Adicionar Teste de Integração
    **Descrição:** A função `find_files` em `src/utils.py` não está adicionando corretamente os diretórios de exclusão passados como argumento à sua lista padrão, resultando na não exclusão de pastas de backup antigas. Além disso, falta um teste de integração robusto para validar este comportamento.
    **Critérios de Aceitação:**
    - [ ] A função `find_files` em `src/utils.py` deve ser modificada para que, se o argumento `exclude_dirs` for fornecido, seus valores sejam *adicionados* à lista de exclusão padrão (`fad-metadados`, `fad-config`, `fad-bkp*`), e não a sobrescrevam.
    - [ ] Todas as chamadas para `find_files` nos arquivos orquestradores (ex: `phase01_orchestrator.py`, `phase02_orchestrator.py`) devem ser revisadas e, se necessário, ajustadas para garantir que funcionem corretamente com a nova lógica.
    - [ ] **Testes:** Um novo teste de integração deve ser criado em `tests/utils/test_file_discovery.py` (ou um nome similar, garantindo um caminho válido no Windows, sem pontos e vírgulas) para validar a correção. O teste deve:
        1. Criar um diretório de teste com arquivos de dados e subdiretórios, incluindo:
            - Uma pasta `fad-metadados`.
            - Uma pasta `fad-config`.
            - Uma pasta de backup antiga (ex: `fad-bkp-old-123`).
            - Uma pasta de backup da execução atual (ex: `fad-bkp-current-456`).
            - Pastas de dados válidas.
        2. Chamar `find_files` passando apenas o diretório de backup da execução atual via `exclude_dirs`.
        3. Assertar que a lista de arquivos retornada por `find_files` **não contém** arquivos de *nenhuma* das pastas excluídas (padrão e as passadas como argumento).

*   **ID:** T031
    **Título:** [UI - Parte 3] Implementar UI para Visualização e Refinamentos Finais
    **Descrição:** Finalizar a implementação da interface gráfica, adicionando a funcionalidade para a fase de Visualização e incorporando refinamentos de UX, como a exibição de relatórios e tratamento de erros.
    **Critérios de Aceitação:**
    - [ ] **Fase Visualization:**
        - [ ] A UI deve exibir um botão para "Iniciar Aplicação de Visualização".
        - [ ] Clicar no botão deve executar o script `src/phases/phase04_visualization/app_explore_single_profile.py` em um subprocesso.
    - [ ] **Exibição de Relatórios:** Após uma execução bem-sucedida de qualquer fase que gere relatório (ex: Discovery, Treatment), a UI deve exibir um link para download direto do relatório HTML/JSON gerado.
    - [ ] **Tratamento de Erros:** Se a execução do subprocesso falhar, a UI deve exibir uma mensagem de erro clara e amigável para o usuário.
    - [ ] **Testes:** Criar testes para validar a construção de comandos para a fase de Visualização e para a exibição/download de relatórios.
    - [ ] **Documentação:** O `COMO_USAR.md` e o `LEIAME.md` devem ser atualizados para apresentar a nova interface gráfica como o método principal de uso interativo do kit de ferramentas.

*   **ID:** T030
    **Título:** [UI - Parte 2] Implementar UI para Fases Discovery e Treatment
    **Descrição:** Expandir a interface gráfica principal para que, ao selecionar as fases `Discovery` ou `Treatment`, a área principal exiba dinamicamente os widgets correspondentes a cada argumento da linha de comando, permitindo a configuração visual das operações.
    **Critérios de Aceitação:**
    - [ ] **Fase Discovery:**
        - [ ] A UI deve exibir checkboxes para `--compare-fields` e `--compare-types`.
        - [ ] A UI deve exibir um seletor para `--report-output` (json/html).
        - [ ] A UI deve exibir um campo de texto para o caminho do arquivo de configuração de limpeza de caracteres (`--generate-char-cleanup-config`).
    - [ ] **Fase Treatment:**
        - [ ] A UI deve exibir um menu suspenso para selecionar a operação (ex: `Remover Espaços`, `Substituir Valores`, `Encontrar e Substituir Texto`, `Concatenar Dados`, `Enriquecer Dados`).
        - [ ] Se a operação selecionada exigir um arquivo de configuração YAML (ex: `--replace-values`, `--find-and-replace-text`, `--concatenate-data`, `--enrich-data`), um widget de upload de arquivo (`st.file_uploader`) deve aparecer para que o usuário possa carregar o arquivo.
        - [ ] A lógica deve ser capaz de salvar o arquivo YAML enviado em um local temporário e passar seu caminho para o comando de execução do subprocesso.
    - [ ] O comando final executado pelo subprocesso deve refletir corretamente todas as opções selecionadas pelo usuário na UI para as fases Discovery e Treatment.
    - [ ] **Testes:** Criar testes para validar a construção de comandos para as diferentes operações e argumentos das fases Discovery e Treatment, garantindo que a UI gere os comandos CLI corretos.
    - [ ] **Documentação:** Nenhuma atualização no `COMO_USAR.md` ou `LEIAME.md` é necessária nesta fase.

*   **ID:** T029
    **Título:** [UI - Parte 1] Criar o Esqueleto da Aplicação de Interface Gráfica
    **Descrição:** Criar a estrutura principal da aplicação Streamlit (`src/app_main_interface.py`) que servirá como um painel de controle para o kit de ferramentas. Esta primeira tarefa foca nos componentes globais e na lógica central de execução de comandos, sem a lógica específica de cada fase.
    **Critérios de Aceitação:**
    - [ ] Um novo arquivo `src/app_main_interface.py` deve ser criado.
    - [ ] A UI deve ter uma barra lateral com um campo de texto para o "Caminho do Projeto de Dados" e um menu suspenso para selecionar a "Fase" (`Discovery`, `Treatment`, etc.).
    - [ ] A área principal deve exibir um botão "Executar".
    - [ ] Ao clicar em "Executar", o script deve construir o comando básico (ex: `python src/run.py -d <caminho> -p <fase>`) e executá-lo em um subprocesso.
    - [ ] A saída do console (stdout/stderr) do subprocesso deve ser capturada e exibida em tempo real dentro de um `st.code()` ou `st.text_area` na UI.
    - [ ] A UI deve exibir uma mensagem de "Concluído" ou "Erro" ao final da execução.
    - [ ] **Testes:** Dada a natureza da UI, testes de unidade formais não são o foco principal. No entanto, a lógica de construção de comandos pode ser testada. Criar um teste simples em `tests/` que valide se a função que monta a lista de argumentos a partir de seleções da UI funciona como esperado.
    - [ ] **Documentação:** Nenhuma atualização no `COMO_USAR.md` é necessária nesta fase.

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