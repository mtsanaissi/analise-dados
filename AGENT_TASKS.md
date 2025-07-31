# Tarefas do Projeto

## Backlog

*   **ID:** T021
    **Título:** Criar Operação de Substituição de Texto e Padrões (Regex)
    **Descrição:** Adicionar uma nova operação na Fase 2, focada em substituição de substrings e padrões (regex) dentro do conteúdo das células, para lidar com casos de limpeza mais complexos que a substituição de valores inteiros não cobre.
    **Critérios de Aceitação:**
    - [ ] Em `src/phases/phase02_treatment/phase02_orchestrator.py`, adicionar um novo argumento ao grupo de operações: `--find-and-replace-text`, que aceita um caminho para um arquivo de configuração YAML.
    - [ ] A configuração YAML deve conter uma lista de regras na chave `text_replacements`. Cada regra deve ter `column`, `pattern` (o texto ou regex a ser encontrado) e `replacement` (o texto de substituição).
    - [ ] Cada regra deve ter um campo opcional `is_regex` (booleano, padrão `false`) para indicar se o `pattern` deve ser tratado como uma expressão regular.
    - [ ] A implementação deve usar `df[column].str.replace(pattern, replacement, regex=is_regex)`.
    - [ ] A funcionalidade de backup e de geração de relatório (detalhando as regras aplicadas e a contagem de substituições) deve ser implementada, de forma similar à operação `--replace-values`.
    - [ ] Criar um novo arquivo de teste em `tests/phases/phase02_treatment/` para validar a funcionalidade de substituição de texto e regex, cobrindo casos de sucesso e de erro.
    - [ ] Atualizar o arquivo `COMO_USAR.md` com a nova seção "Operação 4: Encontrar e Substituir Texto", explicando seu propósito, a diferença para `--replace-values`, e fornecendo exemplos de configuração e uso.

*   **ID:** T020
    **Título:** Aprimorar Operação de Substituição de Valores com Múltiplos Valores
    **Descrição:** Evoluir a operação `--replace-values` para permitir que uma lista de múltiplos valores existentes (`existing_value`) seja mapeada para um único `new_value`, tornando as regras de padronização mais concisas e eficientes.
    **Critérios de Aceitação:**
    - [ ] Modificar a lógica da operação `--replace-values` em `src/phases/phase02_treatment/phase02_orchestrator.py`.
    - [ ] A chave `existing_value` no arquivo de configuração YAML deve agora aceitar tanto um valor único quanto uma lista de valores.
    - [ ] A implementação deve usar `df.replace()` ou `df[column].replace()` de forma que, se `existing_value` for uma lista, todos os seus itens sejam substituídos por `new_value`.
    - [ ] A contagem de substituições no relatório deve somar todas as ocorrências de todos os itens da lista `existing_value`.
    - [ ] Criar um novo arquivo de teste ou modificar um existente em `tests/phases/phase02_treatment/` para validar a funcionalidade com múltiplos valores, cobrindo casos de sucesso e de erro.
    - [ ] Atualizar a documentação da operação `--replace-values` no arquivo `COMO_USAR.md`, mostrando um exemplo de regra com múltiplos `existing_value`.

## Em Andamento

## Concluído
