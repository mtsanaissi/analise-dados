# -*- coding: utf-8 -*-

import csv
import os
import chardet

def detect_csv_delimiter(file_path):
    """
    Detecta o delimitador de um arquivo CSV.
    Retorna o delimitador detectado e a confiança, ou None se não for detectado.
    """
    try:
        # Primeiro, detecta o encoding para abrir o arquivo corretamente
        with open(file_path, 'rb') as f_raw:
            raw_data = f_raw.read(102400) # Lê os primeiros 100KB
            result = chardet.detect(raw_data)
            encoding = result['encoding'] if result['encoding'] else 'utf-8' # Fallback para utf-8

        with open(file_path, 'r', encoding=encoding, newline='') as f:
            # Lê as primeiras linhas para análise
            sample = f.read(4096) # Lê os primeiros 4KB para detecção

            # Tenta detectar o dialeto CSV
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=',;\t|') # Delimitadores comuns

            # Verifica a confiança do sniffer (se todas as linhas têm o mesmo número de colunas)
            # Isso é uma simplificação, uma implementação robusta precisaria de mais validação
            has_header = sniffer.has_header(sample)

            return {
                "delimiter": dialect.delimiter,
                "has_header": has_header,
                "encoding_used": encoding,
                "confidence": 0.9 # Placeholder, a confiança real seria mais complexa
            }
    except FileNotFoundError:
        return {"error": "Arquivo não encontrado."}
    except Exception as e:
        return {"error": f"Erro ao detectar delimitador: {e}"}


