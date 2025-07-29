import os
import pytest
from src.phases.phase01_discovery.core.encoding_detector import detect_encoding, convert_file_to_utf8, process_file_encoding

@pytest.fixture
def latin1_file(tmp_path):
    content = "café".encode('latin-1')
    file = tmp_path / "latin1.txt"
    file.write_bytes(content)
    return str(file)

def test_detect_encoding(latin1_file):
    result = detect_encoding(latin1_file)
    # The detected encoding can be something else, like 'iso-8859-1'
    assert 'latin-1' in result['encoding'].lower() or 'iso-8859-1' in result['encoding'].lower()

def test_convert_file_to_utf8(latin1_file):
    convert_file_to_utf8(latin1_file, 'latin-1')
    with open(latin1_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "café"

def test_process_file_encoding_converts(latin1_file):
    result = process_file_encoding(latin1_file)
    assert result['status'] == 'converted'
    assert 'latin-1' in result['original_encoding'].lower() or 'iso-8859-1' in result['original_encoding'].lower()
    with open(latin1_file, 'r', encoding='utf-8') as f:
        assert f.read() == 'café'

def test_process_file_encoding_skips_utf8(tmp_path):
    utf8_file = tmp_path / "utf8.txt"
    utf8_file.write_text("café", encoding='utf-8-sig') # Use utf-8-sig to ensure it's identifiable
    result = process_file_encoding(str(utf8_file))
    assert result['status'] == 'skipped'
    assert result['reason'] == 'already_utf8'
