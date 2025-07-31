# Tarefas do Projeto

# Tarefas do Projeto

## Backlog

*   **ID:** T019
    **Título:** Aumentar Robustez da Geração de Configuração de Limpeza de Caracteres
    **Descrição:** A funcionalidade `--generate-char-cleanup-config` pode gerar resultados enganosos se a detecção de encoding do arquivo falhar ou tiver baixa confiança, pois isso pode levar à identificação incorreta de caracteres de substituição (U+FFFD) em vez do problema real. Esta tarefa visa adicionar uma camada de verificação para prevenir esse comportamento.
    **Critérios de Aceitação:**
    - [ ] Modificar a lógica do argumento `--generate-char-cleanup-config` em `src/phases/phase01_discovery/phase01_orchestrator.py`.
    - [ ] Antes de chamar `detect_problematic_chars` para um arquivo, a confiança da detecção de encoding (disponível em `results["encoding_analysis"]`) deve ser verificada.
    - [ ] Se a confiança for inferior a 0.9 (90%), a verificação de caracteres para esse arquivo específico deve ser pulada.
    - [ ] Ao pular um arquivo, uma mensagem de aviso (`logging.warning`) deve ser exibida, informando ao usuário qual arquivo foi pulado e por que (baixa confiança no encoding), sugerindo uma validação manual.
    - [ ] Modificar a função `detect_problematic_chars` em `data_integrity_checker.py` para que o bloco `except Exception` capture e logue o erro (`logging.error`) em vez de usar `pass` silenciosamente.

## Em Andamento

## Concluído

*   **ID:** T018
    **Título:** Padronizar Localização de Arquivos de Configuração
    **Descrição:** Atualmente, os comandos que dependem de configuração exigem o caminho completo para o arquivo. Esta tarefa visa padronizar a localização desses arquivos em um diretório `fad-config` dentro do projeto de dados, simplificando os comandos e tornando a estrutura do projeto mais previsível.
    **Critérios de Aceitação:**
    - [x] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py`.
    - [x] Para os argumentos que aceitam um caminho de configuração (`--replace-values`, `--enrich-data`, `--concatenate-data`), a lógica de resolução de caminho deve ser atualizada.
    - [x] Se o caminho fornecido for absoluto, ele deve ser usado diretamente.
    - [x] Se o caminho fornecido for relativo (apenas um nome de arquivo), ele deve ser resolvido para `data/[projeto-dados]/fad-config/[nome_do_arquivo]`.
    - [x] O arquivo `COMO_USAR.md` deve ser atualizado para refletir a nova maneira simplificada de chamar os comandos, assumindo que os arquivos de configuração estão no diretório `fad-config`.

*   **ID:** T017
    **Título:** Padronizar Formato de Arquivos de Configuração para YAML
    **Descrição:** Algumas operações ainda dependem de arquivos de configuração JSON, enquanto as mais novas usam YAML. Esta tarefa visa padronizar todos os arquivos de configuração para o formato YAML, que é mais legível para o usuário.
    **Critérios de Aceitação:**
    - [x] Modificar `src/phases/phase02_treatment/phase02_orchestrator.py`.
    - [x] As operações `--enrich-data` e `--concatenate-data` devem ser refatoradas para ler arquivos de configuração `.yaml` em vez de `.json`.
    - [x] A lógica de carregamento deve usar `yaml.safe_load()` e incluir tratamento de erro para `yaml.YAMLError`.
    - [x] Os textos de ajuda (`help=...`) para esses argumentos devem ser atualizados para indicar que esperam um arquivo YAML.
    - [x] O arquivo `COMO_USAR.md` deve ser atualizado, substituindo os exemplos de configuração JSON por seus equivalentes em YAML para as operações de concatenação e enriquecimento.

*   **ID:** T016
    **Título:** Aprimorar Fase 1 para Gerar Configuração de Limpeza de Caracteres
    **Descrição:** A detecção de caracteres problemáticos na Fase 1 é apenas informativa. Esta tarefa visa transformar essa detecção em uma ferramenta acionável, refatorando a funcionalidade para que ela gere, sob demanda, um arquivo de configuração YAML pronto para ser usado pela Fase 2 e limpando o fluxo de execução padrão.
    **Critérios de Aceitação:**
    - [x] **Refatorar `detect_problematic_chars`**
    - [x] **Desacoplar do Fluxo Padrão**
    - [x] **Novo Argumento na Fase 1**
    - [x] **Geração do YAML**
    - [x] **Atualização da Documentação e Ajuda**

*   **ID:** T015
    **Título:** Refatorar Tratamento Padrão para Substituição de Valores Baseada em Configuração
    **Descrição:** A operação `--apply-standard-treatment` é vaga e mistura responsabilidades. Esta tarefa visa refatorá-la para uma operação focada e configurável de substituição de valores, melhorando a clareza e o controle do usuário.
    **Critérios de Aceitação:**
    - [x] Em `src/phases/phase02_treatment/phase02_orchestrator.py`, renomear o argumento `--apply-standard-treatment` para `--replace-values`.
    - [x] O novo argumento `--replace-values` deve aceitar um caminho para um arquivo de configuração YAML como seu valor.
    - [x] A funcionalidade de `transform_columns` deve ser removida desta operação.
    - [x] A lógica de substituição deve ser guiada por um arquivo de configuração YAML.
    - [x] A lógica deve ser capaz de interpretar um valor `null` no YAML como `None` no pandas.
    - [x] A funcionalidade de backup dos arquivos originais deve ser mantida.
    - [x] A geração de um relatório (`json` ou `html`) deve ser mantida e adaptada.
    - [x] Se o arquivo de configuração YAML não for encontrado ou for inválido, o script deve falhar com uma mensagem de erro clara.

*   **ID:** T014
    **Título:** Delegar Comando de Ajuda para Parsers Específicos da Fase
    **Descrição:** Ao executar o script com a flag de ajuda (`-h` ou `--help`) junto com uma fase específica, a mensagem de ajuda principal é exibida em vez da ajuda para a fase especificada.
    **Critérios de Aceitação:**
    - [x] Modificar `src/run.py`.
    - [x] Quando `python src/run.py -p <phase_name> -h` for executado, a mensagem de ajuda para `<phase_name>` deve ser exibida.
    - [x] A mensagem de ajuda principal ainda deve ser exibida quando `python src/run.py -h` for executado sem especificar uma fase.
    - [x] O comportamento deve funcionar para todas as fases que possuem argumentos específicos.