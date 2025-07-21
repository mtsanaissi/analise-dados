# Projeto de Análise de Dados com Python

Este repositório contém um conjunto de scripts Python desenvolvidos para otimizar e padronizar tarefas de análise e ciência de dados. O objetivo é criar uma caixa de ferramentas modular e reutilizável para acelerar o ciclo de vida de projetos de dados, desde a ingestão e limpeza até a análise exploratória.

## 🚀 Como Começar

Siga os passos abaixo para configurar o ambiente e executar os scripts.

### Pré-requisitos

-   Python 3.11 ou superior
-   Git

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd analise-dados
    ```

2.  **Ative o ambiente virtual:**
    O projeto já inclui um ambiente virtual em `.venv/`.

    -   No **Windows**:
        ```bash
        .venv\Scripts\activate
        ```
    -   No **macOS/Linux**:
        ```bash
        source .venv/bin/activate
        ```

3.  **Instale as dependências:**
    As dependências do projeto estão listadas em `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Fases do Pipeline e Scripts

O projeto é estruturado em fases que representam o ciclo de vida da análise de dados, desde a descoberta até a visualização. Cada fase é implementada em um diretório específico dentro de `src/`.

### Fase 1: Descoberta e Diagnóstico (`src/01_discovery_and_diagnosis`)

O objetivo desta fase é avaliar a qualidade, estrutura e conteúdo dos dados brutos.

*   **`p1_01_discover_and_convert_encoding.py`**: Localiza arquivos e converte seu encoding para UTF-8 para garantir a legibilidade.
*   **`p1_02_calculate_data_volume.py`**: Calcula métricas de volume, como contagem de registros e tamanho dos arquivos.
*   **`p1_03_detect_csv_delimiter.py`**: Detecta o delimitador utilizado em arquivos CSV.
*   **`p1_04_check_column_consistency.py`**: Verifica se múltiplos arquivos CSV possuem a mesma estrutura de colunas.
*   **`p1_05_check_data_integrity.py`**: Realiza um conjunto de verificações de integridade nos dados.
*   **`p1_06_profile_data_columns.py`**: Gera um perfil detalhado de cada coluna, com estatísticas e tipos de dados inferidos.

### Fase 2: Tratamento e Padronização (`src/02_treatment_and_standardization`)

Esta fase foca em corrigir os problemas identificados, limpando e padronizando os dados.

*   **`p2_02_extract_problematic_values.py`**: Identifica e extrai células com valores problemáticos ou malformados.
*   **`p2_03_apply_value_corrections.py`**: Aplica correções em lote com base em um mapa de "de-para".
*   **`p2_04_fix_remove_total_column.py`**: Remove colunas desnecessárias, como "Total", que podem ser adicionadas por planilhas.

### Fase 3: Análise Exploratória e Pré-processamento (`src/03_exploratory_analysis_and_preprocessing`)

Com os dados limpos, esta fase foca em explorar, filtrar e transformar os dados para análise.

*   **`p3_01_explore_distinct_values.py`**: Permite explorar os valores únicos em colunas categóricas.
*   **`p3_02_preprocess_filter_batch.py`**: Filtra os dados em lote com base em regras customizáveis.
*   **`p3_03_transform_denormalize_rows.py`**: Transforma dados, separando uma célula com múltiplos valores em várias linhas.

### Fase 4: Visualização e Dashboards (`src/04_visualization_and_dashboards`)

A fase final, onde os resultados são comunicados através de ferramentas visuais e interativas.

*   **`app_explore_aggregated_profiles.py`**: Dashboard para explorar perfis de dados agregados.
*   **`app_explore_single_profile.py`**: Dashboard para análise profunda de um único perfil de dados.
*   **`app_generic_data_analyzer.py`**: Ferramenta de análise genérica para visualização de dados.
*   **`tool_generate_html_profiles.py`**: Gera relatórios de perfil de dados em formato HTML.

## 📂 Estrutura do Projeto

A estrutura de diretórios foi organizada para refletir as fases do pipeline de análise:

```
/
├── data/
├── src/
│   ├── 01_discovery_and_diagnosis/
│   ├── 02_treatment_and_standardization/
│   ├── 03_exploratory_analysis_and_preprocessing/
│   └── 04_visualization_and_dashboards/
├── .venv/
├── LEIAME.md
└── requirements.txt
```

## 🛠️ Como Usar

Os scripts principais estão localizados no diretório `src/`. Para executá-los, certifique-se de que seu ambiente virtual esteja ativado e então execute o script desejado com os argumentos necessários. Use o sufixo `-h` ou `--help` para ver as opções de cada script.

**Exemplo de execução:**
