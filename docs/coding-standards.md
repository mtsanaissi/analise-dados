# Padrões de Código do Toolkit

Este projeto não é um pacote Python genérico. O código existe para apoiar ingestão, diagnóstico, tratamento, análise exploratória e visualização de dados em workflows reais.

## Convenções obrigatórias

- Use identificadores em inglês.
- Escreva docstrings, comentários e textos literais voltados ao usuário em português do Brasil.
- Adicione type hints em todas as assinaturas novas ou alteradas.
- Prefira funções pequenas e reutilizáveis. Se a lógica puder ser compartilhada entre scripts ou fases, mova para `src/utils.py` ou para um módulo reutilizável da fase.
- Use comentários inline apenas quando for necessário explicar o motivo de uma decisão menos óbvia.

## Organização do código

- `src/run.py` é o ponto de entrada da CLI e concentra a configuração básica de logging.
- `src/app_main_interface.py` é a interface Streamlit.
- `src/phases/` contém a lógica por fase do pipeline.
- `src/connectors/` contém leitores e conectores por tipo de arquivo.
- `src/utils.py` concentra utilidades transversais.

## Limites de responsabilidade

- Isole operações de IO, leitura de ambiente, parsing de arquivos e chamadas a serviços externos em funções ou módulos claros.
- Não espalhe regras de parsing, seleção de separador, encoding ou paths por múltiplos arquivos quando elas puderem ser centralizadas.
- Evite acoplamento entre a lógica de domínio e detalhes de interface. A GUI e a CLI devem chamar funções de lógica, não duplicá-las.

## Robustez e dados

- Trate explicitamente exceções esperadas de IO e parsing, como `FileNotFoundError`, `PermissionError`, `json.JSONDecodeError`, erros de parser do pandas e falhas de leitura de YAML.
- Uma falha em um único arquivo não deve derrubar o processamento inteiro quando houver como continuar com os demais itens.
- Não use `print()` para status ou erro em código novo voltado ao fluxo principal. Prefira `logging`.
- Cuidado com logs que possam expor caminhos sensíveis, dados pessoais ou conteúdo de arquivos reais do usuário.

## Configuração

- Evite parâmetros hardcoded. Exponha configurações por `argparse`, arquivos YAML ou argumentos de função.
- Se uma nova dependência for realmente necessária, ela deve ser justificada e aprovada antes de ser adicionada ao projeto.

## Scripts e documentação

- Novos scripts Python devem seguir o cabeçalho padrão definido em `AGENTS.md`.
- Ao alterar comportamento observável, revise a documentação correspondente em `LEIAME.md`, `COMO_USAR.md` e `docs/`.
