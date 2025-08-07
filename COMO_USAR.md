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

### Resultados

-   O progresso e os logs da execução serão exibidos em tempo real na área principal da tela.
-   Se a execução for bem-sucedida e um relatório for gerado, um botão **Baixar Relatório** aparecerá, permitindo que você salve o arquivo.
-   Em caso de erro, uma mensagem clara será exibida com os detalhes para ajudar a diagnosticar o problema.

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
