# Planejamento de melhorias e evoluções

Este documento detalha as tarefas planejadas para aprimorar os scripts de análise de dados existentes, com foco em aumentar a modularidade, reusabilidade e manutenibilidade do código. Também destaca possibilidades de evolução para o kit de ferramentas.

## 1. Qualidade e Padronização

- [ ] **1.1. Implementar testes unitários**
  - [x] Criar um diretório `tests/`.
  - [x] Adicionar testes com `pytest` para as funções no novo módulo `utils.py`, garantindo que a lógica de busca de arquivos e leitura de CSV funcione como esperado.
  - [ ] Implementar testes para os scripts src\s04\_\*.py.
- [ ] **1.2. Tratamento de erros**
  - [ ] Conferir se o tratamento de erros está adequado em todos os scripts.
- [ ] **1.3. Correção de Erros**
  - [ ] Identificar qual processo está substituindo o delimitador de CSVs por ",".
- [ ] **1.4. Documentação**
  - [ ] Verificar se os comentários são claros e explicativos.
  - [ ] Comentar trechos de código complexos ou que podem gerar dúvida.
  - [ ] Aperfeiçoar o LEIAME.md.
  - [ ] Criar documento com a especificação de cada script / funcionalidade.

## 2. Próximas evoluções

### 2.1. Orquestração e Usabilidade

- 2.1.1. Orquestrador de Pipeline: Um script principal (main.py ou run_pipeline.py) que lê um arquivo de configuração (em formato YAML, por exemplo) e executa os outros scripts na ordem definida. Isso permitiria automatizar todo o fluxo de trabalho com um único comando.
- 2.1.2. Logging Centralizado: Aprimorar o utils.py com uma configuração de logging que possa ser usada por todos os scripts para registrar o progresso, avisos e erros em um arquivo de log padronizado.

### 2.2. Projetos de Análise de Dados

- 2.2.1. Implementar lógica de "projetos" de análise de dados. Cada pasta dentro da pasta \data\ seria um projeto.

## 3. Funcionalidades futuras

### Ingestão de Dados

- Conector de Banco de Dados: Um script ou módulo que possa se conectar a bancos de dados (PostgreSQL, MySQL, SQL Server) usando uma string de conexão e executar uma query para extrair dados diretamente para um DataFrame Pandas.
- Cliente de API: Uma função utilitária para consumir dados de APIs REST. Ela receberia uma URL, parâmetros e headers (para autenticação) e retornaria os dados, geralmente em formato JSON, já prontos para serem transformados em DataFrame.
- Coletor de Dados Web (Web Scraper): Um script básico usando bibliotecas como BeautifulSoup e Requests para extrair tabelas HTML de páginas da web.

### Limpeza e Pré-processamento Avançado

- Tratamento de Dados Ausentes (Imputation): Um script que, com base no relatório de perfil (data_profile.json), sugere e aplica estratégias para tratar valores nulos:
  Remoção (de linhas ou colunas) baseada em um limiar (ex: remover colunas com > 50% de nulos).
- Preenchimento (imputação) com média, mediana, moda para colunas numéricas.
- Preenchimento com um valor constante ("Desconhecido") para colunas categóricas.
- Detecção e Tratamento de Outliers: Um script para identificar outliers em colunas numéricas usando métodos como o Z-score ou o intervalo interquartil (IQR) e oferecer opções para tratá-los (ex: remoção, clipping ou transformação logarítmica).
- Padronização e Normalização de Dados: Funções para escalar dados numéricos (ex: StandardScaler ou MinMaxScaler do Scikit-learn), uma etapa crucial para muitos algoritmos de Machine Learning.

### Engenharia de Features (Feature Engineering)

- Criação de Features Temporais: Um script que recebe colunas de data/hora e extrai novas features, como ano, mês, dia da semana, trimestre, etc.
- Criação de Features Categóricas: Funções para aplicar técnicas de encoding em variáveis categóricas, como One-Hot Encoding ou Label Encoding.
- Binning (Discretização): Uma função para converter variáveis numéricas contínuas em categorias (bins), como transformar "idade" em "faixas etárias".

### Análise e Modelagem

- Análise de Correlação: Um script que gera e salva uma matriz de correlação (para variáveis numéricas) e um mapa de calor (heatmap) para facilitar a visualização de relações entre as features.
- Kit Básico de Machine Learning: Um conjunto de scripts para um pipeline simples de ML:
- Divisão de Dados: Para separar os dados em conjuntos de treino e teste.
- Treinamento de Modelos: Scripts que treinam modelos básicos de classificação (ex: Regressão Logística, Random Forest) e regressão (ex: Regressão Linear, XGBoost).
- Avaliação de Modelos: Calcula e exibe métricas de performance (Acurácia, Precisão, Recall, F1-Score para classificação; R², MSE para regressão).
