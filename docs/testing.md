# Testes e Validação

Os testes deste projeto precisam refletir o comportamento de um toolkit de análise de dados, não apenas o de uma biblioteca isolada.

## Comando atual

Com o ambiente virtual ativado, rode:

```bash
pytest
```

Se preferir chamar o executável diretamente:

- Windows: `.venv\\Scripts\\pytest`
- Linux/macOS: `./.venv/bin/pytest`

O arquivo `pytest.ini` atual define `pythonpath = .`, então os testes assumem execução a partir da raiz do repositório.

## O que validar em mudanças relevantes

- Caminhos de sucesso e falha na leitura de CSV, XLSX, JSON, TXT e YAML.
- Processamento resiliente quando um arquivo está ausente, vazio, bloqueado ou malformado.
- Saídas geradas em diretórios de projeto de dados, como relatórios `discovery_report.*`, backups `fad-bkp-*` e saídas `fad-*`.
- Compatibilidade dos comandos da CLI em `src/run.py`.
- Compatibilidade das chamadas diretas da interface Streamlit quando a mudança toca a GUI.
- Integridade de conectores e funções utilitárias usadas por mais de uma fase.

## Boas práticas para este repositório

- Prefira testes unitários rápidos para regras isoladas.
- Adicione testes de integração focados quando houver interação entre módulos, arquivos de configuração, conectores ou geração de relatórios.
- Use fixtures pequenas e legíveis em `tests/data/` sempre que possível.
- Não presuma que dependências opcionais estarão disponíveis em todos os ambientes. Quando uma feature depende de biblioteca adicional, deixe isso explícito nos testes e na documentação.
- Documente verificações manuais quando a mudança afetar visualização Streamlit, notebooks ou saídas HTML difíceis de cobrir integralmente por automação.
