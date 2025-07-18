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

## Fases do Pipeline e Scripts Correspondentes

Seu projeto está organizado como um pipeline de análise e preparação de dados, dividido em fases lógicas que vão desde a descoberta e diagnóstico até a correção e análise exploratória.

### Fase 1: Descoberta e Diagnóstico de Dados

Esta fase foca em encontrar os dados e avaliar sua "saúde" estrutural e de conteúdo.

*   **`s00_discover_and_convert.py`**: O ponto de partida. Ele localiza arquivos com base nas extensões fornecidas e, crucialmente, verifica e converte o encoding para UTF-8. Esta é uma etapa fundamental para evitar erros de leitura nas fases seguintes.
*   **`s01_data_volume.py`**: Fornece uma visão macro dos dados, calculando métricas de volume como contagem de registros e tamanho em disco por tipo de arquivo. É o primeiro passo para entender a escala do conjunto de dados.
*   **`s02_csv_delimiter.py`**: Especializado em CSVs, este script detecta qual delimitador (`;`, `,`, `\t`, etc.) está sendo usado, algo essencial para a leitura correta desses arquivos.
*   **`s03_csv_columns.py`**: Verifica a consistência dos cabeçalhos em múltiplos arquivos CSV, garantindo que todos sigam a mesma estrutura. É vital para processos de `merge` ou `concat`.
*   **`s04_data_integrity.py`**: Um script de diagnóstico mais aprofundado que consolida várias verificações: legibilidade, encoding, estrutura básica (cabeçalhos, planilhas), e a presença de caracteres problemáticos.
*   **`profile_data_columns.py` e `data_profile.json`**: Esta dupla realiza o perfilamento detalhado dos dados. O script analisa cada coluna para inferir tipos de dados e calcular estatísticas descritivas (média, mediana, valores únicos, nulos, etc.), gerando um relatório JSON abrangente.

### Fase 2: Correção e Limpeza de Dados

Com base nos diagnósticos da fase anterior, esta fase aplica as correções.

*   **`s02b_convert_csv_delimiter.py`**: O contraponto do `s02`, este script padroniza os delimitadores dos arquivos CSV, salvando as versões corrigidas em um diretório de saída.
*   **`s04b_extract_problematic_csv_values.py` e `s04b_problematic_csv_values.json`**: O script `s04b` identifica e extrai células com caracteres malformados (provavelmente por problemas de encoding) para um arquivo JSON (`problematic_csv_values.json`), criando uma "lista de tarefas" para correção.
*   **`s04c_apply_corrections.py`**, **`s04c_corrections_map.json`** e **`s04c_corrections_map_2020_2024.json`**: Este conjunto é o "motor de correção". O script `s04c` utiliza um mapa de "de-para" (definido nos arquivos `corrections_map`) para substituir os valores problemáticos identificados pelo `s04b`.
*   **`quick_fix.py`**: Um utilitário específico para um problema comum: remover uma coluna chamada "Total" no final dos arquivos CSV.
*   **`data_transforms.py`**: Outro script de transformação específico, projetado para desnormalizar dados, separando valores de uma célula que contém quebras de linha em múltiplas linhas.

### Fase 3: Análise Exploratória e Transformação Avançada

Uma vez que os dados estão limpos e padronizados, esta fase foca na análise e na preparação para modelos ou relatórios.

*   **`check_distinct_values.py`**: Uma ferramenta de análise exploratória (EDA) que permite ao usuário ver todos os valores únicos para colunas específicas, útil para entender a variedade de dados categóricos.
*   **`filter_data_batch.py`**: Um script poderoso e customizável para filtrar os dados em lote. Ele permite ao usuário definir regras específicas (como manter apenas certos segmentos de mercado) e aplicar essas regras a todos os arquivos, preservando a estrutura de pastas.
*   **`data_analysis.py`**: A joia da coroa da visualização. Usando Streamlit e `ydata-profiling`, este script cria um dashboard interativo para uma análise visual profunda de um único arquivo de dados, exibindo estatísticas, tipos de dados, valores ausentes e um relatório de perfil completo.


## 📂 Estrutura do Projeto

A estrutura de diretórios segue as melhores práticas para projetos de ciência de dados:

```
/
├── data/                # Dados brutos, intermediários e processados
├── notebooks/           # Jupyter notebooks para exploração
├── src/                 # Scripts Python modulares
├── .venv/               # Ambiente virtual Python
├── GEMINI.md            # Guia para o assistente Gemini
├── GEMINI.md            # Guia para o assistente Jules
├── LEIAME.md
└── requirements.txt     # Dependências do projeto
```

## Estrutura de Diretórios e Mapeamento de Scripts

O projeto está organizado em um pipeline claro, onde cada diretório representa uma fase distinta do processo de tratamento e análise de dados.

- **`\src\discovery\`**: **(Descoberta e Diagnóstico)**
  Scripts nesta pasta são focados em entender o estado bruto dos dados. Eles encontram os arquivos e realizam diagnósticos sobre sua estrutura e conteúdo sem modificá-los.

- **`\src\standardize\`**: **(Padronização)**
  O objetivo aqui é deixar os arquivos em um formato técnico consistente. Isso inclui a conversão de encoding e a padronização de estruturas como delimitadores.

- **`\src\sanitize\`**: **(Limpeza e Correção)**
  Esta fase trata de corrigir o _conteúdo_ dos dados. Scripts aqui identificam e corrigem valores problemáticos, como caracteres inválidos ou dados malformados, com base em mapas de correção.

- **`\src\preprocess\`**: **(Pré-processamento)**
  Aqui começam as transformações que preparam os dados para a análise. Isso inclui a seleção de dados de interesse e o tratamento de problemas comuns como valores ausentes.

- **`\src\transform\`**: **(Transformação de Features)**
  Scripts nesta pasta modificam a estrutura dos dados para criar novas representações ou features para análise ou modelagem.

## 🛠️ Como Usar

Os scripts principais estão localizados no diretório `src/`. Para executá-los, certifique-se de que seu ambiente virtual esteja ativado e então execute o script desejado com os argumentos necessários. Use o sufixo `-h` ou `--help` para ver as opções de cada script.

**Exemplo de execução:**
