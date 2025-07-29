# Tarefas do Projeto

## Backlog

*   **ID:** T012
    **Título:** Corrigir Geração de Relatório HTML para Dicionários Planos
    **Descrição:** A função `generate_html_report` na Fase 1 falha com um `ValueError` do pandas ao tentar renderizar seções do relatório que são dicionários "planos" (não aninhados), como `data_volume_analysis`. A lógica atual tenta forçar esses dados em uma única coluna, causando uma incompatibilidade de dimensões.
    **Critérios de Aceitação:**
    - [ ] Modificar `src/phases/phase01_discovery/core/reporting.py`.
    - [ ] A função `generate_html_report` deve ser capaz de diferenciar entre:
        - **Dicionários de Registro Único:** Dicionários "planos" cujos valores são tipos primitivos (strings, números, etc.). Estes devem ser convertidos em um DataFrame de duas colunas (ex: "Métrica", "Valor").
        - **Dicionários de Coleção:** Dicionários aninhados onde os valores são outros dicionários. Estes devem ser convertidos em um DataFrame onde as chaves de primeiro nível são o índice e as chaves de segundo nível são as colunas.
    - [ ] A execução de `python src/run.py -d data/beneficios-qualireg -p discovery --report-output html` deve ser concluída sem erros.
    - [ ] O arquivo `discovery_report.html` gerado deve conter todas as seções do relatório, formatadas corretamente em tabelas HTML.

## Em Andamento

## Concluído

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
