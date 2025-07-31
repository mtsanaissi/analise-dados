# Tarefas do Projeto

## Backlog

*   **ID:** T014
    **Título:** Delegar Comando de Ajuda para Parsers Específicos da Fase
    **Descrição:** Ao executar o script com a flag de ajuda (`-h` ou `--help`) junto com uma fase específica (ex: `python src/run.py -p treatment -h`), a mensagem de ajuda principal é exibida em vez da ajuda para a fase especificada. O script deve ser modificado para detectar essa situação e exibir a mensagem de ajuda do sub-parser da fase selecionada.
    **Critérios de Aceitação:**
    - [ ] Modificar `src/run.py`.
    - [ ] Quando `python src/run.py -p <phase_name> -h` for executado, a mensagem de ajuda para `<phase_name>` deve ser exibida.
    - [ ] A mensagem de ajuda principal ainda deve ser exibida quando `python src/run.py -h` for executado sem especificar uma fase.
    - [ ] O comportamento deve funcionar para todas as fases que possuem argumentos específicos (ex: `discovery`, `treatment`).

## Em Andamento

## Concluído

*   **ID:** T013
    **Título:** Melhorar Usabilidade e Interatividade da Fase 2 (Tratamento)
    **Descrição:** Atualmente, a execução da Fase 2 (`... -p treatment`) realiza um tratamento padrão de forma silenciosa, o que é confuso para o usuário. A tarefa visa reestruturar a fase para que o usuário precise especificar explicitamente qual operação de tratamento deseja executar, melhorando a clareza e a orientação.
    **Critérios de Aceitação:**
    - [x] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py`.
    - [x] As operações (`--concatenate-data`, `--enrich-data`, e o tratamento padrão) devem ser mutuamente exclusivas. O usuário deve ser obrigado a escolher apenas uma.
    - [x] Se o comando `... -p treatment` for executado sem especificar uma operação, o script deve exibir uma mensagem de ajuda clara listando as operações disponíveis (`concatenate`, `enrich`, `apply-standard-treatment`) e sair sem executar nada.
    - [x] O tratamento padrão (correção de valores e transformação de colunas) deve ser movido para um novo argumento, como `--apply-standard-treatment`, que não requer um valor (`action='store_true'`).
    - [x] Se `--concatenate-data` ou `--enrich-data` forem usados sem o caminho para o arquivo de configuração, o script deve falhar com uma mensagem amigável, explicando como fornecer o arquivo e, se possível, um exemplo de uso.
    - [x] A descrição geral da ajuda do `argparse` para a Fase 2 deve ser atualizada para refletir a necessidade de escolher uma sub-operação.

*   **ID:** T012
    **Título:** Corrigir Geração de Relatório HTML para Dicionários Planos
    **Descrição:** A função `generate_html_report` na Fase 1 falha com um `ValueError` do pandas ao tentar renderizar seções do relatório que são dicionários "planos" (não aninhados), como `data_volume_analysis`. A lógica atual tenta forçar esses dados em uma única coluna, causando uma incompatibilidade de dimensões.
    **Critérios de Aceitação:**
    - [x] Modificar `src/phases/phase01_discovery/core/reporting.py`.
    - [x] A função `generate_html_report` deve ser capaz de diferenciar entre:
        - **Dicionários de Registro Único:** Dicionários "planos" cujos valores são tipos primitivos (strings, números, etc.). Estes devem ser convertidos em um DataFrame de duas colunas (ex: "Métrica", "Valor").
        - **Dicionários de Coleção:** Dicionários aninhados onde os valores são outros dicionários. Estes devem ser convertidos em um DataFrame onde as chaves de primeiro nível são o índice e as chaves de segundo nível são as colunas.
    - [x] A execução de `python src/run.py -d data/beneficios-qualireg -p discovery --report-output html` deve ser concluída sem erros.
    - [x] O arquivo `discovery_report.html` gerado deve conter todas as seções do relatório, formatadas corretamente em tabelas HTML.

*   **ID:** T011
    **Título:** Refatorar Fase 2 para Backup de Originais e Substituição In-Place
    **Descrição:** O processo atual da Fase 2 cria novos arquivos tratados (`*_treated.csv`) em um subdiretório, o que pode poluir o projeto de dados. Esta tarefa visa refatorar o processo para que os arquivos originais sejam movidos para um diretório de backup com timestamp, e os arquivos tratados os substituam, mantendo o nome e o caminho originais.
    **Critérios de Aceitação:**
    - [x] No início de `src/phases/phase02_treatment/phase02_orchestrator.py`, gerar um timestamp no formato `YYYYMMDDHHMMSS`.
    - [x] Criar um diretório de backup na raiz do projeto de dados com o nome `fad-bkp-treatment-[timestamp]`.
    - [x] Dentro do loop de processamento de arquivos no orquestrador:
        - [x] Para cada arquivo original, construir um caminho de destino dentro da pasta de backup que preserve sua estrutura de subdiretórios (ex: `original/sub/file.xlsx` -> `backup/sub/file.xlsx`).
        - [x] Mover o arquivo original para o seu novo local no diretório de backup.
        - [x] Após o tratamento do DataFrame, o arquivo resultante deve ser salvo no caminho *exato* do arquivo original (ex: `data/projeto/arquivo.xlsx`).
        - [x] A lógica de salvamento deve ser capaz de lidar com os diferentes formatos de arquivo de origem (no mínimo `.csv` e `.xlsx`), salvando o DataFrame tratado no mesmo formato do arquivo original. Considere criar uma função utilitária para isso.
    - [x] Remover a lógica antiga que salvava arquivos em um diretório `treated` e adicionava o sufixo `_treated.csv`.
    - [x] Validar que, após a execução da Fase 2, a pasta de backup é criada corretamente e contém os arquivos originais, e que os arquivos nos locais originais foram substituídos por suas versões tratadas.
