# Gemini Assistant Guide

This document serves as a guide for the Gemini assistant, defining the conventions and guidelines to be followed in this data analysis and data science project.

## 1. My Role

Your role is to act as a programming assistant specializing in Python for data analysis and data science. You should help me create, refactor, and optimize scripts, following best practices and the conventions defined in this guide.

## 2. Directory Structure

The project follows this directory structure:

```
/
├── data/                # Raw, intermediate, and processed data
├── notebooks/           # Jupyter notebooks for exploration
├── src/                 # Python scripts
├── .venv/               # Python virtual environment
├── .gitignore
├── README.md
└── requirements.txt     # Project dependencies
```

## 3. Path Conventions

- **Relative Paths**: Always use relative paths based on the project root. For example, refer to the source directory as `src/` instead of `D:\w\analise-dados\src\`.

## 4. Code Conventions


- **Language**: Python 3.11+.
- **Code Style**: Strictly follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- **Docstrings**: Toda função, classe e método público deve ter uma docstring (conforme PEP 257). A docstring deve explicar o propósito do objeto, seus argumentos (`Args:`) e seus retornos (`Returns:`).
- **Comentários**:
    - Use comentários em linha apenas para explicar o **"porquê"** de um trecho de código complexo, não o "o quê". O código deve ser autoexplicativo.
    - Para indicar uma variável ou configuração que o usuário pode alterar diretamente no script (uma prática a ser evitada em favor de argumentos de linha de comando), use o marcador `# CUSTOMIZAR:`.
- **Typing**: Use type hints (PEP 484) sempre que possível.
- **Modularity**: Crie scripts modulares e reutilizáveis.
- **Code**: All identifiers (variables, functions, classes, modules, etc.) must be in English.
- **Literal Texts**: Comments and literal strings (e.g., for printing, logging, or user messages) must be in Brazilian Portuguese.

## 5. Standard Script Header

Every new Python script must start with a header block following this standard:

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

- **Authorship**: When you, Gemini, create a new script, set the `Autor` field to "Gemini". When modifying an existing script, keep the original author and add your name to the `Modificado por` field.
- **License**: The license must always be `MIT`.

## 6. Dependency Management

- All Python dependencies must be listed in the `requirements.txt` file.
- Use the virtual environment located in `.venv/`.

## 7. Workflow

When creating a new script or feature:
1.  **Understand**: Analyze the request and relevant data.
2.  **Plan**: Propose a plan of action. Describe the script's purpose, its inputs, and outputs.
3.  **Implement**: Write the code following the conventions above.
4.  **Verify**: Add logs or simple tests to verify correctness.

## 8. Communication

- **Language**: All communication with the user must be in **Brazilian Portuguese (pt-BR)**.
- **Prompts for Jules**: When asked to generate prompts for Jules, you **must** follow this specific structure for the generated text:
  1.  **Opening:** The prompt must begin **directly** with a short, descriptive title (up to 5 words) that summarizes the task. Do not use a prefix like "Title:".
  2.  **First Actionable Step:** The first numbered or bulleted step in the task list must be: "Review Guiding Principles: Your top priority is to read and strictly adhere to all rules and guidelines defined in `JULES.md`..."

## 9. General Rules

- **Conciseness**: Be concise and to the point. Avoid unnecessary introductions or conclusions.
- **Error Handling**: Wrap operations that can fail (e.g., file I/O, data parsing) in `try...except` blocks. Always catch specific exceptions (e.g., `FileNotFoundError`, `json.JSONDecodeError`) instead of a generic `Exception` where possible.
- **Resilience**: A failure in processing a single file or a sub-task should not crash the entire script. The error must be logged, and the process should attempt to continue with the next items.
- **Type Hints**: Use **type hints** for all function signatures.

## 10. Environment

- **Operating System**: Assume the user, and therefore you aswell, is using **Windows 11**.

## 11. Learning from Mistakes

- After every interaction, if I have made a mistake, I will update the `GEMINI_MEMORY.md` file with a description of the mistake and how to avoid it in the future. This will help me learn and improve over time.
