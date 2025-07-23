# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Ponto de entrada principal para a execução do projeto.
#            Este script garante que os caminhos de importação estejam corretos
#            antes de chamar o orquestrador principal.
# Exemplo de uso: python src/run.py -d data/meu_projeto -p discovery
#
# Autor: Gemini
# Criado em: 23/07/2025
# Versão: 1.0
#
# Licença: MIT
# --------------------------------------------------------------------------------

from main.orchestrator import main

if __name__ == "__main__":
    """
    Ponto de entrada que executa a função principal do orquestrador.
    """
    main()
