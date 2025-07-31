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

Esta fase ajuda a diagnosticar seus dados brutos. Ela gera relatórios sobre o volume, integridade, codificação e estrutura dos arquivos.

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

---

## Fase 2: Tratamento (`treatment`)

Esta fase é usada para modificar os dados. **Você deve escolher apenas uma das operações abaixo por execução.**

### Operação 1: Tratamento Padrão (`--apply-standard-treatment`)

Aplica um conjunto de limpezas padrão (correção de valores, transformação de colunas) nos arquivos.

**Importante:** Esta operação **substitui** os arquivos originais. Um backup dos arquivos originais é criado automaticamente em uma pasta `fad-bkp-treatment-[timestamp]` dentro do seu projeto de dados.

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --apply-standard-treatment
```

### Operação 2: Concatenar Dados (`--concatenate-data`)

Junta múltiplos arquivos de um diretório em um único arquivo de saída.

#### Configuração

Esta operação requer um arquivo de configuração JSON. Crie um arquivo (ex: `config_concat.json`) com a seguinte estrutura:

```json
{
  "input_folder": "caminho/para/pasta/com/arquivos",
  "output_file": "caminho/para/arquivo_final.csv",
  "file_format": "csv"
}
```

*   `input_folder`: O diretório contendo os arquivos a serem concatenados.
*   `output_file`: O nome e caminho do arquivo de saída.
*   `file_format`: O formato dos arquivos de entrada (`csv`, `xlsx`, etc.).

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --concatenate-data caminho/para/config_concat.json
```

### Operação 3: Enriquecer Dados (`--enrich-data`)

Adiciona informações a um arquivo principal (main) com base em um arquivo de consulta (lookup), similar a um `JOIN` em bancos de dados.

#### Configuração

Requer um arquivo de configuração JSON (ex: `config_enrich.json`):

```json
{
  "main_file": "caminho/para/arquivo_principal.csv",
  "lookup_file": "caminho/para/arquivo_consulta.csv",
  "output_file": "caminho/para/arquivo_enriquecido.csv",
  "main_key": "coluna_chave_principal",
  "lookup_key": "coluna_chave_consulta",
  "columns_to_add": ["coluna1_da_consulta", "coluna2_da_consulta"]
}
```

*   `main_file`: O arquivo que receberá as novas informações.
*   `lookup_file`: O arquivo que contém as informações a serem adicionadas.
*   `output_file`: O nome e caminho do arquivo de saída.
*   `main_key` / `lookup_key`: As colunas usadas para combinar os dois arquivos.
*   `columns_to_add`: A lista de colunas do arquivo de consulta que serão adicionadas ao arquivo principal.

#### Comando

```bash
python src/run.py -d data/meu_projeto -p treatment --enrich-data caminho/para/config_enrich.json
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
