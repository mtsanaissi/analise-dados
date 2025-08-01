# Guia de Uso: Kit de Ferramentas de Análise de Dados

Este documento detalha como usar os comandos disponíveis neste projeto para executar as diferentes fases de análise de dados.

## Estrutura do Comando Principal

Todos os comandos são executados através do script `src/run.py`. A estrutura básica é a seguinte:

```bash
python src/run.py -d <caminho_para_dados> -p <fase> [argumentos_da_fase...]
```

### Argumentos Principais:

*   `-d, --data-project-path`: **(Obrigatório)** Caminho para a pasta do seu projeto de dados. É aqui que a ferramenta irá procurar arquivos para analisar e onde salvará os metadados e relatórios.
*   `-p, --phase`: **(Obrigatório)** A fase do processo de análise que você deseja executar. As opções são:
    *   `discovery`: Para entender a estrutura, qualidade e características dos dados.
    *   `treatment`: Para limpar, padronizar, enriquecer ou concatenar os dados.
    *   `exploratory`: (Em desenvolvimento) Para análises exploratórias.
    *   `visualization`: Para iniciar aplicações de visualização de dados.

---

## Fase 1: Descoberta (`discovery`)

Esta fase ajuda a diagnosticar seus dados brutos. Ela gera relatórios sobre o volume, integridade, codificação e estrutura dos arquivos, sem alterar os dados originais.

### Comando Básico

```bash
python src/run.py -d data/meu_projeto -p discovery
```

### Argumentos Específicos da Fase `discovery`

*   `--report-output <formato>`: Define o formato do arquivo de relatório.
    *   `json` (padrão): Gera um `discovery_report.json` na pasta `fad_metadata` do seu projeto de dados.
    *   `html`: Gera um `discovery_report.html` visualmente mais amigável.
    *   **Exemplo:**
        ```bash
        python src/run.py -d data/meu_projeto -p discovery --report-output html
        ```

*   `--compare-fields`: Compara as colunas (para CSV/Excel) ou chaves (para JSON) entre os arquivos do mesmo tipo. Isso é útil para verificar se múltiplos arquivos que deveriam ter a mesma estrutura realmente a têm.
    *   **Exemplo:**
        ```bash
        python src/run.py -d data/meu_projeto -p discovery --compare-fields
        ```

*   `--generate-char-cleanup-config <caminho_saida.yaml>`: Realiza uma verificação específica por caracteres problemáticos (como caracteres de controle invisíveis ou de substituição) em todos os arquivos. Se encontrados, gera um arquivo de configuração YAML no caminho especificado. Este arquivo pode ser usado pela Fase 2 para realizar a limpeza.
    *   **Exemplo:**
        ```bash
        python src/run.py -d data/meu_projeto -p discovery --generate-char-cleanup-config configs/limpeza_chars.yaml
        ```

---

## Fase 2: Tratamento (`treatment`)

Esta fase é usada para modificar os dados. **Você deve escolher apenas uma das operações abaixo por execução.**

**Nota sobre Arquivos de Configuração:** Por padrão, a ferramenta espera que os arquivos de configuração YAML para esta fase estejam localizados em um diretório chamado `fad-config` dentro da pasta do seu projeto de dados (`--data-project-path`). Se você fornecer apenas o nome do arquivo (ex: `correcoes.yaml`), ele será procurado nesse local. Caminhos absolutos para arquivos de configuração ainda são suportados.

### Operação 1: Substituir Valores (`--replace-values`)

Aplica um conjunto de substituições de valores em múltiplos arquivos, com base em um arquivo de configuração YAML. É ideal para corrigir erros de digitação, padronizar termos ou remover caracteres indesejados de forma controlada.

**Importante:** Esta operação **substitui** os arquivos originais. Um backup dos arquivos originais é criado automaticamente em uma pasta `fad-bkp-treatment-[timestamp]` dentro do seu projeto de dados.

#### Configuração

Requer um arquivo de configuração YAML (ex: `correcoes.yaml`) com uma lista de regras de substituição. Cada regra pode ser global ou específica para uma coluna.

```yaml
# Lista de regras de substituição a serem aplicadas.
replacements:
  # Regra 1: Substitui um valor específico na coluna "Status".
  - column: "Status"
    existing_value: "Inativo"
    new_value: "Desativado"

  # Regra 2: Usa uma lista para padronizar múltiplos valores para um valor nulo,
  # apenas na coluna "Status".
  - column: "Status"
    existing_value: ["N/D", "NA", "Sem Info", "?"]
    new_value: null

  # Regra 3: Substituição global (em todas as colunas).
  # Útil para remover caracteres problemáticos ou padronizar valores globalmente.
  - existing_value: '\uFFFD'
    new_value: ''
```

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --replace-values correcoes.yaml
```

### Operação 2: Concatenar Dados (`--concatenate-data`)

Junta múltiplos arquivos de um diretório em um único arquivo de saída.

#### Configuração

Esta operação requer um arquivo de configuração YAML. Crie um arquivo (ex: `config_concat.yaml`) com a seguinte estrutura:

```yaml
input_folder: "caminho/para/pasta/com/arquivos"
output_file: "caminho/para/arquivo_final.csv"
file_type: "csv"
```

*   `input_folder`: O diretório contendo os arquivos a serem concatenados.
*   `output_file`: O nome e caminho do arquivo de saída.
*   `file_type`: O formato dos arquivos de entrada (`csv`, `xlsx`, etc.).

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --concatenate-data config_concat.yaml
```

### Operação 3: Enriquecer Dados (`--enrich-data`)

Adiciona informações a um arquivo principal (main) com base em um arquivo de consulta (lookup), similar a um `JOIN` em bancos de dados.

#### Configuração

Requer um arquivo de configuração YAML (ex: `config_enrich.yaml`):

```yaml
main_file: "caminho/para/arquivo_principal.csv"
lookup_file: "caminho/para/arquivo_consulta.csv"
output_file: "caminho/para/arquivo_enriquecido.csv"
main_key: "coluna_chave_principal"
lookup_key: "coluna_chave_consulta"
columns_to_add:
  - "coluna1_da_consulta"
  - "coluna2_da_consulta"
```

*   `main_file`: O arquivo que receberá as novas informações.
*   `lookup_file`: O arquivo que contém as informações a serem adicionadas.
*   `output_file`: O nome e caminho do arquivo de saída.
*   `main_key` / `lookup_key`: As colunas usadas para combinar os dois arquivos.
*   `columns_to_add`: A lista de colunas do arquivo de consulta que serão adicionadas ao arquivo principal.

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --enrich-data config_enrich.yaml
```

---

### Operação 4: Encontrar e Substituir Texto (`--find-and-replace-text`)

Esta operação é ideal para fazer substituições parciais dentro de células de texto, como corrigir parte de uma palavra, remover ou alterar um padrão específico usando texto simples ou expressões regulares (regex).

**Diferença para `--replace-values`**:
*   `--replace-values`: Substitui o **valor inteiro** de uma célula. Ex: `Status: "Inativo"` se torna `Status: "Desativado"`.
*   `--find-and-replace-text`: Substitui uma **parte do texto** dentro de uma célula. Ex: `Descrição: "REF-123-PROD"` pode se tornar `Descrição: "ID-123-PROD"` ao substituir apenas "REF".

**Importante:** Esta operação também **substitui** os arquivos originais e cria um backup automático.

#### Configuração

Requer um arquivo de configuração YAML (ex: `substituicoes_texto.yaml`) com uma lista de regras na chave `text_replacements`.

*   `column`: A coluna onde a substituição deve ser aplicada.
*   `pattern`: O texto ou a expressão regular a ser encontrada.
*   `new_value`: O novo valor que substituirá o padrão encontrado.
*   `is_regex`: Um booleano (`true` ou `false`) que indica se o `pattern` deve ser tratado como uma expressão regular.

```yaml
# Lista de regras para encontrar e substituir texto.
text_replacements:
  # Regra 1: Substituição de substring simples na coluna 'description'.
  # Transforma "Produto A-123" em "SKU-A-123".
  - column: "description"
    pattern: "Produto A"
    new_value: "SKU-A"
    is_regex: false

  # Regra 2: Substituição com expressão regular na coluna 'category'.
  # Remove hífens de categorias como "Eletronicos-Info".
  - column: "category"
    pattern: "(\\w+)-(\\w+)"
    new_value: "\\1 \\2"
    is_regex: true
```

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --find-and-replace-text substituicoes_texto.yaml
```

---

## Fase 4: Visualização (`visualization`)

Esta fase lança aplicações interativas para explorar os dados.

### Aplicação: Explorador de Perfil de Dados

Inicia uma aplicação web (Streamlit) para gerar e visualizar um relatório de *profiling* detalhado de um único arquivo de dados.

#### Comando

```bash
python src/phases/phase04_visualization/app_explore_single_profile.py
```

Após executar o comando, uma página web será aberta no seu navegador. Você poderá então:
1.  Especificar o diretório onde seus dados estão.
2.  Buscar por arquivos (`.csv`, `.xlsx`, etc.).
3.  Selecionar um arquivo da lista para gerar e visualizar o relatório interativo.
