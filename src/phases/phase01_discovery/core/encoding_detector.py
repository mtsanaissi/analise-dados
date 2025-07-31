# -*- coding: utf-8 -*-

import os
import chardet
import sys

# Lista de extensões que são tipicamente binárias e não devem ser convertidas
BINARY_EXTENSIONS = ['xlsx', 'xls', 'ods', 'doc',
                     'docx', 'pdf', 'zip', 'gz', 'png', 'jpg']


def detect_encoding(file_path):
    """
    Tenta detectar o encoding de um arquivo lendo os primeiros 100KB.
    Retorna o encoding detectado e a confiança.
    """
    try:
        with open(file_path, 'rb') as f:  # Abre em modo binário
            raw_data = f.read(102400)  # Lê os primeiros 100KB
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result.get('confidence', 0)

            if encoding:
                return {"file_path": file_path, "encoding": encoding, "confidence": confidence}
            else:
                return {"file_path": file_path, "encoding": None, "confidence": 0, "error": "Não foi possível detectar o encoding."}

    except FileNotFoundError:
        return {"file_path": file_path, "encoding": None, "confidence": 0, "error": "Arquivo não encontrado durante a detecção de encoding."}
    except Exception as e:
        return {"file_path": file_path, "encoding": None, "confidence": 0, "error": f"Erro ao ler o arquivo para detecção: {e}"}


def convert_file_to_utf8(file_path, source_encoding):
    """
    Converte um arquivo para UTF-8 de forma segura.
    1. Renomeia o original para .bak (backup).
    2. Lê do backup com o encoding original e escreve no novo arquivo com UTF-8.
    3. Se falhar, restaura o backup.
    Retorna um dicionário com o status da conversão.
    """
    backup_path = str(file_path) + ".bak"

    try:
        # Passo 1: Criar o backup
        os.rename(file_path, backup_path)

        # Passo 2: Ler do backup e escrever no original com o novo encoding
        with open(backup_path, 'r', encoding=source_encoding, errors='replace') as infile, \
                open(file_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                outfile.write(line)

        return {"status": "success", "message": f"Arquivo '{os.path.basename(file_path)}' convertido para UTF-8.", "backup_path": backup_path}

    except Exception as e:
        # Se a conversão falhar, restaura o arquivo original
        os.rename(backup_path, file_path)
        return {"status": "error", "message": f"ERRO na conversão: {e}. Restaurando arquivo original.", "backup_path": backup_path}

def process_file_encoding(file_path):
    """
    Processa um único arquivo para detectar e converter seu encoding para UTF-8, se necessário.
    Retorna um dicionário com o resultado do processamento.
    """
    _, file_ext_with_dot = os.path.splitext(file_path)
    file_extension = file_ext_with_dot.lstrip('.').lower()

    if file_extension in BINARY_EXTENSIONS:
        return {"file": file_path, "status": "skipped", "reason": "binary_extension", "message": "Arquivo com extensão binária conhecida. Pulando verificação de encoding."}

    encoding_result = detect_encoding(file_path)
    if encoding_result["encoding"] is None:
        return {"file": file_path, "status": "skipped", "reason": "encoding_detection_failed", "message": encoding_result["error"]}

    detected_encoding = encoding_result["encoding"]
    confidence = encoding_result["confidence"]

    # Se a confiança for muito baixa, é mais seguro usar um padrão comum
    if confidence < 0.7:
        detected_encoding = 'latin-1' # Usando 'latin-1' como alternativa segura.

    if detected_encoding.lower() in ['utf-8', 'ascii', 'utf-8-sig']:
        return {"file": file_path, "status": "skipped", "reason": "already_utf8", "message": "O arquivo já está no formato UTF-8. Nenhuma ação necessária."}

    conversion_result = convert_file_to_utf8(file_path, detected_encoding)
    if conversion_result["status"] == "success":
        return {"file": file_path, "status": "converted", "original_encoding": detected_encoding, "message": conversion_result["message"]}
    else:
        return {"file": file_path, "status": "failed_conversion", "original_encoding": detected_encoding, "message": conversion_result["message"]}
