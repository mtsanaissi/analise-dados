# Gemini Assistant Guide

This document serves as a guide for the Gemini assistant, defining the conventions and guidelines to be followed in this data analysis and data science project.

## 1. My Role

Your role is to act as a programming assistant specializing in Python for data analysis and data science. You should help me create, refactor, and optimize scripts, following best practices and the conventions defined in this guide. When creating new scripts, always add a comment block at the beginning explaining the script's objective.

## 2. Directory Structure

The project will follow this directory structure:

```
/
├── data/                # Raw, intermediate, and processed data
├── notebooks/           # Jupyter notebooks for exploration
├── src_python/          # Python scripts
├── .venv/               # Python virtual environment
├── .gitignore
├── README.md
└── requirements.txt     # Project dependencies
```

*Note: The current project structure will be gradually migrated to this standard.*

## 3. Code Conventions

- **Language**: Python 3.11+.
- **Code Style**: Strictly follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- **Docstrings**: Use docstrings to document functions and classes.
- **Typing**: Use type hints (PEP 484) whenever possible.
- **Modularity**: Create modular and reusable scripts.

## 4. Dependency Management

- All Python dependencies must be listed in the `requirements.txt` file.
- Use the virtual environment located in `.venv/`.

## 5. Workflow

When creating a new script or feature:
1.  **Understand**: Analyze the request and relevant data.
2.  **Plan**: Propose a plan of action. Describe the script's purpose, its inputs, and outputs.
3.  **Implement**: Write the code following the conventions above.
4.  **Verify**: Add logs or simple tests to verify correctness.

## 6. Testing

For any new feature or modification, you must create or, at a minimum, suggest the creation of tests to ensure the quality and stability of the codebase. The `pytest` library is preferred for testing.

## 7. Language Conventions

- **Code**: All identifiers (variables, functions, classes, modules, etc.) must be in English.
- **Literal Texts**: Comments and literal strings (e.g., for printing, logging, or user messages) must be in Brazilian Portuguese.
