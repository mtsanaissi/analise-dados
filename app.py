# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Wrapper do Streamlit para iniciar a interface principal sem hacks de
#            importação via sys.path.
# Exemplo de uso: streamlit run app.py
#
# Autor: Jules
# Criado em: 23/03/2026
# Versão: 1.0
#
# Modificado por: Jules
# Modificado em: 23/03/2026
# Licença: MIT
# --------------------------------------------------------------------------------

from src.app_main_interface import main


if __name__ == "__main__":
    main()
