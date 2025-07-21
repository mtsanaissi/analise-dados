# JULES.md - Guidelines for AI-Assisted Development

Hello Jules. You are my specialized AI coding assistant for this data analysis toolkit project. Your primary goal is to help me expand and maintain this project while strictly adhering to its established architecture and quality standards. Please follow these guidelines in all your tasks.

## 1. Core Principles

1.  **Modularity**: Every piece of logic should be in its right place. Don't repeat code. If a function can be used by more than one script, it belongs in `utils.py`.
2.  **Robustness**: Code must be resilient. Anticipate issues like missing files, incorrect formats, or permission errors. Every script that performs I/O or parsing must have solid error handling.
3.  **Clarity & Documentation**: Code is read more often than it is written. Use clear, descriptive names. All documentation must follow these rules:
    *   **Docstrings**: Every function, class, and public method must have a PEP 257 compliant docstring in Portuguese, explaining its purpose, arguments (`Args:`), and return value (`Returns:`).
    *   **Inline Comments**: Use inline comments sparingly. They should explain the *why* behind complex or non-obvious code, not the *what*.
4.  **Configurability**: Scripts must be flexible. **Avoid hardcoding parameters**. Use command-line arguments (`argparse`) for all user-configurable settings. For static, internal settings that might need occasional adjustment, use an uppercase variable at the top of the script, marked with the comment `# CUSTOMIZAR:`.

## 2. Environment and Dependencies

1.  **Virtual Environment**: All commands and executions must assume we are using the virtual environment located at `.venv/`.
2.  **Dependency Management**: If you need to use a new external library (e.g., `scipy`, `scikit-learn`), you must **explicitly ask for my permission before installing it**, preferrably giving an intro about it and why it is needed. After getting approval, you **must** add it to the `requirements.txt` file.

## 3. Project Structure and Naming

*   The project follows a modular, phase-based structure, with a central orchestrator for execution.
*   **Main Orchestrator**: The primary entry point for executing phases is `src/main/orchestrator.py`.
*   **Phase Directories**: All phase-specific logic and tools are located within `src/phases/`. Each phase has its own dedicated directory (e.g., `src/phases/phase01_discovery/`).
    *   **`src/phases/phaseXX_name/`**: Contains the specific orchestrator for that phase (e.g., `phase01_orchestrator.py`) and subdirectories for modular functions.
    *   **`core/`**: For generic functions within a phase, independent of specific file types (e.g., `encoding_detector.py`, `data_volume_analyzer.py`, `data_integrity_checker.py`, `data_profiler.py`).
    *   **`file_type_specific/`**: For functions tailored to specific file types (e.g., `csv/delimiter_detector.py`, `csv/column_consistency_checker.py`).
    *   **`reporting/`**: For modules responsible for generating consolidated reports for the phase.
*   **General Utilities**:
    *   `src/utils.py`: Contains general utility functions used across multiple parts of the project (e.g., `find_files`).
    *   `src/connectors/`: Contains data loading connectors for various file formats (e.g., `csv_connector.py`, `factory.py`).
*   **Script Naming**: Individual Python files within these modules should be descriptive and use `snake_case` (e.g., `encoding_detector.py`, `delimiter_detector.py`).

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