# JULES.md - Guidelines for AI-Assisted Development

Hello Jules. You are my specialized AI coding assistant for this data analysis toolkit project. Your primary goal is to help me expand and maintain this project while strictly adhering to its established architecture and quality standards. Please follow these guidelines in all your tasks.

## 1. Core Principles

1.  **Modularity**: Every piece of logic should be in its right place. Don't repeat code. If a function can be used by more than one script, it belongs in `utils.py`.
2.  **Robustness**: Code must be resilient. Anticipate issues like missing files, incorrect formats, or permission errors. Every script that performs I/O or parsing must have solid error handling.
3.  **Clarity**: Code is read more often than it is written. Use clear, descriptive names for variables and functions. Every script and function must be documented.
4.  **Configurability**: Scripts should be flexible. Avoid hardcoding paths, filenames, or important parameters. Use command-line arguments for user-configurable settings.

## 2. Environment and Dependencies

1.  **Virtual Environment**: All commands and executions must assume we are using the virtual environment located at `.venv/`.
2.  **Dependency Management**: If you need to use a new external library (e.g., `scipy`, `scikit-learn`), you must **explicitly ask for my permission before installing it**, preferrably giving an intro about it and why it is needed. After getting approval, you **must** add it to the `requirements.txt` file.

## 3. Project Structure and Naming

*   All new scripts must be placed in the appropriate subfolder within `\src\` based on their function:
    *   **`\01_discovery\`**: For scripts that diagnose and explore data without changing it.
    *   **`\02_standardize\`**: For scripts that standardize file formats (encoding, delimiters, etc.).
    *   **`\03_sanitize\`**: For scripts that fix the content of the data (e.g., correcting values).
    *   **`\04_preprocess\`**: For scripts that handle missing data, outliers, or initial feature selection.
    *   **`\05_transform\`**: For scripts that perform structural data transformations (e.g., binning, pivoting).
*   Script names should be descriptive and use snake_case (e.g., `analyze_data_volume.py`).

## 4. Standard Script Header
Every new Python script must start with a header block following this standard.

```python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------
# Descrição: [Descrição concisa do propósito do script em português.]
# Exemplo de uso: [Exemplo de uso do script a partir da linha de comando.]
#
# Autor: [Nome do autor]
# Criado em: [DD/MM/AAAA]
# Versão: 1.0
#
# Modificado por: [Nome de quem modificou]
# Modificado em: [DD/MM/AAAA]
# Licença: MIT
# --------------------------------------------------------------------------------
```

**Authorship:** When you, Jules, create a new script, set the `Autor` field to "Jules". When modifying an existing script, keep the original author and add your name to the `Modificado por` field. The license must always be `MIT`.

## 5. Workflow

When creating a new script or feature:
1.  **Understand**: Analyze the request and relevant data.
2.  **Plan**: Propose a plan of action. Describe the script's purpose, its inputs, and outputs.
3.  **Implement**: Write the code following all conventions listed here.
4.  **Verify**: Add logs or simple tests to verify correctness.

## 6. Testing

For any new feature or modification, you must create or, at a minimum, suggest the creation of tests to ensure the quality and stability of the codebase. The `pytest` library is preferred for testing.

## 7. Language Conventions

*   **Code**: All identifiers (variables, functions, classes, modules, etc.) must be in **English**.
*   **Literal Texts**: Comments, docstrings, and literal strings for user interaction (e.g., `print()`, `logging`, `argparse` help messages) must be in **Brazilian Portuguese**.

## 8. General Rules

*   Wrap all file I/O operations in `try...except` blocks, catching specific exceptions.
*   Provide user feedback using `print()` for progress and `sys.stderr` for errors.
*   Use **type hints** for all function signatures.

## 9. Communication and Versioning

*   **Language**: All communication with the user must be in **Brazilian Portuguese (pt-BR)**.
*   **Branching**: When creating a new branch, use a significant name in **pt-BR** that describes the feature or fix (e.g., `feature/padroniza-cabecalhos`, `fix/corrige-bug-leitura`).