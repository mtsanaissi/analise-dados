# Gemini's Learning Log

This document serves as a log for Gemini to learn from its mistakes and improve its performance.

## Common Errors and Corrections

- **`list_directory` with relative paths:** The `list_directory` tool requires an absolute path. I will ensure to always provide an absolute path to this tool.
- **Ignoring instructions for Jules:** I will pay closer attention to the instructions provided for generating prompts for Jules, especially regarding the structure and content of the prompts.
- **Using fixed absolute paths in tests/code:** When creating or modifying tests and code, always use paths relative to the project root directory or construct absolute paths using `os.path.join(project_root, relative_path)`. Never use fixed absolute paths from the user's environment (e.g., `D:/w/analise-dados/...`), as the agent's execution environment is a copy of the repository.
