# Projeto de Análise de Dados com Python

Este repositório contém um conjunto de scripts Python desenvolvidos para otimizar e padronizar tarefas de análise e ciência de dados. O objetivo é criar uma caixa de ferramentas modular e reutilizável para acelerar o ciclo de vida de projetos de dados, desde a ingestão e limpeza até a análise exploratória.

## 🚀 Como Começar

Siga os passos abaixo para configurar o ambiente e executar os scripts.

### Pré-requisitos

- Python 3.11 ou superior
- Git

### Instalação

1.  **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd analise-dados
    ```

2.  **Ative o ambiente virtual:**
    O projeto já inclui um ambiente virtual em `.venv/`.

    - No **Windows**:
      ```bash
      .venv\Scripts\activate
      ```
    - No **macOS/Linux**:
      ```bash
      source .venv/bin/activate
      ```

3.  **Instale as dependências:**
    As dependências do projeto estão listadas em `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Opcional: habilite os hooks locais de qualidade**
    Se você quiser validar higiene básica de arquivos antes dos commits:
    ```bash
    pip install pre-commit
    pre-commit install
    ```

## Fases do Pipeline e Ferramentas

O projeto é estruturado em fases que representam o ciclo de vida da análise de dados, desde a descoberta até a visualização. Cada fase contém um conjunto de ferramentas modulares, orquestradas por um script principal.

### Visão Geral das Fases

- **Fase 1: Descoberta e Diagnóstico**: Avalia a qualidade, estrutura e conteúdo dos dados brutos.
- **Fase 2: Tratamento e Padronização**: Foca em corrigir problemas identificados, limpando e padronizando os dados.
- **Fase 3: Análise Exploratória e Pré-processamento**: Explora, filtra e transforma os dados para análise.
- **Fase 4: Visualização e Dashboards**: Comunica os resultados através de ferramentas visuais e interativas.

## 📂 Estrutura do Projeto

A estrutura de diretórios foi organizada para refletir as fases do pipeline de análise e centralizar o ponto de entrada principal:

```
/
├── data/                      # Dados brutos, intermediários e processados
│   └── <nome_do_projeto>/     # Ex: data/dados_consumidor_br
│       ├── arquivo1.csv
│       └── ...
├── src/
│   ├── run.py                 # Módulo principal da CLI (executado via python -m src.run)
│   ├── phases/                # Lógica e ferramentas de cada fase
│   │   ├── phase01_discovery/
│   │   │   ├── core/
│   │   │   ├── file_type_specific/
│   │   │   └── phase01_orchestrator.py
│   │   ├── phase02_treatment/
│   │   ├── phase03_exploratory/
│   │   └── phase04_visualization/
│   ├── app_main_interface.py  # Lógica da interface gráfica Streamlit
│   ├── connectors/            # Conectores para diferentes fontes de dados
│   └── utils.py               # Funções utilitárias gerais
├── docs/                      # Documentação técnica específica do projeto
├── .venv/                     # Ambiente virtual Python
├── app.py                     # Wrapper da interface Streamlit
├── .gitignore
├── .pre-commit-config.yaml
└── requirements.txt           # Dependências do projeto
```

## 🛠️ Como Usar

A ferramenta pode ser operada de duas formas: através da **Interface Gráfica (GUI)** ou da **Linha de Comando (CLI)**.

### Interface Gráfica (Recomendado para iniciantes)

Para uma experiência visual e interativa, use a interface baseada em Streamlit.

**Como iniciar:**
```bash
streamlit run app.py
```
Para instruções detalhadas sobre como usar a interface gráfica, consulte o **[Guia de Uso Completo](COMO_USAR.md)**.
Para convenções técnicas e de contribuição, consulte também a pasta **[docs/](docs/README.md)**.

### Linha de Comando (CLI)

Para automação e usuários avançados, a CLI oferece acesso direto a todas as funcionalidades. O ponto de entrada canônico é o módulo `src.run`.

**Estrutura básica:**
```bash
python3 -m src.run <comando> [sub-comando] [opções]
```

**Comandos principais:**
- `discovery`: Para análise e diagnóstico de dados.
- `treatment`: Para limpeza e transformação de dados.

Use a opção `--help` para ver todos os detalhes de um comando:
```bash
python3 -m src.run discovery --help
python3 -m src.run treatment --help
```

**Exemplo 1: Executar a fase de `discovery`**

Este comando analisa todos os arquivos no diretório `data/sample` e gera um relatório HTML.
```bash
python3 -m src.run discovery --data-project-path ./data/sample --report-output html
```

**Exemplo 2: Enriquecer dados usando o `treatment`**

Este comando enriquece um arquivo principal com dados de um arquivo de consulta (lookup).
```bash
python3 -m src.run treatment enrich \
    --main-file ./data/sample/consumidorgovbr_2025-01.csv \
    --lookup-file ./data/sample/lookup.csv \
    --main-key "CNPJ" \
    --lookup-key "CNPJ" \
    --columns-to-add "NOME FANTASIA" \
    --output-file ./data/sample/consumidor_enriquecido.csv
```

**Exemplo 3: Renomear colunas de um CSV ou XLSX**

```bash
python3 -m src.run treatment rename_columns \
    --input-file ./data/sample/clientes.csv \
    --old-columns "CPF" "NOME" \
    --new-columns "documento" "nome" \
    --delimiter ";"
```

Como conveniência, também existe um wrapper fino em `src/scripts/rename_columns.py`, executável como módulo:

```bash
python3 -m src.scripts.rename_columns --input-file ./data/sample/clientes.xlsx --old-columns "CPF" "NOME" --new-columns "documento" "nome" --sheet-name Planilha1
```

Para mais exemplos e uma explicação detalhada de todos os comandos e sub-comandos, consulte a seção **Uso via Linha de Comando (CLI)** no nosso **[Guia de Uso Completo](COMO_USAR.md)**.
