# Tarefas do Projeto

# Tarefas do Projeto

## Backlog

*   **ID:** T018
    **Título:** Padronizar Localização de Arquivos de Configuração
    **Descrição:** Atualmente, os comandos que dependem de configuração exigem o caminho completo para o arquivo. Esta tarefa visa padronizar a localização desses arquivos em um diretório `fad-config` dentro do projeto de dados, simplificando os comandos e tornando a estrutura do projeto mais previsível.
    **Critérios de Aceitação:**
    - [ ] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py`.
    - [ ] Para os argumentos que aceitam um caminho de configuração (`--replace-values`, `--enrich-data`, `--concatenate-data`), a lógica de resolução de caminho deve ser atualizada.
    - [ ] Se o caminho fornecido for absoluto, ele deve ser usado diretamente.
    - [ ] Se o caminho fornecido for relativo (apenas um nome de arquivo), ele deve ser resolvido para `data/[projeto-dados]/fad-config/[nome_do_arquivo]`.
    - [ ] O arquivo `COMO_USAR.md` deve ser atualizado para refletir a nova maneira simplificada de chamar os comandos, assumindo que os arquivos de configuração estão no diretório `fad-config`.

*   **ID:** T017
    **Título:** Padronizar Formato de Arquivos de Configuração para YAML
    **Descrição:** Algumas operações ainda dependem de arquivos de configuração JSON, enquanto as mais novas usam YAML. Esta tarefa visa padronizar todos os arquivos de configuração para o formato YAML, que é mais legível para o usuário.
    **Critérios de Aceitação:**
    - [ ] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py`.
    - [ ] As operações `--enrich-data` e `--concatenate-data` devem ser refatoradas para ler arquivos de configuração `.yaml` em vez de `.json`.
    - [ ] A lógica de carregamento deve usar `yaml.safe_load()` e incluir tratamento de erro para `yaml.YAMLError`.
    - [ ] Os textos de ajuda (`help=...`) para esses argumentos devem ser atualizados para indicar que esperam um arquivo YAML.
    - [ ] O arquivo `COMO_USAR.md` deve ser atualizado, substituindo os exemplos de configuração JSON por seus equivalentes em YAML para as operações de concatenação e enriquecimento.

## Concluído

*   **ID:** T016
    **Título:** Aprimorar Fase 1 para Gerar Configuração de Limpeza de Caracteres
    **Descrição:** A detecção de caracteres problemáticos na Fase 1 é apenas informativa. Esta tarefa visa transformar essa detecção em uma ferramenta acionável, refatorando a funcionalidade para que ela gere, sob demanda, um arquivo de configuração YAML pronto para ser usado pela Fase 2 e limpando o fluxo de execução padrão.
    **Critérios de Aceitação:**
    - [x] **Refatorar `detect_problematic_chars`:**
        - A função em `src/phases/phase01_discovery/core/data_integrity_checker.py` deve ser modificada para retornar um `set` de caracteres problemáticos únicos, em vez de uma lista de amostras.
    - [x] **Desacoplar do Fluxo Padrão:**
        - A chamada a `detect_problematic_chars` deve ser removida da execução normal da Fase 1 (da função `check_csv_file`, `check_json_file`, etc.).
        - A seção de caracteres problemáticos deve ser removida dos relatórios `json` e `html` padrão da Fase 1.
    - [x] **Novo Argumento na Fase 1:**
        - Adicionar um novo argumento ao `phase01_orchestrator.py`: `--generate-char-cleanup-config <caminho_do_arquivo.yaml>`.
        - A execução da detecção de caracteres e a geração do YAML só devem ocorrer quando este argumento for fornecido.
    - [x] **Geração do YAML:**
        - Ao usar a nova flag, o orquestrador deve consolidar os caracteres problemáticos de todos os arquivos em um conjunto único.
        - Um arquivo YAML deve ser gerado no caminho especificado.
        - No YAML, cada `existing_value` deve ser a representação textual segura do caractere (ex: `\'\uFFFD\'`, `\'\x07\'`), usando PyYAML para garantir a escrita correta como escape literal.
        - O `new_value` padrão deve ser uma string vazia (`\'\'`).
        - A regra não deve conter a chave `column`.
    - [x] **Atualização da Documentação e Ajuda:**
        - O texto de ajuda (`-h`) da Fase 1 deve ser atualizado para incluir o novo argumento.
        - O arquivo `COMO_USAR.md` deve ser atualizado para remover a menção da detecção de caracteres do fluxo padrão e adicionar uma nova seção explicando como usar `--generate-char-cleanup-config` para criar um arquivo de limpeza para a Fase 2.


*   **ID:** T015
    **Título:** Refatorar Tratamento Padrão para Substituição de Valores Baseada em Configuração
    **Descrição:** A operação `--apply-standard-treatment` é vaga e mistura responsabilidades. Esta tarefa visa refatorá-la para uma operação focada e configurável de substituição de valores, melhorando a clareza e o controle do usuário.
    **Critérios de Aceitação:**
    - [x] Em `src/phases/phase02_treatment/phase02_orchestrator.py`, renomear o argumento `--apply-standard-treatment` para `--replace-values`.
    - [x] O novo argumento `--replace-values` deve aceitar um caminho para um arquivo de configuração YAML como seu valor.
    - [x] A funcionalidade de `transform_columns` deve ser removida desta operação. O foco deve ser exclusivamente na substituição de valores.
    - [x] A lógica de substituição deve ser guiada por um arquivo de configuração YAML (ex: `replace_config.yaml`) que contém uma lista de regras na chave `replacements`.
    - [x] Cada regra na lista deve conter `existing_value` e `new_value`. A chave `column` será opcional.
        - Se `column` for especificada, a substituição ocorrerá apenas na coluna indicada.
        - Se `column` for omitida, a substituição será aplicada a todas as colunas do DataFrame.
    - [x] A lógica deve ser capaz de interpretar um valor `null` no YAML como `None` no pandas, permitindo a substituição para valores nulos.
    - [x] A funcionalidade de backup dos arquivos originais em um diretório `fad-bkp-treatment-[timestamp]` deve ser mantida.
    - [x] A geração de um relatório (`json` ou `html`) deve ser mantida e adaptada para detalhar, para cada arquivo, quais regras foram aplicadas e quantas substituições foram feitas por regra.
    - [x] Se o arquivo de configuração YAML não for encontrado ou for inválido, o script deve falhar com uma mensagem de erro clara.

*   **ID:** T014
    **Título:** Delegar Comando de Ajuda para Parsers Específicos da Fase
    **Descrição:** Ao executar o script com a flag de ajuda (`-h` ou `--help`) junto com uma fase específica (ex: `python src/run.py -p treatment -h`), a mensagem de ajuda principal é exibida em vez da ajuda para a fase especificada. O script deve ser modificado para detectar essa situação e exibir a mensagem de ajuda do sub-parser da fase selecionada.
    **Critérios de Aceitação:**
    - [x] Modificar `src/run.py`.
    - [x] Quando `python src/run.py -p <phase_name> -h` for executado, a mensagem de ajuda para `<phase_name>` deve ser exibida.
    - [x] A mensagem de ajuda principal ainda deve ser exibida quando `python src/run.py -h` for executado sem especificar uma fase.
    - [x] O comportamento deve funcionar para todas as fases que possuem argumentos específicos (ex: `discovery`, `treatment`).

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
