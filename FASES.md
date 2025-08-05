# O Ciclo de Vida de um Projeto de Ciência de Dados

Este documento define as fases macro de um projeto de ciência de dados, servindo como um guia estratégico para o desenvolvimento de um kit de ferramentas modular, flexível e poderoso.

---

### **Fase 0: Planejamento e Definição do Problema**

O alicerce de qualquer projeto de sucesso. O objetivo aqui é traduzir uma necessidade de negócio em um problema de dados bem definido.

- **Objetivo:** Entender o problema de negócio, definir os objetivos da análise e/ou do modelo, e estabelecer os critérios de sucesso.
- **Atividades Principais:**
  - Reuniões com stakeholders para definir a dor e o valor esperado.
  - Formulação da pergunta de negócio (análise) ou do objetivo preditivo (modelagem).
  - Definição de hipóteses iniciais.
  - Mapeamento dos KPIs que medirão o sucesso.
- **Entregáveis:**
  - Documento de escopo do projeto.
  - Lista de perguntas e hipóteses.
  - Métricas de sucesso (offline e online) definidas.

---

### **Fase 1: Descoberta e Diagnóstico de Dados**

O primeiro contato técnico com os dados brutos, focado em avaliar a "saúde" e a viabilidade para o projeto.

- **Objetivo:** Identificar, coletar e avaliar a qualidade, estrutura e conteúdo dos dados para diagnosticar problemas que possam impactar a modelagem.
- **Atividades Principais (Orquestradas):**
  - **Descoberta de Arquivos:** Localização de fontes de dados, respeitando regras de exclusão.
  - **Análise de Metadados:** Detecção de encoding, delimitadores, análise de volume (tamanho, nº de linhas/colunas).
  - **Verificação de Integridade:** Checagens de legibilidade, validação estrutural e detecção de caracteres problemáticos.
  - **Análise de Consistência:** Verificação da consistência de colunas e tipos de dados entre diferentes arquivos.
- **Entregáveis:**
  - **Relatório de Diagnóstico:** Um resumo técnico dos problemas encontrados e um parecer sobre a adequação dos dados para o projeto.
- **Escalabilidade:**
  - **Simples:** Análise de um conjunto de arquivos locais.
  - **Complexo:** Conexão a múltiplas fontes de dados (bancos, APIs), com relatórios detalhados e um sumário executivo agregado.

---

### **Fase 2: Tratamento e Limpeza de Dados**

Com o diagnóstico em mãos, esta fase é focada em transformar dados brutos e "sujos" em um material confiável e pronto para análise.

- **Objetivo:** Corrigir, padronizar, enriquecer e transformar os dados, garantindo consistência e qualidade.
- **Atividades Principais (Orquestradas):**
  - **Limpeza e Padronização:** Substituição de valores, limpeza de texto (regex), remoção de duplicatas.
  - **Conversão de Tipos:** Garantir que cada coluna tenha o tipo de dado correto (numérico, categórico, data/hora).
  - **Tratamento de Dados Faltantes:** Aplicação de estratégias como preenchimento (média, mediana, valor fixo) ou remoção.
  - **Consolidação e Enriquecimento:** Junção de múltiplos arquivos e enriquecimento com dados de fontes secundárias (lookup).
- **Entregáveis:**
  - Conjunto de dados limpo e processado.
  - **Relatório de Tratamento:** Um log de auditoria detalhado de todas as operações, garantindo a rastreabilidade das alterações.
- **Escalabilidade:**
  - **Simples:** Aplicar uma regra de substituição a um único arquivo.
  - **Complexo:** Orquestrar um pipeline com múltiplas etapas de limpeza, configurado via YAML, com um relatório completo no final.

---

### **Fase 3: Análise Exploratória e Engenharia de Atributos**

Com dados limpos, iniciamos a exploração para gerar insights e, crucialmente, criar os atributos (features) que alimentarão os modelos.

- **Objetivo:** Entender os padrões nos dados e criar/transformar variáveis para maximizar o poder preditivo dos modelos.
- **Atividades Principais (Orquestradas):**
  - **Análise Estatística e Visual:** Cálculo de estatísticas descritivas, análise de distribuição e correlação.
  - **Engenharia de Atributos (Feature Engineering):**
    - Criação de novas features (ex: a partir de datas, interações entre variáveis).
    - Transformação de variáveis (log, normalização, padronização).
    - Codificação de variáveis categóricas (one-hot, target encoding).
  - **Seleção de Atributos (Feature Selection):** Aplicação de técnicas para selecionar os atributos mais relevantes para o modelo.
- **Entregáveis:**
  - Notebook de análise com insights e visualizações.
  - Conjunto de dados final, pré-processado e pronto para a modelagem.
  - **Dicionário de Atributos:** Documentação das novas features criadas.
- **Escalabilidade:**
  - **Simples:** Gerar um relatório de perfil de dados e criar duas ou três features manualmente.
  - **Complexo:** Construir um pipeline de feature engineering reutilizável e aplicar métodos estatísticos para seleção de atributos.

---

### **Fase 4: Modelagem Preditiva**

O coração da ciência de dados: treinar, avaliar e selecionar o melhor modelo para resolver o problema de negócio.

- **Objetivo:** Aplicar algoritmos de Machine Learning para construir um modelo preditivo robusto e com performance validada.
- **Atividades Principais (Orquestradas):**
  - **Seleção de Algoritmos:** Escolha de modelos candidatos apropriados para a tarefa (regressão, classificação, etc.).
  - **Treinamento e Validação:**
    - Divisão dos dados em conjuntos de treino, validação e teste.
    - Uso de **Validação Cruzada (Cross-Validation)** para uma estimativa robusta da performance.
  - **Otimização de Hiperparâmetros:** Ajuste fino dos modelos para maximizar o desempenho.
  - **Avaliação de Modelos:** Comparação dos modelos candidatos usando as métricas de negócio definidas na Fase 0.
- **Entregáveis:**
  - Modelo treinado e serializado (salvo em arquivo).
  - **Relatório de Performance do Modelo:** Métricas de validação, matriz de confusão, curva ROC, etc.
  - Código para registro do experimento (ex: com MLflow).
- **Escalabilidade:**
  - **Simples:** Treinar uma Regressão Logística e uma Árvore de Decisão em um notebook.
  - **Complexo:** Orquestrar o treinamento e a otimização de múltiplos modelos, registrar todos os experimentos e selecionar o campeão de forma automatizada.

---

### **Fase 5: Apresentação de Resultados e Interpretabilidade**

Um modelo só gera valor se for confiável e se seus resultados puderem ser comunicados de forma eficaz para impulsionar a tomada de decisão.

- **Objetivo:** Traduzir os resultados técnicos em insights de negócio, garantir a interpretabilidade do modelo e comunicar as conclusões aos stakeholders.
- **Atividades Principais (Orquestradas):**
  - **Interpretação de Modelos:** Análise da importância das features (feature importance) e uso de técnicas como SHAP ou LIME para explicar as previsões do modelo.
  - **Criação de Dashboards Interativos:** Desenvolvimento de painéis que permitam a exploração dos resultados do modelo.
  - **Storytelling com Dados:** Construção de uma narrativa coesa que guia o stakeholder através do problema, da solução e das recomendações.
- **Entregáveis:**
  - Dashboard interativo para análise de cenários ("what-if").
  - Relatório de interpretabilidade do modelo.
  - Apresentação executiva com as conclusões e o impacto de negócio.
