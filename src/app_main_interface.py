# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: Interface principal do Streamlit para o kit de ferramentas de análise de dados.
#            Permite ao usuário selecionar a fase do projeto e o caminho dos dados,
#            executando o processo correspondente e exibindo a saída em tempo real.
# Exemplo de uso: streamlit run src/app_main_interface.py
#
# Autor: Jules
# Criado em: 01/08/2025
# Versão: 1.0
#
# Modificado por: -
# Modificado em: -
# Licença: MIT
# --------------------------------------------------------------------------------

import streamlit as st
import subprocess
import os
import re
import tempfile
import chardet
import json
from src.utils import build_command
from src.connectors.factory import get_data_loader


def load_lookup_columns(project_path: str, lookup_file: str, delimiter: str = None) -> list:
    """
    Carrega as colunas de um arquivo de lookup.

    Args:
        project_path (str): O caminho do projeto de dados.
        lookup_file (str): O nome do arquivo de lookup.
        delimiter (str, optional): O delimitador para arquivos CSV. Defaults to None.

    Returns:
        list: A lista de colunas do arquivo de lookup.
    """
    if not lookup_file or not project_path:
        return []

    try:
        # Constrói o caminho absoluto para o lookup_file
        file_path = os.path.join(project_path, lookup_file)
        if not os.path.exists(file_path):
            # Tenta como caminho absoluto se não encontrar no projeto
            if os.path.exists(lookup_file):
                file_path = lookup_file
            else:
                st.warning(f"Arquivo de lookup não encontrado: {lookup_file}")
                return []

        connector = get_data_loader(file_path, delimiter=delimiter)
        df = connector.read()

        if df is not None and not df.empty:
            return df.columns.tolist()
        return []
    except Exception as e:
        st.error(f"Erro ao carregar colunas do arquivo de lookup: {e}")
        return []


def run_process(command: list[str], output_placeholder):
    """
    Executa um comando em um subprocesso e exibe a saída em tempo real.

    Args:
        command (List[str]): O comando a ser executado.
        output_placeholder: O elemento Streamlit onde a saída será exibida.

    Returns:
        Tuple[int, str]: O código de retorno e a saída completa do processo.
    """
    process = None
    full_output = ""
    return_code = -1
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            env=env
        )
        for line in iter(process.stdout.readline, ''):
            full_output += line
            output_placeholder.code(full_output)
        process.stdout.close()
        return_code = process.wait()
    except FileNotFoundError:
        full_output += f"\nErro: O comando '{command[0]}' não foi encontrado. Verifique se o Python está no PATH."
    except Exception as e:
        full_output += f"\nOcorreu um erro inesperado: {e}"
    finally:
        if process and process.poll() is None:
            process.kill()
    return return_code, full_output


def find_report_path(output: str) -> str | None:
    """
    Encontra o caminho de um arquivo de relatório na saída do processo.

    Args:
        output (str): A saída do processo.

    Returns:
        str | None: O caminho do relatório, se encontrado.
    """
    match = re.search(r"Relatório salvo em: (.*)", output)
    if match:
        return match.group(1).strip()
    return None


def main_interface():
    st.set_page_config(
        layout="wide", page_title="Kit de Ferramentas de Análise de Dados")
    st.title("Painel de Controle do Kit de Ferramentas")

    # Inicialização do estado da sessão
    # Inicialização do estado da sessão
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'last_run_results' not in st.session_state:
        st.session_state.last_run_results = None
    if 'temp_config_path' not in st.session_state:
        st.session_state.temp_config_path = None

    with st.sidebar:
        st.header("Configurações de Execução")
        project_path = st.text_input(
            "Caminho do Projeto de Dados",
            "data/sample",
            help="Forneça o caminho para o diretório do projeto contendo os dados.",
            disabled=st.session_state.running
        )
        phases = ["discovery", "treatment"]
        selected_phase = st.selectbox(
            "Fase do Projeto",
            options=phases,
            help="Selecione a fase do projeto a ser executada.",
            disabled=st.session_state.running
        )

        discovery_args = {}
        treatment_args = {}

        if selected_phase == "discovery":
            with st.expander("Opções da Fase de Discovery", expanded=True):
                discovery_args["compare_fields"] = st.checkbox(
                    "Comparar Campos/Colunas", help="Habilita a comparação de campos/colunas.", disabled=st.session_state.running)
                discovery_args["compare_types"] = st.checkbox(
                    "Comparar Tipos de Dados", help="Habilita a comparação de tipos de dados.", disabled=st.session_state.running)
                discovery_args["report_output"] = st.selectbox("Formato do Relatório", options=[
                                                               "json", "html"], help="Selecione o formato do relatório.", disabled=st.session_state.running)
                discovery_args["char_cleanup_path"] = st.text_input(
                    "Gerar Config. de Limpeza", help="Opcional. Especifique um caminho para o arquivo de configuração de limpeza.", disabled=st.session_state.running)

        if selected_phase == "treatment":
            with st.expander("Opções da Fase de Treatment", expanded=True):
                operations = ["Selecione uma operação", "Remover Espaços", "Substituir Valores",
                              "Encontrar e Substituir Texto", "Concatenar Dados", "Enriquecer Dados"]
                treatment_args["operation"] = st.selectbox(
                    "Operação de Tratamento", options=operations, help="Selecione a operação de tratamento.", disabled=st.session_state.running)

                # Operação de Enriquecimento de Dados
                if treatment_args["operation"] == "Enriquecer Dados":
                    st.subheader("Configuração de Enriquecimento")

                    # Inicializa o estado da sessão para os campos do formulário
                    if 'enrich_main_file' not in st.session_state:
                        st.session_state.enrich_main_file = ''
                    if 'enrich_lookup_file' not in st.session_state:
                        st.session_state.enrich_lookup_file = ''
                    if 'enrich_main_key' not in st.session_state:
                        st.session_state.enrich_main_key = ''
                    if 'enrich_lookup_key' not in st.session_state:
                        st.session_state.enrich_lookup_key = ''
                    if 'enrich_columns_to_add' not in st.session_state:
                        st.session_state.enrich_columns_to_add = []
                    if 'lookup_columns' not in st.session_state:
                        st.session_state.lookup_columns = []

                    main_file = st.text_input("Arquivo Principal",
                                              value=st.session_state.enrich_main_file,
                                              help="Nome do arquivo principal a ser enriquecido (ex: `vendas.csv`).",
                                              disabled=st.session_state.running)

                    lookup_file = st.text_input("Arquivo de Lookup",
                                                value=st.session_state.enrich_lookup_file,
                                                help="Caminho para o arquivo de lookup (ex: `produtos.xlsx`).",
                                                disabled=st.session_state.running)

                    # Carrega as colunas do arquivo de lookup dinamicamente
                    if lookup_file and lookup_file != st.session_state.get('last_lookup_file'):
                        st.session_state.lookup_columns = load_lookup_columns(
                            project_path, lookup_file)
                        st.session_state.last_lookup_file = lookup_file

                    main_key = st.text_input("Chave no Principal",
                                             value=st.session_state.enrich_main_key,
                                             help="Nome da coluna chave no arquivo principal.",
                                             disabled=st.session_state.running)

                    lookup_key = st.text_input("Chave no Lookup",
                                               value=st.session_state.enrich_lookup_key,
                                               help="Nome da coluna chave no arquivo de lookup.",
                                               disabled=st.session_state.running)

                    columns_to_add = st.multiselect("Colunas a Adicionar",
                                                    options=st.session_state.lookup_columns,
                                                    default=st.session_state.enrich_columns_to_add,
                                                    help="Selecione as colunas do arquivo de lookup para adicionar ao principal.",
                                                    disabled=st.session_state.running)

                    # Atualiza o estado da sessão com os valores atuais
                    st.session_state.enrich_main_file = main_file
                    st.session_state.enrich_lookup_file = lookup_file
                    st.session_state.enrich_main_key = main_key
                    st.session_state.enrich_lookup_key = lookup_key
                    st.session_state.enrich_columns_to_add = columns_to_add

                # Lógica genérica para outras operações que usam upload de YAML
                elif treatment_args["operation"] in ["Substituir Valores", "Encontrar e Substituir Texto", "Concatenar Dados"]:
                    uploaded_file = st.file_uploader("Carregar Arquivo de Configuração YAML", type=[
                        'yaml', 'yml'], help="Faça o upload do arquivo de configuração YAML.", disabled=st.session_state.running)
                    if uploaded_file is not None and st.session_state.temp_config_path is None:
                        # Processar o arquivo imediatamente após o upload
                        content_bytes = uploaded_file.getvalue()
                        detected_encoding = chardet.detect(
                            content_bytes)['encoding'] or 'utf-8'
                        decoded_content = content_bytes.decode(
                            detected_encoding)

                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}", mode='w', encoding='utf-8') as tmp:
                            st.session_state.temp_config_path = tmp.name
                            tmp.write(decoded_content)
                        st.rerun()

        button_label = "Nova Execução" if st.session_state.last_run_results else "Executar"
        if st.sidebar.button(button_label, type="primary", use_container_width=True, disabled=st.session_state.running):
            if not project_path or not os.path.isdir(project_path):
                st.error(
                    f"O caminho '{project_path}' não é um diretório válido.")
            else:
                st.session_state.last_run_results = None
                st.session_state.running = True
                st.rerun()

        if st.sidebar.button("Limpar Resultados", use_container_width=True, disabled=st.session_state.running):
            if st.session_state.temp_config_path and os.path.exists(st.session_state.temp_config_path):
                os.remove(st.session_state.temp_config_path)

            # Limpa todo o estado da sessão
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Lógica de execução do processo
    if st.session_state.running:
        try:
            if selected_phase == "treatment":
                # Para "Enriquecer Dados", gera o YAML dinamicamente
                if treatment_args.get("operation") == "Enriquecer Dados":
                    enrich_config = {
                        'main_file': st.session_state.get('enrich_main_file'),
                        'lookup_file': st.session_state.get('enrich_lookup_file'),
                        'main_key': st.session_state.get('enrich_main_key'),
                        'lookup_key': st.session_state.get('enrich_lookup_key'),
                        'columns_to_add': st.session_state.get('enrich_columns_to_add')
                    }

                    # Validação simples
                    if not all(enrich_config.values()):
                        st.error(
                            "Todos os campos de configuração de enriquecimento devem ser preenchidos.")
                        st.session_state.running = False
                        st.rerun()
                        return

                    with tempfile.NamedTemporaryFile(delete=False, suffix="_enrich_config.yaml", mode='w', encoding='utf-8') as tmp:
                        import yaml
                        yaml.dump(enrich_config, tmp)
                        st.session_state.temp_config_path = tmp.name
                    treatment_args["config_file_path"] = st.session_state.temp_config_path

                # Para outras operações, usa o arquivo de upload, se houver
                elif st.session_state.get('temp_config_path'):
                    treatment_args["config_file_path"] = st.session_state.temp_config_path

            command = build_command(
                project_path, selected_phase, discovery_args=discovery_args, treatment_args=treatment_args)
            st.session_state.last_command = command
            st.info(f"Executando comando: `{' '.join(command)}`")
            output_placeholder = st.empty()
            output_placeholder.code("Iniciando a execução...")

            with st.spinner("Processando... Por favor, aguarde."):
                return_code, full_output = run_process(
                    command, output_placeholder)

            st.session_state.last_run_results = {
                "return_code": return_code, "full_output": full_output, "selected_phase": selected_phase}
        finally:
            # A limpeza do arquivo temporário agora é feita pelo botão "Limpar Resultados"
            st.session_state.running = False
            st.rerun()

    # Exibição dos resultados da última execução
    if st.session_state.get('last_run_results'):
        results = st.session_state.last_run_results
        return_code = results.get("return_code")
        full_output = results.get("full_output", "")
        selected_phase = results.get("selected_phase", "Desconhecida")
        executed_command = st.session_state.get(
            "last_command", "Comando não encontrado.")

        # Mensagem de status
        if return_code == 0:
            st.success(f"Fase '{selected_phase}' concluída com sucesso!")
        else:
            st.error("Ocorreu um erro durante a execução.")

        # Expander para detalhes da execução
        with st.expander("Ver Detalhes da Execução"):
            st.subheader("Comando Executado")
            st.code(' '.join(executed_command), language='bash')
            st.subheader("Log de Saída")
            st.code(full_output, language='bash')

        # Visualização do relatório
        report_path = find_report_path(full_output)
        if report_path and os.path.exists(report_path):
            st.subheader("Visualizador de Relatório")

            try:
                if report_path.endswith('.html'):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(
                        html_content, height=600, scrolling=True)

                elif report_path.endswith('.json'):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        json_content = json.load(f)
                    st.json(json_content)

                # Manter o botão de download
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Baixar Relatório",
                        data=f,
                        file_name=os.path.basename(report_path),
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Erro ao ler ou exibir o arquivo de relatório: {e}")


if __name__ == "__main__":
    main_interface()
