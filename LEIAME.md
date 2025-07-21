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

## Fases do Pipeline e Ferramentas

O projeto é estruturado em fases que representam o ciclo de vida da análise de dados, desde a descoberta até a visualização. Cada fase contém um conjunto de ferramentas modulares, orquestradas por um script principal.

### Visão Geral das Fases

*   **Fase 1: Descoberta e Diagnóstico**: Avalia a qualidade, estrutura e conteúdo dos dados brutos.
*   **Fase 2: Tratamento e Padronização**: Foca em corrigir problemas identificados, limpando e padronizando os dados.
*   **Fase 3: Análise Exploratória e Pré-processamento**: Explora, filtra e transforma os dados para análise.
*   **Fase 4: Visualização e Dashboards**: Comunica os resultados através de ferramentas visuais e interativas.

## 📂 Estrutura do Projeto

A estrutura de diretórios foi organizada para refletir as fases do pipeline de análise e centralizar o orquestrador:

```
/
├── data/                      # Dados brutos, intermediários e processados
│   └── <nome_do_projeto>/     # Ex: data/dados_consumidor_br
│       ├── arquivo1.csv
│       └── ...
├── src/
│   ├── main/                  # Contém o orquestrador principal
│   │   └── orchestrator.py
│   ├── phases/                # Lógica e ferramentas de cada fase
│   │   ├── phase01_discovery/
│   │   │   ├── core/
│   │   │   ├── file_type_specific/
│   │   │   └── phase01_orchestrator.py
│   │   ├── phase02_treatment/
│   │   ├── phase03_exploratory/
│   │   └── phase04_visualization/
│   ├── connectors/            # Conectores para diferentes fontes de dados
│   └── utils.py               # Funções utilitárias gerais
├── .venv/                     # Ambiente virtual Python
├── .gitignore
├── README.md
└── requirements.txt           # Dependências do projeto
```

## 🛠️ Como Usar

O orquestrador principal (`src/main/orchestrator.py`) é o ponto de entrada para executar as diferentes fases do pipeline.

Para executar uma fase, certifique-se de que seu ambiente virtual esteja ativado e use o seguinte comando:

```bash
python src/main/orchestrator.py --data-project-path <caminho_para_sua_pasta_de_dados> --phase <nome_da_fase>
```

*   **`<caminho_para_sua_pasta_de_dados>`**: O caminho para o diretório que contém os arquivos de dados do seu projeto (ex: `data/meu_projeto`).
*   **`<nome_da_fase>`**: A fase que você deseja executar. As opções são: `discovery`, `treatment`, `exploratory`, `visualization`.

**Exemplo de execução da fase de Descoberta e Diagnóstico:**

```bash
python src/main/orchestrator.py --data-project-path data/meu_projeto --phase discovery
```

Use o sufixo `-h` ou `--help` com o `orchestrator.py` para ver as opções disponíveis.

**Exemplo de execução:**
