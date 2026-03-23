# Guia de Uso: Kit de Ferramentas de Análise de Dados

Este guia foca em como utilizar a interface gráfica do "Painel de Controle do Kit de Ferramentas" para executar as fases de análise de dados.

## Iniciando a Aplicação

Para começar, execute o seguinte comando no seu terminal a partir da raiz do projeto:

```bash
streamlit run src/app_main_interface.py
```

Isso iniciará a aplicação e abrirá uma nova aba no seu navegador.

## Configurações Principais

No painel lateral esquerdo, você encontrará as "Configurações de Execução", que são a base para qualquer operação.

1.  **Caminho do Projeto de Dados**: Insira o caminho para a pasta que contém os arquivos de dados que você deseja analisar. Por padrão, ele aponta para `data/sample`, que contém dados de exemplo.

2.  **Fase do Projeto**: Selecione a fase que deseja executar. Atualmente, as fases `discovery` e `treatment` estão disponíveis na interface.

## Fase 1: Discovery

A fase de *Discovery* é usada para diagnosticar seus dados brutos. Ela gera relatórios sobre a estrutura, qualidade e características dos arquivos, sem modificar os dados originais.

### Como Usar

1.  Selecione `discovery` na lista de "Fase do Projeto".
2.  Configure as opções na seção "Opções da Fase de Discovery":
    -   **Comparar Campos/Colunas**: Marque esta opção para verificar se arquivos do mesmo tipo (ex: múltiplos CSVs) possuem as mesmas colunas.
    -   **Comparar Tipos de Dados**: Marque para comparar os tipos de dados inferidos para colunas de mesmo nome entre diferentes arquivos.
    -   **Formato do Relatório**: Escolha entre `json` (para análise de máquina) ou `html` (para um relatório visual e interativo).
    -   **Gerar Config. de Limpeza de Caracteres**: Se desejar procurar por caracteres problemáticos e gerar um arquivo de configuração para a fase de tratamento, especifique um nome de arquivo aqui (ex: `config_limpeza.yaml`).

3.  Clique no botão **Executar**.

### Visualizando os Resultados

Após cada execução, a interface apresentará os resultados da seguinte forma:

1.  **Mensagem de Status**: Uma notificação de sucesso ou erro aparecerá no topo, indicando o resultado da operação.

2.  **Detalhes da Execução (Colapsável)**:
    -   Para manter a interface limpa, os detalhes técnicos da execução ficam ocultos por padrão dentro de uma seção chamada **"Ver Detalhes da Execução"**.
    -   Clique nesta seção para expandi-la e visualizar:
        -   **Comando Executado**: O comando completo que foi executado nos bastidores.
        -   **Log de Saída**: O log completo do processo, útil para depuração e para entender cada passo da execução.

3.  **Visualizador de Relatório**:
    -   Se a sua operação gerou um relatório (`.html` ou `.json`), ele será exibido diretamente na interface, abaixo da seção de detalhes.
        -   Relatórios **HTML** são renderizados como páginas interativas.
        -   Relatórios **JSON** são exibidos em um formato estruturado e legível.
    -   O botão **"Baixar Relatório"** continua disponível, localizado logo abaixo do visualizador, para que você possa salvar o arquivo em sua máquina.

## Fase 2: Treatment

A fase de *Treatment* é usada para limpar, padronizar e modificar seus dados.

### Como Usar

1.  Selecione `treatment` na lista de "Fase do Projeto".
2.  Na seção "Opções da Fase de Treatment", escolha a **Operação de Tratamento** que deseja realizar.

#### Opções de Tratamento

-   **Remover Espaços**: Remove espaços em branco do início e do fim de todos os valores em todos os arquivos. Nenhuma configuração adicional é necessária.

-   **Substituir Valores**: Substitui valores inteiros em células específicas.
    -   **Requer Configuração**: Faça o upload de um arquivo YAML contendo as regras de substituição.

-   **Encontrar e Substituir Texto**: Substitui partes de texto dentro das células, útil para correções com regex.
    -   **Requer Configuração**: Faça o upload de um arquivo YAML com as regras de busca e substituição.

-   **Concatenar Dados**: Junta múltiplos arquivos em um único arquivo de saída.
    -   **Requer Configuração**: Faça o upload de um arquivo YAML especificando os arquivos de entrada e o de saída.

-   **Enriquecer Dados**: Adiciona colunas a um arquivo principal com base em dados de um arquivo de consulta (lookup).
    -   **Configuração Interativa**: Esta operação agora possui uma interface dedicada para configuração.
        -   **Arquivo Principal**: Especifique o nome do arquivo (dentro do projeto de dados) que receberá as novas colunas.
        -   **Arquivo de Lookup**: Forneça o caminho para o arquivo que contém os dados a serem adicionados. Pode ser um caminho relativo ao projeto ou um caminho absoluto.
        -   **Chave no Principal / Chave no Lookup**: Defina as colunas que serão usadas para combinar os dois arquivos.
        -   **Colunas a Adicionar**: Este campo é preenchido dinamicamente! Após especificar um "Arquivo de Lookup" válido, a lista de colunas disponíveis aparecerá aqui para você selecionar.

3.  Após configurar a operação e, se necessário, fazer o upload do arquivo de configuração, clique em **Executar**.

### Resultados

-   Assim como na fase de Discovery, o output da execução será exibido em tempo real.
-   Como as operações de tratamento modificam os arquivos, um backup dos dados originais é criado automaticamente em uma pasta `fad-bkp-treatment-[timestamp]` dentro do seu projeto de dados.
-   Uma mensagem de sucesso ou erro será exibida ao final da execução. Se um relatório for gerado (dependendo da operação), um link para download será fornecido.

---

**Nota**: Enquanto uma operação está em andamento, todos os controles da interface são desabilitados para prevenir múltiplas execuções simultâneas. Um indicador visual (spinner) mostrará que a aplicação está ocupada.

---

## Uso via Linha de Comando (CLI)

Além da interface gráfica, o kit de ferramentas oferece uma poderosa interface de linha de comando (CLI) para automação e execução de tarefas. O ponto de entrada para a CLI é o script `src/run.py`.

### Estrutura do Comando

O uso geral segue o formato:
```bash
python src/run.py [comando] [sub-comando] [argumentos...]
```

- **`[comando]`**: A fase principal a ser executada (`discovery` ou `treatment`).
- **`[sub-comando]`**: Uma operação específica dentro da fase `treatment` (ex: `enrich`, `correct_values`).
- **`[argumentos]`**: Parâmetros para configurar a execução.

### Comando `discovery`

Executa a fase de descoberta e diagnóstico dos dados.

**Uso:**
```bash
python src/run.py discovery [argumentos...]
```

**Argumentos:**

| Argumento                           | Descrição                                                                                             | Exemplo                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `--data-project-path` (obrigatório) | Caminho para o diretório do projeto de dados.                                                           | `--data-project-path ./data/sample`                    |
| `--extensions`                      | Lista de extensões de arquivo a serem analisadas (padrão: `csv`, `xlsx`, `xls`, `json`, `txt`).          | `--extensions csv xlsx`                                |
| `--no-recursive`                    | Desativa a busca recursiva por arquivos no diretório.                                                   | `--no-recursive`                                       |
| `--output-format`                   | Formato da saída no console (`text` ou `interactive`, padrão: `text`).                                  | `--output-format interactive`                          |
| `--report-output`                   | Formato do arquivo de relatório (`json`, `html`, ou `none`, padrão: `json`).                             | `--report-output html`                                 |
| `--compare-fields`                  | Ativa a comparação de estrutura (colunas/campos) entre arquivos do mesmo tipo.                          | `--compare-fields`                                     |
| `--compare-types`                   | Ativa a comparação de tipos de dados para colunas de mesmo nome entre arquivos.                         | `--compare-types`                                      |
| `--generate-char-cleanup-config`    | Gera um arquivo de configuração YAML para a limpeza de caracteres problemáticos.                        | `--generate-char-cleanup-config clean_up.yml`          |

**Exemplo Completo:**
```bash
python src/run.py discovery --data-project-path ./data/sample --report-output html --compare-fields --compare-types
```

### Comando `treatment`

Executa a fase de tratamento para limpar, padronizar e modificar os dados. O comando `treatment` requer um sub-comando para especificar a operação.

#### Sub-comando `enrich`

Enriquece um arquivo de dados com base em outro (lookup).

**Uso:**
```bash
python3 src/run.py treatment enrich [argumentos...]
```

**Argumentos:**

| Argumento              | Descrição                                                    |
| ---------------------- | ------------------------------------------------------------ |
| `--main-file`          | Caminho para o arquivo principal a ser enriquecido.          |
| `--lookup-file`        | Caminho para o arquivo de consulta (lookup).                 |
| `--main-key`           | Nome da coluna chave no arquivo principal.                   |
| `--lookup-key`         | Nome da coluna chave no arquivo de consulta.                 |
| `--columns-to-add`     | Nomes das colunas a serem adicionadas do arquivo de consulta. |
| `--output-file`        | Caminho para salvar o arquivo de saída enriquecido.          |
| `--join-how`           | Tipo de junção (`left`, `right`, `outer`, `inner`, padrão: `left`). |
| `--sep`                | Delimitador dos arquivos CSV (padrão: `,`).                  |

**Exemplo:**
```bash
python3 src/run.py treatment enrich --main-file a.csv --lookup-file b.csv --main-key id --lookup-key id --columns-to-add nome --output-file c.csv
```

#### Sub-comando `correct_values`

Corrige valores em colunas com base em um arquivo de mapeamento.

**Uso:**
```bash
python3 src/run.py treatment correct_values --data-project-path [caminho] --config-file [arquivo_config]
```

#### Sub-comando `replace_text`

Substitui textos em colunas com base em regras de um arquivo de configuração.

**Uso:**
```bash
python3 src/run.py treatment replace_text --data-project-path [caminho] --config-file [arquivo_config]
```

#### Sub-comando `remove_whitespace`

Remove espaços em branco do início e fim dos valores.

**Uso:**
```bash
python3 src/run.py treatment remove_whitespace --data-project-path [caminho]
```

#### Sub-comando `transform_columns`

Remove a coluna final `Total` de arquivos CSV em um diretório.

**Uso:**
```bash
python3 src/run.py treatment transform_columns --data-project-path [caminho]
```

#### Sub-comando `rename_columns`

Renomeia colunas de um único arquivo CSV ou Excel sem duplicar a lógica de tratamento em scripts avulsos.

**Uso:**
```bash
python3 src/run.py treatment rename_columns --input-file [arquivo] --old-columns [coluna_antiga ...] --new-columns [coluna_nova ...]
```

**Argumentos:**

| Argumento        | Descrição |
| ---------------- | --------- |
| `--input-file`   | Caminho para o arquivo CSV ou XLSX que terá o cabeçalho alterado. |
| `--old-columns`  | Lista com os nomes atuais das colunas a serem renomeadas. |
| `--new-columns`  | Lista com os novos nomes das colunas, na mesma ordem de `--old-columns`. |
| `--output-file`  | Caminho do arquivo de saída. Quando omitido, o arquivo original é sobrescrito. |
| `--delimiter`    | Delimitador do CSV. Quando omitido, o sistema tenta detectar automaticamente. |
| `--sheet-name`   | Nome da planilha para arquivos XLSX. Quando omitido, usa a primeira planilha. |

**Exemplos:**
```bash
python3 src/run.py treatment rename_columns --input-file ./data/sample/clientes.csv --old-columns CPF NOME --new-columns documento nome --delimiter ";"
python3 src/run.py treatment rename_columns --input-file ./data/sample/clientes.xlsx --old-columns CPF NOME --new-columns documento nome --sheet-name Planilha1
python3 -m src.scripts.rename_columns --input-file ./data/sample/clientes.csv --old-columns CPF NOME --new-columns documento nome --delimiter ";"
```

#### Sub-comando `concatenate`

Concatena múltiplos arquivos em um único.

**Uso:**
```bash
python3 src/run.py treatment concatenate --data-project-path [caminho] --output-file [arquivo_saida] --file-type [csv|xlsx]
```
